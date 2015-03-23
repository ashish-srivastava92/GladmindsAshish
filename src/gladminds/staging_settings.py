# pylint: disable=W0401,W0614
import os
from settings import *

PROJECT_DIR = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
BASE_DIR = os.path.join(PROJECT_DIR, os.pardir)
STATIC_DIR = os.path.join(BASE_DIR, "src/static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "src/templates")
OUT_DIR = os.path.join(BASE_DIR, "out")

DB_PASSWORD = os.environ.get('DB_PASSWORD', 'gladmindsqa2')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

MEDIA_ROOT = 'afterbuy.s3-website-us-east-1.amazonaws.com'
CONN_MAX_AGE = None
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gm',
        'USER': 'gladminds',
        'PASSWORD': DB_PASSWORD,
        'HOST': 'gladminds-staging.chnnvvffqwop.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    },
    'bajaj': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bajaj',
        'USER': 'gladminds',
        'PASSWORD': DB_PASSWORD,
        'HOST': 'gladminds-staging.chnnvvffqwop.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    },
    'demo': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'demo',
        'USER': 'gladminds',
        'PASSWORD': DB_PASSWORD,
        'HOST': 'gladminds-staging.chnnvvffqwop.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    },
    'afterbuy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'afterbuy',
        'USER': 'gladminds',
        'PASSWORD': DB_PASSWORD,
        'HOST': 'gladminds-staging.chnnvvffqwop.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }
}



BROKER_URL = 'redis://localhost:6379'
REDIS_URL = 'redis://localhost:6379'

JOBCARD_DIR = '{0}/jobcards/qa/'

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
# # SMS_CLIENT_DETAIL = {
#                      'OTP_TWILIO_ACCOUNT' : 'ACbb8cb45f6113b8f2f6243c8eaa5ff971',
#                      'OTP_TWILIO_AUTH' : 'aa445a4f0a7e651738e89810601f8860',
#                      'OTP_TWILIO_FROM' : '+1 469-513-9856',
#                      'OTP_TWILIO_URI' : 'https://api.twilio.com/2010-04-01/Accounts/{0}/Messages.json'
#                 }
FILE_CACHE_DURATION = 0

SMS_CLIENT = "MOCK"
FEED_TYPE = 'CSV'

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

ASC_WSDL_URL = "http://staging.bajaj.gladminds.co/api/v1/asc-feed/?wsdl&v0"

COUPON_WSDL_URL = "http://staging.bajaj.gladminds.co/api/v1/redeem-feed/?wsdl&v0"
COUPON_WSDL = 'qa_coupon_redeem.wsdl'

CUSTOMER_REGISTRATION_WSDL_URL = "http://staging.bajaj.gladminds.co/api/v1/customer-feed/?wsdl&v0"
CUSTOMER_REGISTRATION_WSDL = 'qa_customer_registration.wsdl'

VIN_SYNC_WSDL_URL="http://staging.bajaj.gladminds.co/api/v1/vin-sync-feed/?wsdl&v0"
VIN_SYNC_WSDL='qa_vin_sync.wsdl'

MEMBER_SYNC_WSDL_URL="http://staging.bajaj.gladminds.co/api/v1/member-sync-feed/?wsdl&v0"
MEMBER_SYNC_WSDL='qa_member_sync_feed.wsdl'

PURCHASE_SYNC_WSDL_URL="http://staging.bajaj.gladminds.co/api/v1/purchase-sync-feed/?wsdl&v0"
PURCHASE_SYNC_WSDL='qa_purchase_sync_feed.wsdl'

WSDL_TNS="http://staging.bajaj.gladminds.co/api/v1/feed/"

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

########################SQS Queue Name
SQS_QUEUE_NAME = "gladminds-staging"
SQS_QUEUE_NAME_SMS = "gladminds-staging-sms"
######################################
UCN_RECOVERY_MAIL_DETAIL["subject"] = "GladMinds UCN Recovery Mail QA"
VIN_DOES_NOT_EXIST_DETAIL["receiver"] = ["gmdev@hashedin.com"]
FEED_FAILURE["receiver"] = ["gmdev@hashedin.com"]
VIN_SYNC_FEED["receiver"] = ["gmdev@hashedin.com"]
###################Change Mail Subject on QA##########################
MAIL_DETAIL["subject"] = "GladMinds Feed Report QA"
MAIL_DETAIL["receiver"] = ["gmdev@hashedin.com"]
#######################################################################
ENV = "staging"


CACHES = {
    'default': {
        'BACKEND': 'django_elasticache.memcached.ElastiCache',
        'LOCATION': 'gladminds-memcache.t2nfas.cfg.use1.cache.amazonaws.com:11211'
    }
}
