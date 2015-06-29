from datetime import datetime
from random import randint

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import get_current_timezone_name
from django_otp.oath import TOTP
import pytz

from gladminds.afterbuy import models as afterbuy_model
from gladminds.core.exceptions import OtpFailedException
from gladminds.settings import TOTP_SECRET_KEY, OTP_VALIDITY


def save_otp(token, **kwargs):
    if 'user' in kwargs.keys():
        user = afterbuy_model.Consumer.objects.get(user = kwargs.get('user'))
        afterbuy_model.OTPToken.objects.filter(user=user).delete()
        token_obj = afterbuy_model.OTPToken(user=user, token=str(token), request_date=datetime.now(), email=user.user.email)
    else:
        phone_number = kwargs.get('phone_number')
        afterbuy_model.OTPToken.objects.filter(phone_number=phone_number).delete()
        token_obj = afterbuy_model.OTPToken(token=str(token), request_date=datetime.now(), phone_number=phone_number)
    token_obj.save()


def generate_otp(phone_number):
    totp = TOTP(TOTP_SECRET_KEY+str(randint(10000,99999))+str(phone_number))
    totp.time = 30
    token = totp.token()
    return token


def validate_otp(otp, **kwargs):
    if 'user' in kwargs.keys():
        token_obj = afterbuy_model.OTPToken.objects.filter(user = kwargs.get('user'))[0]
    else:
        phone_number = kwargs.get('phone_number')
        token_obj = afterbuy_model.OTPToken.objects.get(phone_number=phone_number)

    if int(otp) == int(token_obj.token) and (timezone.now()-token_obj.request_date).seconds <= OTP_VALIDITY:
        return True
    elif (timezone.now()-token_obj.request_date).seconds > OTP_VALIDITY:
        token_obj.delete()
    raise OtpFailedException("Not an valid otp")


def get_otp(**kwargs):
    if 'user' in kwargs.keys():
        phone_number = afterbuy_model.Consumer.objects.get(user = kwargs.get('user')).phone_number
    else:
        phone_number = kwargs.get('phone_number')
    otp = generate_otp(phone_number)
    save_otp(otp, **kwargs)
    return otp


def get_template(template_key):
    object = afterbuy_model.MessageTemplate.objects.get(template_key=template_key)
    return object.template


def get_date_from_string(date, fmt="%Y-%m-%dT%H:%M:%S", timezone=None):
    if timezone is None:
        timezone = get_current_timezone_name()
    date_object = datetime.strptime(date, fmt)
    date_object.replace(tzinfo=pytz.timezone(timezone))
    return date_object


def mobile_format(phone_number):
    '''
        GM store numbers in +91 format
        And when airtel pull message from customer
        or service advisor we will check that number in +91 format'''
    return '+91' + phone_number[-10:]

