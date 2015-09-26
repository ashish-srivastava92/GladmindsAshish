import base64
import calendar
import datetime
import hashlib
from importlib import import_module
import logging
import operator
import os
from random import randint
import re
import uuid

from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connections
from django.db.models import Count
from django.db.models.fields.files import FieldFile
from django.db.models.query_utils import Q
from django.utils import timezone
from django_otp.oath import TOTP
import pytz

from gladminds.core.apis.image_apis import uploadFileToS3
from gladminds.core.auth_helper import Roles
from gladminds.core.base_models import STATUS_CHOICES
from gladminds.core.constants import TIME_FORMAT, DATE_FORMAT
from gladminds.core.core_utils.date_utils import convert_utc_to_local_time
from gladminds.core.core_utils.utils import dictfetchall
from gladminds.core.managers.mail import get_email_template
from gladminds.settings import TOTP_SECRET_KEY, OTP_VALIDITY
from django.forms.models import model_to_dict   
from gladminds.core.model_fetcher import get_model, models

logger = logging.getLogger('gladminds')

def check_password(password):
    s = password
    rules = [lambda s:any(x.isupper() for x in s),
        lambda s:any(x.islower() for x in s),
        lambda s:any(x.isdigit() for x in s),
        lambda s:len(s) >= 6,
        lambda s:bool(re.search(r'[^a-zA-Z0-9]',s))
        ]
    if not all(rule(s) for rule in rules):
        return True
    return False

def generate_temp_id(prefix_value):
    for x in range(5):
        key = base64.b64encode(hashlib.sha256(str(datetime.datetime.now())).digest())
        key = re.sub("[a-z/=+]", "", key)
        if len(key) < 6:
            continue
        return "%s%s" % (prefix_value, key[:6])
    logger.log('Could not generate SAP ID after 5 attempts')

#FIXME: need to make class for coupon service as well
def get_handler(handler, brand=None):
    if not brand:
        brand = settings.BRAND
    try:
        import_module('gladminds.{0}'.format(brand))
    except Exception as ex:
        brand='core'
    func_handler = '.'.join(handler.split('.')[-1:])
    service_handler = '.'.join(handler.split('.')[-2:-1])
    try:
        rel_path = '.'.join(handler.split('.')[:-1])
        return getattr(import_module('gladminds.{0}.services.{1}'.format(brand, rel_path)), func_handler)
    except Exception as ex:
        logger.error(ex)
        rel_path = '.'.join(handler.split('.')[:-2])
        service_class = getattr(import_module('gladminds.{0}.services.{1}'.format(brand, rel_path)), service_handler)
        return getattr(service_class, func_handler)

def generate_unique_customer_id():
    bytes_str = os.urandom(24)
    unique_str = hashlib.md5(bytes_str).hexdigest()[:10]
    return unique_str.upper()

def import_json():
    try:
        import simplejson as json
    except ImportError:
        try:
            import json
        except ImportError:
            try:
                from django.utils import simplejson as json
            except:
                raise ImportError("Requires either simplejson, Python 2.6 or django.utils!")
    return json


def mobile_format(phone_number):
    '''
        GM store numbers in +91 format
        And when airtel pull message from customer
        or service advisor we will check that number in +91 format
    '''
    return '+91' + phone_number[-10:]
    #return '+256' + phone_number


def format_message(message):
    '''
        This function removes extra spaces from message
    '''
    keywords = message.split(' ')
    return ' '.join([keyword for keyword in keywords if keyword])


#FIXME: when phone number format will come for bajajib then we will not use hard code.
#NOTE: when mobile number format will come, we will use this for bajajib
# def get_phone_number_format_bajajib(phone_number):
#     if settings.BRAND == 'bajajib':
#         country_name = get_model('Country').objects.get(name = 'UGA')
#         area_code = country_name.area_code
#         try:
#             phone_number_uganda = phone_number.split(area_code,1)[1]
#             return   phone_number_uganda
#         except Exception as ex:
#             return phone_number[-10:]


def get_phone_number_format(phone_number):
    '''
        This is used when we are sending message through sms client
    '''
    
#TODO: when bajajib format will come change this and return only--> phone_number[-10:]
    country_name = get_model('Country').objects.get(name = 'UGA')
    area_code = country_name.area_code
    try:
        phone_number_uganda = phone_number.split(area_code,1)[1]
        return   phone_number_uganda
    except Exception as ex:
        return phone_number[-10:]


