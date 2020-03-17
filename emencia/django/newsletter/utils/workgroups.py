"""Utils for workgroups"""
from emencia.django.newsletter.models import WorkGroup, Contact, MailingList, Newsletter
from emencia.django.newsletter.settings import IGNORE_WORKGROUPS

def request_workgroups(request):
    return WorkGroup.objects.filter(group__in=request.user.groups.all())

def request_workgroups_contacts_pk(request):
    if not IGNORE_WORKGROUPS:
        contacts = []
        for workgroup in request_workgroups(request):
            contacts.extend([c.pk for c in workgroup.contacts.all()])
    else:
        contacts = [c.pk for c in Contact.objects.all()]
    return set(contacts)

def request_workgroups_mailinglists_pk(request):
    if not IGNORE_WORKGROUPS:
        mailinglists = []
        for workgroup in request_workgroups(request):
            mailinglists.extend([ml.pk for ml in workgroup.mailinglists.all()])
    else:
        mailinglists = [c.pk for c in MailingList.objects.all()]
    return set(mailinglists)

def request_workgroups_newsletters_pk(request):
    if not IGNORE_WORKGROUPS:
        newsletters = []
        for workgroup in request_workgroups(request):
            newsletters.extend([n.pk for n in workgroup.newsletters.all()])
    else:
        newsletters = [nl.pk for nl in Newsletter.objects.all()]
    return set(newsletters)
