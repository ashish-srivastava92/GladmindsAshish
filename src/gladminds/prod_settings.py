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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gladmindsdb',
        'USER': 'gladminds',
        'PASSWORD': 'gladminds123',
        'HOST': 'gladminds-production.chnnvvffqwop.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }
}



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

SMS_CLIENT = "KAP"

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
AWS_ACCESS_KEY_ID = 'AKIAIL7IDCSTNCG2R6JA'
AWS_SECRET_ACCESS_KEY = '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'

SAP_CRM_DETAIL = {
                  'username':'pisuper',
                  'password':'welcome123'
                  }
ASC_WSDL_URL = "http://api.gladmindsplatform.co/api/v1/asc-feed/?wsdl&v0"
COUPON_WSDL_URL = "http://api.gladmindsplatform.co/api/v1/redeem-feed/?wsdl&v0"
COUPON_WSDL = 'prod_coupon_redeem.wsdl'
CUSTOMER_REGISTRATION_WSDL_URL = "http://api.gladmindsplatform.co/api/v1/customer-feed/?wsdl&v0"
CUSTOMER_REGISTRATION_WSDL = 'prod_customer_registration.wsdl'

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
SQS_QUEUE_NAME = "gladminds-prod"
########################################################################
FEED_FAILURE_MAIL_DETAIL["subject"] = "GladMinds Feed Failure Mail"
UCN_RECOVERY_MAIL_DETAIL["subject"] = "GladMinds UCN Recovery Mail"
UCN_RECOVERY_MAIL_DETAIL["receiver"] = ["gladminds@hashedin.com"," nvhasabnis@bajajauto.co.in","ssozarde@bajajauto.co.in","jojibabu.vege@gladminds.co","support@gladminds.co"]
VIN_DOES_NOT_EXIST_DETAIL["receiver"] = ["jojibabu.vege@gladminds.co","ssozarde@bajajauto.co.in","skdixit@bajajauto.co.in","nvhasabnis@bajajauto.co.in"]
########################################################################
###################Change Mail Subject on Prod##########################
MAIL_DETAIL["subject"] = "GladMinds Feed Report"
#######################Feed Fail Failure Info###########################
FEED_FAILURE_DIR = 'aftersell/{0}/feed-logs/dev/'
FEED_FAILURE_BUCKET = 'gladminds'
#######################################################################
ENABLE_SERVICE_DESK = False
ENV = "prod"