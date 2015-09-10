import logging
from PIL.PngImagePlugin import PngImageFile
logger = logging.getLogger('gladminds')
from parse import *
from django.conf import settings
from django.db import transaction
from gladminds.core.managers.audit_manager import sms_log
from gladminds.core import utils
from gladminds.core.services import message_template as templates

LOGGER = logging.getLogger('gladminds')
ANGULAR_FORMAT = lambda x: x.replace('{', '<').replace('}', '>')
AUDIT_ACTION = 'SEND TO QUEUE'

class SmsException(Exception):
    def __init__(self, message=None, template=None):
        Exception.__init__(self, message)
        self.template = template

class InvalidMessage(SmsException): {}

class InvalidKeyWord(SmsException): {}

class InvalidFormat(SmsException): {}

def sms_parser(*args, **kwargs):
    message = kwargs['message']

    parse_message = parse(templates.RCV_MESSAGE_FORMAT, message)
    #FIXME: Find a generic way to handle message
    if not parse_message:
        message = message + " message"
        parse_message = parse(templates.RCV_MESSAGE_FORMAT, message)
        
    keyword = None
    try:
        keyword = parse_message['key']
    except:
        raise InvalidMessage(message='invalid message', template=templates.get_template('SEND_INVALID_MESSAGE'))
    if not parse_message:
        raise InvalidMessage(message='invalid message', template=templates.get_template('SEND_INVALID_MESSAGE'))
    #Check appropriate received message template and parse the message data
    template_mapper = templates.get_message_template_mapper()
    lower_keyword = keyword.lower()
    if lower_keyword in template_mapper.keys():
        key_args = parse(template_mapper[lower_keyword]['receive'], parse_message['message'])
        logging.info("valid message format")
        if not key_args:
            raise InvalidFormat(message='invalid message format',
                                template=keyword+' '+template_mapper[lower_keyword]['receive'])
        #Added the Message keyword and handler in return dictionary
        key_args.named['keyword'] = lower_keyword
        key_args.named['handler'] = template_mapper[lower_keyword]['handler']
        key_args.named['auth_rule'] = template_mapper[lower_keyword]['auth_rule']
        return key_args.named
    else:
        raise InvalidKeyWord(message='invalid keyword',
                             template=templates.get_template('SEND_CUSTOMER_SUPPORTED_KEYWORD'))

def sms_processing(phone_number, message, brand):
    sms_dict = {}
    error_template = None
    phone_number = utils.get_phone_number_format(phone_number)
    message = utils.format_message(message)
    logger.info('[sms_processing]: settings brand {0}'.format(settings.BRAND))
    sms_log(brand, action='RECEIVED', sender=phone_number,
            receiver='+1 469-513-9856', message=message)
    LOGGER.info('Received Message from phone number: {0} and message: {1}'.format(phone_number, message))
    try:
        sms_dict = sms_parser(message=message)
    except InvalidKeyWord as ink:
        error_template = ink.template
    except InvalidMessage as inm:
        error_template = inm.template
    except InvalidFormat as inf:
        error_template = ANGULAR_FORMAT('CORRECT FORMAT: ' + inf.template)
    if error_template:
        sms_log(brand, receiver=phone_number,
                action=AUDIT_ACTION, message=error_template)
        raise ValueError(error_template)
    to_be_serialized = {}
    handler = utils.get_handler(sms_dict['handler'])
    with transaction.atomic():
        to_be_serialized = handler(sms_dict,
                        utils.mobile_format(phone_number))
    return to_be_serialized

def render_sms_template(keyword=None, status=None, template=None, *args, **kwargs):
    keyword = keyword
    template = template
    message = None
    if template:
        message = template.format(*args, **kwargs)
    if not template and keyword:
        status = status
        template_mapper = templates.get_message_template_mapper()
        template_obj = template_mapper[keyword]
        message_template = template_obj[status]
        message = message_template.format(*args, **kwargs)
    return message
