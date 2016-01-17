import logging

from django.http import HttpResponseBadRequest
from django.conf import settings

from gladminds.bajaj import models as common
from gladminds.core.managers import sms_parser
from gladminds.core.middlewares.dynamicsite_middleware import make_tls_property

logger = logging.getLogger('gladminds')

__all__ = ['GladmindsMiddleware', 'GladmindsMessageMiddleware']
SMS_CLIENT = settings.__dict__['_wrapped'].__class__.SMS_CLIENT =  make_tls_property()

"""
Gladminds middleware to identify the IP from where the message request came
and reply through the same platform
"""

class GladmindsMessageMiddleware(object):
    '''If the request is come on message APIs,
    then based on the IP we set sms client'''

    def process_request(self, request, **kwargs):
        source_client = request.GET.get('__gm_source', None)

        if settings.ENV in ['local', 'test', 'staging']:
            SMS_CLIENT.value = "KAP"
            return

        if source_client == settings.SMS_CLIENT_DETAIL['KAP']['params']:
            SMS_CLIENT.value = "KAP"
        else :
            try:
                SMS_CLIENT.value = settings.BRAND_SMS_GATEWAY.get(settings.BRAND)
            except:
                SMS_CLIENT.value = "AIRTEL"

"""
Gladminds middleware to identify the user type (i.e Customer, Service Advisor and Admin).
And set the it into request object
"""
class GladmindsMiddleware(object):
    ''' If the request is come on message APIs,
        then it coming from SA or
        Customer. Verify the customer and
        Dealer as per phone number and message text'''

    def process_view(self, request, view_func, view_args, view_kwargs):
        # If user is authenticated then it's an admin user
        if request.user.is_authenticated():
            return
        if request.path is '/v1/messages':
            message = None
            phone_number = None
            if request.POST.get('text'):
                message = request.POST.get('text')
                phone_number = request.POST.get('phoneNumber')
            else:
                # Putting a random phone, will change once we get correct format of message
                phone_number = '+91 7834671232'
                message = request.body
            message_args = sms_parser.sms_parser(message=message)
            auth_rule = message_args['auth_rule']
            if 'open' in auth_rule:
                request.user['role'] = 'Customer'
                request.user['phone_number'] = phone_number
                return
            elif 'sa' in auth_rule:
                try:
                    common.ServiceAdvisor.objects.get(phone_number=phone_number)
                    request.user['role'] = 'SA'
                    request.user['phone_number'] = phone_number
                except common.ServiceAdvisor.DoesNotExist:
                    raise HttpResponseBadRequest()
            elif 'customer' in auth_rule:
                try:
                    object = common.UserProfile.objects.get(phone_number=phone_number)
                    request.user['role'] = 'Customer'
                    request.user['phone_number'] = phone_number
                except common.UserProfile.DoesNotExist:
                    raise HttpResponseBadRequest()
        return
