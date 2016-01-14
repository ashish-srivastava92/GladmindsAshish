'''
Helper class which contains custom input fields
'''
import re

from django.utils.translation import gettext as _
from django.db import models
from django.core.validators import RegexValidator
from django.forms.widgets import TextInput
from django.forms import fields
from django.core.exceptions import ValidationError
from django.conf import settings


phone_re = re.compile(r'^\+?1?\d{9,15}$')
validate_phone = RegexValidator(phone_re, _("Phone number must be entered in the format: '+919999999999'. Up to 15 digits allowed."), 'invalid')

def format_phone_number(phone_number):
    '''
    This is used to format phone
    '''
    phone_number = phone_number.strip()
    if phone_number.startswith('+91'):
        phone_number = phone_number[3:]
    numbers = re.compile('\d+(?:\d+)?')
    phone_number = ''.join(numbers.findall(phone_number))
    if len(phone_number) > 0:
        phone_number = '+91' + phone_number
    return phone_number


class PhoneInput(TextInput):
    input_type = 'phone'


class PhoneNoField(fields.CharField):
    widget = PhoneInput

    def clean(self, value):
        value = self.to_python(value).strip()
        value = format_phone_number(value)
        return super(PhoneNoField, self).clean(value)


class PhoneField(models.CharField):
    description = _("Phone Field")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 15)
        if 'skip_check' in kwargs:
            kwargs.pop('skip_check')
        else:
            self.default_validators = [validate_phone]
        models.CharField.__init__(self, *args, **kwargs)

    def formfield(self, **kwargs):
        # As with CharField, this will cause email validation to be performed
        # twice.
        defaults = {
            'form_class': PhoneNoField,
        }
        defaults.update(kwargs)
        return super(PhoneField, self).formfield(**defaults)


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([
        (
            [PhoneField],
            [],
            {},
        ),
    ], ["gladminds\.core\.model_helpers\.PhoneField"])
except ImportError:
    pass

from south.management.commands import convert_to_south
def validate_image(fieldfile_obj):
        if not hasattr(fieldfile_obj.file, 'content_type'):
            return
        filesize = fieldfile_obj.file.size
        content = fieldfile_obj.file.content_type
        content_type = content.split('/')[1]
        if content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise ValidationError("Only these image types are allowed %s" % ','.join(settings.ALLOWED_IMAGE_TYPES))

        megabyte_limit = settings.MAX_UPLOAD_IMAGE_SIZE
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError("Image size cannot exceed %sMB" % str(megabyte_limit))

def validate_file(fieldfile_obj):
        if not hasattr(fieldfile_obj.file, 'content_type'):
            return
        filesize = fieldfile_obj.file.size
        content = fieldfile_obj.file.content_type
        content_type = content.split('/')[1]
        if content_type not in settings.ALLOWED_FILE_TYPES.values():
            raise ValidationError("Only these file types are allowed %s" % ','.join(settings.ALLOWED_FILE_TYPES.keys()))

        megabyte_limit = settings.MAX_UPLOAD_FILE_SIZE
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError("File size cannot exceed %sMB" % str(megabyte_limit))


def create_upload_path(folder, instance, filename):
    
    brand_path =  getattr(instance, '_state').__dict__['db']
    return u'{0}/{1}/{2}/{3}'.format(settings.ENV,brand_path, folder, filename)


def set_service_training_material_path(instance,filename):
    return create_upload_path('training_material', instance, filename)

def set_mechanic_image_path(instance,filename):
    return create_upload_path('mechanics', instance, filename)

def set_retailer_image_path(instance,filename):
    return create_upload_path('retailer', instance, filename)

def set_product_catalog_image_path(instance,filename):
    return create_upload_path('redeem_product', instance, filename)

def set_redemption_pod_path(instance,filename):
    return create_upload_path('redemption', instance, filename)

def set_welcome_kit_pod_path(instance,filename):
    return create_upload_path('welcome', instance, filename)

def set_plate_image_path(instance,filename):
    return create_upload_path('plates', instance, filename)

def set_plate_with_part_image_path(instance,filename):
    return create_upload_path('plates_with_part', instance, filename)

def set_brand_product_image_path(instance,filename):
    return create_upload_path('brand_product', instance, filename)

def set_afterbuy_consumer_image(instance, filename):
    return create_upload_path('afterbuy_consumer', instance, filename)

def set_afterbuy_user_product_image(instance, filename):
    return create_upload_path('afterbuy_user_product', instance, filename)

def set_brand_image(instance, filename):
    return create_upload_path('brand_image', instance, filename)