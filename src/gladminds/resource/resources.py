from datetime import datetime
from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.forms.models import model_to_dict
from gladminds import smsparser, utils, audit, message_template as templates
from gladminds.models import common
from gladminds.tasks import send_registration_detail, send_service_detail, \
    send_coupon_detail_customer, send_coupon, \
    send_brand_sms_customer, send_close_sms_customer, send_invalid_keyword_message
from gladminds.resource.valid import AfterBuyAuthentication
from tastypie import fields
from tastypie.http import HttpBadRequest, HttpUnauthorized
from tastypie.resources import Resource, ModelResource
from tastypie.utils.urls import trailing_slash
from tastypie import http
from tastypie.exceptions import ImmediateHttpResponse
from django.db.models import Q
import logging
from gladminds.utils import mobile_format, format_message
logger = logging.getLogger('gladminds')
json = utils.import_json()


__all__ = ['GladmindsTaskManager']
AUDIT_ACTION = 'SEND TO QUEUE'
angular_format = lambda x: x.replace('{', '<').replace('}', '>')


class GladmindsResources(Resource):

    class Meta:
        resource_name = 'messages'

    def base_urls(self):
        return [
            url(r"^messages", self.wrap_view('dispatch_gladminds'))
        ]

    def dispatch_gladminds(self, request, **kwargs):
        sms_dict = {}
        if request.POST.get('text'):
            message = request.POST.get('text')
            phone_number = request.POST.get('phoneNumber')
        elif request.GET.get('cli'):
            message = request.GET.get('msg')
            phone_number = request.GET.get('cli')
        elif request.POST.get("advisorMobile"):
            phone_number = request.POST.get('advisorMobile')
            customer_id = request.POST.get('customerId')
            if request.POST.get('action') == 'validate':
                logger.info('Validating the service coupon for customer {0}'.format(customer_id))
                odo_read = request.POST.get('odoRead')
                service_type = request.POST.get('serviceType')
                message = 'A {0} {1} {2}'.format(customer_id, odo_read, service_type)
                logger.info('Message to send: ' + message)
            else:
                ucn = request.POST.get('ucn')
                logger.info('Terminating the service coupon {0}'.format(ucn))
                message = 'C {0} {1}'.format(customer_id, ucn)
                logger.info('Message to send: ' + message)
        phone_number = mobile_format(phone_number)
        message = format_message(message)
        audit.audit_log(action='RECIEVED', sender=phone_number, reciever='+1 469-513-9856', message=message, status='success')
        logger.info('Recieved Message from phone number: {0} and message: {1}'.format(phone_number, message))
        try:
            sms_dict = smsparser.sms_parser(message=message)
        except smsparser.InvalidKeyWord as ink:
            message = ink.template
            send_invalid_keyword_message.delay(phone_number=phone_number, message=message)
            audit.audit_log(reciever=phone_number, action=AUDIT_ACTION, message=message)
            raise ImmediateHttpResponse(HttpBadRequest(ink.message))
        except smsparser.InvalidMessage as inm:
            message = inm.template
            send_invalid_keyword_message.delay(phone_number=phone_number, message=message)
            audit.audit_log(reciever=phone_number, action=AUDIT_ACTION, message=message)
            raise ImmediateHttpResponse(HttpBadRequest(inm.message))
        except smsparser.InvalidFormat as inf:
            message = angular_format('CORRECT FORMAT: ' + inf.template)
            send_invalid_keyword_message.delay(phone_number=phone_number, message=message)
            audit.audit_log(reciever=phone_number, action=AUDIT_ACTION, message=message)
            raise ImmediateHttpResponse(HttpBadRequest(inf.message))
        handler = getattr(self, sms_dict['handler'], None)
        to_be_serialized = handler(sms_dict, phone_number)
        to_be_serialized = {"status": to_be_serialized}
        return self.create_response(request, data=to_be_serialized)

    def register_customer(self, sms_dict, phone_number):
        customer_name = sms_dict['name']
        email_id = sms_dict['email_id']
        try:
            object = common.GladMindUsers.objects.get(phone_number=phone_number)
            gladmind_customer_id = object.gladmind_customer_id
            customer_name = object.customer_name
        except ObjectDoesNotExist as odne:
            gladmind_customer_id = utils.generate_unique_customer_id()
            registration_date = datetime.now()
            customer = common.GladMindUsers(
                gladmind_customer_id=gladmind_customer_id, phone_number=phone_number,
                customer_name=customer_name, email_id=email_id,
                registration_date=registration_date)
            customer.save()
        # Please update the template variable before updating the keyword-argument
        message = smsparser.render_sms_template(status='send', keyword=sms_dict['keyword'], customer_id=gladmind_customer_id)
        phone_number = utils.get_phone_number_format(phone_number)
        logging.info("customer is registered with message %s" % message)
        send_registration_detail.delay(phone_number=phone_number, message=message)
        audit.audit_log(reciever=phone_number, action=AUDIT_ACTION, message=message)
        return True

    def customer_service_detail(self, sms_dict, phone_number):
        sap_customer_id = sms_dict.get('sap_customer_id', None)
        message = None
        try:
            customer_product_data = common.CouponData.objects.select_related \
                                        ('vin', 'customer_phone_number__phone_number').\
                                        filter(vin__customer_phone_number__phone_number=phone_number, \
                                        vin__sap_customer_id=sap_customer_id).\
                                        order_by('vin', 'valid_days') if sap_customer_id else \
                                        common.CouponData.objects.select_related('vin', 'customer_phone_number__phone_number').\
                                        filter(vin__customer_phone_number__phone_number=phone_number).\
                                        order_by('vin', 'valid_days')
            logger.info(customer_product_data)
            valid_product_data = []
            for data in customer_product_data:
                if data.status == 1 or data.status == 4:
                    valid_product_data.append(data)
            valdata = [valid_product_data[0]]
            service_list = map(lambda object: {'vin': object.vin.vin, 'usc': object.unique_service_coupon, 'valid_days': object.valid_days, 'valid_kms':object.valid_kms}, valdata)
            template = templates.get_template('SEND_CUSTOMER_SERVICE_DETAIL')
            msg_list = [template.format(**key_args) for key_args in service_list]
            if not msg_list:
                raise Exception()
            message = ', '.join(msg_list)
        except Exception as ex:
            message = smsparser.render_sms_template(status='invalid', keyword=sms_dict['keyword'], sap_customer_id=sap_customer_id)
        logging.info("Send Service detail %s" % message)
        phone_number = utils.get_phone_number_format(phone_number)
        send_service_detail.delay(phone_number=phone_number, message=message)
        audit.audit_log(reciever=phone_number, action=AUDIT_ACTION, message=message)
        return True

    def get_customer_phone_number_from_vin(self, vin):
        product_obj = common.ProductData.objects.filter(vin=vin).select_related('customer_phone_number__phone_number')
        return product_obj[0].customer_phone_number.phone_number

    def expire_less_kms_coupon(self, actual_kms, vin):
        '''
            Expire those coupon whose kms limit is small then actual kms limit
        '''
        expire_coupon = common.CouponData.objects.filter(status=1, vin__vin=vin, valid_kms__lt=actual_kms).update(status=3)
        logger.info("%s are expired" % expire_coupon)

    def get_vin(self, sap_customer_id):
        try:
            customer_product_data = common.CouponData.objects.select_related \
                                            ('vin').filter(vin__sap_customer_id=sap_customer_id).order_by('vin', 'valid_days')
            return customer_product_data[0].vin.vin
        except Exception as ax:
            logger.error("Vin is not in customer_product_data Error %s " % ax)

    def update_coupon(self, valid_coupon, actual_kms, dealer_data, status, update_time=datetime.now()):
        valid_coupon.actual_kms = actual_kms
        valid_coupon.actual_service_date = update_time
        valid_coupon.status = status
        valid_coupon.sa_phone_number = dealer_data
        valid_coupon.save()

    @transaction.commit_manually()
    def validate_coupon(self, sms_dict, phone_number):
        actual_kms = int(sms_dict['kms'])
        service_type = sms_dict['service_type']
        dealer_message = None
        customer_phone_number = None
        customer_message = None
        customer_message_countdown = 1800
        sap_customer_id = sms_dict.get('sap_customer_id', None)
        dealer_data = self.validate_dealer(phone_number)
        if not self.is_valid_data(customer_id=sap_customer_id, sa_phone=phone_number):
            return False
        try:
            vin = self.get_vin(sap_customer_id)
            valid_coupon = common.CouponData.objects.select_for_update().filter(Q(status=1) |  Q(status=4), vin__vin=vin, valid_kms__gte=actual_kms).select_related ('vin', 'customer_phone_number__phone_number').order_by('service_type')
            if len(valid_coupon):
                valid_coupon = valid_coupon[0]

            in_progress_coupon = common.CouponData.objects.select_for_update().filter(vin__vin=vin, valid_kms__gte=actual_kms, status=4).select_related ('vin', 'customer_phone_number__phone_number').order_by('service_type')
            self.expire_less_kms_coupon(actual_kms, vin)
            try:
                customer_phone_number = self.get_customer_phone_number_from_vin(vin) 
            except Exception as ax:
                logger.error('Customer Phone Number is not stored in DB %s' % ax)
            logger.info(valid_coupon.service_type)
            if len(in_progress_coupon) > 0:
                logger.info("Validate_coupon: in_progress_coupon")
                dealer_message = templates.get_template('SEND_SA_VALID_COUPON').format(service_type=in_progress_coupon[0].service_type, customer_id=sap_customer_id)
                customer_message = templates.get_template('SEND_CUSTOMER_VALID_COUPON').format(coupon=in_progress_coupon[0].unique_service_coupon, service_type=in_progress_coupon[0].service_type)
            elif valid_coupon:
                logger.info("Validate_coupon: valid_coupon.service_type")
                self.update_coupon(valid_coupon, actual_kms, dealer_data, 4)
                dealer_message = templates.get_template('SEND_SA_VALID_COUPON').format(service_type=valid_coupon.service_type, customer_id=sap_customer_id)
                customer_message = templates.get_template('SEND_CUSTOMER_VALID_COUPON').format(coupon=valid_coupon.unique_service_coupon, service_type=valid_coupon.service_type)
            else:
                logger.info("Validate_coupon: ELSE PART")
                customer_message_countdown = 10
                requested_coupon = common.CouponData.objects.get(vin__vin=vin, service_type=service_type)
                dealer_message = templates.get_template('SEND_SA_EXPIRED_COUPON').format(service_type=requested_coupon.service_type, customer_id=sap_customer_id)
                customer_message = templates.get_template('SEND_CUSTOMER_EXPIRED_COUPON').format(service_type=requested_coupon.service_type)
            send_coupon_detail_customer.apply_async( kwargs={ 'phone_number': utils.get_phone_number_format(customer_phone_number), 'message':customer_message}, countdown=customer_message_countdown)
            audit.audit_log(reciever=customer_phone_number, action=AUDIT_ACTION, message=customer_message)
        except IndexError as ie:
            dealer_message = templates.get_template('SEND_INVALID_VIN_OR_FSC')
        except ObjectDoesNotExist as odne:
            dealer_message = templates.get_template('SEND_INVALID_SERVICE_TYPE').format(service_type=service_type)
        except Exception as ex:
            dealer_message = templates.get_template('SEND_INVALID_MESSAGE')
        finally:
            logging.info("validate message send to SA %s" % dealer_message)
            phone_number = utils.get_phone_number_format(phone_number)
            send_service_detail.delay(phone_number=phone_number, message=dealer_message)
            audit.audit_log(reciever=phone_number, action=AUDIT_ACTION, message=dealer_message)
            transaction.commit()
        return True

    def get_phone_number_format(self, phone_number):
        return phone_number[-10:]

    @transaction.commit_manually()
    def close_coupon(self, sms_dict, phone_number):
        sa_object = self.validate_dealer(phone_number)
        unique_service_coupon = sms_dict['usc']
        sap_customer_id = sms_dict.get('sap_customer_id', None)
        message = None
        if not self.is_valid_data(customer_id=sap_customer_id, coupon=unique_service_coupon, sa_phone=phone_number):
            return False
        if not self.is_sa_initiator(unique_service_coupon, phone_number):
            logger.info("SA is not the coupon initiator.")
            transaction.commit()
            return False
        try:
            vin = self.get_vin(sap_customer_id)
            coupon_object = common.CouponData.objects.select_for_update().filter(vin__vin=vin, unique_service_coupon=unique_service_coupon).select_related ('vin', 'customer_phone_number__phone_number')[0]
            customer_phone_number = coupon_object.vin.customer_phone_number.phone_number
            coupon_object.status = 2
            coupon_object.closed_date = datetime.now()
            coupon_object.save()
            common.CouponData.objects.filter(Q(status=1) | Q(status=4), vin__vin=vin, service_type__lt=coupon_object.service_type).update(status=3)
            message = templates.get_template('SEND_SA_CLOSE_COUPON').format(customer_id=sap_customer_id, usc=unique_service_coupon)
        except Exception as ex:
            message = templates.get_template('SEND_INVALID_MESSAGE')
        finally:
            logging.info("Close coupon with message %s" % message)
            phone_number = utils.get_phone_number_format(phone_number)
            send_coupon.delay(phone_number=phone_number, message=message)
            audit.audit_log(reciever=phone_number, action=AUDIT_ACTION, message=message)
            transaction.commit()
        return True

    def validate_dealer(self, phone_number):
        try:
            service_advisor_obj = common.ServiceAdvisor.objects.get(phone_number=phone_number)
            all_sa_dealer_obj = common.ServiceAdvisorDealerRelationship.objects.filter(service_advisor_id = service_advisor_obj, status = u'Y')
            if len(all_sa_dealer_obj) == 0:
                raise
        except:
            message = 'You are not an authorised user to avail this service'
            audit.audit_log(reciever=phone_number, action=AUDIT_ACTION, message=message)
            raise ImmediateHttpResponse(HttpUnauthorized("Not an authorised user"))
        return service_advisor_obj

    def is_sa_initiator(self, coupon_id, phone_sa):
        coupon_data = common.CouponData.objects.filter(unique_service_coupon = coupon_id)
        if coupon_data:
            coupon_initiator = common.ServiceAdvisor.objects.filter(phone_number = coupon_data[0].sa_phone_number)
            return phone_sa == coupon_initiator[0].phone_number
        return False
    
    def is_valid_data(self, customer_id=None, coupon=None, sa_phone=None):
        '''
            Error During wrong entry of Customer ID or UCN (message to the service advisor)
            -    "Wrong Customer ID; please check"
            -    "Wrong UCN; please check"
            -    "Wrong Customer ID and wrong UCN; please check"
        '''
        coupon_obj = customer_obj = message = None
        if coupon: coupon_obj = common.CouponData.objects.filter(unique_service_coupon=coupon)
        if customer_id: customer_obj = common.ProductData.objects.filter(sap_customer_id=customer_id)
        
        if ((customer_id and customer_obj) and (coupon and coupon_obj) and coupon_obj[0].vin.vin != customer_obj[0].vin) or\
            ((customer_id and not customer_obj) and (coupon and not coupon_obj)):
            message=templates.get_template('SEND_SA_WRONG_CUSTOMER_UCN')
        elif customer_id and not customer_obj:
            message=templates.get_template('SEND_SA_WRONG_CUSTOMER')
        elif coupon and not coupon_obj:
            message=templates.get_template('SEND_SA_WRONG_UCN')

        if message:
            send_invalid_keyword_message.delay(phone_number=sa_phone, message=message)
            audit.audit_log(reciever=sa_phone, action=AUDIT_ACTION, message=message)
            logger.info("Message sent to SA : " + message)
            return False
        return True


    def get_brand_data(self, sms_dict, phone_number):
        brand_id = sms_dict['brand_id']
        try:
            product_data = common.ProductData.objects.select_related('product_type__brand_id').filter(customer_phone_number__phone_number=phone_number, product_type__brand_id__brand_id=brand_id)
            if product_data:
                product_list = map(lambda object: {'sap_customer_id':object.sap_customer_id, 'vin': object.vin}, product_data)
                template = templates.get_template('SEND_BRAND_DATA')
                msg_list = [template.format(**key_args) for key_args in product_list]
                message = ', '.join(msg_list)
            else: 
                raise Exception
        except Exception as ex:
            message = templates.get_template('SEND_INVALID_MESSAGE')
        send_brand_sms_customer.delay(phone_number=phone_number, message=message)
        audit.audit_log(reciever=phone_number, action=AUDIT_ACTION, message=message)
        return True

    def determine_format(self, request):
        return 'application/json'
    
    
