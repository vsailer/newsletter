# -*- coding: utf-8 -*-
"""Models for emencia.django.newsletter"""
from smtplib import SMTP
from datetime import datetime
from datetime import timedelta
from hashids import Hashids

from django.conf import settings
from django.db import models
from django.utils.encoding import smart_str
from django.urls import reverse
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group

from emencia.django.newsletter.managers import ContactManager
from emencia.django.newsletter.settings import DEFAULT_HEADER_REPLY
from emencia.django.newsletter.settings import DEFAULT_HEADER_SENDER
from emencia.django.newsletter.settings import NEWSLETTER_BASE_PATH
# from emencia.django.newsletter.utils.vcard import vcard_contact_export

# Patch for Python < 2.6
try:
    getattr(SMTP, 'ehlo_or_helo_if_needed')
except AttributeError:
    def ehlo_or_helo_if_needed(self):
        if self.helo_resp is None and self.ehlo_resp is None:
            if not (200 <= self.ehlo()[0] <= 299):
                (code, resp) = self.helo()
                if not (200 <= code <= 299):
                    raise SMTPHeloError(code, resp)
    SMTP.ehlo_or_helo_if_needed = ehlo_or_helo_if_needed


class SMTPServer(models.Model):
    """Configuration of a SMTP server"""
    name = models.CharField(_('name'), max_length=255)
    host = models.CharField(_('server host'), max_length=255)
    user = models.CharField(_('server user'), max_length=128, blank=True,
                            help_text=_('Leave it empty if the host is public.'))
    password = models.CharField(_('server password'), max_length=128, blank=True,
                                help_text=_('Leave it empty if the host is public.'))
    port = models.IntegerField(_('server port'), default=25)
    tls = models.BooleanField(_('server use TLS'))

    headers = models.TextField(_('custom headers'), blank=True,
                               help_text=_('key1: value1 key2: value2, splitted by return line.'))
    mails_hour = models.IntegerField(_('mails per hour'), default=0)

    def connect(self):
        """Connect the SMTP Server"""
        smtp = SMTP(smart_str(self.host), int(self.port))
        smtp.ehlo_or_helo_if_needed()
        if self.tls:
            smtp.starttls()
            smtp.ehlo_or_helo_if_needed()

        if self.user or self.password:
            smtp.login(smart_str(self.user), smart_str(self.password))
        return smtp

    def credits(self):
        """Return how many mails the server can send"""
        return self.mails_hour
        if not self.mails_hour:
            return 1000 # Arbitrary value

        last_hour = datetime.now() - timedelta(hours=1)
        sent_last_hour = ContactMailingStatus.objects.filter(
            models.Q(status=ContactMailingStatus.SENT) |
            models.Q(status=ContactMailingStatus.SENT_TEST),
            newsletter__server=self,
            creation_date__gte=last_hour).count()
        return self.mails_hour - sent_last_hour

    @property
    def custom_headers(self):
        if self.headers:
            headers = {}
            for header in self.headers.split('\r\n'):
                if header:
                    key, value = header.split(':')
                    headers[key.strip()] = value.strip()
            return headers
        return {}

    def __str__(self):
        return '%s (%s)' % (self.name, self.host)

    class Meta:
        verbose_name = _('SMTP server')
        verbose_name_plural = _('SMTP servers')


class HashContactManager(ContactManager):
    ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    MIN_LENGTH = 7
    SALT = 'edn' + settings.SECRET_KEY

    def to_hashid(self, i):
        h = Hashids(salt=self.SALT, alphabet=self.ALPHABET, min_length=self.MIN_LENGTH)
        return self.ALPHABET[i%len(self.ALPHABET)]+h.encode(i)

    def from_hashid(self, i):
        i = i[1:]
        h = Hashids(salt=self.SALT, alphabet=self.ALPHABET, min_length=self.MIN_LENGTH)
        ids = h.decode(i)
        if len(ids):
            return ids[0]
        else:
            return 0

    def get_by_hashid(self, hashid):
        id = self.from_hashid(hashid)
        return self.get_queryset().get(id=id)


