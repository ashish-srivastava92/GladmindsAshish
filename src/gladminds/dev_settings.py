# pylint: disable=W0401,W0614
import os
from settings import *

PROJECT_DIR = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
BASE_DIR = os.path.join(PROJECT_DIR, os.pardir)
STATIC_DIR = os.path.join(BASE_DIR, "src/static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "src/templates")
OUT_DIR = os.path.join(BASE_DIR, "out")

DEBUG = True
TEMPLATE_DEBUG = DEBUG


# BRAND_BASE_URL = 'staging.bajaj.gladminds.co'
API_FLAG = True 
BROKER_URL = 'redis://localhost:6379'
REDIS_URL = 'redis://localhost:6379'


JOBCARD_DIR = '{0}/jobcards/dev/'

FEED_FAILURE_DIR = 'aftersell/{0}/feed-logs/dev/'
FEED_FAILURE_BUCKET = 'gladminds'

MAIL_SERVER = 'localhost'


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

######################################################
#ADDED SETTINGS TO TEST CAPSYSTEM ON DEV ENV
###########################################################
ENABLE_AMAZON_SQS = False

FILE_CACHE_DURATION = 0
SMS_CLIENT = "KAP"

########################SQS Queue Name
SQS_QUEUE_NAME = "gladminds-dev"
######################################

FEED_TYPE = 'CSV'
FEED_FAILURE_MAIL_ENABLED = True

MAIL_DETAIL["subject"] = "GladMinds Feed Report DEV"
MAIL_DETAIL["receiver"] = ["naureen.razi@hashedin.com"]

FEED_FAILURE["receiver"] = ["naureen.razi@hashedin.com"]
CUSTOMER_PHONE_NUMBER_UPDATE["receiver"] = ["naureen.razi@hashedin.com"]
UCN_RECOVERY_MAIL_DETAIL["subject"] = "GladMinds UCN Recovery Mail DEV"
VIN_DOES_NOT_EXIST_DETAIL["receiver"] = ["naureen.razi@hashedin.com"]

#############################################################################
ENV = "dev"

WSDL_TNS="http://dev.bajaj.gladminds.co/api/v1/feed/"
CORE_WSDL_TNS="http://dev.bajajcv.gladminds.co/api/v1/feed/"
IB_WSDL_TNS="http://dev.bajajib.gladminds.co/api/v1/feed/"

BRAND_META["bajaj"]["base_url"]= "staging.bajaj.gladminds.co"
BRAND_META["bajajcv"]["base_url"]= "staging.bajajcv.gladminds.co"
BRAND_META["bajajib"]["base_url"]= "staging.bajajib.gladminds.co"
