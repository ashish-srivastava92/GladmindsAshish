import logging
import json
import random
import datetime
import operator
import re
import requests

from gladminds.core.utils import check_password
from tastypie.http import HttpBadRequest
from collections import OrderedDict
from django.shortcuts import render_to_response, render
from django.http.response import HttpResponseRedirect, HttpResponse,\
    HttpResponseBadRequest, Http404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.db.models.query_utils import Q
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F

from gladminds.bajaj import models
from gladminds.core import utils
from gladminds.sqs_tasks import send_otp, send_customer_phone_number_update_message,\
    send_mail_for_feed_failure,send_mail_customer_phone_number_update_exceeds
from gladminds.core.managers.mail import sent_otp_email,\
    send_recovery_email_to_admin, send_mail_when_vin_does_not_exist
from gladminds.bajaj.services.coupons.import_feed import SAPFeed
from gladminds.core.apis.coupon_apis import CouponDataResource
from gladminds.core.managers.feed_log_remark import FeedLogWithRemark
from gladminds.core.cron_jobs.scheduler import SqsTaskQueue
from gladminds.core.constants import PROVIDER_MAPPING, PROVIDERS, GROUP_MAPPING,\
    USER_GROUPS, REDIRECT_USER, TEMPLATE_MAPPING, ACTIVE_MENU, MONTHS
from gladminds.core.utils import get_email_template, format_product_object,\
    get_file_name
from gladminds.core.auth_helper import Roles
from gladminds.core.auth.service_handler import check_service_active, Services
from gladminds.core.core_utils.utils import log_time
from gladminds.core.cron_jobs.queue_utils import send_job_to_queue
from gladminds.core.services.message_template import get_template
from gladminds.core.managers.audit_manager import sms_log
from gladminds.bajaj.services.coupons import export_feed
from gladminds.core.auth import otp_handler
from django.core.serializers.json import DjangoJSONEncoder
from django.template import loader
from django.template.context import Context

logger = logging.getLogger('gladminds')
TEMP_ID_PREFIX = settings.TEMP_ID_PREFIX
TEMP_SA_ID_PREFIX = settings.TEMP_SA_ID_PREFIX
AUDIT_ACTION = 'SEND TO QUEUE'

@check_service_active(Services.FREE_SERVICE_COUPON)
def auth_login(request, provider):
    if request.method == 'GET':
            if provider not in PROVIDERS:
                return HttpResponseBadRequest()
            return render(request, PROVIDER_MAPPING.get(provider, 'asc/login.html'))

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/aftersell/provider/redirect')
    return HttpResponseRedirect(request.path_info+'?auth_error=true')


@check_service_active(Services.FREE_SERVICE_COUPON)
def redirect_user(request):
    user_groups = utils.get_user_groups(request.user)
    for group in USER_GROUPS:
        if group in user_groups:
            return HttpResponseRedirect(REDIRECT_USER.get(group))
#     data = {'message': 'Invalid Credentials'}
#     return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponseBadRequest('Not Allowed')

@check_service_active(Services.FREE_SERVICE_COUPON)
def user_logout(request):
    if request.method == 'GET':
        #TODO: Implement brand restrictions.
        user_groups = utils.get_user_groups(request.user)
        for group in USER_GROUPS:
            if group in user_groups:
                logout(request)
                return HttpResponseRedirect(GROUP_MAPPING.get(group))

        return HttpResponseBadRequest()
    return HttpResponseBadRequest('Not Allowed')

@check_service_active(Services.FREE_SERVICE_COUPON)
@login_required()
def change_password(request):
    if request.method == 'GET':
        return render(request, 'portal/change_password.html')
    if request.method == 'POST':
        groups = utils.stringify_groups(request.user)
        if Roles.DEALERS in groups or Roles.ASCS in groups:
            user = User.objects.get(username=request.user)
            old_password = request.POST.get('oldPassword')
            new_password = request.POST.get('newPassword')
            check_pass = user.check_password(str(old_password))
            if check_pass:
                invalid_password = check_password(new_password)
                if (invalid_password):
                    data = {'message':"password does not match the rules",'status':False}
                else:    
                    user.set_password(str(new_password))
                    user.save()
                    data = {'message': 'Password Changed successfully', 'status': True}
            else:
                data = {'message': 'Old password wrong', 'status': False}
            return HttpResponse(json.dumps(data), content_type='application/json')
        else:
            return HttpResponseBadRequest('Not Allowed')


