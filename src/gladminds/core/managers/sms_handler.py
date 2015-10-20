'''Receives the sms and parse
   it to figure out the handlers'''

import logging

from django.conf.urls import url
from django.conf import settings
from tastypie.resources import Resource
from tastypie.http import HttpBadRequest

from gladminds.core.managers.sms_parser import sms_processing, InvalidKeyWord
from gladminds.core.cron_jobs.queue_utils import send_job_to_queue
from gladminds.sqs_tasks import send_invalid_keyword_message
import json

LOGGER = logging.getLogger('gladminds')
ANGULAR_FORMAT = lambda x: x.replace('{', '<').replace('}', '>')
AUDIT_ACTION = 'SEND TO QUEUE'

class SMSResources(Resource):

    class Meta:
        resource_name = 'messages'

    def base_urls(self):
        return [
            url(r"^messages", self.wrap_view('render_sms'))
        ]
        
    def render_sms(self, request, **kwargs):
        phone_number = ""
        message = ""
        if request.POST.get('text'):
            message = request.POST.get('text')
            phone_number = request.POST.get('phoneNumber')
        elif request.GET.get('cli'):
            message = request.GET.get('msg')
            phone_number = request.GET.get('cli')
        elif request.POST.get("advisorMobile"):
            phone_number = request.POST.get('advisorMobile')
            customer_id = request.POST.get('customerId')
            if request.POST.get('action') == 'validate':
                LOGGER.info('Validating the service coupon for customer {0}'.format(customer_id))
                odo_read = request.POST.get('odoRead')
                service_type = request.POST.get('serviceType')
                message = '{3} {0} {1} {2}'.format(customer_id, odo_read,
                    service_type, settings.ALLOWED_KEYWORDS['check'].upper())
                LOGGER.info('Message to send: ' + message)
            else:
                ucn = request.POST.get('ucn')
                LOGGER.info('Terminating the service coupon {0}'.format(ucn))
                message = '{2} {0} {1}'.format(customer_id,
                    ucn, settings.ALLOWED_KEYWORDS['close'].upper())
                LOGGER.info('Message to send: ' + message)
        try:    
            to_be_serialized=sms_processing(phone_number, message, settings.BRAND)
            print "/////////////////////////smshand to be ser//",to_be_serialized
        except InvalidKeyWord as ink:
            
            print "///////////////////////sms_hadler---ex",ink
            LOGGER.info("The database failed to perform {0}:{1}".format(
                                            request.POST.get('action'), ink))
            send_job_to_queue(send_invalid_keyword_message, {"phone_number":phone_number, "message":ink.template, "sms_client":settings.SMS_CLIENT})
            return HttpBadRequest(json.dumps({'status':False, 'message':ink.template}))
        except Exception as ex:
            LOGGER.info("The database failed to perform {0}:{1}".format(
                                            request.POST.get('action'), ex))
            return HttpBadRequest(json.dumps({'status':False, 'message':ex}))
        return self.create_response(request, data=to_be_serialized)
        
    
    def determine_format(self, request):
        return 'application/json'

sms_resource = SMSResources(Resource)
