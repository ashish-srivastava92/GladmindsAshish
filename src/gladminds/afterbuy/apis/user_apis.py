import json
import logging
import operator

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth import  login
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites.models import RequestSite
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query_utils import Q
from django.db.transaction import atomic
from django.forms.models import model_to_dict
from django.http.response import HttpResponse
from tastypie import fields, http
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpBadRequest
from tastypie.resources import  ALL, ModelResource
from tastypie.utils.urls import trailing_slash

from gladminds.afterbuy import models as afterbuy_model
from gladminds.afterbuy import utils as afterbuy_utils
from gladminds.afterbuy.apis.validations import ConsumerValidation, \
    UserValidation
from gladminds.core.apis.authentication import AccessTokenAuthentication
from gladminds.core.apis.authorization import CustomAuthorization, \
    MultiAuthorization
from gladminds.core.apis.base_apis import CustomBaseModelResource
from gladminds.core.auth import otp_handler
from gladminds.core.auth_helper import GmApps
from gladminds.core.cron_jobs.queue_utils import send_job_to_queue
from gladminds.core.managers.mail import sent_otp_email
from gladminds.core.model_fetcher import get_model
from gladminds.core.model_helpers import format_phone_number

from gladminds.core.utils import check_password, generate_unique_customer_id
from gladminds.core.views.auth_view import create_access_token
from gladminds.sqs_tasks import send_otp

logger = logging.getLogger("gladminds")


