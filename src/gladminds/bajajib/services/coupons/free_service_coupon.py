'''Handlers for free service coupon logic'''

from datetime import datetime, timedelta
import logging

from django.conf import settings
from django.db.models import Q
from django.db.models.aggregates import Max
from django.utils import timezone

from gladminds.bajajib import models
from gladminds.core import utils
from gladminds.core.base_models import STATUS_CHOICES
from gladminds.core.core_utils.utils import log_time
from gladminds.core.cron_jobs.queue_utils import send_job_to_queue
from gladminds.core.managers.audit_manager import sms_log
from gladminds.core.services import message_template as templates
from gladminds.core.stats import LOGGER
from gladminds.settings import COUPON_VALID_DAYS
from gladminds.sqs_tasks import send_service_detail, \
    send_coupon_detail_customer, send_coupon, send_invalid_keyword_message
import pytz
import unicodedata

LOG = logging.getLogger('gladminds')
json = utils.import_json()


__all__ = ['GladmindsTaskManager']
AUDIT_ACTION = 'SEND TO QUEUE'


def update_coupon_expiry(product, purchase_date):
    coupon_data = models.CouponData.objects.filter(product=product)
    for coupon in coupon_data:
        mark_expired_on = purchase_date + timedelta(days=int(coupon.valid_days))
        coupon.mark_expired_on = mark_expired_on
        coupon.save()
    return

@log_time
def register_owner(sms_dict, phone_number):
    '''
       A function that handles owner registration
    '''
    dealer = models.Dealer.objects.active_dealer(phone_number)
    service_advisor = validate_sa_for_registration(phone_number)
    if not dealer  and (service_advisor is None) :
        message = templates.get_template('UNAUTHORISED_DEALER')
        return {'message' : message, 'status': False}
    registration_number = sms_dict['registration_number']
    owner_phone_number = sms_dict['phone_number']
    customer_name = sms_dict['customer_name']
    customer_district = sms_dict['district']
    customer_support = models.Constant.objects.get(constant_name='customer_support_number_uganda').constant_value
    try:
        purchase_date_format = models.Constant.objects.get(constant_name='purchase_date_format',
                                                           country__name='UGA').constant_value
        purchase_date = datetime.strptime(sms_dict['purchase_date'], purchase_date_format)
        
        if purchase_date > datetime.now():
            message = templates.get_template('INVALID_REGISTRATION_NUMBER_OR_PURCHASE_DATE').format(phone_number=customer_support)
            return {'message' : message, 'status': False}
            
        product = models.ProductData.objects.get(veh_reg_no=registration_number)
        all_products = models.ProductData.objects.all().aggregate(Max('customer_id'))
        if all_products['customer_id__max']:
            customer_id = int(all_products['customer_id__max']) + 1
        else:
            customer_id = models.Constant.objects.get(constant_name='customer_id').constant_value
        if not product.purchase_date:
            product.customer_name = customer_name
            product.customer_phone_number = owner_phone_number
            product.purchase_date = purchase_date
            product.customer_id = customer_id
            product.customer_district = customer_district
            update_coupon_expiry(product, purchase_date)
            product.save()

            owner_message = templates.get_template('SEND_OWNER_REGISTER').format(customer_name=product.customer_name,
                                                                            customer_id=product.customer_id)
            sms_log(settings.BRAND, receiver=product.customer_phone_number, action=AUDIT_ACTION, message=owner_message)
            send_job_to_queue(send_coupon, {"phone_number":product.customer_phone_number, "message": owner_message,
                                            "sms_client":settings.SMS_CLIENT})

        elif(product.customer_phone_number != owner_phone_number):
            update_history = models.CustomerUpdateHistory(updated_field='phone_number',
                                                          old_value=product.customer_phone_number,
                                                          new_value=owner_phone_number,
                                                          product=product)
            update_history.save()
            old_number = product.customer_phone_number
            product.customer_phone_number = owner_phone_number
            product.save()
            owner_message = templates.get_template('OWNER_MOBILE_NUMBER_UPDATE').format(customer_name=product.customer_name,
                                                                            new_number=owner_phone_number, phone_number=customer_support)
            
            for phone_number in [old_number, owner_phone_number]:
                sms_log(settings.BRAND, receiver=phone_number, action=AUDIT_ACTION, message=owner_message)
                send_job_to_queue(send_coupon, {"phone_number":phone_number, "message": owner_message,
                                        "sms_client":settings.SMS_CLIENT})
        else:
            if product.customer_phone_number == owner_phone_number:
                sa_message_for_owner = templates.get_template('OWNER_MOBILE_NUMBER_EXIST')
                send_job_to_queue(send_service_detail, {"phone_number": phone_number,
                                                "message": sa_message_for_owner,
                                                "sms_client": settings.SMS_CLIENT})
            
        data = {'message' : owner_message, 'status': True}
    except Exception as ex:
        LOG.info('[register_owner]:Exception : '.format(ex))
        message = templates.get_template('INVALID_REGISTRATION_NUMBER_OR_PURCHASE_DATE').format(phone_number=customer_support)
        sms_log(settings.BRAND, receiver=owner_phone_number, action=AUDIT_ACTION, message=message)
