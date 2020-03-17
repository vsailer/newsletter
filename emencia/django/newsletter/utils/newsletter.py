"""Utils for newsletter"""
import urllib.request, urllib.error, urllib.parse

from bs4 import BeautifulSoup, Tag
from django.urls import reverse

from emencia.django.newsletter.models import Link

def get_webpage_content(url):
    """Return the content of the website
    located in the body markup"""
    request = urllib.request.Request(url)
    page = urllib.request.urlopen(request)
    soup = BeautifulSoup(page)

    return soup.body.prettify()

def body_insertion(content, insertion, end=False):
    """Insert an HTML content into the body HTML node"""

    soup = BeautifulSoup(content)
    if content.find('<body') == -1:
        content = '<body>%s</body>' % content
    soup = BeautifulSoup(content, 'html.parser')
    insertion = BeautifulSoup(insertion, 'html.parser')

    if end:
        soup.body.append(insertion)
    else:
        soup.body.insert(0, insertion)
    return str(soup)

def track_links(content, context):
    """Convert all links in the template for the user
    to track his navigation"""
    if not context.get('uidb36'):
        return content

    soup = BeautifulSoup(content)
    domain = context.get('NEWSLETTER_PORTAL_URL')
    for link_markup in soup('a'):
        if link_markup.get('href'):
            link_href = link_markup['href']
            #don't capture internal hashlinks
            if not link_href.startswith('#') \
                and not link_href.startswith('mailto:') \
                and not link_href.startswith('tel:'):
                link_title = link_markup.get('title', link_href)[:255]
                link, created = Link.objects.get_or_create(url=link_href,
                                                           defaults={'title': link_title})
                link_markup['href'] = '%s%s' % (domain, reverse('newsletter_newsletter_tracking_link',
                                                                args=[context['newsletter'].slug,
                                                                context['uidb36'], context['token'],
                                                                link.pk]))
    return str(soup)

