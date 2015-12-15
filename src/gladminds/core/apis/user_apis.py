import json
import logging
from datetime import datetime, timedelta, date

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models.aggregates import Count, Sum
from django.http.response import HttpResponse
from django.db.models.query_utils import Q
from django.contrib.sites.models import RequestSite

from tastypie.utils.urls import trailing_slash
from tastypie import fields,http, bundle
from tastypie.http import HttpBadRequest
from tastypie.authorization import Authorization
from tastypie.authorization import DjangoAuthorization
from tastypie.constants import ALL_WITH_RELATIONS, ALL
from tastypie.exceptions import ImmediateHttpResponse
from gladminds.core import constants
from gladminds.core.apis.authentication import AccessTokenAuthentication
from gladminds.core.apis.authorization import MultiAuthorization,\
    LoyaltyCustomAuthorization,\
     ZSMCustomAuthorization, DealerCustomAuthorization,\
     RMCustomAuthorization,CHCustomAuthorization,DistributorCustomAuthorization
from gladminds.core.apis.base_apis import CustomBaseModelResource
from gladminds.core.auth.access_token_handler import create_access_token, \
    delete_access_token
from gladminds.core.auth_helper import Roles
from gladminds.core.managers.user_manager import RegisterUser
from gladminds.core.model_fetcher import models
from gladminds.sqs_tasks import send_otp
from gladminds.core.cron_jobs.queue_utils import send_job_to_queue
from gladminds.core.auth import otp_handler
from gladminds.core.model_helpers import format_phone_number
from gladminds.core.utils import check_password
from gladminds.afterbuy import utils as core_utils
from gladminds.core.model_fetcher import get_model
import csv
import StringIO
from gladminds.core.core_utils.utils import dictfetchall

from django.db import connections

LOG = logging.getLogger('gladminds')

from celery.worker.consumer import Heart
from boto.gs.cors import HEADERS

logger = logging.getLogger('gladminds')

register_user = RegisterUser()

class UserResource(CustomBaseModelResource):
    '''
    Auth user resource
    '''
    class Meta:
        queryset = User.objects.all()
        resource_name = 'users'
        excludes = ['password', 'is_superuser']
        authorization = Authorization()
#         authentication = AccessTokenAuthentication()
#         authorization = MultiAuthorization(DjangoAuthorization())
        allowed_methods = ['get', 'post', 'put']
        filtering = {
                     "is_active": ALL,
                     "username" : ALL,
                     "id" : ALL,
                     "email" : ALL
                     }
        always_return_data = True
        ordering = ['username', 'email']

class UserProfileResource(CustomBaseModelResource):
    '''
    Extended user profile resource
    '''
    user = fields.ForeignKey(UserResource, 'user', null=True, blank=True, full=True)

    class Meta:
        queryset = models.UserProfile.objects.all()
        resource_name = 'gm-users'
        authorization = Authorization()