#         send_job_to_queue(send_coupon, {"phone_number":owner_phone_number, "message": message,
#                                             "sms_client":settings.SMS_CLIENT})

        data = {'message' : message, 'status': False}

    return data 

@log_time
def register_rider(sms_dict, phone_number):
    '''
    A function that handles rider registration
    '''
    dealer = models.Dealer.objects.active_dealer(phone_number)
    service_advisor = validate_sa_for_registration(phone_number)
    if not dealer and service_advisor is None:
        message = templates.get_template('UNAUTHORISED_DEALER')
        return {'message' : message}

    registration_number = sms_dict['registration_number']
    rider_phone_number = sms_dict['phone_number']
    try:
        customer_support = models.Constant.objects.get(constant_name='customer_support_number_uganda').constant_value
        product = models.ProductData.objects.get(veh_reg_no=registration_number)
        if product:
            riders = models.FleetRider.objects.filter(product=product, phone_number=rider_phone_number)
            if not riders:
                rider = models.FleetRider(product=product, is_active=True, phone_number=rider_phone_number)
                rider.save()
            else:
                riders.update(is_active=True)
                    
            riders = models.FleetRider.objects.filter(Q(product=product),~Q(phone_number=rider_phone_number))
            riders.update(is_active=False)
            
            rider_message = templates.get_template('SEND_RIDER_REGISTER').format(phone_number=rider_phone_number)
            sms_log(settings.BRAND, receiver=rider_phone_number, action=AUDIT_ACTION, message=rider_message)
            send_job_to_queue(send_coupon, {"phone_number":rider_phone_number, "message": rider_message,
                                            "sms_client":settings.SMS_CLIENT})
            owner_message = templates.get_template('SEND_RIDER_REGISTER_TO_OWNER').format(customer_name=product.customer_name,
                                                                                          registration_number=product.registration_number,
                                                                                          phone_number=customer_support)
            sms_log(settings.BRAND, receiver=product.customer_phone_number, action=AUDIT_ACTION, message=owner_message)
            send_job_to_queue(send_coupon, {"phone_number":product.customer_phone_number, "message": owner_message,
                                            "sms_client":settings.SMS_CLIENT})
            
            message = templates.get_template('RIDER_SUCCESSFULLY_REGISTERED')
            data = {'message' : message, 'status': True}
    except Exception as ex:
        LOG.info('[register_rider]:Exception : '.format(ex))
        message = templates.get_template('INVALID_REGISTRATION_NUMBER').format(phone_number=customer_support)
        data = {'message' : message, 'status': False}
    
    return data

@log_time
def update_customer(sms_dict, phone_number):
    pass

@log_time
def validate_coupon(sms_dict, phone_number):
    '''
        A function that handles coupon check
    '''
    #vehicle_registration_no = sms_dict['veh_reg_no']
    service_type = sms_dict['service_type']
    dealer_message = None
    customer_message = None
    customer_phone_number = None
    customer_message_countdown = settings.DELAY_IN_CUSTOMER_UCN_MESSAGE
    vehicle_registration_no = sms_dict.get('veh_reg_no', None)
    service_advisor = validate_service_advisor(phone_number)
    
    if settings.LOGAN_ACTIVE:
        LOGGER.post_event("check_coupon", {'sender':phone_number,
                                          'brand':settings.BRAND})
    if not service_advisor:
        return {'status': False, 'message': templates.get_template('UNAUTHORISED_SA')}
     
