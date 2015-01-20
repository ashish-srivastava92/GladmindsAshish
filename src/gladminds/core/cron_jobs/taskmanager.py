from django.db import transaction
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q

from gladminds.core.managers.audit_manager import sms_log
from gladminds.core.services import message_template as templates
from gladminds.bajaj import models
from gladminds.afterbuy import models as afterbuy_models
from gladminds.core.base_models import CouponData
from gladminds.core.constants import COUPON_STATUS
from django.db.models.aggregates import Sum
from email import email

AUDIT_ACTION = "SENT TO QUEUE"


@transaction.commit_manually()
def get_customers_to_send_reminder(*args, **kwargs):
    from gladminds.sqs_tasks import send_reminder_message
    day = kwargs.get('reminder_day', None)
    today_date = datetime.now().date()
    reminder_date = datetime.now().date()+timedelta(days=day)
    results = CouponData.objects.select_for_update().filter(mark_expired_on__range=(today_date,
                                    reminder_date), last_reminder_date__isnull=True,
                                    status=1).select_related('vin', 'customer_phone_number__phone_number')
    for reminder in results:
        product = reminder.vin
        phone_number = product.customer_phone_number.phone_number
        usc = reminder.unique_service_coupon
        vin = product.vin
        expired_date = reminder.mark_expired_on.strftime('%d/%m/%Y')
        valid_kms = reminder.valid_kms
        message = templates.get_template('SEND_CUSTOMER_COUPON_REMINDER').format(usc=usc, vin=vin, expired_date=expired_date, valid_kms=valid_kms)
        send_reminder_message.delay(phone_number=phone_number, message=message)
        sms_log(receiver=phone_number, action=AUDIT_ACTION, message=message)
        reminder.last_reminder_date = datetime.now()
        reminder.save()
        user = models.UserProfile.objects.filter(phone_number=phone_number)
        notification = afterbuy_models.UserNotification(user=user[0],message=message, notification_date=datetime.now(),
                                                        notification_read=0)
        notification.save()
    transaction.commit()
    
@transaction.commit_manually()  
def get_customers_to_send_reminder_by_admin(*args, **kwargs):
    from gladminds.sqs_tasks import send_reminder_message
    today = datetime.now().date()
    results = models.CouponData.objects.filter(schedule_reminder_date__day=today.day, schedule_reminder_date__month=today.month, schedule_reminder_date__year=today.year, status=1).select_related('product_id', 'customer_phone_number')
    for reminder in results:
        product_obj = reminder.product
        phone_number = product_obj.customer_phone_number
        usc = reminder.unique_service_coupon
        vin = product_obj.product_id
        expired_date = reminder.mark_expired_on.strftime('%d/%m/%Y')
        valid_kms = reminder.valid_kms
        message = templates.get_template('SEND_CUSTOMER_COUPON_REMINDER').format(usc=usc, vin=vin, expired_date=expired_date, valid_kms=valid_kms)
        send_reminder_message.delay(phone_number=phone_number, message=message)
        sms_log(receiver=phone_number, action=AUDIT_ACTION, message=message)
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
    feedback_closed_date = datetime.now()-timedelta(days=2)
    models.Feedback.objects.filter(status = 'Resolved', resloved_date__lte = feedback_closed_date )\
                                        .update(status = 'Closed', closed_date = datetime.now())

def import_data_from_sap(*args, **kwargs):
    pass

def get_data_feed_log_detail(start_date=None, end_date=None):
    start_date = start_date
    end_date = end_date
    feed_logs = models.DataFeedLog.objects.filter(timestamp__range=(start_date, end_date))
    return feed_logs.values('feed_type','action').annotate(total_count=Sum('total_data_count'),
                                                                  total_success_data_count=Sum('success_data_count'),
                                                                  total_failed_data_count=Sum('failed_data_count'))

def get_feed_failure_log_detail(type=None):
    feed_logs = models.FeedFailureLog.objects.filter(email_flag=False, feed_type=type)
    feed_data = []
    for feed in feed_logs:
        data = {}
        data['feed_type'] = feed.feed_type
        data['reason'] = feed.reason
        data['created_date'] = feed.created_date
        feed_data.append(data)
    feed_logs.update(email_flag=True)
    return feed_data

def get_customer_details(start_date=None, end_date=None, type=None):
    start_date = start_date
    end_date = end_date
    customer_details = models.CustomerTempRegistration.objects.filter(modified_date__range=(start_date, end_date),
                                                                      dealer_asc_id__isnull=False)
    customer_data = []
    for customer in customer_details:
        data = {}
        data['dealer_asc_id'] = customer.dealer_asc_id
        data['customer_id'] = customer.temp_customer_id
        data['customer_name'] = customer.new_customer_name
        data['new_number'] = customer.new_number
        data['old_number'] = customer.old_number
        customer_data.append(data)
    return customer_data

def get_vin_sync_feeds_detail():
    feed_logs = models.VinSyncFeedLog.objects.filter(email_flag=False)
    feed_data = []
    for feed in feed_logs:
        data = {}
        data['vin'] = feed.product_id
        data['dealer_asc_id'] = feed.dealer_asc_id
        data['status_code'] = feed.status_code
        feed_data.append(data)
    feed_logs.update(email_flag=True)
    return feed_data

    
    