#########################AfterBuy Resources############################################
class GladmindsBaseResource(ModelResource):
    def determine_format(self, request):
        return 'application/json'
    
class BrandResources(GladmindsBaseResource):
    class Meta:
        queryset = common.BrandData.objects.all()
        resource_name = 'brands'

class ProductTypeResources(GladmindsBaseResource):
    class Meta:
        queryset = common.ProductTypeData.objects.all()
        resource_name = 'product-type'
        
class ProductResources(GladmindsBaseResource):
    class Meta:
        queryset = common.ProductData.objects.all()
        resource_name = 'products'

class UserResources(GladmindsBaseResource):
    products = fields.ListField()
    class Meta:
        queryset = common.GladMindUsers.objects.all()
        resource_name = 'users'
#        authentication = AfterBuyAuthentication()
    
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/products%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_products'), name="api_get_products"),
        ]    
        
    def obj_get(self, bundle, **kwargs):
        request = bundle.request
        customer_id = kwargs['pk']
        try:
            customer_detail = common.GladMindUsers.objects.get(gladmind_customer_id=customer_id)
            return customer_detail
        except:
            raise ImmediateHttpResponse(response=http.HttpBadRequest())
    
    
    
    def get_products(self, request, **kwargs):
        user_id = kwargs['pk']
        products = common.ProductData.objects.filter(customer_phone_number__gladmind_customer_id=user_id).select_related('customer_phone_number')
        products = [model_to_dict(product) for product in products]
        to_be_serialized = {"products": products}
        return self.create_response(request, data=to_be_serialized)
    
    def dehydrate(self, bundle):
        products = common.ProductData.objects.filter(customer_phone_number__id=bundle.data['id']).select_related('customer_phone_number')
        bundle.data['products'] = [model_to_dict(product) for product in products]
        return bundle
        