class Contact(models.Model):
    """Contact for emailing"""
    email = models.EmailField(_('email'), unique=True)
    title = models.CharField(_('Bezeichnung'), max_length=255, blank=True)
    degree = models.CharField(_('Titel'), max_length=50, blank=True)
    company = models.CharField(_('Firma'), max_length=255, blank=True)
    salutation = models.CharField(_('Anrede'), max_length=50, blank=True)
    first_name = models.CharField(_('first name'), max_length=100, blank=True)
    last_name = models.CharField(_('last name'), max_length=100, blank=True)

    subscriber = models.BooleanField(_('subscriber'), default=True)
    valid = models.BooleanField(_('valid email'), default=True)
    tester = models.BooleanField(_('contact tester'), default=False)

    content_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    modification_date = models.DateTimeField(_('modification date'), auto_now=True)

    activation_date = models.DateTimeField(_('Bestätigungsdatum'), null=True, blank=True)

    import_id = models.CharField(_('ImportID'), editable=False, null=True, blank=True, max_length=255)
    source = models.CharField(_('Quelle'), default="web", max_length=20)
    syncing = models.BooleanField(_('wird synchronisiert'), default=False, editable=False)

    objects = HashContactManager()

    def subscriptions(self):
        """Return the user subscriptions"""
        return MailingList.objects.filter(subscribers=self)

    def unsubscriptions(self):
        """Return the user unsubscriptions"""
        return MailingList.objects.filter(unsubscribers=self)

    def vcard_format(self):
        return vcard_contact_export(self)

    def mail_format(self):
        if self.first_name and self.last_name:
            return '%s %s <%s>' % (self.last_name, self.first_name, self.email)
        return self.email
    mail_format.short_description = _('mail format')

    def get_absolute_url(self):
        if self.content_type and self.object_id:
            return self.content_object.get_absolute_url()
        return reverse('admin:newsletter_contact_change', args=(self.pk,))

    def __str__(self):
        if self.first_name and self.last_name:
            return '%s %s' % (self.last_name, self.first_name)
        return '%s' % self.email

    class Meta:
        ordering = ('creation_date',)
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')

    def get_hashid(self):
        return Contact.objects.to_hashid(self.id)


class MailingList(models.Model):
    """Mailing list"""
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    subscribers = models.ManyToManyField(Contact, verbose_name=_('subscribers'),
                                         related_name='mailinglist_subscriber')
    unsubscribers = models.ManyToManyField(Contact, verbose_name=_('unsubscribers'),
                                           related_name='mailinglist_unsubscriber', blank=True)

    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    modification_date = models.DateTimeField(_('modification date'), auto_now=True)

    def subscribers_count(self):
        return self.subscribers.all().count()
    subscribers_count.short_description = _('subscribers')

    def unsubscribers_count(self):
        return self.unsubscribers.all().count()
    unsubscribers_count.short_description = _('unsubscribers')

    def expedition_set(self):
        unsubscribers_id = self.unsubscribers.values_list('id', flat=True)
        return self.subscribers.valid_subscribers().exclude(
            id__in=unsubscribers_id)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('creation_date',)
        verbose_name = _('mailing list')
        verbose_name_plural = _('mailing lists')


class MultiMailingListWrapper(object):
    def __init__(self, newsletter):
        self.newsletter = newsletter

    def expedition_set(self):
        ids = []
        for mailing_list in self.newsletter.mailing_lists.all():
            ids += list(mailing_list.expedition_set().values_list('id', flat=True))
        return Contact.objects.filter(id__in=ids)

    @property
    def unsubscribers(self):
        ids = []
        for mailing_list in self.newsletter.mailing_lists.all():
            ids += list(mailing_list.unsubscribers.values_list('id', flat=True))
        return Contact.objects.filter(id__in=ids)

    @property
    def subscribers(self):
        ids = []
        for mailing_list in self.newsletter.mailing_lists.all():
            ids += list(mailing_list.subscribers.values_list('id', flat=True))
        return Contact.objects.filter(id__in=ids)

    @property
    def name(self):
        names = list(self.newsletter.mailing_lists.values_list('name', flat=True))
        return ", ".join(names)

    def subscribers_count(self):
        return self.subscribers.all().count()
    subscribers_count.short_description = _('subscribers')

    def unsubscribers_count(self):
        return self.unsubscribers.all().count()
    unsubscribers_count.short_description = _('unsubscribers')

    def __str__(self):
        return ", ".join([l.name for l in self.newsletter.mailing_lists.all()])