def save_otp(user, token, email):
    models.OTPToken.objects.filter(user=user).delete()
    token_obj = models.OTPToken(user=user, token=str(token), request_date=datetime.datetime.now(), email=email)
    token_obj.save()


def get_token(user, phone_number, email=''):
    if email and user.email_id != email:
        raise
    totp = TOTP(TOTP_SECRET_KEY+str(randint(10000, 99999))+str(phone_number))
    totp.time = 30
    token = totp.token()
    save_otp(user, token, email)
    return token


def validate_otp(user, otp, phone):
    token_obj = models.OTPToken.objects.filter(user=user)[0]
    if int(otp) == int(token_obj.token) and (timezone.now()-token_obj.request_date).seconds <= OTP_VALIDITY:
        return True
    elif (timezone.now()-token_obj.request_date).seconds > OTP_VALIDITY:
        token_obj.delete()
    raise

def update_pass(otp, password):
    token_obj = models.OTPToken.objects.filter(token=otp)[0]
    user = token_obj.user.user
    invalid_password = check_password(password)

    if (invalid_password):
        data = {'message':"password does not match the rules",'status':False}
    else:    
        user.set_password(str(password))
        user.save(using=settings.BRAND)
        user_obj =  get_model('UserProfile').objects.get(user=user)
        user_obj.reset_password = True
        user_obj.reset_date = datetime.datetime.now()
        user_obj.save(using=settings.BRAND)
        data = {'message': 'Password Changed successfully', 'status': True}
        token_obj.delete()

    return data


def format_product_object(product_obj):
    purchase_date = convert_utc_to_local_time(product_obj.purchase_date).strftime('%d/%m/%Y')
    return {'id': product_obj.customer_id,
            'phone': get_phone_number_format(str(product_obj.customer_phone_number)), 
            'name': product_obj.customer_name, 
            'purchased': purchase_date,
            'vin': product_obj.product_id}

def get_sa_list_for_login_dealer(user):
    dealer = models.Dealer.objects.filter(
                dealer_id=user)[0]
    service_advisors = models.ServiceAdvisor.objects\
                                .filter(dealer=dealer, status='Y')
    return service_advisors

def get_asc_list_for_login_dealer(user):
    ascs = models.Dealer.objects.filter(
                dealer_id=user)
    asc_list_with_detail = []
    for asc in ascs:
        asc_detail = User.objects.filter(username=asc.dealer_id)
        asc_list_with_detail.append(asc_detail[0])
    return asc_list_with_detail
    
def get_coupon_info(data):
    customer_id = get_updated_customer_id(data['customerId'])
    try:
        coupon_data = models.CouponData.objects.get(product__customer_id=customer_id, status=4)
        coupon_data.special_case = True
        coupon_data.save()
    except Exception as ex:
        coupon_data = None
        logger.error('[UCN_RECOVERY_ERROR]:: {0}'.format(ex))
    return coupon_data

def upload_file(destination, bucket, file_obj,logger_msg):
    path = uploadFileToS3(destination=destination, file_obj=file_obj, 
                          bucket=bucket, logger_msg=logger_msg)
    return path

def get_file_name(data, file_obj):
    requester = data['current_user']
    if Roles.DEALERS in requester.groups.all():
        filename_prefix = requester
    else:
        #TODO: Implement dealerId in prefix when we have Dealer and ASC relationship
        filename_prefix = requester
    filename_suffix = str(uuid.uuid4())
    ext = file_obj.name.split('.')[-1]
    customer_id = data['customerId']
    return str(filename_prefix)+'_'+customer_id+'_'+filename_suffix+'.'+ext


def get_user_groups(user):
    groups = []
    for group in user.groups.all():
        groups.append(str(group.name))
    return groups

def stringify_groups(user):
    groups = []
    for group in user.groups.all():
        groups.append(str(group.name))
    return groups

def format_date_string(date_string, date_format='%d/%m/%Y'):
    '''
    This function converts the date from string to datetime format
    '''
    date = datetime.datetime.strptime(date_string, date_format)
    return date

def get_dict_from_object(object):
    temp_dict = {}
    for key in object:
        if isinstance(object[key], datetime.datetime):
            temp_dict[key] = object[key].astimezone(tz.tzutc()).strftime('%Y-%m-%dT%H:%M:%S')
        elif isinstance(object[key], FieldFile):
            temp_dict[key] = None
        else:
            temp_dict[key] = object[key]
    return temp_dict

