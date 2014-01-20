from parse import *
from gladminds import utils, message_template as templates

class InvalidMessage(Exception):{}

def sms_parser(*args, **kwargs):
    message = kwargs['message']
    parse_message = parse(templates.RCV_MESSAGE_FORMAT, message)
    keyword = parse_message['key']
    if not parse_message:
        raise InvalidMessage("incorrect message format")
        
    #Check appropriate received message template and parse the message data
    template_mapper = templates.MESSAGE_TEMPLATE_MAPPER
    if keyword.lower() in template_mapper.keys():
        key_args = parse(template_mapper[keyword]['receive'], parse_message['message'])
        if not key_args:
            raise InvalidMessage("invalid message")
        return key_args.named
    else:
        raise InvalidMessage("invalid message")

def render_sms_template(*args, **kwargs):
    key = kwargs.get('key', None)
    template = kwargs.get('template', None)
    message = None
    if template:
        message = template.format(*args, **kwargs)
    
    if not template and key:
        status = kwargs.get('status', None)
        template_mapper = templates.MESSAGE_TEMPLATE_MAPPER[key]
        message_template = template_mapper[status]
        message = message_template.format(*args, **kwargs)
    return message

    
    
    