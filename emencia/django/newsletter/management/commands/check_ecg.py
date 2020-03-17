"""Command for sending the newsletter"""
import os
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Send the newsletter in queue"""
    help = 'Check Contacts in ECG List'
    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete blacklisted contacts',
        )
        parser.add_argument(
            '--hashfile',
            dest='hashfile',
            help='Optional custom hashfile',
        )


    def handle(self, delete=False, hashfile=None, **kw):
        # from emencia.django.newsletter.mailer import Mailer
        from ecglist import ECGList
        from emencia.django.newsletter import ecg
        from emencia.django.newsletter.models import Contact

        if not hashfile:
            hashfile = os.path.join(ecg.__path__[0], 'ecg-liste.hash')
        blacklist = ECGList(filename=hashfile)

        for contact in Contact.objects.all():
            status = blacklist.get_blacklist_status(contact.email)
            if status:
                print(status, contact.email)
                if delete and "blacklisted" in status:
                    print("[DELETE] Blacklisted Contact: %s" % contact)
                    contact.delete()