class DjangoUserResources(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'users'
        authentication = AccessTokenAuthentication()
        validation = UserValidation()
        authorization = MultiAuthorization(Authorization(), CustomAuthorization())
        allowed_methods = ['get', 'post', 'put']
        excludes = ['password', 'is_superuser']
        always_return_data = True
        
class ConsumerResource(CustomBaseModelResource):

    user = fields.ForeignKey(DjangoUserResources, 'user', null=True, blank=True, full=True)

    class Meta:
        queryset = afterbuy_model.Consumer.objects.all()
        resource_name = "consumers"
        authentication = AccessTokenAuthentication()
        validation = ConsumerValidation()
        authorization = MultiAuthorization(Authorization(), CustomAuthorization())
        authorization = Authorization()
        allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        filtering = {
                     "consumer_id": ALL
                     }

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/registration/phone%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('user_registration_phone'), name="user_registration_phone"),
            url(r"^(?P<resource_name>%s)/registration/email%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('user_registration_email'), name="user_registration_email"),
            url(r"^(?P<resource_name>%s)/activate-email%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('activate_email'), name="activate_email"),
            url(r"^(?P<resource_name>%s)/phone-number/send-otp%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('sent_otp_user_phone_number'), name="sent_otp_user_phone_number"),
            url(r"^(?P<resource_name>%s)/authenticate-email%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('authenticate_user_email_id'), name="authenticate_user_email_id"),
            url(r"^(?P<resource_name>%s)/send-otp/forgot-password%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('authenticate_user_send_otp'), name="authenticate_user_send_otp"),
            url(r"^(?P<resource_name>%s)/forgot-password/(?P<type>[a-zA-Z0-9.-]+)%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('change_user_password'), name="change_user_password"),
            url(r"^(?P<resource_name>%s)/login%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('auth_login'), name="auth_login"),
            url(r"^(?P<resource_name>%s)/validate-otp/phone%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('validate_otp_phone'), name="validate_otp_phone"),
            url(r"^(?P<resource_name>%s)/validate-otp/email%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('validate_otp_email'), name="validate_otp_email"),
            url(r"^(?P<resource_name>%s)/logout%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('logout'), name="logout"),
            url(r"^(?P<resource_name>%s)/product-details%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_product_details'), name="get_product_details")
        ]

    def sent_otp_user_phone_number(self, request, **kwargs):
        '''
        Send OTP to user's phone on successfull registration
        Args : phone number
        Returns : OTP is sent to user's phone number
        '''
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message":"method not allowed"}), content_type="application/json",status=401)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        phone_number = load.get('phone_number')
        if not phone_number:
            return HttpBadRequest("phone_number is required.")
        try:
            otp = otp_handler.get_otp(phone_number=phone_number)
            message = afterbuy_utils.get_template('SEND_OTP').format(otp)
            send_job_to_queue(send_otp, {'phone_number':phone_number, 'message':message, 'sms_client':settings.SMS_CLIENT})
            logger.info('OTP sent to mobile {0}'.format(phone_number))
            data = {'status': 1, 'message': "OTP sent_successfully"}

        except Exception as ex:
            logger.error('Invalid details, mobile {0} and exception {1}'.format(request.POST.get('phone_number', ''),ex))
            data = {'status': 0, 'message': ex}
        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def generate_access_token(self, request, consumer):
        http_host = request.META.get('HTTP_HOST', 'localhost')
        password = consumer.consumer_id+'@123'
        user_auth = authenticate(username=consumer.consumer_id,
                        password=password)
        if user_auth is not None:
            try:
                access_token = create_access_token(user_auth, consumer.user.username,
                                                   password, http_host)
                if user_auth.is_active:
                    login(request, user_auth)
                    data = {'status':1 , 'message':'success', 'access_token': access_token,
                            'consumer_id' : consumer.user.id}
                else:
                    data = {'status': 0, 'message': "failure"}
            except Exception as ex:
                logger.info('Exception while generating access token {0}'.format(ex))
        return data
    
    def create_user(self, is_active, phone_number, email=None):
        consumer_id = generate_unique_customer_id()
        password = consumer_id+settings.PASSWORD_POSTFIX
        user_obj = User.objects.using(settings.BRAND).create(username=consumer_id)
        user_obj.set_password(password)
        user_obj.is_active = is_active
        if email:
            user_obj.email=email
        user_obj.save(using=settings.BRAND)
        consumer_obj = get_model('Consumer', settings.BRAND)(user=user_obj, phone_number=phone_number,
                                                              consumer_id=consumer_id)
        consumer_obj.save(using=settings.BRAND)
        return {'consumer_obj': consumer_obj}
    
    @atomic(using=settings.BRAND)
    def user_registration_phone(self, request, **kwargs):
        '''
        Register user with valid phone number
        Args : phone number
        Returns : OTP is sent to user's phone on successful registration
        
        '''
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message":"method not allowed"}), content_type="application/json",status=401)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        phone_number = load.get('phone_number')
        if not phone_number:
            return HttpBadRequest("Enter phone number")
        try:
            consumer_obj = get_model('Consumer', settings.BRAND).objects.get(phone_number=phone_number,
                                                                             user__is_active=True)
            data = {'status': 1, 'message': 'phone number already registered'}
        except Exception as ObjectDoesNotExist:
            logger.info('Exception while registering user - {0}'.format(ObjectDoesNotExist))
            try:
                user_obj = self.create_user(True, phone_number=phone_number)
                consumer_obj = user_obj['consumer_obj']
                data = {'status':1, 'message': 'Phone number registered successfully'}
            except Exception as ex:
                logger.info("Exception while registering user with phone number - {0}".format(ex))
                return HttpBadRequest("Phone number could not be registered")
        try:
            otp = otp_handler.get_otp(phone_number=phone_number)
            message = afterbuy_utils.get_template('SEND_OTP').format(otp)
            send_job_to_queue(send_otp, {'phone_number': phone_number,
                                             'message': message,'sms_client': settings.SMS_CLIENT})
            consumer_obj.is_phone_verified = False
            consumer_obj.save()
            logger.info('OTP sent to mobile {0}'.format(phone_number))
            return HttpResponse(json.dumps(data), content_type="application/json")
        except Exception as ex:
            logger.info('Exception while generating OTP - {0}'.format(ex))
            return HttpBadRequest("OTP could not be generated")
    
    def update_consumer_email(self, consumer_obj, email, is_email_verified):
        user_obj = consumer_obj.user
        user_obj.email = email
        user_obj.save(using=settings.BRAND)
        consumer_obj.is_email_verified = is_email_verified
        consumer_obj.save(using=settings.BRAND)
    
    def send_otp_to_mail(self, phone_number, email):
        otp = otp_handler.get_otp(phone_number=phone_number, email=email)
        sent_otp_email(data=otp, receiver=email, subject='User registration')
        logger.info('OTP sent to email {0}'.format(email))
        return HttpResponse(json.dumps({'status':1, 'message' : 'OTP sent successfully'}),
                                        content_type='application/json')
#Fixme          
    def user_registration_email(self, request, **kwargs):
        '''
        Register the user with email
        
        Args: phone number , email
        Return : Access token if email id doesnt exist else otp is sent to user's email 
        '''
        if request.method != 'POST':
            return HttpResponse(json.dumps({'message':'Method not allowed'}),
                                content_type='application/json')
        load = json.loads(request.body)
        email = load.get('email', None)
        phone_number = load.get('phone_number', None)
        if not email or not phone_number:
            return HttpBadRequest("Phone number and email is mandatory")
        try:
            consumer = get_model('Consumer', settings.BRAND).objects.get_active_consumers_with_email(email)
            if consumer.phone_number == phone_number:
                access_token = self.generate_access_token(request, consumer)
                return HttpResponse(json.dumps(access_token),
                                    content_type='application/json')
            else:
                consumer_obj = get_model('Consumer', settings.BRAND).objects.\
                get_active_consumers_with_phone(phone_number)
                if not consumer_obj.user.email:
                    self.update_consumer_email(consumer_obj, email, False)
                    self.send_otp_to_mail(phone_number, email)
                    return HttpResponse(json.dumps({'status':1, 'message' : 'OTP sent successfully'}),
                                        content_type='application/json')
                else:
                    self.create_user(False, phone_number, email)
                    self.send_otp_to_mail(phone_number, email)
                    return HttpResponse(json.dumps({'status':1, 'message' : 'OTP sent successfully'}),
                                        content_type='application/json')
                    
        except Exception as ex:
            logger.info("Exception while registering user whose email exists - {0}".format(ex))
            try:
                consumer_obj = get_model('Consumer', settings.BRAND).objects.\
                get_active_consumers_with_phone(phone_number)
                if not consumer_obj.user.email:
                    self.update_consumer_email(consumer_obj, email, True)
                    access_token = self.generate_access_token(request, consumer_obj)
                    return HttpResponse(json.dumps(access_token),
                                        content_type='application/json')
                else:
                    consumer_obj = get_model('Consumer', settings.BRAND).objects.get(Q(phone_number=phone_number) &
                                                                                     ~Q(user__email=email) &
                                                                                     Q(user__is_active=True)    
                                                                                     )
                    user_obj = self.create_user(False, phone_number, email)
                    self.send_otp_to_mail(phone_number, email)
                    return HttpResponse(json.dumps({'status':1, 'message' : 'OTP sent successfully'}),
                                        content_type='application/json')
            except Exception as ex:
                logger.info("Exception while registering user whose email doesnot exist - {0}".format(ex))
                return HttpBadRequest("Could not register the user with this email")
            
    def activate_email(self, request, **kwargs):
        activation_key = request.GET['activation_key']
        activated_user = afterbuy_model.EmailToken.objects.activate_user(activation_key)
        if activated_user:
            data = {'status': 1, 'message': 'email-id validated'}
        else:
            data = {'status': 0, 'message': 'email-id not validated'}
        return HttpResponse(json.dumps(data), content_type="application/json")
        
    def validate_otp_phone(self, request, **kwargs):
        '''
        Validate otp sent to phone
        args : phone number and otp
        return : status 1 on successfull validation
        '''
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message":"method not allowed"}),
                                content_type="application/json",status=401)
        try:       
            load = json.loads(request.body)
            otp_token = load.get('otp_token')
            phone_number = load.get('phone_number')
            if not otp_token or not phone_number:
                return HttpBadRequest("OTP and phone number is mandatory")
            
            try:
                consumer_user = get_model('Consumer', settings.BRAND).objects.get(phone_number=phone_number, 
                                                                         is_email_verified=True)
                otp_handler.validate_otp(otp_token, phone_number=phone_number)
                access_token = self.generate_access_token(request, consumer_user)
                return HttpResponse(json.dumps({'status': 1,'access_token':access_token, 'message':'OTP validated'}),
                                    content_type='application/json')            
        
            except Exception as ex:                
                    user = get_model('Consumer', settings.BRAND).objects.get(phone_number=phone_number, user__is_active=True)
                    otp_handler.validate_otp(otp_token, phone_number=phone_number)
                    user.is_phone_verified = True
                    user.save(using=settings.BRAND)
                    logger.info("Exception checking exisiting user {0}".format(ex))
                    return HttpResponse(json.dumps({'status': 1, 'message':'OTP validated'}),
                                content_type='application/json')
                                     
        except Exception as ex:
                logger.info("Exception while validating OTP {0}".format(ex))
                return HttpBadRequest("OTP couldnot be validated")


    @atomic(using=settings.BRAND)
    def validate_otp_email(self, request, **kwargs):
        '''
        Validate the otp sent to email and map user products
        Args : email , phone number , otp
        Returns : map the products and returns access token 
        '''
        if request.method != 'POST':
            return HttpResponse(json.dumps({'message':"Method not allowed"}),
                                content_type='application/json')
        try:
            load = json.loads(request.body)
            phone_number = load.get('phone_number')
            otp_token = load.get('otp_token')
            email = load.get('email')
            if not otp_token or not phone_number or not email:
                return HttpBadRequest("OTP , phone number , email is mandatory")
            otp_handler.validate_otp(otp_token, email=email)
            
            consumer = get_model('Consumer', settings.BRAND).objects.select_related('user').get(user__email=email,
                                                                         phone_number=phone_number)
            user = consumer.user
            user.is_active = True
            user.save(using=settings.BRAND)
            consumer.is_email_verified = True
            consumer.save(using=settings.BRAND)
            
            user_products = get_model('UserProduct', settings.BRAND).objects.\
                    select_related('consumer').filter(~Q(consumer__phone_number=phone_number) &
                                                      Q(consumer__user__email=email) &
                                                      Q(consumer__user__is_active=True))
            if len(user_products) >0:   
                for product in user_products:
                    user = product.consumer.user
                    user.is_active =  False
                    user.save(using=settings.BRAND)
                    product.save(using=settings.BRAND)
                
                products = []
                for product in user_products:
                    products.append(get_model('UserProduct', settings.BRAND)(consumer=consumer,
                                                                             nick_name=product.nick_name,
                                                                             product_type=product.product_type,
                                                                             purchase_date=product.purchase_date,
                                                                             brand_product_id=product.brand_product_id,
                                                                             image_url=product.image_url,
                                                                             color=product.color,
                                                                             is_deleted=product.is_deleted,
                                                                             description=product.description,
                                                                             is_accepted=product.is_accepted,
                                                                             service_reminder=product.service_reminder,
                                                                             details_completed=product.details_completed,
                                                                             manual_link=product.manual_link,
                                                                             warranty_year=product.warranty_year,
                                                                             insurance_year=product.insurance_year))
                new_products = get_model('UserProduct', settings.BRAND).objects.bulk_create(products)
                new_products = get_model('UserProduct', settings.BRAND).objects.\
                        select_related('consumer').filter(Q(consumer__phone_number=phone_number) &
                                                          Q(consumer__user__email=email))
    
                
                product_dict = {}
                for user_product in user_products:
                    product_mapping = filter(lambda product : product.brand_product_id == user_product.brand_product_id,
                                             new_products)
                    product_dict[user_product.brand_product_id] = product_mapping[0]
                
                insurance_details = get_model('ProductInsuranceInfo', settings.BRAND).objects.filter(product__in=user_products)
                self.update_product_insurance_warranty(product_dict, insurance_details)
                
                warranty_details = get_model('ProductWarrantyInfo', settings.BRAND).objects.filter(product__in=user_products)
                self.update_product_insurance_warranty(product_dict, warranty_details)
            else:
                consumers = get_model('Consumer', settings.BRAND).objects.select_related('user').filter(Q(user__email=email)&
                                                                                 ~Q(phone_number=phone_number),
                                                                                 Q(user__is_active=True))
                for consumer_obj in consumers:
                    user = consumer_obj.user
                    user.is_active = False
                    user.save(using=settings.BRAND)
                    consumer_obj.save(using=settings.BRAND)
            
            
            all_consumers = get_model('Consumer', settings.BRAND).objects.select_related('user')\
                                                                            .filter(Q(phone_number=phone_number) &
                                                                            ~Q(user__email=email) &
                                                                            Q(user__is_active=True))
            if len(all_consumers) >0:
                all_consumers[0].has_discrepancy = True
                user_obj = all_consumers[0].user
                user_obj.is_active = False
                user_obj.save(using=settings.BRAND)
                all_consumers[0].save(using=settings.BRAND)

            access_token = self.generate_access_token(request, consumer)
            return HttpResponse(json.dumps(access_token),
                                    content_type='application/json')

        except Exception as ex:
            logger.info("Exception while validating email otp - {0}".format(ex))
            return HttpBadRequest("OTP could not be validated")
    
    
    def update_product_insurance_warranty(self, product_dict, details):
        for data in details:
            if product_dict.has_key(data.product.brand_product_id):
                product = product_dict[data.product.brand_product_id]
                data.product = product
                data.save(using=settings.BRAND)
          
          
    def validate_user_phone_number(self,phone_number, otp):
        if not otp and not phone_number :
            return HttpBadRequest("otp and phone_number required")
        try:
            otp_handler.validate_otp(otp, phone_number=phone_number)

        except Exception as ex:
                data = {'status': 0, 'message': "invalid OTP"}
                logger.info("[Exception OTP]:{0}".
                            format(ex))
        return HttpResponse(json.dumps(data), content_type="application/json")

    def authenticate_user_email_id(self, request, **kwargs):
        email_id = request.POST.get('email_id')
        if not email_id:
            return HttpBadRequest("email id is required")
        try:
            afterbuy_model.Consumer.objects.get(user__email=email_id, is_email_verified=True)
            data = {'status': 1, 'message': "emailid verified"}
            return HttpResponse(json.dumps(data), content_type="application/json")
        except Exception as ex:
                log_message = "new user :{0}".format(ex)
                logger.info(log_message)
                data = {'status': 0, 'message': "Either your email is not verified"}
        return HttpResponse(json.dumps(data), content_type="application/json")

    def authenticate_user_send_otp(self, request, **kwargs):
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message":"method not allowed"}), content_type="application/json",status=401)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        email = load.get('email_id')
        phone_number = load.get('phone_number')
        if not phone_number and not email:
            return HttpBadRequest("phone_number or email is required")
        try:
            if phone_number:
                phone_number = format_phone_number(phone_number)
                logger.info('OTP request received. Mobile: {0}'.format(phone_number))
                user_obj = afterbuy_model.Consumer.objects.get(phone_number=phone_number).user
                otp = otp_handler.get_otp(user=user_obj)
                message = afterbuy_utils.get_template('SEND_OTP').format(otp)
                send_job_to_queue('send_otp', {'phone_number': phone_number,
                                               'message': message, "sms_client": settings.SMS_CLIENT})
                logger.info('OTP sent to mobile {0}'.format(phone_number))
                data = {'status': 1, 'message': "OTP sent_successfully"}
                #Send email if email address exist
            if email:
                try:
                    consumer_obj = afterbuy_model.Consumer.objects.get(user__email=email, is_email_verified=True)
                    site = RequestSite(request)
                    afterbuy_model.EmailToken.objects.create_email_token(consumer_obj, email, site, trigger_mail='forgot-password')
                    data = {'status': 1, 'message': "Password reset link sent successfully"}
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as ex:
                        log_message = "new user :{0}".format(ex)
                        logger.info(log_message)
                        data = {'status': 0, 'message': "Either your email is not verified or its not exist"}
        except Exception as ex:
            logger.error('Invalid details, mobile {0} and exception {1}'.format(request.POST.get('phone_number', ''),ex))
            data = {'status': 0, 'message': "inavlid phone_number/email_id"}
        return HttpResponse(json.dumps(data), content_type="application/json")

    def change_user_password(self, request, **kwargs):
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message":"method not allowed"}), content_type="application/json",status=401)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        type = kwargs['type']
        otp_token = load.get('otp_token')
        password = load.get('password1')
        repassword = load.get('password2')
        invalid_password = check_password(repassword)
        if (invalid_password):
            return HttpBadRequest("password is not meant according to the rules")
        auth_key = load.get('auth_key')
        user_details = {}
        if not type:
            return HttpBadRequest("type not defined use email/phone")
        if password != repassword:
            return HttpBadRequest("password1 and password2 not matched")
        try:
            if type=='phone':
                try:
                    if not (settings.ENV in settings.IGNORE_ENV and otp_token in settings.HARCODED_OTPS):
                        consumer = afterbuy_model.OTPToken.objects.get(token=otp_token).user
                        otp_handler.validate_otp(otp_token, user=consumer)
                except Exception:
                    raise ImmediateHttpResponse(
                        response=http.HttpBadRequest('Wrong OTP!'))
                user_details['id'] = consumer.user.id
            elif type=='email':
                try:
                    user_obj = afterbuy_model.EmailToken.objects.get(activation_key=auth_key).user
                except Exception:
                    
                    raise ImmediateHttpResponse(
                        response=http.HttpBadRequest('invalid authentication key!'))
                user_details['email'] = user_obj.user.email
            user = User.objects.filter(**user_details)[0]
            user.set_password(password)
            user.save()
            data = {'status': 1, 'message': "password updated successfully"}
        except Exception as ex:
            logger.error('Invalid details, mobile {0} and exception {1}'.format(request.POST.get('phone_number', ''),ex))
            data = {'status': 0, 'message': "password not updated"}
        return HttpResponse(json.dumps(data), content_type="application/json")

    def auth_login(self, request, **kwargs):
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message":"method not allowed"}), content_type="application/json",status=401)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        phone_number = load.get('phone_number')
        email_id = load.get('email_id')
        password = load.get('password')
        if not phone_number and not email_id and password:
            return HttpBadRequest("Phone Number/email_id and password  required.")
        try:
            if phone_number:
                user_obj = afterbuy_model.Consumer.objects.get(phone_number
                                                 =phone_number).user
            elif email_id:
                    user_obj = afterbuy_model.Consumer.objects.get(user__email=email_id, is_email_verified=True).user
            http_host = request.META.get('HTTP_HOST', 'localhost')
            user_auth = authenticate(username=str(user_obj.username),
                                password=password)
            if user_auth is not None:
                access_token = create_access_token(user_auth, user_obj.username, password, http_host)
                if user_auth.is_active:
                    login(request, user_auth)
                    data = {'status': 1, 'message': "login successfully", 'access_token': access_token, "user_id": user_auth.id}
            else:
                data = {'status': 0, 'message': "login unsuccessfull"}
        except Exception as ex:
                data = {'status': 0, 'message': "login unsuccessfull"}
                logger.info("[Exception get_user_login_information]:{0}".
                            format(ex))
        return HttpResponse(json.dumps(data), content_type="application/json")

    def logout(self, request, **kwargs):
        from provider.oauth2.models import AccessToken
        access_token = request.GET.get('access_token')
        if access_token:
            try:
                at_obj = AccessToken.objects.using(settings.BRAND).get(token=access_token)
                if settings.OAUTH_DELETE_EXPIRED:
                    at_obj.delete()
                data = {'status': 0, 'message': "logout successfully"}
            except Exception as ex:
                data = {'status': 0, 'message': "access_token_not_valid"}
                logger.info("[Exception get_user_login_information]:{0}".
                            format(ex))
        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def get_product_details(self, request, **kwargs):
        self.is_authenticated(request)
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message":"method not allowed"}), content_type="application/json",status=401)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)

        phone_number = load.get('phone_number', None)
        product_id = load.get('product_id', None)
        query_args1 = []
        query_args2 = []
        if product_id:
            query_args1.append(Q(product__product_id=product_id))
            query_args2.append(Q(product_id=product_id))
        
        if phone_number:
            query_args1.append(Q(product__customer_phone_number__contains=phone_number))
            query_args2.append(Q(customer_phone_number__contains=phone_number))
        
        coupons = get_model('CouponData', GmApps.BAJAJ).objects.filter(reduce(operator.and_, query_args1))
        products = get_model('ProductData', GmApps.BAJAJ).objects.filter(reduce(operator.and_, query_args2))
        if not products:
            return HttpResponse(json.dumps({'message': 'No products associated with the data'}),
                                content_type='application/json')
        try:
            result = []
            for coupon in coupons:
                data = {}
                data['coupons'] = model_to_dict(coupon)
                user_product = filter(lambda product : product.id==coupon.product_id, products)
                if user_product:
                    data['sku_code'] = user_product[0].sku_code
                    data['product_id'] = user_product[0].product_id
                    data['customer_phone_number'] = user_product[0].customer_phone_number
                    data['customer_name'] = user_product[0].customer_name
                result.append(data)
            return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), content_type='application/json')
        except Exception as ex :
            logger.info("[Exception while fetching product details]:{0}".format(ex))
            return HttpResponse(json.dumps({'message': 'Error while fetching data'}),
                                content_type='application/json')

class UserNotificationResource(CustomBaseModelResource):
    consumer = fields.ForeignKey(ConsumerResource, 'consumer', null=True, blank=True, full=True)

    class Meta:
        queryset = afterbuy_model.UserNotification.objects.all()
        resource_name = "notifications"
        authentication = AccessTokenAuthentication()
        authorization = CustomAuthorization()
        detail_allowed_methods = ['get', 'post', 'put']
        allowed_update_fields = ['notification_read']
        always_return_data = True
        filtering = {
                     "consumer": ALL,
                     "id": ALL,
                     "notification_read": ALL
                     }


class ServiceTypeResource(CustomBaseModelResource):

    class Meta:
        queryset = afterbuy_model.ServiceType.objects.all()
        resource_name = "service-types"
        authentication = AccessTokenAuthentication()
        authorization = DjangoAuthorization()
        always_return_data = True


class ServiceResource(CustomBaseModelResource):
    consumer = fields.ForeignKey(ConsumerResource, 'consumer')
    service_type = fields.ForeignKey(ServiceTypeResource, 'service_type', full=True)

    class Meta:
        queryset = afterbuy_model.Service.objects.all()
        resource_name = "services"
        authentication = AccessTokenAuthentication()
        authorization = MultiAuthorization(DjangoAuthorization(), CustomAuthorization())
        always_return_data = True
        filtering = {
                     "consumer": ALL,
                     "service_type": ALL,
                     "is_active": ALL
                     }

class UserMobileInfoResource(CustomBaseModelResource):
    consumer = fields.ForeignKey(ConsumerResource, 'consumer')
    
    class Meta:
        queryset = get_model('UserMobileInfo', settings.BRAND).objects.all()
        resource_name = 'user-mobile-info'
        authentication = AccessTokenAuthentication()
        authorization = Authorization()
        always_return_data = True
        