class Newsletter(models.Model):
    """Newsletter to be sended to contacts"""
    DRAFT  = 0
    WAITING  = 1
    SENDING = 2
    SENT = 4
    CANCELED = 5

    STATUS_CHOICES = ((DRAFT, _('draft')),
                      (WAITING, _('waiting sending')),
                      (SENDING, _('sending')),
                      (SENT, _('sent')),
                      (CANCELED, _('canceled')),
                      )

    title = models.CharField(_('title'), max_length=255)
    content = models.TextField(_('content'), help_text=_('Or paste an URL.'),
                               default='')

    # mailing_list = models.ForeignKey(MailingList, verbose_name=_('mailing list'))
    mailing_lists = models.ManyToManyField(MailingList, verbose_name=_('mailing lists'))
    test_contacts = models.ManyToManyField(Contact, verbose_name=_('test contacts'),
                                           blank=True)

    server = models.ForeignKey(SMTPServer, verbose_name=_('smtp server'),
                               default=1, on_delete=models.PROTECT)
    header_sender = models.CharField(_('sender'), max_length=255,
                                     default=DEFAULT_HEADER_SENDER)
    header_reply = models.CharField(_('reply to'), max_length=255,
                                    default=DEFAULT_HEADER_REPLY)

    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=DRAFT)
    sending_date = models.DateTimeField(_('sending date'), default=datetime.now)

    slug = models.SlugField(help_text=_('Used for displaying the newsletter on the site.'), unique=True)
    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    modification_date = models.DateTimeField(_('modification date'), auto_now=True)

    def mails_sent(self):
        return self.contactmailingstatus_set.filter(status=ContactMailingStatus.SENT).count()

    @property
    def mailing_list(self):
        return MultiMailingListWrapper(self)

    def get_absolute_url(self):
        return reverse('newsletter_newsletter_preview', args=(self.slug,))

    def get_historic_url(self):
        return reverse('newsletter_newsletter_historic', args=(self.slug,))

    def get_statistics_url(self):
        return reverse('newsletter_newsletter_statistics', args=(self.slug,))

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('creation_date',)
        verbose_name = _('newsletter')
        verbose_name_plural = _('newsletters')
        permissions = (('can_change_status', ugettext('Can change status')),)


class Link(models.Model):
    """Link sended in a newsletter"""
    title = models.CharField(_('title'), max_length=255)
    url = models.CharField(_('url'), max_length=255)

    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)

    def get_absolute_url(self):
        return self.url

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('creation_date',)
        verbose_name = _('link')
        verbose_name_plural = _('links')


def get_newsletter_storage_path(self, filename):
    return '/'.join([NEWSLETTER_BASE_PATH, self.newsletter.slug, filename])

class Attachment(models.Model):
    """Attachment file in a newsletter"""

    newsletter = models.ForeignKey(Newsletter, verbose_name=_('newsletter'), on_delete=models.PROTECT)
    title = models.CharField(_('title'), max_length=255)
    file_attachment = models.FileField(_('file to attach'),
                                       upload_to=get_newsletter_storage_path)

    class Meta:
        verbose_name = _('attachment')
        verbose_name_plural = _('attachments')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return self.file_attachment.url


class ContactMailingStatus(models.Model):
    """Status of the reception"""
    SENT_TEST = -1
    SENT = 0
    ERROR = 1
    INVALID = 2
    OPENED = 4
    OPENED_ON_SITE = 5
    LINK_OPENED = 6
    UNSUBSCRIPTION = 7

    STATUS_CHOICES = ((SENT_TEST, _('sent in test')),
                      (SENT, _('sent')),
                      (ERROR, _('error')),
                      (INVALID, _('invalid email')),
                      (OPENED, _('opened')),
                      (OPENED_ON_SITE, _('opened on site')),
                      (LINK_OPENED, _('link opened')),
                      (UNSUBSCRIPTION, _('unsubscription')),
                      )

    newsletter = models.ForeignKey(Newsletter, verbose_name=_('newsletter'), on_delete=models.PROTECT)
    contact = models.ForeignKey(Contact, verbose_name=_('contact'), on_delete=models.PROTECT)
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES)
    link = models.ForeignKey(Link, verbose_name=_('link'),
                             blank=True, null=True, on_delete=models.PROTECT)

    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)

    def __str__(self):
        return '%s : %s : %s' % (self.newsletter.__str__(),
                                 self.contact.__str__(),
                                 self.get_status_display())

    class Meta:
        ordering = ('creation_date',)
        verbose_name = _('contact mailing status')
        verbose_name_plural = _('contact mailing statuses')

class WorkGroup(models.Model):
    """Work Group for privatization of the ressources"""
    name = models.CharField(_('name'), max_length=255)
    group = models.ForeignKey(Group, verbose_name=_('permissions group'), on_delete=models.PROTECT)

    contacts = models.ManyToManyField(Contact, verbose_name=_('contacts'),
                                      blank=True)
    mailinglists = models.ManyToManyField(MailingList, verbose_name=_('mailing lists'),
                                          blank=True)
    newsletters = models.ManyToManyField(Newsletter, verbose_name=_('newsletters'),
                                         blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('workgroup')
        verbose_name_plural = _('workgroups')
