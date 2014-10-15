# This file is part of the plan timetable generator, see LICENSE for details.

import socket
import urlparse

from django.conf import settings
from django.core import urlresolvers
from django.utils import translation

_ = translation.gettext_lazy


def processor(request):
    sitename = (settings.TIMETABLE_HOSTNAME or
                request.META.get('HTTP_HOST', socket.getfqdn()))
    scheme = 'https://' if request.is_secure() else 'http://'
    url = scheme + sitename + urlresolvers.reverse('frontpage')

    share_links = []
    for icon, name, link in settings.TIMETABLE_SHARE_LINKS:
        share_links.append((icon, name, link % {'url': url}))

    institution_links = []
    for name, url in settings.TIMETABLE_INSTITUTION_LINKS:
        institution_links.append((_(name), url))

    static_domain = urlparse.urlparse(settings.STATIC_URL).netloc.split(':')[0]
    if static_domain == sitename:
        static_domain = None

    return {'ANALYTICS_CODE': settings.TIMETABLE_ANALYTICS_CODE,
            'INSTITUTION': settings.TIMETABLE_INSTITUTION,
            'INSTITUTION_LINKS': institution_links,
            'INSTITUTION_SITE': settings.TIMETABLE_INSTITUTION_SITE,
            'ADMINS': settings.ADMINS,
            'SHARE_LINKS': share_links,
            'SOURCE_URL': settings.TIMETABLE_SOURCE_URL,
            'STATIC_DOMAIN': static_domain,
            'SITENAME': sitename}

