# pylint: disable=W0401,W0614
import os
from settings import *

PROJECT_DIR = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
BASE_DIR = os.path.join(PROJECT_DIR, os.pardir)
STATIC_DIR = os.path.join(BASE_DIR, "src/static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "src/templates")
OUT_DIR = os.path.join(BASE_DIR, "out")


DEBUG = False
ALLOWED_HOSTS = ['*']
TEMPLATE_DEBUG = DEBUG

MEDIA_ROOT = 'afterbuy.s3-website-us-east-1.amazonaws.com'

BROKER_URL = 'redis://localhost:6379'
REDIS_URL = 'redis://localhost:6379'


STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    STATIC_DIR,
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    TEMPLATE_DIR,
)

# SMS_CLIENT = "TWILIO"
#  SMS_CLIENT_DETAIL = {
#                      'OTP_TWILIO_ACCOUNT' : 'ACbb8cb45f6113b8f2f6243c8eaa5ff971',
#                      'OTP_TWILIO_AUTH' : 'aa445a4f0a7e651738e89810601f8860',
#                      'OTP_TWILIO_FROM' : '+1 469-513-9856',
#                      'OTP_TWILIO_URI' : 'https://api.twilio.com/2010-04-01/Accounts/{0}/Messages.json'
#                 }

FILE_CACHE_DURATION = 1800

FEED_TYPE = 'CSV'

SMS_CLIENT = "AIRTEL"

#AfterBuy File Upload location configuration
AFTERBUY_LOC = os.path.join(PROJECT_DIR, "afterbuy")
AFTERBUY_USER_LOC = os.path.join(AFTERBUY_LOC, "users")
AFTERBUY_PRODUCT_LOC = os.path.join(AFTERBUY_LOC, "products")
AFTERBUY_BRAND_LOC = os.path.join(AFTERBUY_LOC, "brands")
AFTERBUY_PRODUCT_TYPE_LOC = os.path.join(AFTERBUY_LOC, "productType")
AFTERBUY_PRODUCT_WARRENTY_LOC = os.path.join(AFTERBUY_PRODUCT_LOC, "warrenty")
AFTERBUY_PRODUCT_INSURANCE_LOC = os.path.join(AFTERBUY_PRODUCT_LOC, "insurance")
AFTERBUY_PRODUCT_INVOICE_LOC = os.path.join(AFTERBUY_PRODUCT_LOC, "invoice")
MEDIA_ROOT = AFTERBUY_LOC
MEDIA_URL = '/media/'


#S3 Configuration
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

SAP_CRM_DETAIL = {
                  'username':'pisuper',
                  'password':'welcome123'
                  }

COUPON_WSDL = 'prod_wsdl/prod_coupon_redeem.wsdl'
CUSTOMER_REGISTRATION_WSDL = 'prod_wsdl/prod_customer_registration.wsdl'
VIN_SYNC_WSDL='prod_wsdl/prod_vin_sync.wsdl'
PURCHASE_SYNC_WSDL='prod_wsdl/prod_purchase_sync_feed.wsdl'
CTS_WSDL = 'prod_wsdl/prod_container_tracker.wsdl'

MEMBER_SYNC_WSDL='prod_wsdl/prod_member_sync_feed.wsdl'
ACCUMULATION_SYNC_WSDL = 'prod_wsdl/prod_accumulation_feed.wsdl'
REDEMPTION_SYNC_WSDL = 'prod_wsdl/prod_redemption_feed.wsdl'
DISTRIBUTOR_SYNC_WSDL = 'prod_wsdl/prod_distributor_sync_feed.wsdl' 

COUPON_WSDL_URL = "http://bajaj.gladminds.co/api/v1/coupon-redeem/?wsdl&v0"
CUSTOMER_REGISTRATION_WSDL_URL = "http://bajaj.gladminds.co/api/v1/customer-feed/?wsdl&v0"
VIN_SYNC_WSDL_URL="http://bajaj.gladminds.co/api/v1/vin-sync/?wsdl&v0"
PURCHASE_SYNC_WSDL_URL="http://bajaj.gladminds.co/api/v1/purchase-sync/?wsdl&v0"
CTS_WSDL_URL = "http://bajaj.gladminds.co/api/v1/container-tracker/?wsdl&v0"

MEMBER_SYNC_WSDL_URL="http://bajaj.gladminds.co/api/v1/member-sync/?wsdl&v0"
ACCUMULATION_SYNC_WSDL_URL = "http://bajaj.gladminds.co/api/v1/accumulation-request/?wsdl&v0"
REDEMPTION_SYNC_WSDL_URL = "http://bajaj.gladminds.co/api/v1/redemption-request/?wsdl&v0"
DISTRIBUTOR_SYNC_WSDL_URL = "http://bajaj.gladminds.co/api/v1/distributor-sync/?wsdl&v0"

ENABLE_AMAZON_SQS = True

AFTER_BUY_CONSTANTS = {
                       "username": 'support@gladminds.com',
                       "password": 'gladminds123',
                       "key_prefix": 'qa',
                       "app_path": 'afterbuy_script/afterbuy.zip',
                       "phonegap_build_url": 'https://build.phonegap.com/',
                       "try_count": 300,
                       "android_apk_loc": "afterbuy_script/qa_android_afterbuy.apk",
                       "ios_apk_loc": "afterbuy_script/qa_ios_afterbuy.ipa",
                       "create_method": "file",
                       "package": "com.gladminds.afterbuyv1",
                       "version": "0.1.0",
                       "title": "Afterbuy V1 App"
                       }

