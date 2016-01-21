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

########################SQS Queue Name
SQS_QUEUE_NAME = "gladminds-dev"
######################################

FEED_TYPE = 'CSV'
FEED_FAILURE_MAIL_ENABLED = True

MAIL_DETAIL["subject"] = "GladMinds Feed Report DEV"
MAIL_DETAIL["receiver"] = ["priyanka.n@hashedin.com"]

UCN_RECOVERY_MAIL_DETAIL["subject"] = "GladMinds UCN Recovery Mail DEV"
VIN_DOES_NOT_EXIST_DETAIL["receiver"] = ["priyanka.n@hashedin.com"]

LOG_BASE_PATH = 'log'
LOGGING['handlers']['gladminds_logs']['filename'] = 'log/gladminds.log'
LOGGING['handlers']['afterbuy_logs']['filename'] = 'log/afterbuy.log'
LOGGING['handlers']['sql']['filename'] = 'log/sql.log'
LOGGING['loggers']['gladminds']['handlers']=['gladminds_logs']

ENV = "local"

WSDL_TNS="http://local.bajaj.gladminds.co:8000/api/v1/feed/"
CORE_WSDL_TNS="http://local.bajajcv.gladminds.co:8000/api/v1/feed/"
IB_WSDL_TNS="http://local.bajajib.gladminds.co:8000/api/v1/feed/"

BRAND_META["bajaj"]["base_url"]= "local.bajaj.gladminds.co"
BRAND_META["bajajcv"]["base_url"]= "local.bajajcv.gladminds.co"
BRAND_META["bajajib"]["base_url"]= "local.bajajib.gladminds.co"
BRAND_META["mechaneed"]["base_url"]= "local.mechaneed.gladminds.co"