def get_list_from_set(set_data):
    created_list = []
    for set_object in set_data:
        created_list.append(list(set_object)[1])
    return created_list

def create_purchase_feed_data(post_data, product_data, temp_customer_id):
    data = {}
    data['sap_customer_id'] = temp_customer_id
    product_purchase_date = format_date_string(post_data['purchase-date'])
    data['product_purchase_date'] = product_purchase_date
    data['customer_phone_number'] = mobile_format(post_data['customer-phone'])
    data['customer_name'] = post_data['customer-name']
    data['engine'] = product_data.engine
    data['veh_reg_no'] = product_data.veh_reg_no
    data['vin'] = product_data.product_id
    data['pin_no'] = data['state'] = data['city'] = None
    return data

def create_dispatch_feed_data(product_data):
    data = {}
    data['vin'] = product_data['CHASSIS']
    data['product_type'] = product_data['PRDT_TYPE']
    data['invoice_date'] = product_data['VEH_DIS_DT']
    data['dealer_id'] = product_data['KUNNR']
    data['unique_service_coupon'] = product_data['UCN_NO']
    data['valid_days'] = product_data['DAYS_LIMIT_TO']
    data['valid_kms'] = product_data['KMS_TO']
    data['service_type'] = product_data['SERV_TYP']
    data['coupon_status'] = settings.DEFAULT_COUPON_STATUS
    return data
    
def create_sa_feed_data(post_data, user_id, temp_sa_id):
    data ={}
    data['id'] = user_id
    data['phone_number'] = mobile_format(post_data['phone-number'])
    data['service_advisor_id'] = temp_sa_id
    data['name'] = post_data['name'].upper()
    data['status'] = post_data['status']
    data['address'] = None
    data['cdms_flag'] = False
    return data

def create_context(email_template_name, feedback_obj, comment_obj=None):
    ''' feedback due date not defined when ticket is created'''
    if comment_obj:
        comment = comment_obj.comment
    else:
        comment = ""
    created_date = convert_utc_to_local_time(feedback_obj.created_date, True)
    try:
        assignee = feedback_obj.assignee.user_profile.user.username
    except:
        assignee = ""
    try:
        due_date = feedback_obj.due_date.strftime(DATE_FORMAT)
    except:
        due_date = ""
    if settings.BRAND == 'bajaj':
        type = feedback_obj.type
    else:
        type = "feedback"
    data = get_email_template(email_template_name, settings.BRAND)
    data['newsubject'] = data['subject'].format(id = feedback_obj.id)
    data['content'] = data['body'].format(id=feedback_obj.id, type = type, reporter = feedback_obj.reporter.user_profile.user.username, 
                                          message = feedback_obj.description, created_date = created_date, 
                                          assign_to = assignee ,  priority =  feedback_obj.priority, comment = comment,
                                          root_cause = feedback_obj.root_cause, resolution = feedback_obj.resolution,
                                          due_date = due_date, resolution_time=total_time_spent(feedback_obj))

    return data

def subtract_dates(start_date, end_date): 
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d") 
    return start_date - end_date

def search_details(data):
    kwargs = {}
    search_results = []
    if data.has_key('VIN'):
        kwargs[ 'product_id' ] = data['VIN']
    elif data.has_key('Customer-ID'):
        kwargs[ 'customer_id' ] = get_updated_customer_id(data['Customer-ID'])
    elif data.has_key('Customer-Mobile'):
        kwargs[ 'customer_phone_number' ] = mobile_format(data['Customer-Mobile'])
    product_obj = models.ProductData.objects.filter(**kwargs)
    if not product_obj or not product_obj[0].purchase_date:
        key = data.keys()
        message = '''{0} '{1}' has no associated customer. Please register the customer.'''.format(key[0], data[key[0]])            
        logger.info(message)
        return {'message': message}
    for product in product_obj:
        data = format_product_object(product)
        search_results.append(data)
    return search_results

def get_search_query_params(request, class_self):
    custom_search_enabled = False
    if 'custom_search' in request.GET and 'val' in request.GET:
        class_self.search_fields = ()
        request.GET = request.GET.copy()
        class_self.search_fields = (request.GET.pop("custom_search")[0],)
        search_value = request.GET.pop("val")[0]
        request.GET["q"] = search_value
        request.META['QUERY_STRING'] = 'q=%s'% search_value
        custom_search_enabled = True
    return custom_search_enabled

