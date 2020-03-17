"""Settings for emencia.django.newsletter"""
from django.conf import settings

USE_WORKGROUPS = getattr(settings, 'NEWSLETTER_USE_WORKGROUPS', False)
IGNORE_WORKGROUPS = not USE_WORKGROUPS#getattr(settings, 'NEWSLETTER_INGORE_WORKGROUPS', True)

SEND_PLAINTEXT = getattr(settings, 'NEWSLETTER_SEND_PLAINTEXT', False)

INCLUDE_UNSUBSCRIPTION = getattr(settings, 'NEWSLETTER_INCLUDE_UNSUBSCRIPTION', True)

DEFAULT_HEADER_REPLY = getattr(settings, 'NEWSLETTER_DEFAULT_HEADER_REPLY', 'Emencia Newsletter<noreply@emencia.com>')
DEFAULT_HEADER_SENDER = getattr(settings, 'NEWSLETTER_DEFAULT_HEADER_SENDER', 'Emencia Newsletter<noreply@emencia.com>')

TRACKING_LINKS = getattr(settings, 'NEWSLETTER_TRACKING_LINKS', True)
TRACKING_IMAGE = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAAAXNSR0IArs4c6QAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9kKEwwvINGR5lYAAAAZdEVYdENvbW1lbnQAQ3JlYXRlZCB3aXRoIEdJTVBXgQ4XAAAADElEQVQI12P4//8/AAX+Av7czFnnAAAAAElFTkSuQmCC'

MEDIA_URL = getattr(settings, 'NEWSLETTER_MEDIA_URL', '/edn/')

NEWSLETTER_BASE_PATH = getattr(settings, 'NEWSLETTER_BASE_PATH', 'uploads/newsletter')
HTML_TEMPLATE = getattr(settings, 'NEWSLETTER_HTML_TEMPLATE', None)
TEXT_TEMPLATE = getattr(settings, 'NEWSLETTER_TEXT_TEMPLATE', None)