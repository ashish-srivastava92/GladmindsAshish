from __future__ import absolute_import
from celery import shared_task
from django.conf import settings
from gladminds.audit import audit_log
from gladminds.dao.smsclient import load_gateway, MessageSentFailed
from datetime import datetime, timedelta
from gladminds import mail
import logging
from gladminds import taskmanager, feed, export_file, exportfeed

logger = logging.getLogger("gladminds")

sms_client = load_gateway()


"""
This task send sms to customer on customer registration
"""


@shared_task
def send_registration_detail(*args, **kwargs):
    status = "success"
    logger.info("message addded")
    try:
        phone_number = kwargs.get('phone_number', None)
        message = kwargs.get('message', None)
        respone_data = sms_client.send_stateless(**kwargs)
    except (Exception, MessageSentFailed) as ex:
        status = "failed"
        send_registration_detail.retry(
            exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    finally:
        audit_log(status=status, reciever=phone_number, message=message)

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
        send_service_detail.retry(
            exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    finally:
        audit_log(status=status, reciever=phone_number, message=message)

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
        send_coupon_validity_detail.retry(
            exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    finally:
        audit_log(status=status, reciever=phone_number, message=message)

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
        send_coupon_detail_customer.retry(
            exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    finally:
        audit_log(status=status, reciever=phone_number, message=message)

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
        send_reminder_message.retry(
            exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    finally:
        audit_log(status=status, reciever=phone_number, message=message)

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
        send_coupon_close_message.retry(
            exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    finally:
        audit_log(status=status, reciever=phone_number, message=message)


@shared_task
def send_coupon(*args, **kwargs):
    status = "success"
    try:
        phone_number = kwargs.get('phone_number', None)
        message = kwargs.get('message', None)
        respone_data = sms_client.send_stateless(**kwargs)
    except (Exception, MessageSentFailed) as ex:
        status = "failed"
        send_coupon.retry(exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    finally:
        audit_log(status=status, reciever=phone_number, message=message)

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
        send_close_sms_customer.retry(
            exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    finally:
        audit_log(status=status, reciever=phone_number, message=message)


@shared_task
def send_brand_sms_customer(*args, **kwargs):
    status = "success"
    try:
        phone_number = kwargs.get('phone_number', None)
        message = kwargs.get('message', None)
        respone_data = sms_client.send_stateless(**kwargs)
    except (Exception, MessageSentFailed) as ex:
        status = "failed"
        send_brand_sms_customer.retry(
            exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    finally:
        audit_log(status=status, reciever=phone_number, message=message)

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
        send_invalid_keyword_message.retry(
            exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    finally:
        audit_log(status=status, reciever=phone_number, message=message)


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
        send_on_product_purchase.retry(
            exc=ex, countdown=10, kwargs=kwargs, max_retries=5)
    finally:
        audit_log(status=status, reciever=phone_number, message=message)

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
def export_close_coupon_data(*args, **kwargs):
    export_file.export_data_csv()


@shared_task
def export_coupon_redeem_to_sap(*args, **kwargs):
#     today = datetime.now().date()
    today = datetime.now()
    start_date = today - timedelta(days=1)
    end_date = today
    redeem_obj = feed.CouponRedeemFeedToSAP()
    feed_export_data = redeem_obj.export_data(
        start_date=start_date, end_date=end_date)
    if len(feed_export_data[0]) > 0:
        coupon_redeem = exportfeed.ExportCouponRedeemFeed(username=settings.SAP_CRM_DETAIL[
            'username'], password=settings.SAP_CRM_DETAIL['password'], wsdl_url=settings.COUPON_WSDL_URL)
        coupon_redeem.export(items=feed_export_data[0], item_batch=feed_export_data[
                             1], total_failed_on_feed=feed_export_data[2])
    else:
        logger.info("tasks.py: No Coupon closed during last day")

'''
Cron Job to send report email for data feed
'''


@shared_task
def send_report_mail_for_feed(*args, **kwargs):
    day = kwargs['day_duration']
    today = datetime.now().date()
    start_date = today - timedelta(days=day)
    end_date = today + timedelta(days=1)
    feed_data = taskmanager.get_data_feed_log_detail(
        start_date=start_date, end_date=end_date)
    mail.feed_report(feed_data=feed_data)


_tasks_map = {"send_registration_detail": send_registration_detail,

              "send_service_detail": send_service_detail,

              "send_coupon_validity_detail": send_coupon_validity_detail,

              "send_coupon_detail_customer": send_coupon_detail_customer,

              "send_reminder_message": send_reminder_message,

              "send_coupon_close_message": send_coupon_close_message,

              "send_coupon": send_coupon,

              "send_close_sms_customer": send_close_sms_customer,

              "send_brand_sms_customer": send_brand_sms_customer,

              "send_on_product_purchase": send_on_product_purchase,

              "send_reminder": send_reminder,

              "send_schedule_reminder": send_schedule_reminder,

              "expire_service_coupon": expire_service_coupon,

              "import_data": import_data,

              "export_close_coupon_data": export_close_coupon_data,

              "export_coupon_redeem_to_sap": export_coupon_redeem_to_sap,

              "send_report_mail_for_feed": send_report_mail_for_feed,

              }