def get_start_and_end_date(start_date, end_date, format):

    start_date = start_date.strftime(format)
    start_date = datetime.datetime.strptime(start_date, format)
    end_date = end_date.strftime(format)
    end_date = datetime.datetime.strptime(end_date, format)
    return start_date,end_date

def get_min_and_max_filter_date():
    import datetime
    return (datetime.date.today() - datetime.timedelta(6*365/12)).isoformat(), (datetime.date.today()).isoformat()

#TODO Function needs to be refactored
def set_wait_time(feedback_data):
    start_date = feedback_data.pending_from
    end_date = datetime.datetime.now()
    start_date = convert_utc_to_local_time(start_date)
    start_date = start_date.strftime(TIME_FORMAT)
    end_date = end_date.strftime(TIME_FORMAT)
    start_date = datetime.datetime.strptime(start_date, TIME_FORMAT)
    end_date = datetime.datetime.strptime(end_date, TIME_FORMAT)
    wait = end_date - start_date
    wait_time = wait.total_seconds()
    previous_wait = feedback_data.wait_time
    get_model('Feedback').objects.filter(id = feedback_data.id).update(wait_time = wait_time+previous_wait)


def services_search_details(data):
    key = data.keys()
    message = '''No Service Details available for {0} '{1}'. Please register the customer.'''.format(key[0], data[key[0]])
    kwargs = {}
    response = {}
    search_results = []
    if data.has_key('VIN'):
        kwargs[ 'product_id' ] = data['VIN']
    elif data.has_key('Customer-ID'):
        kwargs[ 'customer_id' ] = get_updated_customer_id(data['Customer-ID'])
    product_obj = models.ProductData.objects.filter(**kwargs)
    if len(product_obj) == 1:
        if not product_obj[0].purchase_date:
            return {'message': message}
        try:
            coupon_obj = models.CouponData.objects.filter(product=product_obj[0]).order_by('service_type')
            if len(coupon_obj) > 0:
                for coupon in coupon_obj:
                    temp = {}
                    temp['service_type'] = coupon.service_type
                    temp['status'] = STATUS_CHOICES[coupon.status - 1][1]
                    search_results.append(temp)
                response['search_results'] = search_results
                response['other_details'] = {'vin': product_obj[0].product_id, 'customer_id': product_obj[0].customer_id,\
                                             'customer_name': product_obj[0].customer_name}
                return response
            else:
                return {'message': message}
        except Exception as ex:
            logger.log(ex)
            return {'message': ex}
    else:
        return {'message': message}
    
def get_updated_customer_id(customer_id):
    if customer_id and customer_id.find('T') == 0:
        try:
            temp_customer_obj = models.CustomerTempRegistration.objects.select_related('product_data').\
                                       get(temp_customer_id=customer_id)
            customer_id = temp_customer_obj.product_data.customer_id
        except Exception as ex:
            logger.info("Temporary ID {0} does not exists: {1}".format(customer_id, ex))
    return customer_id


#FIXME: write better logic
def service_advisor_search(data):
    phone_number = mobile_format(data['phone_number'])
    message = phone_number + ' is active under another dealer.' 
    if Roles.ASCS in data['groups']:
        asc_data = models.AuthorizedServiceCenter.objects.get(
                    asc_id=data['current_user'])
        sa_details = models.ServiceAdvisor.objects.filter(user__phone_number=phone_number, asc=asc_data)
        sa_mobile_active = models.ServiceAdvisor.objects.filter(
                                    user__phone_number=phone_number,
                                    status='Y').exclude(asc=asc_data)
    else:
        dealer_data = models.Dealer.objects.get(
                    dealer_id=data['current_user'])
        sa_details = models.ServiceAdvisor.objects.filter(user__phone_number=phone_number, dealer=dealer_data)
        sa_mobile_active = models.ServiceAdvisor.objects.filter(
                                    user__phone_number=phone_number,
                                    status='Y').exclude(dealer=dealer_data)
    if not sa_details and not sa_mobile_active:
        message = 'Service advisor is not associated, Please register the service advisor.'
        return {'message': message}
    if sa_details:
        user_details = sa_details[0].user
        service_advisor_details = {'id': sa_details[0].service_advisor_id,
                                   'phone': data['phone_number'],
                                   'name':  user_details.user.first_name, 
                                   'status': sa_details[0].status,
                                   'active':len(sa_mobile_active),
                                   'message':message}
        return service_advisor_details
    return {'message': message, 'status': 'fail'}

