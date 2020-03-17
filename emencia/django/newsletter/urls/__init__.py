"""Default urls for the emencia.django.newsletter"""
from django.conf.urls import url, include
from . import mailing_list as mailing_list_urls
from . import tracking as tracking_urls
from . import statistics as statistics_urls
from . import newsletter as newsletter_urls

urlpatterns = [
    url(r'^mailing/', include(mailing_list_urls)),
    url(r'^tracking/', include(tracking_urls)),
    url(r'^statistics/', include(statistics_urls)),
    url(r'^', include(newsletter_urls)),
]