@check_service_active(Services.FREE_SERVICE_COUPON)
def generate_otp(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            user = User.objects.get(username=username)
            phone_number = ''
            user_profile_obj = models.UserProfile.objects.filter(user=user)
            if user_profile_obj:
                phone_number = user_profile_obj[0].phone_number
                logger.info('OTP request received . username: {0}'.format(username))
                token = otp_handler.get_otp(user=user)
                message = get_template('SEND_OTP').format(token)
                send_job_to_queue(send_otp, {'phone_number': phone_number, 'message': message,
                                         'sms_client': settings.SMS_CLIENT})
                logger.info('OTP sent to mobile {0}'.format(phone_number))
#             #Send email if email address exist
            if user.email:
                sent_otp_email(data=token, receiver=user.email, subject='Forgot Password')
        
            return HttpResponseRedirect('/aftersell/users/otp/validate?username='+username)
        
        except Exception as ex:
            logger.error('Invalid details, mobile {0}'.format(ex))
            return HttpResponseRedirect('/aftersell/users/otp/generate?details=invalid')    
    
    elif request.method == 'GET':
        return render(request, 'portal/get_otp.html')

@check_service_active(Services.FREE_SERVICE_COUPON)
def validate_otp(request):
    if request.method == 'GET':
        return render(request, 'portal/validate_otp.html')
    elif request.method == 'POST':
        try:
            otp = request.POST['otp']
            username = request.POST['username']
            logger.info('OTP {0} recieved for validation. username {1}'.format(otp, username))
            user = User.objects.get(username=username)
            user_profile = models.UserProfile.objects.get(user=user)
            otp_handler.validate_otp(otp, user=user_profile)
            logger.info('OTP validated for name {0}'.format(username))
            return render(request, 'portal/reset_pass.html', {'otp': otp})
        except Exception as ex:
            logger.error('OTP validation failed for name {0} : {1}'.format(username, ex))
            return HttpResponseRedirect('/aftersell/users/otp/generate?token=invalid')


@check_service_active(Services.FREE_SERVICE_COUPON)
def update_pass(request):
    try:
        otp = request.POST['otp']
        password = request.POST['password']
        data = utils.update_pass(otp, password)
        return HttpResponse(json.dumps(data), content_type='application/json')

    except:
        logger.error('Password update failed.')
        return HttpResponseRedirect('/aftersell/asc/login?error=true')


@check_service_active(Services.FREE_SERVICE_COUPON)
@login_required()
def register(request, menu):
    groups = utils.stringify_groups(request.user)
    use_cdms = True
    if len(set([Roles.ASCS, Roles.DEALERS, Roles.SDMANAGERS]).intersection(set(groups))) == 0:
        return HttpResponseBadRequest()

    if request.method == 'GET':
        user_id = request.user
        reset_password =  models.UserProfile.objects.get(user=request.user).reset_password
        if not reset_password:
            return render(request, 'portal/change_password.html')
        if Roles.DEALERS in groups:
            use_cdms=models.Dealer.objects.get(user__user=user_id).use_cdms
        return render(request, TEMPLATE_MAPPING.get(menu, 'portal/404.html'), {'active_menu' : ACTIVE_MENU.get(menu)\
                                                                    , 'groups': groups,
                                                                    'user_id' : user_id,
                                                                    'use_cdms' : use_cdms})
    elif request.method == 'POST':
        save_user = {
            'asc': save_asc_registration,
            'sa': save_sa_registration,
            'customer': register_customer
        }
        try:
            response_object = save_user[menu](request, groups)
            return HttpResponse(response_object, content_type="application/json")
        except Exception as ex:
            logger.error('[registration failure {0}] : {1}'.format(menu, ex))
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()

ASC_REGISTER_SUCCESS = 'ASC registration is complete.'
EXCEPTION_INVALID_DEALER = 'The dealer-id provided is not registered.'
ALREADY_REGISTERED = 'Already Registered Number.'


@check_service_active(Services.FREE_SERVICE_COUPON)
@log_time
def save_asc_registration(request, groups=None):
    if request.method == 'GET':
        return render(request, 'portal/asc_registration.html',
                      {'asc_registration': True})
    elif request.method == 'POST':
        data = request.POST
        try:
            asc_obj = models.ASCTempRegistration.objects.get(phone_number=data['phone-number'])
            return HttpResponse(json.dumps({'message': ALREADY_REGISTERED}),
                            content_type='application/json')
        except ObjectDoesNotExist as ex:
            
            dealer_data = data["dealer_id"] if data.has_key('dealer_id') else None  
            asc_obj = models.ASCTempRegistration(name=data['name'],
                 address=data['address'], password=data['password'],
                 phone_number=data['phone-number'], email=data['email'],
                 pincode=data['pincode'], dealer_id=dealer_data)
            asc_obj.save()
        return HttpResponse(json.dumps({'message': ASC_REGISTER_SUCCESS}),
                            content_type='application/json')

SA_UPDATE_SUCCESS = 'Service advisor status has been updated.'
SA_REGISTER_SUCCESS = 'Service advisor registration is complete.'
@log_time
def save_sa_registration(request, groups):
    data = request.POST
    existing_sa = False
    data_source = []
    phone_number = utils.mobile_format(str(data['phone-number']))
    if data['sa-id']:
        service_advisor_id = data['sa-id']
        existing_sa = True
    else:
        service_advisor_id = TEMP_SA_ID_PREFIX + str(random.randint(10**5, 10**6))
    data_source.append(utils.create_sa_feed_data(data, request.user.username, service_advisor_id))
    logger.info('[Temporary_sa_registration]:: Initiating dealer-sa feed for ID' + service_advisor_id)
    if Roles.ASCS in groups:
        feed_type='asc_sa'
    else:
        feed_type='dealer'
    feed_remark = FeedLogWithRemark(len(data_source),
                                                feed_type='Dealer Feed',
                                                action='Received', status=True)
    sap_obj = SAPFeed()
    feed_response = sap_obj.import_to_db(feed_type=feed_type,
                        data_source=data_source, feed_remark=feed_remark)
    if feed_response.failed_feeds > 0:
        failure_msg = list(feed_response.remarks.elements())[0]
        logger.info('[Temporary_sa_registration]:: dealer-sa feed fialed ' + failure_msg)
        return json.dumps({"message": failure_msg})
    logger.info('[Temporary_sa_registration]:: dealer-sa feed completed')
    if existing_sa:
        return json.dumps({'message': SA_UPDATE_SUCCESS})
    return json.dumps({'message': SA_REGISTER_SUCCESS})

CUST_UPDATE_SUCCESS = 'Customer phone number has been updated.'
CUST_REGISTER_SUCCESS = 'Customer has been registered with ID: '


@log_time
def register_customer(request, group=None):
    post_data = request.POST
    data_source = []
    existing_customer = False
    product_obj = models.ProductData.objects.filter(product_id=post_data['customer-vin'])
    if not post_data['customer-id']:
        temp_customer_id = utils.generate_temp_id(TEMP_ID_PREFIX)
    else:
        temp_customer_id = post_data['customer-id']
        existing_customer = True
    data_source.append(utils.create_purchase_feed_data(post_data, product_obj[0], temp_customer_id))

    check_with_invoice_date = utils.subtract_dates(data_source[0]['product_purchase_date'], product_obj[0].invoice_date)    
    check_with_today_date = utils.subtract_dates(data_source[0]['product_purchase_date'], datetime.datetime.now())
    if not existing_customer and check_with_invoice_date.days < 0 or check_with_today_date.days > 0:
        message = "Product purchase date should be between {0} and {1}".\
                format((product_obj[0].invoice_date).strftime("%d-%m-%Y"),(datetime.datetime.now()).strftime("%d-%m-%Y"))
        logger.info('[Temporary_cust_registration]:: {0} Entered date is: {1}'.format(message, str(data_source[0]['product_purchase_date'])))
        return json.dumps({"message": message})

    try:
        with transaction.atomic():
            customer_obj = models.CustomerTempRegistration.objects.filter(temp_customer_id = temp_customer_id)
            if customer_obj:
                customer_obj = customer_obj[0]
                if customer_obj.new_number != data_source[0]['customer_phone_number']:
                    update_count = models.Constant.objects.get(constant_name='mobile_number_update_count').constant_value
                    if customer_obj.mobile_number_update_count >= int(update_count) and group[0] != Roles.SDMANAGERS:
                        customer_update = models.CustomerUpdateFailure(product_id = product_obj[0],
                                                                       customer_name = data_source[0]['customer_name'],
                                                                       customer_id = customer_obj.temp_customer_id,
                                                                       updated_by = "dealer-"+ str(request.user),
                                                                       old_number = customer_obj.new_number,
                                                                       new_number = data_source[0]['customer_phone_number'])
                        customer_update.save()
                        message = get_template('PHONE_NUMBER_UPDATE_COUNT_EXCEEDED')
                        return json.dumps({'message' : message})

                    if models.UserProfile.objects.filter(phone_number=data_source[0]['customer_phone_number']):
                        message = get_template('FAILED_UPDATE_PHONE_NUMBER').format(phone_number=data_source[0]['customer_phone_number'])
                        return json.dumps({'message': message})
                    old_number = customer_obj.new_number
                    customer_obj.new_number = data_source[0]['customer_phone_number']
                    customer_obj.product_data = product_obj[0]
                    customer_obj.sent_to_sap = False
                    customer_obj.dealer_asc_id = str(request.user)
                    customer_obj.mobile_number_update_count+=1
                    update_history = models.CustomerUpdateHistory(temp_customer=customer_obj,
                                                                  updated_field='Phone Number',
                                                                  old_value=old_number,
                                                                  new_value=customer_obj.new_number,
                                                                  email_flag=False)
                    update_history.save()
                    message = get_template('CUSTOMER_MOBILE_NUMBER_UPDATE').format(customer_name=customer_obj.new_customer_name, new_number=customer_obj.new_number)
                    for phone_number in [customer_obj.new_number, old_number]:
                        phone_number = utils.get_phone_number_format(phone_number)
                        sms_log(settings.BRAND, receiver=phone_number, action=AUDIT_ACTION, message=message)
                        send_job_to_queue(send_customer_phone_number_update_message, {"phone_number":phone_number, "message":message, "sms_client":settings.SMS_CLIENT})
                            
                    if models.UserProfile.objects.filter(user__groups__name=Roles.BRANDMANAGERS).exists():
                        groups = utils.stringify_groups(request.user)
                        if Roles.ASCS in groups:
                            dealer_asc_id = "asc : " + customer_obj.dealer_asc_id
                        elif Roles.DEALERS in groups:
                            dealer_asc_id = "dealer : " + customer_obj.dealer_asc_id
                        else :
                            dealer_asc_id = "manager : " + customer_obj.dealer_asc_id
                        
                        message = get_template('CUSTOMER_PHONE_NUMBER_UPDATE').format(customer_id=customer_obj.temp_customer_id, old_number=old_number, 
                                                                                  new_number=customer_obj.new_number, dealer_asc_id=dealer_asc_id)
                        managers = models.UserProfile.objects.filter(user__groups__name=Roles.BRANDMANAGERS)
                        for manager in managers:
                            phone_number = utils.get_phone_number_format(manager.phone_number)
                            sms_log(settings.BRAND, receiver=phone_number, action=AUDIT_ACTION, message=message)
                            send_job_to_queue(send_customer_phone_number_update_message, {"phone_number":phone_number, "message":message, "sms_client":settings.SMS_CLIENT})

            else:
                if models.UserProfile.objects.filter(phone_number=data_source[0]['customer_phone_number']):
                    message = get_template('FAILED_UPDATE_PHONE_NUMBER').format(phone_number=data_source[0]['customer_phone_number'])
                    return json.dumps({'message': message})
                customer_obj = models.CustomerTempRegistration(product_data=product_obj[0], 
                                                               new_customer_name = data_source[0]['customer_name'],
                                                               new_number = data_source[0]['customer_phone_number'],
                                                               product_purchase_date = data_source[0]['product_purchase_date'],
                                                               temp_customer_id = temp_customer_id,
                                                               dealer_asc_id = str(request.user))
            customer_obj.save()
            logger.info('[Temporary_cust_registration]:: Initiating purchase feed')
            feed_remark = FeedLogWithRemark(len(data_source),
                                                feed_type='Purchase Feed',
                                                action='Received', status=True)
            sap_obj = SAPFeed()
            feed_response = sap_obj.import_to_db(feed_type='purchase', data_source=data_source, feed_remark=feed_remark)
            if feed_response.failed_feeds > 0:
                logger.info('[Temporary_cust_registration]:: ' + json.dumps(feed_response.remarks))
                raise ValueError('purchase feed failed!')
            logger.info('[Temporary_cust_registration]:: purchase feed completed')
    except Exception as ex: 
        logger.info(ex)

        return HttpResponseBadRequest()
    if existing_customer:
        return json.dumps({'message': CUST_UPDATE_SUCCESS})
    return json.dumps({'message': CUST_REGISTER_SUCCESS + temp_customer_id})


@check_service_active(Services.FREE_SERVICE_COUPON)
def recover_coupon_info(data):
    customer_id = data['customerId']
    logger.info('UCN for customer {0} requested by User {1}'.format(customer_id, data['current_user']))
    coupon_data = utils.get_coupon_info(data)
    if coupon_data:
        user_obj = models.UserProfile.objects.get(user=data['current_user'])
        file_obj = data['job_card']
        customer_id = data['customerId']
        reason = data['reason']
        file_obj.name = get_file_name(data, file_obj)
        destination = settings.JOBCARD_DIR.format('bajaj')
        bucket = settings.JOBCARD_BUCKET
        path = utils.upload_file(destination, bucket, file_obj, logger_msg="JobCard")
        ucn_recovery_obj = models.UCNRecovery(reason=reason, user=user_obj,
                                        customer_id=customer_id, file_location=path,
                                        unique_service_coupon=coupon_data.unique_service_coupon)
        ucn_recovery_obj.save()
        send_recovery_email_to_admin(ucn_recovery_obj, coupon_data)
        message = 'UCN for customer {0} is {1}.'.format(customer_id,
                                                    coupon_data.unique_service_coupon)
        return {'status': True, 'message': message}
    else:
        message = 'No coupon in progress for customerID {0}.'.format(customer_id) 
        return {'status': False, 'message': message}


def get_customer_info_old(data):
    try:
        product_obj = models.ProductData.objects.get(product_id=data['vin'])
    except Exception as ex:
        logger.info(ex)
        message = '''VIN '{0}' does not exist in our records. Please contact customer support: +91-7847011011.'''.format(data['vin'])
        if data['groups'][0] == Roles.DEALERS:
            data['groups'][0] = "Dealer"
        else:
            data['groups'][0] = "ASC"
        template = get_email_template('VIN DOES NOT EXIST', settings.BRAND)['body'].format(data['current_user'], data['vin'], data['groups'][0])
        send_mail_when_vin_does_not_exist(data=template)
        return {'message': message, 'status': 'fail'}
    if product_obj.purchase_date:
        product_data = format_product_object(product_obj)
        product_data['group'] = data['groups'][0] 
        return product_data
    else:
        message = '''VIN '{0}' has no associated customer. Please register the customer.'''.format(data['vin'])
        return {'message': message}

def vin_sync_feed(request):
    message=''
    post_data = request.POST.copy()
    post_data['current_user'] = request.user
    try:
        vin_sync_feed = export_feed.ExportUnsyncProductFeed(username=settings.SAP_CRM_DETAIL[
                       'username'], password=settings.SAP_CRM_DETAIL['password'],
                      wsdl_url=settings.VIN_SYNC_WSDL_URL, feed_type='VIN sync Feed')
        message = vin_sync_feed.export(data=post_data)
    except Exception as ex:
        logger.info(ex)

    return HttpResponse(content=json.dumps({'message':message}),  content_type='application/json')
    
def get_customer_info(data):
    try:
        product_obj = models.ProductData.objects.get(product_id=data['vin'])
    except Exception as ex:
        logger.info(ex)
        message = "The Chassis {0} is not available in the current database, please wait while the Main database is being scanned.".format(data['vin'])
        return {'message': message, 'status': 0}
    if product_obj.purchase_date:
        product_data = format_product_object(product_obj)
        product_data['group'] = data['groups'][0] 
        return {'product': product_data, 'status': 1}
    else:
        message = '''VIN '{0}' has no associated customer. Please register the customer.'''.format(data['vin'])
        return {'message': message, 'status': 1}

@login_required()
def exceptions(request, exception=None):
    groups = utils.stringify_groups(request.user)
    if len(set([Roles.ASCS, Roles.DEALERS, Roles.SDMANAGERS]).intersection(set(groups))) == 0:
        return HttpResponseBadRequest()
    is_dealer = False
    if Roles.DEALERS in groups:
        is_dealer = True
    if request.method == 'GET':
        template = 'portal/exception.html'
        data = None
        if exception in ['close', 'check']:
            if Roles.ASCS in groups:
                data = models.ServiceAdvisor.objects.active_under_asc(request.user)
            else:
                data = models.ServiceAdvisor.objects.active_under_dealer(request.user)
        return render(request, template, {'active_menu': exception,
                                           "data": data, 'groups': groups, 'is_dealer':is_dealer})
    elif request.method == 'POST':
        function_mapping = {
            'customer': get_customer_info,
            'recover': recover_coupon_info,
            'search': utils.search_details,
            'status': utils.services_search_details,
            'serviceadvisor': utils.service_advisor_search
        }
        try:
            post_data = request.POST.copy()
            post_data['current_user'] = request.user
            post_data['groups'] = groups
            if request.FILES:
                post_data['job_card']=request.FILES['jobCard']
            data = function_mapping[exception](post_data)
            return HttpResponse(content=json.dumps(data),  content_type='application/json')
        except Exception as ex:
            logger.error(ex)
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()


@check_service_active(Services.FREE_SERVICE_COUPON)
@login_required()
def users(request, users=None):
    groups = utils.stringify_groups(request.user)
    if not (Roles.ASCS in groups or Roles.DEALERS in groups):
        return HttpResponseBadRequest()
    if request.method == 'GET':
        template = 'portal/users.html'
        data=None
        data_mapping = {
            'sa': utils.get_sa_list_for_login_dealer,
            'asc': utils.get_asc_list_for_login_dealer
        }
        try:
            data = data_mapping[users](request.user)
        except:
            #It is acceptable if there is no data_mapping defined for a function
            pass
        return render(request, template, {'active_menu' : users, "data" : data, 'groups': groups})
    else:
        return HttpResponseBadRequest()


@check_service_active(Services.FREE_SERVICE_COUPON)
@login_required()
def get_sa_under_asc(request, id=None):
    template = 'portal/sa_list.html'
    data = None
    try:
        data = utils.get_sa_list_for_login_dealer(id)
    except:
            #It is acceptable if there is no data_mapping defined for a function
        pass
    return render(request, template, {'active_menu':'sa',"data": data})


def sqs_tasks_view(request):
    return render_to_response('trigger-sqs-tasks.html')


def trigger_sqs_tasks(request):
    sqs_tasks = {
        'send-feed-mail': 'send_report_mail_for_feed',
        'export-coupon-redeem': 'export_coupon_redeem_to_sap',
        'expire-service-coupon': 'expire_service_coupon',
        'send-reminder': 'send_reminder',
        'export-customer-registered': 'export_customer_reg_to_sap',
        'send_reminders_for_servicedesk': 'send_reminders_for_servicedesk',
        'export_purchase_feed_sync_to_sap': 'export_purchase_feed_sync_to_sap',
        'send_mail_for_policy_discrepency': 'send_mail_for_policy_discrepency',
        'export_cts_to_sap': 'export_cts_to_sap',
        'send_mail_for_feed_failure': 'send_mail_for_feed_failure',
        'send_mail_for_customer_phone_number_update':'send_mail_for_customer_phone_number_update',
        'send_mail_for_manufacture_data_discrepancy': 'send_mail_for_manufacture_data_discrepancy',
        'send_vin_sync_feed_details': 'send_vin_sync_feed_details'
    }

    taskqueue = SqsTaskQueue(settings.SQS_QUEUE_NAME, settings.BRAND)
    taskqueue.add(sqs_tasks[request.POST['task']], settings.BRAND)
    return HttpResponse()


def site_info(request):
    if request.method != 'GET':
        raise Http404
    brand = settings.BRAND
    return HttpResponse(json.dumps({'brand': brand}), content_type='application/json')


@check_service_active(Services.FREE_SERVICE_COUPON)
@login_required()
def reports(request):
    groups = utils.stringify_groups(request.user)
    report_data=[]
    if not (Roles.ASCS in groups or Roles.DEALERS in groups):
        return HttpResponseBadRequest()
    status_options = {'4': 'In Progress', '2':'Closed'}
    report_options = {'reconciliation': 'Reconciliation', 'credit':'Credit Note'}
    min_date, max_date = utils.get_min_and_max_filter_date()
    template_rendered = 'portal/reconciliation_report.html'
    report_data =  {'status_options': status_options,
                    'report_options': report_options,
                    'min_date':min_date,
                    'max_date': max_date}
    if request.method == 'POST':
        report_data['params'] = request.POST.copy()
        if report_data['params']['type']== 'credit':
            report_data['params']['status']='2'
            template_rendered = 'portal/credit_note_report.html'
        report_data['records'] = create_reconciliation_report(report_data['params'], request.user)
        if '_download' in request.POST:
            return download_reconcilation_reports(report_data)
    return render(request, template_rendered, report_data)

@log_time
def create_reconciliation_report(query_params, user):
    report_data = []
    filter = {}
    params = {}
    coupon_filter =[]
    args = [Q(status=4), Q(status=2), Q(status=6)]
    if user.groups.filter(name=Roles.DEALERS).exists():
        dealer = models.Dealer.objects.filter(dealer_id=user)
        coupon_filter=[Q(service_advisor__dealer = dealer[0]), Q(servicing_dealer=dealer[0].dealer_id)]
    else:
        ascs = models.AuthorizedServiceCenter.objects.filter(user=user)
        coupon_filter=[Q(service_advisor__asc = ascs[0]), Q(servicing_dealer=ascs[0].asc_id)]
    
    status = query_params.get('status')
    from_date = query_params.get('from')
    to_date = query_params.get('to')
    input_date_range = (str(from_date) + ' 00:00:00', str(to_date) +' 23:59:59')

    if query_params['type']=='credit': 
        filter['credit_date__range'] = input_date_range
    elif status=='4':
        filter['actual_service_date__range'] = input_date_range
    else:
        filter['closed_date__range'] = input_date_range

    if status:
        args = [Q(status=status)]
        if status=='2':
            args = [Q(status=2),Q(status=6)]
    all_coupon_data = models.CouponData.objects.filter(reduce(operator.or_, args), reduce(operator.or_, coupon_filter), **filter).order_by('-actual_service_date')
    map_status = {'6': 'Old FSC Closed', '4': 'In Progress', '2':'DFSC Closed'}
    for coupon_data in all_coupon_data:
        coupon_data_dict = {}
        coupon_data_dict['vin'] = coupon_data.product.product_id
        sa = coupon_data.service_advisor
        try:
            coupon_data_dict['sa_phone_name'] = sa.user.phone_number
        except:
            coupon_data_dict['sa_phone_name'] = None
        coupon_data_dict['service_avil_date'] = coupon_data.actual_service_date
        coupon_data_dict['closed_date'] = coupon_data.closed_date
        coupon_data_dict['service_status'] = map_status[str(coupon_data.status)]
        if query_params['type']== 'credit':
            product_details = coupon_data.product
            coupon_data_dict['customer_name'] = product_details.customer_name
            coupon_data_dict['customer_number'] = product_details.customer_phone_number
            coupon_data_dict['credit_date'] = coupon_data.credit_date
            coupon_data_dict['credit_note'] = coupon_data.credit_note
        else:
            coupon_data_dict['customer_id'] = coupon_data.product.customer_id
            coupon_data_dict['product_type'] = coupon_data.product.product_type
            coupon_data_dict['coupon_no'] = coupon_data.unique_service_coupon
            coupon_data_dict['kms'] = coupon_data.actual_kms
            coupon_data_dict['service_type'] = coupon_data.service_type
            coupon_data_dict['special_case'] = coupon_data.special_case
        report_data.append(coupon_data_dict)
        
    return report_data

#FIXME: Refactor the code
@check_service_active(Services.FREE_SERVICE_COUPON)
def get_active_asc_report(request, role=None):
    '''get number of tickets closed by ASC'''
    if request.method != 'GET':
        return HttpResponse(json.dumps({"message":"method not allowed"}), content_type="application/json",status=401)
    try:
        role = request.path.split('/')[3]
        data = request.GET.copy()
        if data.has_key('month'):
            month = MONTHS.index(data['month']) + 1
            year = data['year']
        else:
            now = datetime.datetime.now()
            year = now.year
            month = now.month
        no_of_days = utils.get_number_of_days(year, month)
        coupon_resource = CouponDataResource()
        asc_query=coupon_resource.closed_ticket(year, month, role)
        asc_list = []
        for asc in asc_query:
            active = filter(lambda active: active['id']==asc['asc_id'], asc_list)
            if not active:
                temp= {}
                temp['id'] = asc['asc_id'] 
                temp['name'] = asc['first_name']
                temp['address'] = asc['address']
                temp['coupon_closed'] = {}
                for day in range(1, no_of_days):
                    temp['coupon_closed'][day] = 0
                day = int(asc['day'])
                temp['total_coupon_closed'] = 0 
                temp['coupon_closed'][day]= asc['cnt']
                temp['total_coupon_closed'] = temp['total_coupon_closed'] + asc['cnt']
                asc_list.append(temp)
            else:
                day = int(asc['day'])
                active[0]['coupon_closed'][day]= asc['cnt']
                active[0]['total_coupon_closed'] = active[0]['total_coupon_closed'] + asc['cnt']
    except Exception as ex:
        logger.error('Exception while counting data : {0}'.format(ex))
        return HttpResponseBadRequest()
    years = utils.gernate_years()
    return render(request, 'portal/asc_report.html',\
                  {"data": asc_list,
                   "range": range(1, no_of_days),
                   "month": MONTHS,
                   "years": years,
                   "mon": MONTHS[int(month)-1],
                   "cyear": str(year),
                   "role": role
                   })
    
'''Download the reconciliation report under the filter criteria'''
    
def download_reconcilation_reports(download_data):
    response = HttpResponse(content_type='text/excel')
    response['Content-Disposition'] = 'attachment; filename="ReportList.xlsx"'
    if download_data['params']['type']== 'credit':
        template = loader.get_template('portal/reconciliation_credit_download.html')
    else:
        template = loader.get_template('portal/reconciliation_download.html')
    c = Context({
        'data': download_data['records'],
    })
    response.write(template.render(c))
    return response
