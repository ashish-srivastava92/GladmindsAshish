from django.conf import settings
from django.utils.cache import patch_vary_headers
import os

import logging
from django_extensions.management.utils import import_module
logger = logging.getLogger('gladminds')

def make_tls_property(default=None):
    """Creates a class-wide instance property with a thread-specific value."""
    class TLSProperty(object):
        def __init__(self):
            from threading import local
            self.local = local()

        def __get__(self, instance, cls):
            if not instance:
                return self
            return self.value

        def __set__(self, instance, value):
            self.value = value

        def _get_value(self):
            return getattr(self.local, 'value', default)

        def _set_value(self, value):
            self.local.value = value
        value = property(_get_value, _set_value)

    return TLSProperty()


BRAND = settings.__dict__['_wrapped'].__class__.BRAND = make_tls_property()


class DynamicSitesMiddleware(object):
    """
    Sets settings.BRAND based on request's domain.
    Also handles hostname redirects, and ensures the
    proper subdomain is requested for the site
    """
    def process_request(self, request):
        self.request = request
        self.domain, self.port = self.get_domain_and_port()
        BRAND.value = self.get_fields(self.domain)
        
    #Note: its a hack which is implemented for tata motors
        if BRAND.value == 'tatamotors':
            BRAND.value = 'daimler'
              
        if BRAND.value == 'admin':
            request.urlconf = 'gladminds.urls'
            return
        try:
            import_module('gladminds.{0}.urls'.format(BRAND.value))
            request.urlconf = 'gladminds.{0}.urls'.format(BRAND.value)
        except:
            request.urlconf = 'gladminds.core.urls'

    def process_response(self, request, response):
        if getattr(request, "urlconf", None):
            patch_vary_headers(response, ('Host',))
        return response

    def get_fields(self, domain):
        fields = domain.split('.')
        if fields[0] in ['local', 'dev', 'qa', 'staging', 'development']:
            fields = fields[1:]
        if fields[0] in ['api'] and fields[1] in ['afterbuy']:
            fields = fields[1:]
        return fields[0]

    def get_domain_and_port(self):
        """
        Django's request.get_host() returns the requested host and possibly the
        port number.  Return a tuple of domain, port number.
        Domain will be lowercased
        """
        host = self.request.get_host()
        if ':' in host:
            domain, port = host.split(':')
            return (domain.lower(), port)
        else:
            return (host.lower(),
                self.request.META.get('SERVER_PORT'))