#     if not is_valid_data(customer_registration=customer_registration, sa_phone=phone_number):
#         return {'status': False, 'message': templates.get_template('SEND_SA_WRONG_CUSTOMER_UCN'

    if service_type not in ['1','2','3']:
        return {'status': False, 'message': templates.get_template('INVALID_ST')}
    try:
        product_data_list = get_product(sms_dict)
        customer_support = models.Constant.objects.get(constant_name='customer_support_number_uganda').constant_value
        if not product_data_list:
                    # This new line is added 
                    message = templates.get_template('INVALID_VEH_REG_NO').format(
                                                    support_number=customer_support)
                    return {'status': False, 'message': message}
                   # return {'status': False, 'message': templates.get_template('INVALID_VEH_REG_NO')}
        LOG.info("Associated product %s" % product_data_list.product_id)
#         update_exceed_limit_coupon(actual_kms, product, service_advisor)
        valid_coupon = models.CouponData.objects.filter( (Q(status=1) | Q(status=4) | Q(status=5))  & Q(product=product_data_list.id)
                                                         & Q(service_type=service_type )) 
        try :
            closed_coupon_latest = models.CouponData.objects.filter( Q(status=2) & Q(product=product_data_list.id) ).latest('closed_date')
        except:
            closed_coupon_latest = []
            
        if not valid_coupon:
            return {'status': False, 'message': templates.get_template('COUPON_ALREADY_CLOSED')}
        LOG.info("List of available valid coupons %s" % valid_coupon)
        if len(valid_coupon) > 0:
            valid_coupon = valid_coupon[0]
            LOG.info("valid coupon %s" % valid_coupon)
            coupon_sa_obj = models.ServiceAdvisorCouponRelationship.objects.filter(unique_service_coupon=valid_coupon\
                                                                                ,service_advisor=service_advisor)
            LOG.info('Coupon_sa_obj exists: %s' % coupon_sa_obj)
            if not len(coupon_sa_obj):
                coupon_sa_obj = models.ServiceAdvisorCouponRelationship(unique_service_coupon=valid_coupon\
                                                                        ,service_advisor=service_advisor)
                coupon_sa_obj.save()
                LOG.info('Coupon obj created: %s' % coupon_sa_obj)

        in_progress_coupon = models.CouponData.objects.filter(product=product_data_list.id, status=4) \
                             .select_related ('product').order_by('service_type')
                             
        try:
            customer_phone_number = product_data_list.customer_phone_number
        except Exception as ax:
            LOG.error('Customer Phone Number is not stored in DB %s' % ax)
            
        rider = models.FleetRider.objects.filter(product=product_data_list, is_active=True)
        rider_message={'message':None}
        if rider:
            rider_phone_number = rider[0].phone_number
        else:
            rider = None
            
        if len(in_progress_coupon) > 0:
            update_inprogress_coupon(in_progress_coupon[0], service_advisor)
            LOG.info("Validate_coupon: Already in progress coupon")
            if (in_progress_coupon[0] == valid_coupon):
                dealer_message = templates.get_template('COUPON_ALREADY_INPROGRESS').format(
                                                    service_type=service_type,
                                                    customer_id=product_data_list.customer_id)
                
                
                customer_message = templates.get_template('SEND_CUSTOMER_VALID_COUPON').format(customer_name=product_data_list.customer_name,
                                                    coupon=in_progress_coupon[0].unique_service_coupon,
                                                    service_type=in_progress_coupon[0].service_type)
                rider_message  = customer_message
                
            else:
                #in_progress_coupon_name = in_progress_coupon[0].unique_service_coupon
                dealer_message = templates.get_template('PLEASE_CLOSE_INPROGRESS_COUPON').format(
                                                    coupon=in_progress_coupon[0].unique_service_coupon)
                
                #dealer_message = templates.get_template('PLEASE_CLOSE_INPROGRESS_COUPON')
        elif valid_coupon:
            
            if closed_coupon_latest:
                closed_coupon_date = closed_coupon_latest.closed_date
                today = datetime.now(pytz.utc)
                free_service_coupon_diffrence = (today-closed_coupon_date).days
                if free_service_coupon_diffrence < 15:
                    return {'status': False, 'message': templates.get_template('INVALID_SERVICE_DIFFERENCE')}
            
            LOG.info("Validate_coupon: valid coupon")
            update_coupon(valid_coupon, service_advisor, 4, datetime.now())
            dealer_message = templates.get_template('SEND_SA_VALID_COUPON').format(
                                            service_type=service_type,
                                            customer_id=product_data_list.customer_id, customer_phone=product_data_list.customer_phone_number)
            customer_message = templates.get_template('SEND_CUSTOMER_VALID_COUPON').format(
                                        customer_name=product_data_list.customer_name,coupon=valid_coupon.unique_service_coupon,
                                        service_type=valid_coupon.service_type)
            rider_message = customer_message
        else:
            LOG.info("Validate_coupon: No valid or in-progress coupon")
            requested_coupon_status = get_requested_coupon_status(product_data_list.id, service_type)
            dealer_message = templates.get_template('SEND_SA_OTHER_VALID_COUPON').format(
                                        req_service_type=service_type,
                                        req_status=requested_coupon_status,
                                        customer_id=product_data_list.customer_id)
            customer_message = dealer_message
            rider_message = dealer_message
            
        try:
            val =unicodedata.normalize('NFKD', rider_message).encode('ascii','ignore')
            if rider and val != None:
                sms_log(settings.BRAND, receiver=rider_phone_number, action=AUDIT_ACTION, message=rider_message)
                send_job_to_queue(send_coupon, {"phone_number":rider_phone_number, "message": rider_message,
                                                        "sms_client":settings.SMS_CLIENT})
        except Exception as ex:
            LOG.info('[Rider_message]:Exception : '.format(ex))
        sms_log(settings.BRAND, receiver=customer_phone_number, action=AUDIT_ACTION, message=customer_message)
        send_job_to_queue(send_coupon_detail_customer, {"phone_number":utils.get_phone_number_format(customer_phone_number), "message":customer_message, "sms_client":settings.SMS_CLIENT},
                          delay_seconds=customer_message_countdown)
        sms_log(settings.BRAND, receiver=phone_number, action=AUDIT_ACTION, message=dealer_message)
        send_job_to_queue(send_service_detail, {"phone_number": phone_number,
                                                "message": dealer_message,
                                                "sms_client": settings.SMS_CLIENT})

    except Exception as ex:
        LOG.info('[validate_coupon]:Exception : '.format(ex))
        dealer_message = templates.get_template('SEND_INVALID_MESSAGE')
    finally:
        LOG.info("validate message send to SA %s" % dealer_message)
        phone_number = utils.get_phone_number_format(phone_number)
        sms_log(settings.BRAND, receiver=phone_number, action=AUDIT_ACTION, message=dealer_message)
        send_job_to_queue(send_service_detail, {"phone_number": phone_number,
                                                "message": dealer_message,
                                                "sms_client": settings.SMS_CLIENT})
    return {'status': True, 'message': dealer_message}


