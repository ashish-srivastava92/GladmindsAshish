from __future__ import absolute_import
from celery import shared_task
from django.conf import settings
from gladminds.audit import audit_log
from gladminds.dao.smsclient import load_gateway, MessageSentFailed
from gladminds import taskmanager, feed,export_file

sms_client = load_gateway()

"""
This task send sms to customer on customer registration
"""
@shared_task
def send_registration_detail(*args, **kwargs):
    status = "success"
    try:
        phone_number = kwargs.get('phone_number', None)
        message = kwargs.get('message', None)
        respone_data = sms_client.send_stateless(**kwargs)
    except (Exception, MessageSentFailed) as ex:
        status = "failed"
        send_registration_detail.retry(exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    audit_log(status = status, reciever=phone_number, message=message)
        
"""
This task send customer valid service detail
""" 
@shared_task
def send_service_detail(*args, **kwargs):
    status = "success"
    try:
        phone_number = kwargs.get('phone_number', None)
        message = kwargs.get('message', None)
        response_data = sms_client.send_stateless(**kwargs)
    except (Exception, MessageSentFailed) as ex:
        status = "failed"
        send_service_detail.retry(exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    audit_log(status = status, reciever=phone_number, message=message)

"""
This job send sms to service advisor, whether the coupon is valid or not 
"""
@shared_task
def send_coupon_validity_detail(*args, **kwargs):
    status = "success"
    try:
        phone_number = kwargs.get('phone_number', None)
        message = kwargs.get('message', None)
        respone_data = sms_client.send_stateless(**kwargs)
    except (Exception, MessageSentFailed) as ex:
        status = "failed"
        send_coupon_validity_detail.retry(exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    audit_log(status = status, reciever=phone_number, message=message)

"""
This job send sms to customer when SA send 
 query, whether the coupon is valid or not 
"""
@shared_task
def send_coupon_detail_customer(*args, **kwargs):
    status = "success"
    try:
        phone_number = kwargs.get('phone_number', None)
        message = kwargs.get('message', None)
        respone_data = sms_client.send_stateless(**kwargs)
    except (Exception, MessageSentFailed) as ex:
        status = "failed"
        send_coupon_detail_customer.retry(exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    audit_log(status = status, reciever=phone_number, message=message)

"""
This job send reminder sms to customer
"""
@shared_task
def send_reminder_message(*args, **kwargs):
    status = "success"
    try:
        phone_number = kwargs.get('phone_number', None)
        message = kwargs.get('message', None)
        respone_data = sms_client.send_stateless(**kwargs)
    except (Exception, MessageSentFailed) as ex:
        status = "failed"
        send_reminder_message.retry(exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    audit_log(status = status, reciever=phone_number, message=message)

"""
This job send coupon close message
"""
@shared_task
def send_coupon_close_message(*args, **kwargs):
    status = "success"
    try:
        phone_number = kwargs.get('phone_number', None)
        message = kwargs.get('message', None)
        respone_data = sms_client.send_stateless(**kwargs)
    except (Exception, MessageSentFailed) as ex:
        status = "failed"
        send_coupon_close_message.retry(exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    audit_log(status = status, reciever=phone_number, message=message)

"""
This job send coupon close message to customer
"""
@shared_task
def send_close_sms_customer(*args, **kwargs):
    status = "success"
    try:
        phone_number = kwargs.get('phone_number', None)
        message = kwargs.get('message', None)
        respone_data = sms_client.send_stateless(**kwargs)
    except (Exception, MessageSentFailed) as ex:
        status = "failed"
        send_close_sms_customer.retry(exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    audit_log(status = status, reciever=phone_number, message=message)

@shared_task
def send_brand_sms_customer(*args, **kwargs):
    status = "success"
    try:
        phone_number = kwargs.get('phone_number', None)
        message = kwargs.get('message', None)
        respone_data = sms_client.send_stateless(**kwargs)
    except (Exception, MessageSentFailed) as ex:
        status = "failed"
        send_brand_sms_customer.retry(exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    audit_log(status = status, reciever=phone_number, message=message)

"""
This task send Invalid Keyword message
"""
@shared_task
def send_invalid_keyword_message(*args, **kwargs):
    status = "success"
    try:
        phone_number = kwargs.get('phone_number', None)
        message = kwargs.get('message', None)
        respone_data = sms_client.send_stateless(**kwargs)
    except (Exception, MessageSentFailed) as ex:
        status = "failed"
        send_brand_sms_customer.retry(exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    audit_log(status = status, reciever=phone_number, message=message)


"""
This job send on customer product purchase
"""
@shared_task
def send_on_product_purchase(*args, **kwargs):
    status = "success"
    try:
        phone_number = kwargs.get('phone_number', None)
        message = kwargs.get('message', None)
        respone_data = sms_client.send_stateless(**kwargs)
    except (Exception, MessageSentFailed) as ex:
        status = "failed"
        send_on_product_purchase.retry(exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    audit_log(status = status, reciever=phone_number, message=message)
        
"""
Crontab to send reminder sms to customer 
"""
@shared_task
def send_reminder(*args, **kwargs):
    taskmanager.get_customers_to_send_reminder(*args, **kwargs)
    
"""
Crontab to send scheduler reminder sms setup by admin
"""
@shared_task
def send_schedule_reminder(*args, **kwargs):
    taskmanager.get_customers_to_send_reminder_by_admin(*args, **kwargs)


"""
Crontab to set the is_expire=True for all those coupon which expire till current date time
"""
@shared_task
def expire_service_coupon(*args, **kwargs):
    taskmanager.expire_service_coupon(*args, **kwargs)

"""
Crontab to import data from SAP to Gladminds Database
"""
@shared_task
def import_data(*args, **kwargs):
    feed.load_feed()
    

'''
Cronjob to export close coupon data into csv file
'''
@shared_task
def export_close_coupon_data(*args,**kwargs):
    export_file.export_data_csv()