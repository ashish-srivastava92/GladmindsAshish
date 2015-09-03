from gladminds.core.model_fetcher import get_model
import datetime
from django.conf import settings
from gladminds.core.stats import LOGGER
import logging
logger = logging.getLogger("gladminds")

def sms_log(brand, action='SENT', sender='+1 469-513-9856', receiver=None,
              message=None, status='success'):
    if receiver == '9999999999':
        status = 'fail'
    sm_model = get_model('SMSLog', brand=brand)
    sms_log = sm_model(action=action, sender=sender,
                               receiver=receiver, status=status,
                               message=message)
    sms_log.save(using=brand)
#     if action=='SENT' and settings.LOGAN_ACTIVE:
#         try:
#             LOGGER.post_event("sms_sent", {'receiver':receiver,
#                                           'message':message,
#                                           'brand':brand})
#         except Exception as ex:
#             logger.error("[LOGAN-EXCEPTION]:: {0}".format(ex))


def feed_log(brand, feed_type=None, total_data_count=None, failed_data_count=None,
     success_data_count=None, status=None, action=None, remarks=None, file_location=None):

    feed_log_model = get_model('DataFeedLog', brand=brand)
    data_feed_log = feed_log_model(feed_type=feed_type,
                                     total_data_count=total_data_count,
                                     failed_data_count=failed_data_count,
                                     success_data_count=success_data_count,
                                     status=status, action=action,
                                     remarks=remarks, file_location=file_location)
    data_feed_log.save(using=brand)

def email_log(brand, subject, message, sender, receiver):
    email_model = get_model('EmailLog', brand=brand)
    email_log = email_model(subject=subject, message=message, sender=sender, receiver=receiver)
    email_log.save()

def feed_failure_log(brand, feed_type=None, reason=None):
    feed_failure_log_model = get_model('FeedFailureLog', brand=brand)
    feed_failure_log = feed_failure_log_model(feed_type=feed_type,
                                     reason=reason, created_date=datetime.datetime.now())
    feed_failure_log.save(using=brand)
    