@log_time
def close_coupon(sms_dict, phone_number):
    '''
        A function that handles coupon close
    '''
    service_advisor = validate_service_advisor(phone_number, close_action=True)
    unique_service_coupon = sms_dict['usc']
    customer_id = sms_dict.get('sap_customer_id', None)
    message = None
    if settings.LOGAN_ACTIVE:
        LOGGER.post_event("close_coupon", {'sender':phone_number,
                                          'brand':settings.BRAND})
    if not service_advisor:
        return {'status': False, 'message': templates.get_template('UNAUTHORISED_SA')}
    
    sa_uinitiator_result, msg = is_sa_initiator(unique_service_coupon, service_advisor, phone_number)
    if not is_sa_initiator(unique_service_coupon, service_advisor, phone_number):
        return {'status': False, 'message': msg}
    
    try:
        product = get_product(sms_dict)
        if not product:
                    return {'status': False, 'message': templates.get_template('INVALID_CUSTOMER_ID')}
        coupon_object = models.CouponData.objects.filter(product=product.id,
                                                         unique_service_coupon=unique_service_coupon).select_related ('product')
        if not coupon_object:
                    return {'status': False, 'message': templates.get_template('INVALID_UCN')}
        coupon_object = coupon_object[0]     
        if coupon_object.status == 2 or coupon_object.status == 6:
            message = templates.get_template('COUPON_ALREADY_CLOSED')
        elif coupon_object.status == 4:
            customer_phone_number = coupon_object.product.customer_phone_number
            coupon_object.status = 2
            coupon_object.service_advisor = service_advisor
            coupon_object.closed_date = datetime.now()
            coupon_object.save()
            message = templates.get_template('SEND_SA_CLOSE_COUPON').format(customer_id=customer_id, usc=unique_service_coupon)
        else:
            message = templates.get_template('SEND_SA_WRONG_CUSTOMER_UCN')
    except Exception as ex:
        LOG.error("[Exception_coupon_close] {0}".format(ex))
        message = templates.get_template('SEND_INVALID_MESSAGE')
    finally:
        LOG.info("Close coupon with message %s" % message)
        phone_number = utils.get_phone_number_format(phone_number)
        sms_log(settings.BRAND, receiver=phone_number, action=AUDIT_ACTION, message=message)
        send_job_to_queue(send_coupon, {"phone_number":phone_number, "message": message, "sms_client":settings.SMS_CLIENT})
    return {'status': True, 'message': message}