########################SQS Queue Name##################################
SQS_QUEUE_NAME = "gladminds-prod2"
SQS_QUEUE_NAME_SMS = "gladminds-prod-sms"
########################################################################
UCN_RECOVERY_MAIL_DETAIL["subject"] = "GladMinds UCN Recovery Mail"
UCN_RECOVERY_MAIL_DETAIL["receiver"] = ["suresh@hashedin.com", "gladminds@hashedin.com", "nvhasabnis@bajajauto.co.in", "ssozarde@bajajauto.co.in", "support@gladminds.co", "suma.l@gladminds.co", "skolluri@bajajauto.co.in"]
VIN_DOES_NOT_EXIST_DETAIL["receiver"] = ["suresh@hashedin.com","ssozarde@bajajauto.co.in", "gladminds@hashedin.com", "Dhazarika@bajajauto.co.in", "Rkjena@bajajauto.co.in", "skolluri@bajajauto.co.in", "sudhir.patil@gladminds.co", "suma.l@gladminds.co",
                                         "skolluri@bajajauto.co.in"]
FEED_FAILURE["subject"] = "Consolidated Report: GladMinds Feed Failure - "
FEED_FAILURE["receiver"] = ["suresh@hashedin.com", "ssozarde@bajajauto.co.in", "skolluri@bajajauto.co.in",
                            "sudhir.patil@gladminds.co", "rkjena@bajajauto.co.in", "dhazarika@bajajauto.co.in",
                            "gladminds@hashedin.com", "naveen.shankar@gladminds.co", "ashakiran@gladminds.co", "aparajita.reang@gladminds.co",
                            "suma.l@gladminds.co", "skolluri@bajajauto.co.in"]
CUSTOMER_PHONE_NUMBER_UPDATE["receiver"] = ["suresh@hashedin.com", "ssozarde@bajajauto.co.in",
                                            "skolluri@bajajauto.co.in", "sudhir.patil@gladminds.co",
                                            "rkjena@bajajauto.co.in", "dhazarika@bajajauto.co.in",
                                            "gladminds@hashedin.com", "ashakiran@gladminds.co", "aparajita.reang@gladminds.co",
                                            "suma.l@gladminds.co"]
PHONE_NUMBER_UPDATE_COUNT_EXCEEDED_MAIL_TO_ASM["receiver"] = ["suresh@hashedin.com", "ssozarde@bajajauto.co.in",
                                                              "skolluri@bajajauto.co.in", "sudhir.patil@gladminds.co",
                                                              "rkjena@bajajauto.co.in", "dhazarika@bajajauto.co.in",
                                                              "gladminds@hashedin.com", "ashakiran@gladminds.co", "aparajita.reang@gladminds.co",
                                                              "suma.l@gladminds.co"]
VIN_SYNC_FEED["receiver"] = ["suresh@hashedin.com", "rkjena@bajajauto.co.in", "dhazarika@bajajauto.co.in", "ssozarde@bajajauto.co.in", "gladminds@hashedin.com",
                             "suma.l@gladminds.co"]

DISCREPANCY_MAIL_TO_MANAGER ["receiver"] = ["suresh@hashedin.com", "ssozarde@bajajauto.co.in",
                                                   "sudhir.patil@gladminds.co", "rkjena@bajajauto.co.in", "dhazarika@bajajauto.co.in",
                                                   "gladminds@hashedin.com", "naveen.shankar@gladminds.co",
                                                   "ashakiran@gladminds.co", "aparajita.reang@gladminds.co",
                                                   "suma.l@gladminds.co"]
########################################################################
###################Change Mail Subject on Prod##########################
MAIL_DETAIL["subject"] = "Report: GladMinds Feed Summary"
MAIL_DETAIL["receiver"] = ["ssozarde@bajajauto.co.in", "skolluri@bajajauto.co.in",
                            "sudhir.patil@gladminds.co", "rkjena@bajajauto.co.in", "dhazarika@bajajauto.co.in",
                            "gladminds@hashedin.com", "suresh@hashedin.com", "naveen.shankar@gladminds.co",
                            "sudhir.patil@gladminds.co", "ashakiran@gladminds.co", "aparajita.reang@gladminds.co",
                            "suma.l@gladminds.co","skolluri@bajajauto.co.in"]

#######################Feed Fail Failure Info###########################
FEED_FAILURE_DIR = 'aftersell/{0}/feed-logs/dev/'
FEED_FAILURE_BUCKET = 'gladminds'
#######################################################################
ENABLE_SERVICE_DESK = False
ENV = "prod"

WSDL_TNS="http://bajaj.gladminds.co/api/v1/feed/"
CORE_WSDL_TNS="http://bajajcv.gladminds.co/api/v1/feed/"
IB_WSDL_TNS="http://bajajib.gladminds.co/api/v1/feed/"

ADMIN_DETAILS = {GmApps.BAJAJ: {'user': 'bajaj001', 'password': 'bajaj001'},
          GmApps.DEMO: {'user': 'demo', 'password': 'demo'},
          GmApps.AFTERBUY: {'user': 'afterbuy', 'password': 'afterbuy'},
          GmApps.GM: {'user': 'gladminds', 'password': 'gladminds'},
          GmApps.BAJAJCV: {'user': 'bajajcv', 'password': 'bajajcv'},
          GmApps.DAIMLER: {'user': 'daimler', 'password': 'daimler'},
          GmApps.PROBIKING: {'user': 'probiking', 'password': 'probiking'}
          }


# CACHES = {
#     'default': {
#         'BACKEND': 'django_elasticache.memcached.ElastiCache',
#         'LOCATION': 'gladminds-memcache.t2nfas.cfg.use1.cache.amazonaws.com:11211'
#     }
# }

COUPON_URL = 'bajaj.gladminds.co'
API_FLAG = True 