#         authorization = MultiAuthorization(DjangoAuthorization())
#         authentication = AccessTokenAuthentication()
        allowed_methods = ['get', 'post', 'put']
        filtering = {
                     "user":  ALL_WITH_RELATIONS,
                     "phone_number": ALL,
                     "state": ALL,
                     "country": ALL,
                     "pincode": ALL
                     }
        always_return_data = True 
        ordering = ['user', 'phone_number']
        
        
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login%s" % (self._meta.resource_name,
                                                     trailing_slash()),
                self.wrap_view('login'), name="login"),
            url(r"^(?P<resource_name>%s)/activate-email%s" % 
                (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('activate_email'), name="activate_email"),
            url(r"^(?P<resource_name>%s)/authenticate-email%s" % 
                (self._meta.resource_name, trailing_slash()), self.wrap_view
                ('authenticate_user_email_id'),
                 name="authenticate_user_email_id"),
            url(r"^(?P<resource_name>%s)/forgot-password/generate-link%s" % 
                (self._meta.resource_name, trailing_slash()), self.wrap_view
                ('generate_reset_link'), name="generate_reset_link"),
            url(r"^(?P<resource_name>%s)/forgot-password/email%s" % 
                (self._meta.resource_name, trailing_slash()), self.wrap_view
                ('change_user_password'), name="change_user_password"),
            url(r"^(?P<resource_name>%s)/phone-number/send-otp%s" % 
                (self._meta.resource_name, trailing_slash()), self.wrap_view
                ('sent_otp_user_phone_number'),
                 name="sent_otp_user_phone_number"),
            url(r"^(?P<resource_name>%s)/send-otp/forgot-password%s" % 
                (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('authenticate_user_send_otp'), 
                name="authenticate_user_send_otp"),
            url(r"^(?P<resource_name>%s)/validate-otp%s" % 
                (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('validate_otp'), name="validate_otp"),
            url(r"^(?P<resource_name>%s)/logout%s" % (self._meta.resource_name,
                                                      trailing_slash()),
                self.wrap_view('logout'), name="logout"),
            url(r"^(?P<resource_name>%s)/change-password%s" % 
                (self._meta.resource_name, trailing_slash()), self.wrap_view
                ('change_password'), name="change_password"),
            url(r"^(?P<resource_name>%s)/reset-password%s" % 
                (self._meta.resource_name, trailing_slash()), self.wrap_view
                ('reset_password'), name="reset_password"),

        ]
    
    def reset_password(self, request, **kwargs):
        '''
           The function resets the function of a user.
           params:
              oldPassword: earlier password
              newPassword : new password
        '''        
        try:
            new_password = request.POST['newPassword']
            old_password = request.POST['oldPassword'] 
            user = User.objects.get(username=request.user)
            check_pass = user.check_password(str(old_password))
            if check_pass:
                invalid_password = check_password(new_password)
                if (invalid_password):
                    data = {'message':"password does not match the rules",'status':False}
                else:    
                    user.set_password(str(new_password))
                    user.save(using=settings.BRAND)
                    user_obj =  get_model('UserProfile').objects.get(user=user)
                    user_obj.reset_password = True
                    user_obj.reset_date = datetime.now()
                    user_obj.save(using=settings.BRAND)
                    data = {'message': 'Password Changed successfully', 'status': True}
            else:
                data = {'message': 'Old password wrong', 'status': False}
            return HttpResponse(json.dumps(data), content_type='application/json')
        except Exception as ex:
            logger.error('Exception while changing password {0}'.format(ex))
        return HttpBadRequest()
    
    def sent_otp_user_phone_number(self, request, **kwargs):
        '''
           Send OTP to a registered number
           params:
               phone_number: the number to send OTP
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
            message = core_utils.get_template('SEND_OTP').format(otp)
            send_job_to_queue(send_otp, {'phone_number':phone_number, 'message':message, 'sms_client':settings.SMS_CLIENT})
            logger.info('OTP sent to mobile {0}'.format(phone_number))
            data = {'status': 1, 'message': "OTP sent_successfully"}

        except Exception as ex:
            logger.error('Invalid details, mobile {0} and exception {1}'.format(request.POST.get('phone_number', ''),ex))
            data = {'status': 0, 'message': ex}
        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def activate_email(self, request, **kwargs):
        '''
           verify and email based on the activation key
        '''
        activation_key = request.GET['activation_key']
        activated_user = models.EmailToken.objects.activate_user(activation_key)
        if activated_user:
            data = {'status': 1, 'message': 'email-id validated'}
        else:
            data = {'status': 0, 'message': 'email-id not validated'}
        return HttpResponse(json.dumps(data), content_type="application/json")

    def validate_user_phone_number(self,phone_number, otp):
        '''
           Validate OTP of a phone number
           params:
               phone_number: number to validate
               otp: token to validate
        '''
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
        '''
           Authenticates if an email belongs to a valid user
           params:
               email: email id to be authenticated
        '''
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        email_id = load.get('email')

        if not email_id:
            return HttpBadRequest("email id is required")
        try:
            models.UserProfile.objects.get(user__email=email_id)
            data = {'status': 1, 'message': "email id verified"}
            return HttpResponse(json.dumps(data), content_type="application/json")
        except Exception as ex:
                log_message = "new user :{0}".format(ex)
                logger.info(log_message)
                data = {'status': 0, 'message': "Either your email is not verified"}
        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def authenticate_user_send_otp(self, request, **kwargs):
        '''
           Authenticates if a user by sending OTP
           params:
               email: email id to be authenticated
               phone_number: phone number to be authenticated
        '''
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message":"method not allowed"}), content_type="application/json",status=401)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        email = load.get('email')
        phone_number = load.get('phone_number')
        if not phone_number and not email:
            return HttpBadRequest("phone_number or email is required")
        try:
            if phone_number:
                phone_number = format_phone_number(phone_number)
                logger.info('OTP request received. Mobile: {0}'.format(phone_number))
                user_obj = models.UserProfile.objects.get(phone_number=phone_number).user
                otp = otp_handler.get_otp(user=user_obj)
                message = core_utils.get_template('SEND_OTP').format(otp)
                
                send_job_to_queue(send_otp, {'phone_number': phone_number,
                                             'message': message, "sms_client": settings.SMS_CLIENT},
                                  brand=settings.BRAND)
                logger.info('OTP sent to mobile {0}'.format(phone_number))
                data = {'status': 1, 'message': "OTP sent_successfully"}
                #Send email if email address exist
            if email:
                try:
                    user_obj = models.UserProfile.objects.get(user__email=email)
                    site = RequestSite(request)
                    get_model('EmailToken').objects.create_email_token(user_obj, email, site, trigger_mail='forgot-password')
                    data = {'status': 1, 'message': "Password reset link sent successfully"}
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as ex:
                    log_message = "Send email for forgot password :{0}".format(ex)
                    logger.info(log_message)
                    data = {'status': 0, 'message': "Either your email is not verified or its not exist"}
        except Exception as ex:
            logger.error('Invalid details, mobile {0} and exception {1}'.format(request.POST.get('phone_number', ''),ex))
            data = {'status': 0, 'message': "inavlid phone_number/email_id"}
        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def generate_reset_link(self,request, **kwargs):
        '''
           Generate password reset link on forgot password
           params:
               email: email id to send the link
        '''
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message":"method not allowed"}), content_type="application/json",status=401)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        email = load.get('email')
        try:
            user_obj = models.UserProfile.objects.get(user__email=email)
        except Exception as ex:
            return HttpBadRequest("Either your email is not verified or its not exist")
        site = RequestSite(request)
        token = models.EmailToken.objects.create_email_token(user_obj, email, site, trigger_mail='forgot-password')
        activation_key = token.activation_key
        data = {'status': 1, 'message': "Password reset link sent successfully"}
        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def change_user_password(self, request, **kwargs):
        '''
           Change password of a user
           params:
              password1: new password
              password2 : retyped password
        '''
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message":"method not allowed"}), content_type="application/json",status=401)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        email = load.get('email')
        password = load.get('password1')
        repassword = load.get('password2')
        user_details = {}
        if password != repassword:
            return HttpBadRequest("password1 and password2 not matched")
        try:
            user_obj = models.UserProfile.objects.get(user__email=email)
        except Exception as ex:
            logger.info("[Exception while changing password]:{0}".format(ex))
            raise ImmediateHttpResponse(
                response=http.HttpBadRequest('invalid authentication key!'))
        user_details['email'] = user_obj.user.email
        user = User.objects.filter(**user_details)[0]
        user.set_password(password)
        user.save()
        data = {'status': 1, 'message': "password updated successfully"}
        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def change_password(self, request, **kwargs):
        '''
           Change password of a user
           params:
              old_password: earlier password
              new_password : new password
              confirm_password : retyped new password
        '''
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message":"method not allowed"}), content_type="application/json",status=401)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        email = load.get('email_id')
        old_password = load.get('old_password')
        password = load.get('new_password')
        repassword = load.get('confirm_password')

        user_details = {}
        try:
            user_obj = models.UserProfile.objects.get(user__email=email)
            user_auth = authenticate(username=str(user_obj.user.username),
                            password=old_password)
            if not user_auth:
                data = {"status":0, "message" : "Old password is wrong"}
            else:
                if password != repassword:
                    return HttpBadRequest("Passwords do not match")
                user_details['email'] = user_obj.user.email
                user = User.objects.filter(**user_details)[0]
                user.set_password(password)
                user.save()
                data = {'status': 1, 'message': "password updated successfully"}
        except Exception as ex:
            logger.info("[Exception while changing password]:{0}".format(ex))
            raise ImmediateHttpResponse(
                response=http.HttpBadRequest('invalid authentication key!'))
        return HttpResponse(json.dumps(data), content_type="application/json")

    def login(self, request, **kwargs):
        '''
           Logs in valid users and generates access token
           params:
               email: registered email ID
               username: registered mobile number
               password: valid password
        '''
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message":"method not allowed"}), content_type="application/json",status=401)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        phone_number = load.get('phone_number')
        email_id = load.get('email')
        username = load.get('username')
        password = load.get('password')
        if not phone_number and not email_id and not username:
            return HttpBadRequest("phone_number/email/username required.")
        try:
            if phone_number:
                user_obj = models.UserProfile.objects.get(phone_number
                                                 =phone_number,is_phone_verified=True).user
            elif email_id:
                user_obj = models.UserProfile.objects.using(settings.BRAND).get(user__email=
                                                                      email_id,is_email_verified=True).user
            elif username:
                user_obj = User.objects.using(settings.BRAND).get(username=
                                                                      username)
    
            http_host = request.META.get('HTTP_HOST', 'localhost')
            user_auth = authenticate(username=str(user_obj.username),
                                password=password)
    
            if user_auth is not None:
                access_token = create_access_token(user_auth, http_host)
                user_groups = []
                if user_auth.is_active:
                    for group in user_auth.groups.values():
                        user_groups.append(group['name'])
                    login(request, user_auth)
                    data = {'status': 1, 'message': "login successfully",
                            'access_token': access_token, "user_id": user_auth.id, "user_groups" : user_groups}
            else:
                logger.error('[login]: {0} {1} {2}', user_auth, user_obj.username, password)
                data = {'status': 0, 'message': "login unsuccessful"}
        except Exception as ex:
            logger.error(ex)
            data = {'status': 0, 'message': "user is not registered"}
        return HttpResponse(json.dumps(data), content_type="application/json")

    def logout(self, request, **kwargs):
        '''
           logs out the logged in user and
           delete the access token
        '''
        access_token = request.GET.get('access_token')
        try:
            delete_access_token(access_token)
            data = {'status': 1, 'message': "logout successfully"}
        except Exception as ex:
            data = {'status': 0, 'message': "access_token_not_valid"}
            logger.info("[Exception get_user_login_information]:{0}".
                        format(ex))
        return HttpResponse(json.dumps(data), content_type="application/json")

class CircleHeadResource(CustomBaseModelResource):
        '''
           Circle head resource
        '''
        user = fields.ForeignKey(UserProfileResource, 'user', full=True)
        class Meta:
            queryset = get_model('CircleHead',settings.BRAND).objects.all()
            resource_name = "circle-heads"
            authentication = AccessTokenAuthentication()
            authorization = MultiAuthorization(DjangoAuthorization())
            allowed_methods = ['get']
            filtering = {
                     "user": ALL_WITH_RELATIONS,
                     }
            always_return_data = True
            
        def prepend_urls(self):
            return [
                 url(r"^(?P<resource_name>%s)/register%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('register_circle_head'), name="register_circle_head"),
                 url(r"^(?P<resource_name>%s)/update/(?P<user_id>\d+)%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('update_circle_head'), name="update_circle_head"),
               ]
        
        def register_circle_head(self, request, **kwargs):
            '''
               Register a new circle_head
               params:
                   phone_number: number of the circlehead
                   name: name of the circlehead
                   email: email of the Circle head
            '''
            self.is_authenticated(request)
            if request.method != 'POST':
                return HttpResponse(json.dumps({"message" : "Method not allowed"}), content_type= "application/json",
                                status=400)
            if not request.user.is_superuser:
                return HttpResponse(json.dumps({"message" : "Not Authorized to add circle_head"}), content_type= "application/json",
                                status=401)
            try:
                load = json.loads(request.body)
            except:
                return HttpResponse(content_type="application/json", status=404)
            name = load.get('name')
            phone_number = load.get('phone_number')
            email = load.get('email')
            
            
            try:
                user = get_model('CircleHead',settings.BRAND).objects.get(user__user__username=email)
                data = {'status': 0 , 'message' : 'Circle head with this username already exists'}
            except Exception as ex:
                logger.info("[register_circle_head]:New circle_head registration")
                user_data = register_user.register_user(Roles.CIRCLEHEADS,username=email,
                                                        phone_number=phone_number,
                                                        first_name=name,
                                                        email = email,
                                                        APP=settings.BRAND)
                circle_head_data = get_model('CircleHead',settings.BRAND)(user=user_data)
                circle_head_data.save(using=settings.BRAND)
                data = {"status": 1 , "message" : "Circle Head registered successfully"}
            return HttpResponse(json.dumps(data), content_type="application/json")
        
        def update_circle_head(self, request, **kwargs):
            '''
               Update an existing circle head
               params:
               user_id: id of the CH to be updated
               phone_number: number of the CH
               name: name of the CH
               email: email id of CH
               
            '''
        
            self.is_authenticated(request)
            if request.method != 'POST':
                return HttpResponse(json.dumps({"message" : "Method not allowed"}), content_type= "application/json",
                                    status=400)
            if not request.user.is_superuser:
                return HttpResponse(json.dumps({"message" : "Not Authorized to edit CH"}), content_type= "application/json",
                                status=401)
            user_id=kwargs['user_id']
            try:
                ch_obj = get_model('CircleHead',settings.BRAND).objects.get(user__user_id=user_id)
                load = json.loads(request.body)
            
                ch_profile = ch_obj.user
                ch_profile.phone_number = load.get('phone_number')

                ch_user= ch_obj.user.user
                ch_user.first_name=load.get('name')
                ch_user.email=load.get('email')
            
                ch_user.save(using=settings.BRAND)
                ch_profile.save()
                ch_obj.save()
                data = {'status': 1 , 'message' : 'Circle head updated successfully'}
            except Exception as ex:
                logger.info("[update_circle_head]: Invalid User ID:: {0}".format(ex))
                return HttpResponse(json.dumps({"message" : "User ID not found"}),content_type="application/json", status=404)
            return HttpResponse(json.dumps(data), content_type="application/json")
        

class RegionalManagerResource(CustomBaseModelResource):
    '''
       Regional sales manager resource
    '''
    user = fields.ForeignKey(UserProfileResource, 'user', full=True)
    circle_head = fields.ForeignKey(CircleHeadResource, 'circle_head')
    class Meta:
        queryset = models.RegionalManager.objects.all()
        resource_name = "regional-sales-managers"
        authentication = AccessTokenAuthentication()
        authorization = MultiAuthorization(DjangoAuthorization(),CHCustomAuthorization())
        allowed_methods = ['get']
        filtering = {
                     "user": ALL_WITH_RELATIONS,
                     "region": ALL,
                     "circle_head": ALL_WITH_RELATIONS                  
                     }
        always_return_data = True
        
    def prepend_urls(self):
        return [
                 url(r"^(?P<resource_name>%s)/register%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('register_regional_sales_manager'), name="register_regional_sales_manager"),
                 url(r"^(?P<resource_name>%s)/update/(?P<user_id>\d+)%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('update_regional_sales_manager'), name="update_regional_sales_manager"),
               ]
        
   
   
               
    def register_regional_sales_manager(self, request, **kwargs):
        '''
           Register a new RM
           params:
               phone_number: number of the dealer
               name: name of the dealer
               regional-office: region under the rm
               circle_head_user_id: user_id of Circle Head, incharge of RM
        '''
        self.is_authenticated(request)
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message" : "Method not allowed"}), content_type= "application/json",
                                status=400)
        if not request.user.is_superuser and not request.user.groups.filter(name=Roles.CIRCLEHEADS).exists():
            return HttpResponse(json.dumps({"message" : "Not Authorized to add RM"}), content_type= "application/json",
                                status=401)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        region = load.get('regional-office')
        
        name = load.get('name')
        phone_number = load.get('phone_number')
        email = load.get('email')
        circle_head_user_id = load.get('circle_head_user_id')
        try:
            user = models.RegionalManager.objects.get(user__user__username=email)
            data = {'status': 0 , 'message' : 'Regional Manager with this username already exists'}
        except Exception as ex:
            logger.info("[register_regional_sales_manager]:New RM registration")
            user_data = register_user.register_user(Roles.REGIONALMANAGERS,username=email,
                                                    phone_number=phone_number,
                                                    first_name=name,
                                                    email = email,
                                                    APP=settings.BRAND)
            try:
                circle_head_data = get_model('CircleHead',settings.BRAND).objects.get(user__user_id=circle_head_user_id)
                rm_data = models.RegionalManager(region=region, user=user_data, circle_head=circle_head_data)
                rm_data.save()
                data = {"status": 1 , "message" : "Regional sales manager registered successfully"}
            except Exception as ex:
                logger.info("[register_regional_sales_manager]: Invalid CH User ID provided :: {0}".format(ex))
                return HttpResponse(json.dumps({"message" : "Invalid CH User ID provided "}),content_type="application/json", status=404)
                 
        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def update_regional_sales_manager(self, request, **kwargs):
        '''
           Update an existing regional sales manager
           params:
               user_id: id of the RM to be updated
               phone_number: number of the RM
               name: name of the RM
               regional-office: region under the RM
               email: email id of RM
               ch_user_id: User id of CH incharge of RM
        '''
        self.is_authenticated(request)
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message" : "Method not allowed"}), content_type= "application/json",
                                status=400)
        if not request.user.is_superuser and not request.user.groups.filter(name=Roles.CIRCLEHEADS).exists():
            return HttpResponse(json.dumps({"message" : "Not Authorized to edit RM"}), content_type= "application/json",
                                status=401)
        user_id=kwargs['user_id']
        try:
            rm_obj = models.RegionalManager.objects.get(user__user_id=user_id)
            load = json.loads(request.body)
            
            rm_profile = rm_obj.user
            rm_profile.phone_number = load.get('phone_number')
            rm_user= rm_obj.user.user
            rm_user.first_name=load.get('name')
            rm_user.email=load.get('email')           
            rm_obj.region = load.get('regional-office')
            ch_user_id = load.get('ch_user_id')
            try:
                ch_data = get_model('CircleHead',settings.BRAND).objects.get(user__user_id=ch_user_id)
                rm_obj.circle_head=ch_data
            except Exception as ex:
                logger.info("[update_regional_sales_manager]: Invalid CH User ID provided :: {0}".format(ex))
                return HttpResponse(json.dumps({"message" : "Invalid CH User ID provided "}),content_type="application/json", status=404)
            rm_user.save(using=settings.BRAND)
            rm_profile.save()
            rm_obj.save()
            data = {'status': 1 , 'message' : 'Regional sales manager updated successfully'}
        except Exception as ex:
            logger.info("[update_regional_sales_manager]: Invalid User ID:: {0}".format(ex))
            return HttpResponse(json.dumps({"message" : "User ID not found"}),content_type="application/json", status=404)
        return HttpResponse(json.dumps(data), content_type="application/json")    
    
class AreaSalesManagerResource(CustomBaseModelResource):
        '''
           Area sales manager resource
        '''
        user = fields.ForeignKey(UserProfileResource, 'user', full=True)
        rm = fields.ForeignKey(RegionalManagerResource, 'rm')
        class Meta:
            queryset = models.AreaSalesManager.objects.all()
            resource_name = "area-sales-managers"
            authentication = AccessTokenAuthentication()
            authorization = MultiAuthorization(DjangoAuthorization(),RMCustomAuthorization())
            allowed_methods = ['get']
            filtering = {
                     "user": ALL_WITH_RELATIONS, 
                     "rm": ALL_WITH_RELATIONS,
                     }
            always_return_data = True
        
        #TO-DO : verify about state
        
        def prepend_urls(self):
            return [
                    url(r"^(?P<resource_name>%s)/register%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('register_area_sales_manager'), name="register_area_sales_manager"),
                    url(r"^(?P<resource_name>%s)/update/(?P<user_id>\d+)%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('update_area_sales_manager'), name="update_area_sales_manager")
                
                ]
    
     
        def register_area_sales_manager(self, request, **kwargs):
            '''
               Register a new sm
               params:
                   email: email of the sm
                   phone_number: number of the sm
                   name: name of the sm
                   rm_user_id: user_id of rm incharge of sm
            '''
            list_of_allowed_users = [Roles.CIRCLEHEADS,Roles.REGIONALMANAGERS]
            self.is_authenticated(request)
            if request.method != 'POST':
                return HttpResponse(json.dumps({"message" : "Method not allowed"}), content_type= "application/json",
                                    status=400)
            if not request.user.is_superuser and not request.user.groups.filter(name__in=list_of_allowed_users).exists():
                return HttpResponse(json.dumps({"message" : "Not Authorized to add SM"}), content_type= "application/json",
                                    status=401)
            try:
                load = json.loads(request.body)
            except:
                return HttpResponse(content_type="application/json", status=404)
            name = load.get('name')
            phone_number = load.get('phone_number')
            email = load.get('email')
            rm_user_id = load.get('rm_user_id')
            try:
                user = models.AreaSalesManager.objects.get(user__user__username=email)
                data = {'status': 0 , 'message' : 'Area sales manager with this username already exists'}
            except Exception as ex:
                logger.info("[register_area_sales_manager]: New SM registration:: {0}".format(ex))
                user_data = register_user.register_user(Roles.AREASALESMANAGERS,
                                                        username=email,
                                                        phone_number=phone_number,
                                                        first_name=name,
                                                        email = email,
                                                        APP=settings.BRAND)
                try:
                    rm_data = models.RegionalManager.objects.get(user__user_id=rm_user_id)
                    sm_data = models.AreaSalesManager(user=user_data,rm=rm_data)
                    sm_data.save()
                    data = {"status": 1 , "message" : "Area sales manager registered successfully"}
                except Exception as ex:
                    logger.info("[register_area_sales_manager]: Invalid RM User ID provided :: {0}".format(ex))
                    return HttpResponse(json.dumps({"message" : "Invalid RM User ID provided "}),content_type="application/json", status=404)
            return HttpResponse(json.dumps(data), content_type="application/json")
        
        def update_area_sales_manager(self, request, **kwargs):
            '''
               Update the details of an existing sm
               params:
                   user_id: User ID of the sm to be updated
                   phone_number: number of the sm
                   name: name of the sm
                   email: email id of sm
                   rm_user_id: user_id of rm incharge of sm
            '''
            list_of_allowed_users = [Roles.CIRCLEHEADS,Roles.REGIONALMANAGERS]
            self.is_authenticated(request)
            if request.method != 'POST':
                return HttpResponse(json.dumps({"message" : "Method not allowed"}), content_type= "application/json",
                                    status=400)
            if not request.user.is_superuser and not request.user.groups.filter(name__in=list_of_allowed_users).exists():
                return HttpResponse(json.dumps({"message" : "Not Authorized to edit SM"}), content_type= "application/json",
                                    status=401)
            user_id=kwargs['user_id']
            try:
                sm_obj = models.AreaSalesManager.objects.get(user__user_id=user_id)
                load = json.loads(request.body)
            
                sm_profile = sm_obj.user
                sm_profile.phone_number = load.get('phone_number')
            
                sm_user= sm_obj.user.user
                sm_user.first_name=load.get('name')
                sm_user.email=load.get('email')

                rm_user_id=load.get('rm_user_id')
                try:
                    rm_data = models.RegionalManager.objects.get(user__user_id=rm_user_id)
                    sm_obj.rm=rm_data
                except Exception as ex:
                    logger.info("[update_area_sales_manager]: Invalid RM User ID provided :: {0}".format(ex))
                    return HttpResponse(json.dumps({"message" : "Invalid RM User ID provided"}),content_type="application/json", status=404)
                sm_user.save(using=settings.BRAND)
                sm_profile.save()
                sm_obj.save()
                data = {'status': 1 , 'message' : 'Area sales manager updated successfully'}
            except Exception as ex:
                logger.info("[update_area_sales_manager]: Invalid SM ID :: {0}".format(ex))
                return HttpResponse(json.dumps({"message" : "User ID not found"}),content_type="application/json", status=404)
            return HttpResponse(json.dumps(data), content_type="application/json")
    
        
class ZonalServiceManagerResource(CustomBaseModelResource):
    '''
       Zonal service manager resource
    '''
    user = fields.ForeignKey(UserProfileResource, 'user', full=True)

    class Meta:
        queryset = models.ZonalServiceManager.objects.all()
        resource_name = "zonal-service-managers"
        authentication = AccessTokenAuthentication()
        authorization = MultiAuthorization(DjangoAuthorization())
        allowed_methods = ['get', 'delete']
        filtering = {
                     "user": ALL_WITH_RELATIONS,
                     "zsm_id": ALL,
                     }
        always_return_data = True

    def prepend_urls(self):
        return [
                 url(r"^(?P<resource_name>%s)/register%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('register_zonal_service_manager'), name="register_zonal_service_manager"),
                 url(r"^(?P<resource_name>%s)/update/(?P<zsm_id>\d+)%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('update_zonal_service_manager'), name="update_zonal_service_manager"),
                ]
    
    
    def register_zonal_service_manager(self, request, **kwargs):
        '''
           Register a new ZSM
           params:
               id: id of the ZSM
               phone_number: number of the dealer
               name: name of the dealer
               regional-office: region under the asm
        '''
        self.is_authenticated(request)
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message" : "Method not allowed"}), content_type= "application/json",
                                status=400)
        if not request.user.is_superuser:
            return HttpResponse(json.dumps({"message" : "Not Authorized to add RSM"}), content_type= "application/json",
                                status=401)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        zsm_id = load.get('id')

        try:
            zsm_data = models.ZonalServiceManager.objects.get(zsm_id=zsm_id)
            data = {'status': 0 , 'message' : 'Regional service manager with this id already exists'}
        except Exception as ex:
            logger.info("[register_zonal_service_manager]:New RSM registration:: {0}".format(ex))
            name = load.get('name')
            regional_office = load.get('regional-office')
            phone_number = load.get('phone-number')
            email = load.get('email')
            user_data = register_user.register_user(Roles.ZSM,username=email,
                                             phone_number=phone_number,
                                             first_name=name,
                                             email = email,
                                             APP=settings.BRAND)
            zsm_data = models.ZonalServiceManager(zsm_id=zsm_id, user=user_data,
                                        regional_office=regional_office)
            zsm_data.save()
            data = {"status": 1 , "message" : "Regional service manager registered successfully"}
        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def update_zonal_service_manager(self, request, **kwargs):
        '''
           Update an existing ZSM
           params:
               zsm_id: id of the ZSM to be updated
               phone_number: number of the dealer
               name: name of the dealer
               regional-office: region under the asm
        '''
        self.is_authenticated(request)
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message" : "Method not allowed"}), content_type= "application/json",
                                status=400)
        if not request.user.is_superuser:
            return HttpResponse(json.dumps({"message" : "Not Authorized to edit RSM"}), content_type= "application/json",
                                status=401)
        zsm_id=kwargs['zsm_id']
        try:
            zsm_obj = models.ZonalServiceManager.objects.get(pk=zsm_id)
            load = json.loads(request.body)
            
            zsm_profile = zsm_obj.user
            zsm_profile.phone_number = load.get('phone-number')
            
            zsm_user= zsm_obj.user.user
            zsm_user.first_name=load.get('name')
            
            zsm_obj.regional_office = load.get('regional-office')
            
            zsm_user.save(using=settings.BRAND)
            zsm_profile.save()
            zsm_obj.save()
            data = {'status': 0 , 'message' : 'Regional service manager updated successfully'}
        except Exception as ex:
            logger.info("[update_zonal_service_manager]: Invalid RSM ID:: {0}".format(ex))
            return HttpResponse(json.dumps({"message" : "RSM ID not found"}),content_type="application/json", status=404)
        return HttpResponse(json.dumps(data), content_type="application/json")

class AreaServiceManagerResource(CustomBaseModelResource):
    '''
       Area service managers resource
    '''
    user = fields.ForeignKey(UserProfileResource, 'user', full=True)
    zsm = fields.ForeignKey(ZonalServiceManagerResource, 'zsm', full =True)

    class Meta:
        queryset = models.AreaServiceManager.objects.all()
        resource_name = "area-service-managers"
        authentication = AccessTokenAuthentication()
        authorization = MultiAuthorization(DjangoAuthorization(), ZSMCustomAuthorization())
        allowed_methods = ['get', 'delete']
        filtering = {
                     "user": ALL_WITH_RELATIONS,
                     "asm_id": ALL, 
                     "zsm": ALL_WITH_RELATIONS,
                     "area": ALL,
                     }
        always_return_data = True

    def prepend_urls(self):
        return [
                 url(r"^(?P<resource_name>%s)/register%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('register_area_service_manager'), name="register_area_service_manager"),
                 url(r"^(?P<resource_name>%s)/update/(?P<asm_id>\d+)%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('update_area_service_manager'), name="update_area_service_manager"),
                ]
    
    
    def register_area_service_manager(self, request, **kwargs):
        '''
           Register a new asm
           params:
               id: ID of the ASM
               email: email of the asm
               phone_number: number of the dealer
               name: name of the dealer
               area: region under the asm
               zsm_id: zsm under which asm belongs
        '''
        self.is_authenticated(request)
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message" : "Method not allowed"}), content_type= "application/json",
                                status=400)
        if not request.user.is_superuser and not request.user.groups.filter(name=Roles.ZSM).exists():
            return HttpResponse(json.dumps({"message" : "Not Authorized to add ASM"}), content_type= "application/json",
                                status=401)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        asm_id = load.get('id')
        try:
            asm_data = models.AreaServiceManager.objects.get(asm_id=asm_id)
            data = {'status': 0 , 'message' : 'Area service manager with this id already exists'}
        except Exception as ex:
            logger.info("[register_area_service_manager]: New ASM registration:: {0}".format(ex))
            name = load.get('name')
            area = load.get('area')
            phone_number = load.get('phone-number')
            email = load.get('email')
            zsm_id = load.get('zsm_id')
            zsm_data = models.ZonalServiceManager.objects.get(zsm_id=zsm_id)
            user_data = register_user.register_user(Roles.AREASERVICEMANAGER,
                                             username=email,
                                             phone_number=phone_number,
                                             first_name=name,
                                             email = email,
                                             APP=settings.BRAND)
            asm_data = models.AreaServiceManager(asm_id=asm_id, user=user_data,
                                        area=area, zsm=zsm_data)
            asm_data.save()
            data = {"status": 1 , "message" : "Area service manager registered successfully"}
        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def update_area_service_manager(self, request, **kwargs):
        '''
           Update the details of an existing asm
           params:
               asm_id: ID of the asm to be updated
               phone_number: number of the dealer
               name: name of the dealer
               area: region under the asm
               zsm_id: zsm under which asm belongs
        '''
        self.is_authenticated(request)
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message" : "Method not allowed"}), content_type= "application/json",
                                status=400)
        if not request.user.is_superuser and not request.user.groups.filter(name=Roles.ZSM).exists():
            return HttpResponse(json.dumps({"message" : "Not Authorized to edit ASM"}), content_type= "application/json",
                                status=401)
        asm_id=kwargs['asm_id']
        try:
            asm_obj = models.AreaServiceManager.objects.get(pk=asm_id)
            load = json.loads(request.body)
            
            asm_profile = asm_obj.user
            asm_profile.phone_number = load.get('phone-number')
            
            asm_user= asm_obj.user.user
            asm_user.first_name=load.get('name')
            
            asm_obj.area = load.get('area')
            
            zsm_id=load.get('zsm_id')
            zsm_data = models.ZonalServiceManager.objects.get(zsm_id=zsm_id)
            asm_obj.zsm=zsm_data

            asm_user.save(using=settings.BRAND)
            asm_profile.save()
            asm_obj.save()
            data = {'status': 0 , 'message' : 'Regional service manager updated successfully'}
        except Exception as ex:
            logger.info("[update_area_service_manager]: Invalid ASM ID :: {0}".format(ex))
            return HttpResponse(json.dumps({"message" : "ASM ID not found"}),content_type="application/json", status=404)
        return HttpResponse(json.dumps(data), content_type="application/json")


class DealerResource(CustomBaseModelResource):
    '''
       Dealers under a brand resource
    '''
    user = fields.ForeignKey(UserProfileResource, 'user', full=True)
    asm = fields.ForeignKey(AreaServiceManagerResource, 'asm', full=True, null=True)
    sm = fields.ForeignKey(AreaSalesManagerResource, 'sm', full=True, null=True)
    
    class Meta:
        queryset = models.Dealer.objects.all()
        resource_name = "dealers"
        authentication = AccessTokenAuthentication()
        authorization = MultiAuthorization(DjangoAuthorization(), DealerCustomAuthorization())
        allowed_methods = ['get', 'post']
        filtering = {
                     "user": ALL_WITH_RELATIONS,
                     "dealer_id": ALL,
                     "asm":ALL_WITH_RELATIONS,
                     "sm":ALL_WITH_RELATIONS,
                     }
        always_return_data = True
        ordering = ['user']
        
    def prepend_urls(self):
        return [
                 url(r"^(?P<resource_name>%s)/register%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('register_dealer'), name="register_dealer"),
                url(r"^(?P<resource_name>%s)/active%s" % (self._meta.resource_name,trailing_slash()),
                                                        self.wrap_view('get_active_dealer'), name="get_active_dealer"),
                url(r"^(?P<resource_name>%s)/update/(?P<dealer_id>\d+)%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('update_dealer'), name="update_dealer")
               
                ]
    
    
    def register_dealer(self, request, **kwargs):
        '''
           Registers a new dealer.
           params:
               username: ID of the dealer
               phone_number: number of the dealer
               email: email ID of the dealer
               name: name of the dealer
               asm_id: asm under which dealer belongs
        '''
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message" : "Method not allowed"}), content_type= "application/json",
                                status=400)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        username = load.get('username')
        phone_number = load.get('phone-number')
        email = load.get('email')
        name = load.get('name', '')
        asm = load.get('asm_id', None)
        try:
            user = models.Dealer.objects.get(user__phone_number=phone_number, dealer_id=username)
            data = {'status': 0 , 'message' : 'Dealer with this id or phone number already exists'}

        except Exception as ex:
            logger.info("[register_dealer] : New dealer registration :: {0}".format(ex))
            user_data = register_user.register_user(Roles.DEALERS,username=username,
                                             phone_number=phone_number,
                                             first_name=name,
                                             email = email, APP=settings.BRAND)
            if asm:
                asm = models.AreaServiceManager.objects.get(asm_id=asm)
            dealer_data = models.Dealer(dealer_id=username, user=user_data, asm=asm)
            dealer_data.save()
            data = {"status": 1 , "message" : "Dealer registered successfully"}

        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def get_active_dealer(self, request, **kwargs):
        '''
           Get the count of active dealers of the day
        '''
        result = []
        active_today = models.Dealer.objects.filter(last_transaction_date__startswith=date.today()).count()
        today = {}
        today['count_on'] = 'Today'
        today['active'] = active_today
        result.append(today)
        return HttpResponse(content=json.dumps(result), 
                            content_type='application/json')
        
    def update_dealer(self, request, **kwargs):
        '''
           Update the details of an existing dealer
           params:
               dealer_id: ID of the dealer to be updated
               phone_number: number of the dealer
               email: email ID of the dealer
               name: name of the dealer
               asm_id: asm under which dealer belongs
        '''
        self.is_authenticated(request)
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message" : "Method not allowed"}), content_type= "application/json",
                                status=400)
        dealer_id=kwargs['dealer_id']
        try:
            dealer_obj = models.Dealer.objects.get(user__user__id=dealer_id)
            load = json.loads(request.body)
            asm = load.get('asm_id', None)
            if asm:
                asm = models.AreaServiceManager.objects.get(asm_id=asm)
                dealer_obj.asm=asm
            dealer_profile = dealer_obj.user
            dealer_profile.phone_number = load.get('phone-number')
            
            dealer_user= dealer_obj.user.user
            dealer_user.email=load.get('email')
            dealer_user.first_name=load.get('name')

            dealer_user.save(using=settings.BRAND)
            dealer_profile.save()
            dealer_obj.save()
            data = {'status': 0 , 'message' : 'Dealer details updated successfully'}
        except Exception as ex:
            logger.info("[update_dealer] : Invalid Dealer ID ::{0}".format(ex))
            return HttpResponse(json.dumps({"message" : "Dealer ID not found"}),content_type="application/json", status=404)
        return HttpResponse(json.dumps(data), content_type="application/json")
    
class AuthorizedServiceCenterResource(CustomBaseModelResource):
    '''
       Authorized service centers who service the vehicles resource
    '''
    user = fields.ForeignKey(UserProfileResource, 'user', full=True)
    dealer = fields.ForeignKey(DealerResource, 'dealer', null=True, blank=True, full=True)

    class Meta:
        queryset = models.AuthorizedServiceCenter.objects.all()
        resource_name = "authorized-service-centers"
        authentication = AccessTokenAuthentication()
        authorization = MultiAuthorization(DjangoAuthorization())
        allowed_methods = ['get']
        filtering = {
                     "user": ALL_WITH_RELATIONS,
                     "asc_id": ALL,
                     "dealer": ALL_WITH_RELATIONS
                     }
        always_return_data = True


class ServiceAdvisorResource(CustomBaseModelResource):
    '''
       Service advisors who service the vehicles resource
    '''
    user = fields.ForeignKey(UserProfileResource, 'user', full=True)
    dealer = fields.ForeignKey(DealerResource, 'dealer', null=True, blank=True, full=True)
    asc = fields.ForeignKey(AuthorizedServiceCenterResource, 'asc', null=True, blank=True, full=True)

    class Meta:
        queryset = models.ServiceAdvisor.objects.all()
        resource_name = "service-advisors"
        authentication = AccessTokenAuthentication()
        authorization = MultiAuthorization(DjangoAuthorization())
        allowed_methods = ['get']
        filtering = {
                     "user": ALL_WITH_RELATIONS,
                     "dealer": ALL_WITH_RELATIONS,
                     "asc": ALL_WITH_RELATIONS,
                     "service_advisor_id": ALL,
                     "status": ALL
                     }
        always_return_data = True

class TerritoryResource(CustomBaseModelResource): 
    '''
       Territories under loyalty resource
    '''   
    class Meta:
        queryset = models.Territory.objects.all()
        resource_name = "territories"
        authorization = Authorization()
        allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        filtering = {
                     "territory":ALL
                     }


class StateResource(CustomBaseModelResource):
    '''
       States under loyalty resource
    '''
    territory = fields.ForeignKey(TerritoryResource, 'territory', null=True, blank=True)
    class Meta:
        queryset = models.State.objects.all()
        resource_name = "states"
        authorization = Authorization()
        allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        filtering = {
                     "state_name":ALL, 
                     }

class CityResource(CustomBaseModelResource):
    '''
       Cities under loyalty resource
    '''
    state = fields.ForeignKey(StateResource, 'state')
    class Meta:
        queryset = models.City.objects.all()
        resource_name = "cities"
        authorization = Authorization()
        allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        filtering = {
                     "city":ALL,
                     "state":ALL_WITH_RELATIONS, 
                     }


class NationalSparesManagerResource(CustomBaseModelResource):
    '''
       National spares managers resource
    '''
    class Meta:
        queryset = models.NationalSparesManager.objects.all()
        resource_name = "national-spares-managers"
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        
        
class AreaSparesManagerResource(CustomBaseModelResource):
    '''
       Area spares managers resource
    '''
    class Meta:
        queryset = models.AreaSparesManager.objects.all()
        resource_name = "area-spares-managers"
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        
class PartnerResource(CustomBaseModelResource):
    '''
       Partners for loaylty redemption resource
    '''
    class Meta:
        queryset = models.Partner.objects.all()
        resource_name = "partners"
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        allowed_methods = ['get', 'post', 'put']
        always_return_data = True


class DistributorResource(CustomBaseModelResource):
    '''
       Ditributors under loyalty resource
    '''
    user = fields.ForeignKey(UserProfileResource, 'user', full=True)
    asm = fields.ForeignKey(AreaSparesManagerResource, 'asm', full=True)
    class Meta:
        queryset = models.Distributor.objects.all()
        resource_name = "distributors"
        authorization = Authorization()
        #authorization = MultiAuthorization(DjangoAuthorization(), DistributorCustomAuthorization())
        authentication = AccessTokenAuthentication()
        allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        filtering = {
                     "distributor_id" : ALL
                     }


class RetailerResource(CustomBaseModelResource):
    '''
       Spare part retailers resource
    '''
    class Meta:
        queryset = models.Retailer.objects.all()
        resource_name = "retailers"
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        allowed_methods = ['get', 'post', 'put']
        always_return_data = True

class MemberResource(CustomBaseModelResource):
    '''
       Members under loyalty resource
    '''
    distributor = fields.ForeignKey(DistributorResource, 'registered_by_distributor', null=True, blank=True, full=True) 
    preferred_retailer = fields.ForeignKey(RetailerResource, 'preferred_retailer', null=True, blank=True, full=True)
    state = fields.ForeignKey(StateResource, 'state', full=True)
    
    class Meta:
        queryset = models.Member.objects.all()
        resource_name = "members"
        args = constants.LOYALTY_ACCESS
        authorization = MultiAuthorization(Authorization(), LoyaltyCustomAuthorization(query_field=args['query_field']))
        authentication = AccessTokenAuthentication()
        allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        max_limit= None
        
        filtering = {
                     "state": ALL_WITH_RELATIONS,
                     "distributor" : ALL_WITH_RELATIONS,
                     "locality":ALL,
                     "district":ALL,
                     "last_transaction_date":ALL,
                     "total_accumulation_req":ALL,
                     "total_accumulation_points":ALL,
                     "total_redemption_points":ALL,
                     "total_redemption_req":ALL,
                     "first_name":ALL,
                     "middle_name":ALL,
                     "last_name":ALL,
                     "registered_date":ALL,
                     "member_id" : ALL,
                     "permanent_id" : ALL,
                     "mechanic_id" : ALL,
                     "phone_number" : ALL,
                     "created_date" : ALL
                     }
        ordering = ["state", "locality", "district", "registered_date",
                    "created_date", "mechanic_id", "last_transaction_date", "total_accumulation_req"
                    "total_accumulation_points", "total_redemption_points", "total_redemption_req" ]
        
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(MemberResource, self).build_filters(filters)
         
        if 'member_id' in filters:
            query = filters['member_id']
            qset = (
                    Q(mechanic_id=query)|
                    Q(permanent_id=query)
                      )
            orm_filters.update({'custom':  qset})
        return orm_filters  
                     
            
    def apply_filters(self, request, applicable_filters):
        if 'custom' in applicable_filters:
            custom = applicable_filters.pop('custom')
        else:
            custom = None
        
        semi_filtered = super(MemberResource, self).apply_filters(request, applicable_filters)
        
        return semi_filtered.filter(custom) if custom else semi_filtered
        
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/active%s" % (self._meta.resource_name,
                                                     trailing_slash()),
                self.wrap_view('get_active_member'), name="get_active_member"),
            url(r"^(?P<resource_name>%s)/points%s" % (self._meta.resource_name,
                                                     trailing_slash()),
                self.wrap_view('get_total_points'), name="get_total_points"),
                
            url(r"^(?P<resource_name>%s)/registered-members%s" % (self._meta.resource_name,
                                                     trailing_slash()),
                self.wrap_view('registered_members'), name="registered_members"),
                
            url(r"^(?P<resource_name>%s)/monthly-active-count%s" % (self._meta.resource_name,
                                                     trailing_slash()),
                self.wrap_view('monthly_active_code'), name="monthly_active_code"),
                
            url(r"^(?P<resource_name>%s)/monthly-inactive-count%s" % (self._meta.resource_name,
                                                     trailing_slash()),
                self.wrap_view('monthly_inactive_code'), name="monthly_inactive_code"),
            
        ]
        

    def registered_members(self, request, **kwargs):
        registered_date__gte = request.GET.get('registered_date__gte')
        registered_date__lte = request.GET.get('registered_date__lte')
        details = self.member_return_date_filter_data(request, registered_date__gte , registered_date__lte)
        csv_data_rcv = self.csv_member_download(details)
         
        return csv_data_rcv
     
    def member_return_date_filter_data(self,request, start,end): 
        conn = connections[settings.BRAND]
        cursor = conn.cursor()

        if request.user.groups.filter(name=Roles.AREASPARESMANAGERS).exists():
            asm_state_list=models.AreaSparesManager.objects.get(user__user=request.user).state.all()
            state_list = []
            state_list_join = ','.join("'"+str(state)+"'" for state in asm_state_list)
            
            query = "SELECT gmm.mechanic_id, gmm.permanent_id, gmm.first_name, gmm.district,gmm.phone_number, \
                     gms.state_name,gmdr.distributor_id,gmm.registered_date,\
                     concat(gmm.shop_name, ', ', gmm.shop_number, ', ',gmm.shop_address,', ',gmm.district, ', ',gms.state_name,', ',gmm.pincode)\
                     as Address\
                     FROM gm_member gmm\
                     join gm_distributor gmdr on gmdr.id = gmm.registered_by_distributor_id \
                     join gm_state gms on gmm.state_id = gms.id \
                     where  gmm.registered_date >=\"{0}\" \
                    and gmm.registered_date<= \"{1}\" and gms.state_name in ({2}) ".format(start, end, state_list_join);
#                     
        else:
            query = "SELECT gmm.mechanic_id, gmm.permanent_id, gmm.first_name, gmm.district,gmm.phone_number, \
                     gms.state_name,gmdr.distributor_id,gmm.registered_date,\
                     concat(gmm.shop_name, ', ', gmm.shop_number, ', ',gmm.shop_address,', ',gmm.district, ', ',gms.state_name,', ',gmm.pincode)\
                     as Address\
                     FROM gm_member gmm\
                     join gm_distributor gmdr on gmdr.id = gmm.registered_by_distributor_id \
                     join gm_state gms on gmm.state_id = gms.id \
                     where gmm.registered_date >=\"{0}\" \
                     and gmm.registered_date<= \"{1}\" ".format(start, end);
                     
            
        rows = cursor.execute(query)
        rows1 = cursor.fetchall()
        conn.close()
        return rows1
    
    def csv_member_download(self,rows1):
        file_name='registration_download' + datetime.now().strftime('%d_%m_%y')
        headers = ['Mechanic ID','Mechanic Permanent ID', 'Mechanic Name','District','Mobile Number','State','Distributor Code','Date Of Registration','Address of garage']
        csvfile = StringIO.StringIO()
        csvwriter = csv.writer(csvfile)  
        csvwriter.writerow(headers)   
        csvwriter.writerows(rows1)
        response = HttpResponse(csvfile.getvalue(), content_type='application/csv')
        response['Content-Disposition'] = 'attachment; filename={0}.csv'.format(file_name)
        return response


    def monthly_active_code(self, request , **kwargs):
        '''
            Get registered member details
            returns in csv format
        '''
#         filter_param = request.GET.get('key')
#         filter_value = request.GET.get('value')
#         applied_filter = {filter_param: filter_value}
        try:
            #filter_data_list = self.get_list(request, **applied_filter)
            active_member_data = self.get_active_member(request, **kwargs)
            csv =  self.csv_convert_monthly_active(active_member_data)
            return csv
        except Exception as ex:
            logger.error(ex)
            data = {'status':0 , 'message': 'key does not exist'}
            return HttpResponse(json.dumps(data), content_type="application/json")
        
    def csv_convert_monthly_active(self, data):
        data_received = json.loads(data.content)
        file_name='monthly_active_download' + datetime.now().strftime('%d_%m_%y')
        headers = []
        headers = headers+constants.MONTHLY_ACTIVE_API_HEADER
        #headers= ['State', 'No of Mechanic Registered (till date)','No of Mechanic messaged','%active','ASM Name']
        csvfile = StringIO.StringIO()
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)
        for k, v in data_received.items():
            data=[]
            for field in headers:
                if field=='State':
                    data.append(k)
                elif field=='No of Mechanic Registered (till date)':
                    data.append(v['registered_count'])
                elif field== 'No of Mechanic messaged': 
                    data.append(v['active_count'])  
                elif field== '%active': 
                    data.append(v['active_percent'])
                else:
                    data.append(v['asm'])
            csvwriter.writerow(data)
        response = HttpResponse(csvfile.getvalue(), content_type='application/csv')
        response['Content-Disposition'] = 'attachment; filename={0}.csv'.format(file_name)
        return response
    
    def monthly_inactive_code(self, request , **kwargs):
        '''
#           Get registered member details
#           returns in csv format
#       '''
        filter_param = request.GET.get('key')
        filter_value = request.GET.get('value')
        applied_filter = {filter_param: filter_value}
        try:
            filter_data_list = self.get_list(request, **applied_filter)
            csv =  self.csv_convert_monthly_inactive(filter_data_list)
            return csv
        except Exception as ex:
            logger.error(ex)
            data = {'status':0 , 'message': 'key does not exist'}
            return HttpResponse(json.dumps(data), content_type="application/json")
    
    def csv_convert_monthly_inactive(self, data):
        pass

          
        
    def get_active_member(self, request, **kwargs):
        '''
           Get active member counts and
           registered member count based on region
        '''
        
        self.is_authenticated(request)
        args={}
        try:
            load = request.GET
        except Exception as ex:
            return HttpResponse(content_type="application/json", status=404)
        try:
            active_days = load.get('active_days', None)
            if not active_days:
                active_days=90
            if not request.user.is_superuser:
                user_group = request.user.groups.values()[0]['name']
                area = self._meta.args['query_field'][user_group]['area']
                region = self._meta.args['query_field'][user_group]['group_region']
                args = LoyaltyCustomAuthorization.get_filter_query(user=request.user, q_user=area, query=args)
            else:
                region='state__state_name'
            registered_member = get_model('Member').objects.filter(**args).values(region).annotate(count= Count('mechanic_id'))
            active_type = load.get('active_type', None)
            if active_type:
                type_model={'accumulation':'AccumulationRequest', 'redemption':'RedemptionRequest'}
                args['created_date__gte']=datetime.now()-timedelta(int(active_days))
                region_filter='member__state__state_name'
                active_member = get_model(type_model[active_type]).objects.filter(**args).values(region_filter).annotate(count= Count('member', distinct = True))
            else:
                region_filter=region
                args['last_transaction_date__gte']=datetime.now()-timedelta(int(active_days))
                active_member = get_model('Member').objects.filter(**args).values(region_filter).annotate(count= Count('mechanic_id'))
            active_asm = get_model('AreaSparesManager').objects.all().values('state__state_name', 'name')
            member_report={}
            for member in registered_member:
                member_report[member[region]]={}
                member_report[member[region]]['registered_count'] = member['count']
                member_report[member[region]]['active_count']= 0
                member_report[member[region]]['active_percent']= 0
                member_report[member[region]]['asm']= ''
                active = filter(lambda active: active[region_filter] == member[region], active_member)
                all_asm = filter(lambda active: active['state__state_name'] == member[region], active_asm)
                if all_asm:
                    asm_list=[]
                    for asm in all_asm:
                        asm_list.append(asm['name'])
                    member_report[member[region]]['asm']= ' , '.join(asm_list)
                if active:
                    member_report[member[region]]['active_count']= active[0]['count']
                    member_report[member[region]]['active_percent']= round(100 * float(active[0]['count'])/float(member['count']), 2)
            
        except Exception as ex:
            logger.error('Active member count requested by {0}:: {1}'.format(request.user, ex))
            member_report = {'status': 0, 'message': 'could not retrieve the count of active members'}
        return HttpResponse(json.dumps(member_report), content_type="application/json")

    def get_total_points(self, request, **kwargs):
        '''
           get total accumulated points
           and redeemed points of the member
        '''
        self.is_authenticated(request)
        args={}
        try:
            load = request.GET
        except Exception as ex:
            return HttpResponse(content_type="application/json", status=404)
        try:
            if not request.user.is_superuser:
                user_group = request.user.groups.values()[0]['name']
                area = 'member__' + self._meta.args['query_field'][user_group]['area']
                region = 'member__' + self._meta.args['query_field'][user_group]['group_region']
                args = LoyaltyCustomAuthorization.get_filter_query(user=request.user, q_user=area, query=args)
            total_redeem_points = models.RedemptionRequest.objects.filter(**args).values(region).annotate(sum=Sum('points'))
            total_accumulate_points = models.AccumulationRequest.objects.filter(**args).values(region).annotate(sum=Sum('points'))
            member_report={}
            for region_point in total_redeem_points:
                member_report[region_point[region]]={}
                member_report[region_point[region]]['total_redeem'] = region_point['sum']
                member_report[region_point[region]]['total_accumulate'] = 0
                active = filter(lambda active: active[region] == region_point[region], total_accumulate_points)
                if active:
                    member_report[region_point[region]]['total_accumulate']= active[0]['sum']
        except Exception as ex:
            logger.error('redemption/accumulation request count requested by {0}:: {1}'.format(request.user, ex))
            member_report = {'status': 0, 'message': 'could not retrieve the sum of points of requests'}
        return HttpResponse(json.dumps(member_report), content_type="application/json")
    

class BrandDepartmentResource(CustomBaseModelResource):
    '''
       Brand Department resource
    '''
    class Meta:
        queryset = models.BrandDepartment.objects.all()
        resource_name = "brand-departments"
        authorization = Authorization()
        allowed_methods = ['get']
        always_return_data = True
        filtering = {
                     "id" : ALL,
                     "name" : ALL
                     }


class DepartmentSubCategoriesResource(CustomBaseModelResource):
    '''
       Department sub categories resource
    '''
    department = fields.ForeignKey(BrandDepartmentResource, 'department', full=True, null=True, blank=True)

    class Meta:
        queryset = models.DepartmentSubCategories.objects.all()
        resource_name = "department-sub-categories"
        authorization = Authorization()
        allowed_methods = ['get']
        always_return_data = True
        filtering = { 
                     "department": ALL_WITH_RELATIONS,
                     "id" : ALL
                     } 


class ServiceDeskUserResource(CustomBaseModelResource):
    '''
       Service desk user resource
    '''
    user = fields.ForeignKey(UserProfileResource, 'user_profile',
                                        full=True, null=True, blank=True)
    sub_department = fields.ForeignKey(DepartmentSubCategoriesResource, 'sub_department',
                                       full=True, null=True, blank=True)

    class Meta:
        queryset = models.ServiceDeskUser.objects.all()
        resource_name = "service-desk-users"
#         authorization = MultiAuthorization(DjangoAuthorization())
#         authentication = MultiAuthentication(AccessTokenAuthentication())
        authorization = Authorization()
        allowed_methods = ['get']
        always_return_data = True
        filtering = {
                        "user": ALL_WITH_RELATIONS,
                        "sub_department" : ALL_WITH_RELATIONS,
                        "id" : ALL
                     }

class TransporterResource(CustomBaseModelResource):
    '''
       Tranporters for CTS resource
    '''
    user = fields.ForeignKey(UserProfileResource, 'user', full=True, null=True, blank=True)
    class Meta:
        queryset = models.Transporter.objects.all()
        resource_name = 'transporters'
        authorization = MultiAuthorization(DjangoAuthorization())
        allowed_methods = ['get']
        always_return_data = True
        filtering = {
                     'user':ALL_WITH_RELATIONS
                     }

class SupervisorResource(CustomBaseModelResource):
    '''
       Supervisors for CTS resource
    '''
    transporter = fields.ForeignKey(TransporterResource, 'transporter', full=True, null=True, blank=True)
    class Meta:
        queryset = models.Supervisor.objects.all()
        resource_name = 'supervisors'
        authorization = MultiAuthorization(DjangoAuthorization())
        allowed_methods = ['get']
        always_return_data = True
        filtering = {
                     'transporter': ALL_WITH_RELATIONS
                     }
        

