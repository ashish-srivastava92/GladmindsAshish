from django.db import models, transaction
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from django.conf import settings

from gladminds.core.managers.audit_manager import sms_log
from gladminds.core import utils
from gladminds.bajaj.services import message_template as templates
from gladminds.bajaj import models
from gladminds.core.base_models import CouponData, STATUS_CHOICES
from gladminds.core.utils import COUPON_STATUS

AUDIT_ACTION = "SENT TO QUEUE"


@transaction.commit_manually()
def get_customers_to_send_reminder(*args, **kwargs):
    from gladminds.core.sqs_tasks import send_reminder_message
    day = kwargs.get('reminder_day', None)
    today_date = datetime.now().date()
    reminder_date = datetime.now().date()+timedelta(days=day)
    results = CouponData.objects.select_for_update().filter(mark_expired_on__range=(today_date, reminder_date), last_reminder_date__isnull=True, status=1).select_related('vin', 'customer_phone_number__phone_number')
    for reminder in results:
        product = reminder.vin
        phone_number = product.customer_phone_number.phone_number
        usc = reminder.unique_service_coupon
        vin = product.vin
        expired_date = reminder.mark_expired_on.strftime('%d/%m/%Y')
        valid_kms = reminder.valid_kms
        message = templates.get_template('SEND_CUSTOMER_COUPON_REMINDER').format(usc=usc, vin=vin, expired_date=expired_date, valid_kms=valid_kms)
        send_reminder_message.delay(phone_number=phone_number, message=message)
        sms_log(reciever=phone_number, action=AUDIT_ACTION, message=message)
        reminder.last_reminder_date = datetime.now()
        reminder.save()
    transaction.commit()
    
@transaction.commit_manually()  
def get_customers_to_send_reminder_by_admin(*args, **kwargs):
    from gladminds.core.cron_jobs.sqs_tasks import send_reminder_message
    today = datetime.now().date()
    results = models.CouponData.objects.select_for_update().filter(schedule_reminder_date__day=today.day, schedule_reminder_date__month=today.month, schedule_reminder_date__year=today.year, status=1).select_related('product_id', 'customer_phone_number')
    for reminder in results:
        product_obj = reminder.product
        phone_number = product_obj.customer_phone_number
        usc = reminder.unique_service_coupon
        vin = product_obj.product_id
        expired_date = reminder.mark_expired_on.strftime('%d/%m/%Y')
        valid_kms = reminder.valid_kms
        message = templates.get_template('SEND_CUSTOMER_COUPON_REMINDER').format(usc=usc, vin=vin, expired_date=expired_date, valid_kms=valid_kms)
        send_reminder_message.delay(phone_number=phone_number, message=message)
        sms_log(reciever=phone_number, action=AUDIT_ACTION, message=message)
        reminder.last_reminder_date = datetime.now()
        reminder.schedule_reminder_date = None
        reminder.save()
    transaction.commit()


def expire_service_coupon(*args, **kwargs):
    today = timezone.now()
    threat_coupons = models.CouponData.objects.filter(mark_expired_on__lte=today.date()).exclude(Q(status=2) | Q(status=3))
    for coupon in threat_coupons:
        #If the coupon was initiated, it will expire if initiated more than 30days ago.
        if coupon.status == COUPON_STATUS['In Progress']:
            extended_date = coupon.extended_date.date()
            if extended_date < today.date():
                coupon.status = COUPON_STATUS['Expired']
                coupon.save()
        #If the coupon is unused and crossed the days limit, it will expire.
        else:
            coupon.status = COUPON_STATUS['Expired']
            coupon.save()
            
def mark_feeback_to_closed(*args, **kwargs):
    fedback_closed_date = datetime.now()-timedelta(days=2)
    models.Feedback.objects.filter(status = 'Resolved', resloved_date__lte = feedback_closed_date ).update(status = 'Closed', closed_date = datetime.now())

def import_data_from_sap(*args, **kwargs):
    pass

def get_data_feed_log_detail(start_date=None, end_date=None):
    start_date = start_date
    end_date = end_date
    feed_logs = models.DataFeedLog.objects.filter(timestamp__range=(start_date, end_date))
    feed_data = []
    for feed in feed_logs:
        data = {}
        data['feed_type'] = feed.feed_type
        data['total_feed_count'] = feed.total_data_count
        data['total_failed_count'] = feed.failed_data_count
        data['total_success_count'] = feed.success_data_count
        data['timestamp'] = feed.timestamp
        data['action'] = feed.action
        feed_data.append(data)
    return feed_data
