import os
import hashlib
from tastypie.serializers import Serializer
from models import logs
from datetime import datetime
         
def generate_unique_customer_id():
    bytes_str = os.urandom(24)
    unique_str = hashlib.md5(bytes_str).hexdigest()[:10]
    return unique_str.upper()

    
def save_log(**kwargs):
    action_log = logs.AuditLog(date=datetime.now(), action=kwargs['action'], sender=kwargs['sender'], reciever=kwargs['reciever'], status=kwargs['status'], message=kwargs['message'])
    action_log.save()

def import_json():
    try:
        import simplejson as json
    except ImportError:
        try:
            import json
        except ImportError:
            try:
                from django.utils import simplejson as json
            except:
                raise ImportError("Requires either simplejson, Python 2.6 or django.utils!")
    return json