def get_sql_data(query):
    conn = connections[settings.BRAND]
    cursor = conn.cursor()
    cursor.execute(query)
    data = dictfetchall(cursor)
    conn.close()
    return data

def total_time_spent(feedback_obj):
    wait_time = feedback_obj.wait_time
    if feedback_obj.resolved_date:
        start_date = convert_utc_to_local_time(feedback_obj.created_date)
        end_date = feedback_obj.resolved_date
        start_date, end_date = get_start_and_end_date(start_date,
                                                     end_date, TIME_FORMAT)
        wait = end_date - start_date
        wait_time = wait.total_seconds() 
        wait_time = wait_time - feedback_obj.wait_time
        minutes, seconds = divmod(wait_time, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        weeks, days = divmod(days, 7)
        return " {0} days ,{1}:{2}:{3}" .format(int(days),int(hours),int(minutes),int(seconds))

def asc_cuopon_data(asc_id, status_type):
    cuopon_details = models.CouponData.objects.filter(service_advisor__asc=asc_id, status=status_type)
    return len(cuopon_details)

def get_asc_data(data, role):
    location_details = {}
    if data.has_key('city') and data.has_key('state'):
        location_details['user__address'] = ', '.join([data['city'].upper(), data['state'].upper()])
    if role == 'asc':
        user_data = models.AuthorizedServiceCenter.objects.filter(**location_details)
        user_ids = user_data.values_list('asc_id', flat=True)
    else:
        user_data = models.Dealer.objects.filter(**location_details)
        user_ids = user_data.values_list('dealer_id', flat=True)
    user_list = User.objects.filter(username__in=user_ids)
    return user_list

def asc_cuopon_details(asc_id, status_type, year, month,role=None):
    if role == 'asc':
        asc_filter=[Q(service_advisor__asc__user = asc_id), Q(servicing_dealer=asc_id.user.username)]
    else:
        asc_filter=[Q(service_advisor__dealer__user = asc_id), Q(servicing_dealer=asc_id.user.username)]
    if month == 12:
        cuopon_details = models.CouponData.objects.filter(reduce(operator.or_, asc_filter),
                                                          status=status_type,
                                                          closed_date__range=[datetime.datetime(int(year),int(month),1,00,00,00),datetime.datetime(int(year)+1,1,1,00,00,00)])  
    else:
        cuopon_details = models.CouponData.objects.filter(reduce(operator.or_, asc_filter),
                                                          status=status_type,
                                                          closed_date__range=[datetime.datetime(int(year),int(month),1,00,00,00),datetime.datetime(int(year),int(month)+1,1,00,00,00)])
    cuopon_count = cuopon_details.extra({"closed_date":"date(closed_date)"}).values('closed_date').annotate(dcount=Count('closed_date'))
    coupon_data = {}
    no_of_days = get_number_of_days(year, month)
    for day in range(1, no_of_days):
        coupon_data[day] = 0
    for coupon in cuopon_count:
        coupon_data[coupon['closed_date'].day] = coupon['dcount']
    return coupon_data

def total_coupon_closed(coupon_data):
    return sum(coupon_data.values())

def get_state_city(details, address):
    if address == None or address == '':
        details['state'] = 'Null'
        details['city'] = 'Null'
    else:
        addr = address.split(',')
        if len(addr) == 2:
            details['state'] = addr[1]
            details['city'] = addr[0]
        else:
            details['city'] = addr[0]
            details['state'] = 'Null'

    return details

def gernate_years():
    start_year = 2013
    current_year = datetime.date.today().year
    year_list = []
    for date in range(start_year, current_year+1):
        year_list.append(str(date))
    return year_list

def get_time_in_seconds(time, unit):
    if unit == 'days':
        total_seconds = time * 86400
    elif unit == 'hrs':
        total_seconds = time * 3600
    else:
        total_seconds = time * 60
    return total_seconds

def get_number_of_days(year, month):
    return calendar.monthrange(int(year), int(month))[1] + 1

def get_escalation_mailing_list(escalation_list):
    escalation_mailing_list = []
    escalation_mobile_list = []
    for element in escalation_list:
        escalation_mailing_list.append(element.user.email)
        escalation_mobile_list.append(element.phone_number)
    return {'mail': escalation_mailing_list, 'sms': escalation_mobile_list}

def model_to_dict_for_datetime(object):
    data = model_to_dict(object)
    data['created_date'] = object.created_date
    data['modified_date'] = object.modified_date
    return data
    
    
    