def validate_service_advisor(phone_number, close_action=False):
    message = None
    all_sa_dealer_obj = models.ServiceAdvisor.objects.active(phone_number)
    if not len(all_sa_dealer_obj):
        message = templates.get_template('UNAUTHORISED_SA')
    elif close_action and all_sa_dealer_obj[0].dealer and all_sa_dealer_obj[0].dealer.use_cdms:
        message = templates.get_template('DEALER_UNAUTHORISED')
    if message:
        sa_phone = utils.get_phone_number_format(phone_number)
        sms_log(settings.BRAND, receiver=sa_phone, action=AUDIT_ACTION, message=message)
        send_job_to_queue(send_service_detail, {"phone_number":sa_phone, "message": message, "sms_client":settings.SMS_CLIENT})
        return None
    service_advisor_obj = all_sa_dealer_obj[0]
    if service_advisor_obj.dealer:
        dealer_asc_obj = service_advisor_obj.dealer
        dealer_asc_obj.last_transaction_date = datetime.now()
    else:
        dealer_asc_obj = service_advisor_obj.asc
        dealer_asc_obj.last_transaction_date = datetime.now()

    dealer_asc_obj.save(using=settings.BRAND) 

    return service_advisor_obj


def is_sa_initiator(coupon_id, service_advisor, phone_number):
    coupon_sa_obj = []
    coupon_data = models.CouponData.objects.filter(unique_service_coupon=coupon_id)
    
    if len(coupon_data) is 0:
        sa_phone = utils.get_phone_number_format(phone_number)
        message = "Unique service coupon you entered is not valid"
        sms_log(settings.BRAND, receiver=sa_phone, action=AUDIT_ACTION, message=message)
        send_job_to_queue(send_invalid_keyword_message, {"phone_number":sa_phone, "message": message, "sms_client":settings.SMS_CLIENT})
        return False, message
    
    else:
        coupon_sa_obj = models.ServiceAdvisorCouponRelationship.objects.filter(unique_service_coupon=coupon_data\
                                                                        ,service_advisor=service_advisor)
    if len(coupon_sa_obj) > 0:
        return True
    else:
        sa_phone = utils.get_phone_number_format(phone_number)
        message = "SA is not the coupon initiator."
        sms_log(settings.BRAND, receiver=sa_phone, action=AUDIT_ACTION, message=message)
        send_job_to_queue(send_invalid_keyword_message, {"phone_number":sa_phone, "message": message, "sms_client":settings.SMS_CLIENT})
    return False, message


def is_valid_data(customer_id=None, coupon=None, sa_phone=None):
    '''
        Error During wrong entry of Customer ID or UCN (message to the service advisor)
        -    "Wrong Customer ID or UCN"
    '''
    coupon_obj = customer_obj = []
    message = ''
    if coupon: 
        coupon_obj = models.CouponData.objects.filter(unique_service_coupon=coupon)
    if customer_id:
        customer_id = models.CustomerTempRegistration.objects.get_updated_customer_id(customer_id)
        customer_obj = models.ProductData.objects.filter(customer_id=customer_id)
    if ((customer_obj and coupon_obj and coupon_obj[0].product.product_id != customer_obj[0].product_id) or\
        (not customer_obj and not coupon_obj)):
        message = templates.get_template('SEND_SA_WRONG_CUSTOMER_UCN')

    elif customer_id and not customer_obj:
        message = templates.get_template('SEND_SA_WRONG_CUSTOMER_UCN')
    elif coupon and not coupon_obj:
        message = templates.get_template('SEND_SA_WRONG_CUSTOMER_UCN')

    if message:
        sa_phone = utils.get_phone_number_format(sa_phone)
        sms_log(settings.BRAND, receiver=sa_phone, action=AUDIT_ACTION, message=message)
        send_job_to_queue(send_invalid_keyword_message, {"phone_number":sa_phone, "message": message, "sms_client":settings.SMS_CLIENT})
        LOG.info("Message sent to SA : " + message)
        return False
    return True

def get_customer_phone_number_from_vin(vin):
    product_obj = models.ProductData.objects.filter(product_id=vin)
    return product_obj[0].customer_phone_number


