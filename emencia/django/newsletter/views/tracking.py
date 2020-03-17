"""Views for emencia.django.newsletter Tracking"""
import base64

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation

from emencia.django.newsletter.models import Link
from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.utils.tokens import untokenize
from emencia.django.newsletter.models import ContactMailingStatus
from emencia.django.newsletter.settings import TRACKING_IMAGE

#### Patched Redirect Supporting MailTo Links
from django.http import HttpResponse
from urllib.parse import urljoin, urlparse
from django.utils.encoding import smart_str, iri_to_uri

class PatchedHttpResponseRedirect(HttpResponse):
    allowed_schemes = ['tel', 'http', 'https', 'ftp', 'mailto']
    status_code = 302

    def __init__(self, redirect_to):
        super(PatchedHttpResponseRedirect, self).__init__()
        if redirect_to.startswith('internal://'):
          from maisen.cmstools.internallinks import resolve_internal_link
          redirect_to = resolve_internal_link(redirect_to)

        parsed = urlparse(redirect_to)
        if parsed.scheme and parsed.scheme not in self.allowed_schemes:
            raise SuspiciousOperation("Unsafe redirect to URL with scheme '%s'" % parsed.scheme)
        self['Location'] = iri_to_uri(redirect_to)


def view_newsletter_tracking(request, slug, uidb36, token):
    """Track the opening of the newsletter by requesting a blank img"""
    newsletter = get_object_or_404(Newsletter, slug=slug)
    contact = untokenize(uidb36, token)
    log = ContactMailingStatus.objects.create(newsletter=newsletter,
                                              contact=contact,
                                              status=ContactMailingStatus.OPENED)
    return HttpResponse(base64.b64decode(TRACKING_IMAGE), content_type='image/png')

def view_newsletter_tracking_link(request, slug, uidb36, token, link_id):
    """Track the opening of a link on the website"""
    newsletter = get_object_or_404(Newsletter, slug=slug)
    contact = untokenize(uidb36, token)
    link = get_object_or_404(Link, pk=link_id)

    log = ContactMailingStatus.objects.create(newsletter=newsletter,
                                              contact=contact,
                                              status=ContactMailingStatus.LINK_OPENED,
                                              link=link)
    return PatchedHttpResponseRedirect(link.url)

@login_required
def view_newsletter_historic(request, slug):
    """Display the historic of a newsletter"""
    opts = Newsletter._meta
    newsletter = get_object_or_404(Newsletter, slug=slug)

    context = {'title': _('Historic of %s') % newsletter.__str__(),
               'original': newsletter,
               'opts': opts,
               'object_id': newsletter.pk,
               'app_label': opts.app_label,}
    return render(request, 'newsletter/newsletter_historic.html', context)