def update_higher_range_coupon(kms, product):
    '''
        Update those coupon have higher value than the least in progress
        coupon. These case existed because some time user add higher value
        of kilometer.
    '''
    updated_coupon = models.CouponData.objects\
                    .filter(Q(status=4) | Q(status=5), product=product, valid_kms__gt=kms)\
                    .update(status=1, service_advisor=None, actual_kms=None,
                            actual_service_date=None)
    LOG.info("%s have higher KMS range" % updated_coupon)


def update_exceed_limit_coupon(actual_kms, product, service_advisor):
    '''
        Exceed Limit those coupon whose kms limit is small then actual kms limit
    '''
    exceed_limit_coupon = models.CouponData.objects\
        .filter(Q(status=1) | Q(status=4), product=product, valid_kms__lt=actual_kms)\
        .update(status=5, actual_kms=actual_kms, service_advisor=service_advisor, actual_service_date=datetime.now())
    LOG.info("%s are exceed limit coupon" % exceed_limit_coupon)


def get_product(sms_dict):
    try:
        if sms_dict.has_key('veh_reg_no'):
                product_data = models.ProductData.objects.get(veh_reg_no = sms_dict['veh_reg_no'])
                
        elif sms_dict.has_key('sap_customer_id'):
                #customer_id = models.CustomerTempRegistration.objects.get_updated_customer_id(sms_dict['customer_id'])
                product_data = models.ProductData.objects.get(customer_id = sms_dict['sap_customer_id'])
        
        return product_data
    except Exception as ax:
        LOG.error("Vehicle registration number OR Customer ID is not in customer_product_data Error %s " % ax)


def update_coupon(valid_coupon, service_advisor, status, \
                                           update_time):
    try:  
        # valid_coupon.actual_kms = actual_kms
        valid_coupon.actual_service_date = update_time
        valid_coupon.extended_date = update_time + timedelta(days=COUPON_VALID_DAYS)
        valid_coupon.status = status
        valid_coupon.service_advisor = service_advisor
        valid_coupon.save()
    except Exception as ex:
        LOG.error("Update coupon error for check command %s " % ex)
        


def update_inprogress_coupon(coupon, service_advisor):
    LOG.info("Expired on %s" % coupon.mark_expired_on)
    LOG.info("Extended on %s" % coupon.extended_date)
    expiry_date = coupon.mark_expired_on
    if coupon.extended_date < expiry_date:
        coupon.extended_date = expiry_date
        coupon.save()

    validity_date = coupon.extended_date
    today = timezone.now()
    current_time = datetime.now()
    if expiry_date >= today:
        coupon.extended_date = current_time + timedelta(days=COUPON_VALID_DAYS)
        update_coupon(coupon,service_advisor, 4, current_time)
    elif validity_date >= today and expiry_date < today:
        coupon.actual_service_date = current_time
        coupon.save()


def get_requested_coupon_status(product, service_type):
    requested_coupon = models.CouponData.objects.filter(product=product,
                                                service_type=service_type) 
    if not requested_coupon:
        status = "not available"
    else:
        status = STATUS_CHOICES[requested_coupon[0].status - 1][1]
    return status


def validate_sa_for_registration( phone_number):
    message = None
    all_sa_dealer_obj = models.ServiceAdvisor.objects.active(phone_number)
    if not len(all_sa_dealer_obj):
        all_sa_dealer_obj = None
#     elif close_action and all_sa_dealer_obj[0].dealer and all_sa_dealer_obj[0].dealer.use_cdms:
#         message = templates.get_template('DEALER_UNAUTHORISED')
#     if message:
#         sa_phone = utils.get_phone_number_format(phone_number)
#         sms_log(settings.BRAND, receiver=sa_phone, action=AUDIT_ACTION, message=message)
#         send_job_to_queue(send_service_detail, {"phone_number":sa_phone, "message": message, "sms_client":settings.SMS_CLIENT})
#         return None
#     service_advisor_obj = all_sa_dealer_obj[0]
#     if service_advisor_obj.dealer:
#         dealer_asc_obj = service_advisor_obj.dealer
#         dealer_asc_obj.last_transaction_date = datetime.now()
#     else:
#         dealer_asc_obj = service_advisor_obj.asc
#         dealer_asc_obj.last_transaction_date = datetime.now()
# 
#     dealer_asc_obj.save(using=settings.BRAND) 

    return all_sa_dealer_obj