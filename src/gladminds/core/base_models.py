from datetime import datetime
from django.db import models
from django.core.exceptions import ValidationError

from composite_field.base import CompositeField
from django.conf import settings
from django.utils.translation import gettext as _

from gladminds.core.managers import user_manager, coupon_manager,\
    service_desk_manager
from gladminds.core.model_helpers import PhoneField, set_plate_image_path,\
    set_plate_with_part_image_path, set_brand_product_image_path,\
    set_brand_image
from gladminds.core import constants
from gladminds.core.core_utils.utils import generate_mech_id, generate_partner_id,\
    generate_nsm_id,generate_asm_id
from gladminds.core.model_helpers import validate_image, validate_file
from gladminds.core.model_helpers import set_service_training_material_path,\
    set_mechanic_image_path,set_product_catalog_image_path,set_redemption_pod_path,\
    set_welcome_kit_pod_path
from gladminds.core.managers.mail import sent_password_reset_link,\
    send_email_activation
from gladminds.core.constants import SBOM_STATUS
from gladminds.core.managers.email_token_manager import EmailTokenManager
from django.core.validators import MinValueValidator, MaxValueValidator


try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now
STATUS_CHOICES=constants.STATUS_CHOICES

def set_user_pic_path(instance, filename):
    return '{0}/{1}/user'.format(settings.ENV,settings.BRAND)

class BaseModel(models.Model):
    '''Base model containing created date and modified date'''
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfile(BaseModel):
    '''User profile model to extend user'''
    phone_number = models.CharField(
                   max_length=15, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateTimeField(null=True, blank=True)
    
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
  
    department = models.CharField(max_length=100, null=True, blank=True)
    
    image_url = models.FileField(upload_to=set_user_pic_path,
                                  max_length=200, null=True, blank=True,
                                  validators=[validate_image])
    reset_password = models.BooleanField(default=False)
    reset_date = models.DateTimeField(null=True, blank=True)
        
    def image_tag(self):
        return u'<img src="{0}/{1}" width="200px;"/>'.format(settings.S3_BASE_URL, self.image_url)
    image_tag.short_description = 'User Image'
    image_tag.allow_tags = True

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Other'),
    )
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES,
                              blank=True, null=True)

    class Meta:
        db_table = "gm_userprofile"
        verbose_name_plural = "User Profile"
        abstract = True

    def __unicode__(self):
        return str(self.phone_number or '') + ' ' + self.user.username


class Industry(BaseModel):
    '''Stores the different industries
    a brand could belong to'''
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_industry"
        verbose_name_plural = "Industries"

    def __unicode__(self):
        return self.name


class Brand(BaseModel):
    '''Details of brands signed up'''
    name = models.CharField(max_length=250)
    image_url = models.FileField(upload_to=set_brand_image,
                              max_length=255, null=True, blank=True,
                              validators=[validate_image])
    is_active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    
    def image_tag(self):
        return u'<img src="{0}/{1}" width="200px;"/>'.format(settings.S3_BASE_URL, self.image_url)
    image_tag.short_description = 'Brand Image'
    image_tag.allow_tags = True

    class Meta:
        abstract = True
        db_table = "gm_brand"
        verbose_name_plural = "Brand Data"

    def __unicode__(self):
        return "Brand: "+self.name+" Industry: "+self.industry.name


class BrandProductCategory(BaseModel):
    '''Different category of product a brand builds'''
    name = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "gm_brandproductcategory"
        abstract = True
        verbose_name_plural = "Brand Categories"


class OTPToken(BaseModel):
    '''Stores the OTPs generated'''
    token = models.CharField(max_length=256, null=False)
    request_date = models.DateTimeField(null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_otptoken"
        verbose_name_plural = "OTPs"

    def __unicode__(self):
        return str(self.phone_number or '') + ' ' +self.token

     
class ZonalServiceManager(BaseModel):
    '''details of Zonal Service Manager'''
    zsm_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    regional_office = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        abstract = True
        db_table = "gm_zonalservicemanager"
        verbose_name_plural = "Zonal Service Managers "
    
    def __unicode__(self):
        return self.zsm_id

class CircleHead(BaseModel):
    
    class Meta:
        abstract = True
        db_table = "gm_circlehead"
        verbose_name_plural = "Circle Heads"
     
class RegionalManager(BaseModel):
    '''details of Regional Manager'''
    region = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        abstract = True
        db_table = "gm_regionalmanager"
        verbose_name_plural = "Regional Managers"

class AreaSalesManager(BaseModel):
    '''details of Area Sales Manager'''
    
    class Meta:
        abstract = True
        db_table = "gm_areasalesmanager"
        verbose_name_plural = "Area Sales Managers"
        
class AreaServiceManager(BaseModel):
    '''details of Area Service Manager'''
    asm_id = models.CharField(max_length=50, unique=True, null=False, blank=False)
    area = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        abstract = True
        db_table = "gm_areaservicemanager"
        verbose_name_plural = "Area Service Managers "
    
    def __unicode__(self):
        return self.asm_id

class Dealer(BaseModel):
    '''Details of Dealer'''
    dealer_id = models.CharField(
        max_length=25, blank=False, null=False, unique=True,
        help_text="Dealer Code must be unique")
    use_cdms = models.BooleanField(default=True)
    last_transaction_date = models.DateTimeField(null=True, blank=True)

    objects = user_manager.DealerManager()
    last_transaction_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_dealer"
        verbose_name_plural = "Dealer Data"

    def __unicode__(self):
        return self.dealer_id


class AuthorizedServiceCenter(BaseModel):
    '''Details of Authorized Service Center'''
    asc_id = models.CharField(
        max_length=25, blank=False, null=False, unique=True,
        help_text="Dealer Code must be unique")
    asc_owner = models.CharField(max_length=100, null=True, blank=True)
    asc_owner_phone = models.CharField(max_length=50, null=True, blank=True)
    asc_owner_email = models.CharField(max_length=100, null=True, blank=True)
    objects = user_manager.AuthorizedServiceCenterManager()
    last_transaction_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_authorizedservicecenter"
        verbose_name_plural = "Service Center Data"

    def __unicode__(self):
        return self.asc_id


class ServiceAdvisor(BaseModel):
    '''Details of Service Advisor'''
    service_advisor_id = models.CharField(
        max_length=15, blank=False, unique=True, null=False)
    status = models.CharField(max_length=10, blank=False, null=False)

    objects = user_manager.ServiceAdvisorManager()

    class Meta:
        abstract = True
        db_table = "gm_serviceadvisor"
        verbose_name_plural = "Service Advisor Data"

    def __unicode__(self):
        return self.service_advisor_id

'''
ProductTypeData  is linked to Brand data
For 1 Brand there can be multiple Products
'''


class ProductType(BaseModel):
    '''Details of Product Type'''
    product_type = models.CharField(max_length=255, unique=True, null=False)
    image_url = models.CharField(
                   max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    overview = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_producttype"
        verbose_name_plural = "Product Type"

    def __unicode__(self):
        return self.product_type

####################################################################

class ProductData(BaseModel):
    '''Details of Product Data'''
    product_id = models.CharField(max_length=215, unique=True)
    customer_id = models.CharField(
        max_length=215, null=True, blank=True, unique=True)
    customer_phone_number = PhoneField(null=True, blank=True)
    customer_name = models.CharField(
        max_length=215, null=True, blank=True)
    customer_city = models.CharField(
        max_length=100, null=True, blank=True)
    customer_state = models.CharField(
        max_length=100, null=True, blank=True)
    customer_pincode = models.CharField(
        max_length=15, null=True, blank=True)
    purchase_date = models.DateTimeField(null=True, blank=True)
    invoice_date = models.DateTimeField(null=True, blank=True)
    engine = models.CharField(max_length=255, null=True, blank=True, unique=True)
    veh_reg_no = models.CharField(max_length=15, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    sku_code = models.CharField(max_length=20, null=True, blank=True)
    
    class Meta:
        abstract = True
        db_table = "gm_productdata"
        verbose_name_plural = "Product Data"

    def __unicode__(self):
        return self.product_id


class CouponData(BaseModel):
    '''Details of Coupon Data'''
    unique_service_coupon = models.CharField(
        max_length=215, unique=True, null=False)
    valid_days = models.IntegerField(max_length=10, null=False)
    valid_kms = models.IntegerField(max_length=10, null=False)
    service_type = models.IntegerField(max_length=10, null=False)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1, db_index=True)
    closed_date = models.DateTimeField(null=True, blank=True)
    mark_expired_on = models.DateTimeField(null=True, blank=True)
    actual_service_date = models.DateTimeField(null=True, blank=True)
    actual_kms = models.CharField(max_length=10, null=True, blank=True)
    last_reminder_date = models.DateTimeField(null=True, blank=True)
    schedule_reminder_date = models.DateTimeField(null=True, blank=True)
    extended_date = models.DateTimeField(null=True, blank=True)
    sent_to_sap = models.BooleanField(default=False)
    credit_date = models.DateTimeField(null=True, blank=True)
    credit_note = models.CharField(max_length=50, null=True, blank=True)
    special_case = models.BooleanField(default=False)
    servicing_dealer = models.CharField(max_length=50, null=True, blank=True)

    objects = coupon_manager.CouponDataManager()

    class Meta:
        abstract = True
        db_table = "gm_coupondata"
        verbose_name_plural = "Coupon Information"

    def __unicode__(self):
        return self.unique_service_coupon

class ServiceAdvisorCouponRelationship(BaseModel):
    '''Details of SA Coupon Relationship'''

    class Meta:
        abstract = True
        db_table = "gm_serviceadvisorcouponrelationship"
        verbose_name_plural = 'Service Advisor And Coupon Relationship'

class UCNRecovery(BaseModel):
    '''Details of UCN Recovery'''
    reason = models.TextField(null=False)
    customer_id = models.CharField(max_length=215, null=True, blank=True)
    file_location = models.CharField(max_length=215, null=True, blank=True)
    unique_service_coupon = models.CharField(max_length=215,
                                            null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_ucnrecovery"
        verbose_name_plural = "UCN recovery logs"

class OldFscData(BaseModel):
    '''Details of Old Fsc Data'''
    unique_service_coupon = models.CharField(
        max_length=215, null=True)
    valid_days = models.IntegerField(max_length=10, null=True)
    valid_kms = models.IntegerField(max_length=10, null=True)
    service_type = models.IntegerField(max_length=10, null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES,
                                      default=1, db_index=True)
    closed_date = models.DateTimeField(null=True, blank=True)
    mark_expired_on = models.DateTimeField(null=True, blank=True)
    actual_service_date = models.DateTimeField(null=True, blank=True)
    actual_kms = models.CharField(max_length=10, null=True, blank=True)
    last_reminder_date = models.DateTimeField(null=True, blank=True)
    schedule_reminder_date = models.DateTimeField(null=True, blank=True)
    extended_date = models.DateTimeField(null=True, blank=True)
    sent_to_sap = models.BooleanField(default=False)
    credit_date = models.DateTimeField(null=True, blank=True)
    credit_note = models.CharField(max_length=50, null=True, blank=True)
    special_case = models.BooleanField(default=False)
    missing_field = models.CharField(max_length=50, null=True, blank=True)
    missing_value = models.CharField(max_length=50, null=True, blank=True)
    servicing_dealer = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_oldfscdata"
        verbose_name_plural = "Old Coupon Information"

class CDMSData(BaseModel):
    received_date = models.DateTimeField(null=True, blank=True)
    cdms_date = models.DateTimeField(null=True, blank=True)
    cdms_doc_number = models.CharField(max_length=25, null=True, blank=True)
    remarks = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_cdmsdata"
        verbose_name_plural = "CDMS Information"

##################################################################
####################Message Template DB Storage###################


class MessageTemplate(BaseModel):
    '''Message Template used for SMS'''
    template_key = models.CharField(max_length=255, unique=True, null=False)
    template = models.CharField(max_length=512, null=False)
    description = models.CharField(max_length=512, null=True)

    class Meta:
        abstract = True
        db_table = "gm_messagetemplate"
        verbose_name_plural = "Message Template"

    def __unicode__(self):
        return self.template_key
##################################################################
####################Message Template DB Storage###################


class EmailTemplate(BaseModel):
    '''Email Template used for email'''
    template_key = models.CharField(max_length=255, unique=True, null=False,\
                                     blank=False)
    sender = models.CharField(max_length=512, null=False)
    receiver = models.CharField(max_length=512, null=False)
    subject = models.CharField(max_length=512, null=False)
    body = models.CharField(max_length=512, null=False)
    description = models.CharField(max_length=512, null=True)

    class Meta:
        abstract = True
        db_table = "gm_emailtemplate"
        verbose_name_plural = "Email Template"

    def __unicode__(self):
        return self.template_key+"- "+ self.subject


########################## TempRegistration #########################

class ASCTempRegistration(BaseModel):
    '''Details of ASC registration'''
    name = models.CharField(max_length=255, null=False)
    password = models.CharField(max_length=255, null=False, blank=False)
    phone_number = models.CharField(max_length=15, null=False, blank=False,
                                                         unique=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(default=datetime.now)
    dealer_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_asctempregistration"
        verbose_name_plural = "ASC Save Form"

class SATempRegistration(BaseModel):
    '''Details of SA registration'''
    name = models.CharField(max_length=255, null=False)
    phone_number = models.CharField(max_length=15,
                                null=False, blank=False, unique=True)
    status = models.CharField(max_length=10, blank=False, null=False)

    class Meta:
        abstract = True
        db_table = "gm_satempregistration"
        verbose_name_plural = "SA Save Form"


class CustomerTempRegistration(BaseModel):
    '''Details of customer registration'''
    new_customer_name = models.CharField(max_length=50, null=True, blank=True)
    new_number = models.CharField(max_length=15, null=True, blank=True)
    dealer_asc_id = models.CharField(max_length=15, null=True, blank=True)
    product_purchase_date = models.DateTimeField(null=True, blank=True)
    temp_customer_id = models.CharField(max_length=50,
                                null=False, blank=False, unique=True)
    sent_to_sap = models.BooleanField(default=False)
    remarks = models.CharField(max_length=500, null=True, blank=True)
    tagged_sap_id = models.CharField(
        max_length=215, null=True, blank=True, unique=True)
    mobile_number_update_count = models.IntegerField(max_length=5, null=True, blank=True, default=0) 
    objects = user_manager.CustomerTempRegistrationManager()

    class Meta:
        abstract = True
        db_table = "gm_customertempregistration"
        verbose_name_plural = "Customer temporary info"

    def __unicode__(self):
        return self.new_customer_name

class CustomerUpdateHistory(BaseModel):
    '''Stores the updated values of registered customer'''
    updated_field = models.CharField(max_length=100)
    old_value = models.CharField(max_length=100)
    new_value = models.CharField(max_length=100)
    email_flag = models.BooleanField(default=False)

    class Meta:
        abstract = True
        db_table = "gm_customerupdatehistory"
        verbose_name_plural = "Customer temporary Update History"

    def __unicode__(self):
        return self.updated_field

class CustomerUpdateFailure(BaseModel):
    '''Stores data when phone number update exceeds the limit'''
    customer_name = models.CharField(max_length=50, null=False, blank=False)
    customer_id = models.CharField(max_length=50,
                                null=False, blank=False, unique=False)
    updated_by = models.CharField(max_length=50, null=False, blank=False)
    old_number = models.CharField(max_length=15, null=False, blank=False)
    new_number = models.CharField(max_length=15, null=False, blank=False)
    email_flag = models.BooleanField(default=False)
    
    class Meta:
        abstract = True
        db_table = "gm_customerupdatefailure"
        verbose_name_plural = 'Update Failures'
    
    def __unicode__(self):
        return self.customer_id

class EmailToken(models.Model):
    ACTIVATED = u"ALREADY_ACTIVATED"
    activation_key = models.CharField(_('activation key'), max_length=40)

    objects = EmailTokenManager()

    class Meta:
        abstract = True
        db_table = "gm_emailtoken"
        verbose_name_plural = 'email_tokens'

        def __unicode__(self):
            return u"Registration information for %s" % self.user

    def activation_key_expired(self):
        import datetime
        """
        Determine whether this ``RegistrationProfile``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired.
        Key expiration is determined by a two-step process:
        1. If the user has already activated, the key will have been
           reset to the string constant ``ACTIVATED``. Re-activating
           is not permitted, and so this method returns ``True`` in
           this case.

        2. Otherwise, the date the user signed up is incremented by
           the number of days specified in the setting
           ``ACCOUNT_ACTIVATION_DAYS`` (which should be the number of
           days after signup during which a user is allowed to
           activate their account); if the result is less than or
           equal to the current date, the key has expired and this
           method returns ``True``.
        """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or \
               (self.user.user.date_joined + expiration_date <= datetime_now())
    activation_key_expired.boolean = True

    def send_activation_email(self, reciever_email, site, trigger_mail):
        """
        Send an activation email to the user associated with this
        The activation email will make use of two templates:

        ``registration/activation_email_subject.txt``
            This template will be used for the subject line of the
            email. Because it is used as the subject line of an email,
            this template's output **must** be only a single line of
            text; output longer than one line will be forcibly joined
            into only a single line.

        ``registration/activation_email.txt``
            This template will be used for the body of the email.

        These templates will each receive the following context
        variables:

        ``activation_key``
            The activation key for the new account.

        ``expiration_days``
            The number of days remaining during which the account may
            be activated.

        ``site``
            An object representing the site on which the user
            registered; depending on whether ``django.contrib.sites``
            is installed, this may be an instance of either
            ``django.contrib.sites.models.Site`` (if the sites
            application is installed) or
            ``django.contrib.sites.models.RequestSite`` (if
            not). Consult the documentation for the Django sites
            framework for details regarding these objects' interfaces.

        """
        ctx_dict = {'activation_key': self.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site,
                    'base_url':settings.DOMAIN_BASE_URL}
        if trigger_mail == 'forgot-password':
            print('============================sent passwordddddd==================================')
            ctx_dict = {'activation_key': self.activation_key,
                    'link': settings.FORGOT_PASSWORD_LINK[settings.BRAND],
                    'base_url': settings.COUPON_URL}
            sent_password_reset_link(reciever_email, ctx_dict)
            print("==============================ctx dict===============================")
        else:
            send_email_activation(reciever_email, ctx_dict)

class UserPreference(BaseModel):
    """
    This model is used for storing user preferences
    """
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=200)

    class Meta:
        abstract = True
        db_table = "gm_userpreference"
        verbose_name_plural = "User Preferences"


class BrandPreference(UserPreference):
    '''stores the preferences of a brand'''
    class Meta:
        abstract = True
        db_table = "gm_brandpreference"
        verbose_name_plural = "Brand Preferences"


class SMSLog(BaseModel):
    '''details of the sms sent and received'''
    action = models.CharField(max_length=250)
    message = models.TextField(null=True, blank=True)
    sender = models.CharField(max_length=15)
    receiver = models.CharField(max_length=15)
    status = models.CharField(max_length=20)

    class Meta:
        abstract = True
        db_table = "gm_smslog"
        verbose_name_plural = "SMS Log"

class EmailLog(BaseModel):
    '''details of the email sent and received'''
    subject = models.CharField(max_length=250, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    sender = models.CharField(max_length=100, null=True, blank=True)
    receiver = models.TextField()
    cc = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_emaillog"
        verbose_name_plural = "Email Log"

class DataFeedLog(BaseModel):
    '''details of the feeds sent and received'''
    data_feed_id = models.AutoField(primary_key=True)
    feed_type = models.CharField(max_length=50, null=False)
    total_data_count = models.IntegerField(null=False)
    failed_data_count = models.IntegerField(null=False)
    success_data_count = models.IntegerField(null=False)
    action = models.CharField(max_length=50, null=False)
    status = models.BooleanField(null=False)
    timestamp = models.DateTimeField(default=datetime.now)
    remarks = models.CharField(max_length=2048, null=True, blank=True)
    file_location = models.CharField(max_length=215, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_datafeedlog"
        verbose_name_plural = "Feed Log"


class FeedFailureLog(BaseModel):
    '''details of all the feeds that failed'''
    feed_type = models.CharField(max_length=50, null=False)
    reason = models.CharField(max_length=2048, null=True, blank=True)
    email_flag = models.BooleanField(default=False)
    
    class Meta:
        abstract = True
        db_table = "gm_feedfailurelog"
        verbose_name_plural = "Feed failure log"

class VinSyncFeedLog(BaseModel):
    ''''details of all vins not found in gladminds db'''
    product_id = models.CharField(max_length=215, null=True, blank=True)
    dealer_asc_id = models.CharField(max_length=15, null=True, blank=True)
    status_code = models.CharField(max_length=15, null=True, blank=True)
    email_flag = models.BooleanField(default=False)
    ucn_count = models.IntegerField(max_length=5, null=True, blank=True)
    sent_to_sap = models.BooleanField(default=False)
    
    class Meta:
        abstract =True
        db_table = "gm_vinsyncfeedlog"
        verbose_name_plural = "Vin Sync Feed"
        
class AuditLog(BaseModel):
    '''details of the requests received'''
    device = models.CharField(max_length=250, null=True, blank=True)
    user_agent = models.CharField(max_length=250, null=True, blank=True)
    urls = models.CharField(max_length=250)
    access_token = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_auditlog"
        verbose_name_plural = "Audit log"

class ServiceDeskUser(BaseModel):
    '''details of Service-Desk User'''
    name = models.CharField(max_length=30, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        abstract = True
        db_table = "gm_servicedeskuser"
        verbose_name_plural = "Service Desk Users"

    def __unicode__(self):
        return self.user_profile.user.username
    
class Activity(BaseModel):
    '''details of activities done by service-desk user'''
    action = models.TextField(null=True, blank=True)
    original_value = models.CharField(max_length=512, null=True, blank=True)
    new_value = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_activity"
        verbose_name_plural = "Activity info"

class BrandDepartment(BaseModel):
    '''Details of departments under a brand'''
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        abstract = True
        db_table = "gm_branddepartment"
        verbose_name_plural = "Department Info"
    
    def __unicode__(self):
        return self.name
    
class DepartmentSubCategories(BaseModel):
    '''Details of subcategories under a department'''
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        abstract = True
        db_table = "gm_departmentsubcategories"
        verbose_name_plural = "Sub-Department Info"

    def __unicode__(self):
        return self.name
    
class Feedback(BaseModel):
    '''details of feedback received'''
    summary = models.CharField(max_length=512, null=True, blank=True)
    description = models.CharField(max_length=512, null=True, blank=False)
    status = models.CharField(max_length=12, choices=constants.FEEDBACK_STATUS)
    type = models.CharField(max_length=20, choices=constants.FEEDBACK_TYPE)
    closed_date = models.DateTimeField(null=True, blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    pending_from = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    wait_time = models.FloatField(max_length=20, null=True, blank=True, default = '0.0')
    remarks = models.CharField(max_length=512, null=True, blank=True)
    ratings = models.CharField(max_length=20, choices=constants.RATINGS)
    root_cause = models.CharField(max_length=20, choices=constants.ROOT_CAUSE)
    resolution = models.CharField(max_length=512, null=True, blank=True)
    role = models.CharField(max_length=50, null=True, blank=True)
    assign_to_reporter = models.BooleanField(default=False)
    assignee_created_date = models.DateTimeField(null=True, blank=True)
    reminder_date = models.DateTimeField(null=True, blank=True)
    reminder_flag = models.BooleanField(default=False)
    resolution_flag = models.BooleanField(default=False)
    file_location = models.CharField(max_length=215, null=True, blank=True)
    fcr = models.BooleanField(default=False)
    objects = service_desk_manager.FeedbackManager()

    class Meta:
        abstract = True
        db_table = "gm_feedback"
        verbose_name_plural = "Feedback info"
    
    def __unicode__(self):
        return self.summary

class Comment(BaseModel):
    '''details of comments given for a feedback'''
    user = models.CharField(max_length=20, null=False, blank=False)
    comment = models.CharField(max_length=100, null=True, blank=True)
    file_location = models.CharField(max_length=215, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_comment"
        verbose_name_plural = "Comment info"
        
class EpcCommentThread(BaseModel):
    '''details of comments'''
    user = models.CharField(max_length=20, null=False, blank=False)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_epccommentthread"
        verbose_name_plural = "Comments information"

class FeedbackEvent(BaseModel):
    '''details of events for a feedback'''
    class Meta:
        abstract = True
        db_table = "gm_feedbackevent"
        verbose_name_plural = "Feedback Event info"

    
class Duration(CompositeField):
    '''Sla time and unit'''
    time = models.PositiveIntegerField()
    unit = models.CharField(max_length=12, choices=constants.TIME_UNIT, verbose_name = 'unit')

class SLA(models.Model):
    '''Sla for feedback'''
    response = Duration()
    reminder = Duration()
    resolution = Duration()
        
    def get_time_in_seconds(self, time , unit):
        if unit == 'days':
            total_time = time * 86400
        elif unit == 'hrs':
            total_time = time * 3600
        else:
            total_time = time * 60
        return total_time
    
    def clean(self, *args, **kwargs):
        response_time = self.get_time_in_seconds(self.response_time, self.response_unit)
        resolution_time = self.get_time_in_seconds(self.resolution_time, self.resolution_unit)
        reminder_time = self.get_time_in_seconds(self.reminder_time, self.reminder_unit)
        
        if reminder_time > response_time and resolution_time > reminder_time:
            super(SLA, self).clean(*args, **kwargs)
        else:
            raise ValidationError("Ensure that Reminder time is greater than Response time and Resolution time is greater than Reminder time")
            
    
    class Meta:
        abstract = True
        db_table = "gm_sla"
        verbose_name_plural = "SLA info"

class ServiceType(models.Model):
    ''' Contains all the services types '''
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract =True
        db_table = "gm_servicetype"
        verbose_name_plural = "Service Types"
        
    def __unicode__(self):
        return self.name
        
class Service(models.Model):
    ''' Contains all the services provided '''
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    training_material_url = models.FileField(upload_to=set_service_training_material_path,
                                  max_length=255, null=True, blank=True,
                                  validators=[validate_file])
    
    def file_tag(self):
        return u'<h1> "{0}/{1}"</h1>'.format(settings.S3_BASE_URL, self.file_url)
    file_tag.short_description = 'Training Material'
    file_tag.allow_tags = True
    
    class Meta:
        abstract = True
        db_table = "gm_service"
        verbose_name_plural = "Services"
        
    def __unicode__(self):
        return self.name


class Constant(BaseModel):
    ''' Contains all the constants '''
    constant_name = models.CharField(max_length=50, null=True, blank=True)
    constant_value = models.CharField(max_length=10, null=True, blank=True)
        
    class Meta:
        abstract = True
        db_table = "gm_constant"
        verbose_name_plural = "Constants"
        
    def __unicode__(self):
        return self.constant_name


class DateDimension(models.Model):
    '''date dimension for reporting'''
    date_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(unique=True)
    timestamp = models.DateTimeField()
    weekend = models.CharField(max_length=10)
    day_of_week = models.CharField(max_length=10)
    month = models.CharField(max_length=10)
    month_day = models.IntegerField()
    year = models.IntegerField()
    week_starting_monday = models.CharField(max_length=2)

    class Meta:
        abstract = True
        db_table = "gm_datedimension"
    
    def __str__(self):
        return str(self.date)

class CouponFact(models.Model):
    '''coupon fact for reporting'''
    closed = models.BigIntegerField()
    inprogress = models.BigIntegerField()
    expired = models.BigIntegerField()
    unused = models.BigIntegerField()
    exceeds = models.BigIntegerField()
    data_type = models.CharField(max_length=20, default='DAILY')

    class Meta:
        abstract = True
        db_table = "gm_couponfact"


############################### CTS MODELS ###################################################

class Supervisor(BaseModel):
    ''' details of Supervisor'''
    supervisor_id = models.CharField(
        max_length=15, blank=False, unique=True, null=False)
    
    class Meta:
        abstract = True
        db_table = "gm_supervisor"
        verbose_name_plural = "Supervisors"
    
    def __unicode__(self):
        return self.supervisor_id
    
class Transporter(BaseModel):
    ''' details of Container Transporter'''
    transporter_id = models.CharField(
        max_length=15, blank=False, unique=True, null=False)
    
    class Meta:
        abstract = True
        db_table = "gm_transporter"
        verbose_name_plural = "Transporter"
    
    def __unicode__(self):
        return self.transporter_id

class ContainerIndent(BaseModel):
    ''' details of Container Indent'''
    
    indent_num = models.CharField(max_length=30, unique=True)
    no_of_containers = models.IntegerField(default=0)
    status = models.CharField(max_length=12, choices=constants.CONSIGNMENT_STATUS, default='Open')
    
    class Meta:
        abstract = True
        db_table = "gm_containerindent"
        verbose_name_plural = "Container Indent"
    
    def __unicode__(self):
        return str(self.indent_num)


class ContainerLR(BaseModel):
    ''' details of Container LR'''
    
    transaction_id = models.AutoField(primary_key=True)
    consignment_id = models.CharField(max_length=30, null=True, blank=True)
    truck_no = models.CharField(max_length=30, null=True, blank=True)
    lr_number = models.CharField(max_length=20, null=True, blank=True)
    lr_date = models.DateField(max_length=10, null=True, blank=True)
    do_num = models.CharField(max_length=30, null=True, blank=True)
    gatein_date = models.DateField(max_length=10, null=True, blank=True)
    gatein_time = models.TimeField(max_length=10, null=True, blank=True)
    seal_no = models.CharField(max_length=40, null=True, blank=True)
    container_no = models.CharField(max_length=40, null=True, blank=True)

    shippingline_id = models.CharField(max_length=50, null=True, blank=True)
    ib_dispatch_dt = models.DateField(null=True, blank=True)
    cts_created_date = models.DateField(null=True, blank=True)
    submitted_by = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=12, choices=constants.CONSIGNMENT_STATUS, default='Open')
    sent_to_sap = models.BooleanField(default=False)
    partner_name = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        abstract = True
        db_table = "gm_containerlr"
        verbose_name_plural = "Container LR"
    
    def __unicode__(self):
        return str(self.transaction_id)
    
    def save(self, *args, **kwargs):
        if not self.submitted_by:
            self.submitted_by = None
        super(ContainerLR, self).save(*args, **kwargs)


class ContainerLR_junk(BaseModel):
    ''' details of Container LR came as NULL'''
    lr_number = models.CharField(max_length=20, null=True, blank=True)
    lr_date = models.DateField(max_length=10, null=True, blank=True)
     
    class Meta:
        abstract = True
        db_table = "gm_containerlr_junk"
        verbose_name_plural = "Container LR junk"
    
class ContainerTracker(BaseModel):
    ''' details of Container Tracker'''
    
    transaction_id = models.AutoField(primary_key=True)
    zib_indent_num = models.CharField(max_length=30, null=True, blank=True)
    consignment_id = models.CharField(max_length=30, null=True, blank=True)
    truck_no = models.CharField(max_length=30, null=True, blank=True)
    lr_number = models.CharField(max_length=20, null=True, blank=True)
    lr_date = models.DateField(max_length=10, null=True, blank=True)
    do_num = models.CharField(max_length=30, null=True, blank=True)
    gatein_date = models.DateField(max_length=10, null=True, blank=True)
    gatein_time = models.TimeField(max_length=10, null=True, blank=True)
    status = models.CharField(max_length=12, choices=constants.CONSIGNMENT_STATUS, default='Open')
    seal_no = models.CharField(max_length=40, null=True, blank=True)
    container_no = models.CharField(max_length=40, null=True, blank=True)
    sent_to_sap = models.BooleanField(default=False)
    submitted_by = models.CharField(max_length=50, null=True, blank=True)

    shippingline_id = models.CharField(max_length=50, null=True, blank=True)
    ib_dispatch_dt = models.DateField(null=True, blank=True)
    cts_created_date = models.DateField(null=True, blank=True)
    no_of_containers = models.IntegerField(default=0)

    class Meta:
        abstract = True
        db_table = "gm_containertracker"
        verbose_name_plural = "Container Tracker"
    
    def __unicode__(self):
        return str(self.transaction_id)
    
    def save(self, *args, **kwargs):
        if not self.submitted_by:
            self.submitted_by = None
        super(ContainerTracker, self).save(*args, **kwargs)

#######################LOYALTY MODELS#################################

class NationalSparesManager(BaseModel):
    '''details of National Spares Manager'''
    nsm_id = models.CharField(max_length=50, unique=True, default=generate_nsm_id)
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    phone_number = PhoneField(skip_check=True, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_nationalsparesmanager"
        verbose_name_plural = "National Spares Managers"

    def __unicode__(self):
        return self.name

class AreaSparesManager(BaseModel):
    '''details of Area Spares Manager'''
    asm_id = models.CharField(max_length=50, unique=True, default=generate_asm_id)
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    phone_number = PhoneField(skip_check=True, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_areasparesmanager"
        verbose_name_plural = "Area Spares Managers"

    def __unicode__(self):
        return self.name

class Distributor(BaseModel):
    '''details of Distributor'''
    distributor_id = models.CharField(max_length=50)
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    phone_number = PhoneField(skip_check=True, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    sent_to_sap = models.BooleanField(default=False)

    class Meta:
        abstract = True
        db_table = "gm_distributor"
        verbose_name_plural = "Distributors"

    def __unicode__(self):
        return self.distributor_id + ' ' +self.name

class DistributorStaff(BaseModel):
    '''details of DistributorStaff'''
    distributor_staff_id = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        db_table = "gm_distributorstaff"
        verbose_name_plural = "Distributor Staff"

    def __unicode__(self):
        return self.distributor_staff_id

class DistributorSalesRep(BaseModel):
    '''details of DistributorSalesRep'''
    distributor_sales_id = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        db_table = "gm_distributorsalesrep"
        verbose_name_plural = "Distributor Sales Rep"

    def __unicode__(self):
        return self.distributor_sales_id


##################### RETAILER IS MODIFIED #####################################
# class Retailer(BaseModel):
#     '''details of Retailer'''
#     retailer_name = models.CharField(max_length=50)
#     retailer_town = models.CharField(max_length=50, null=True, blank=True)
#     approved = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
# 
#     class Meta:
#         abstract = True
#         db_table = "gm_retailer"
#         verbose_name_plural = "Retailers"
# 
#     def __unicode__(self):
#         return self.retailer_name

class Retailer(BaseModel):
    '''details of Retailer'''
    retailer_code = models.CharField(max_length=50)
    retailer_name = models.CharField(max_length=50)
    retailer_town = models.CharField(max_length=50, null=True, blank=True)
    #approved = models.BooleanField(default=False)# we have to uncomment it after SFA API-Test
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        db_table = "gm_retailer"
        verbose_name_plural = "Retailers"

    def __unicode__(self):
        return self.retailer_name

 
class DSRWrokAllocation(BaseModel):
    '''details of DSRWrokAllocation'''
    status = models.CharField(max_length=12, choices=constants.WORKFLOW_STATUS, default='Open')

    class Meta:
        abstract = True
        db_table = "gm_dsrworkallocation"
        verbose_name_plural = "DSR Work Allocation"

    def __unicode__(self):
        return self.retailer_name   


class Member(BaseModel):
    '''details of Member'''
    mechanic_id = models.CharField(max_length=50, unique=True, default=generate_mech_id)
    permanent_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    total_points = models.IntegerField(max_length=50, null=True, blank=True, default=0)

    first_name = models.CharField(max_length=50, null=True, blank=True)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    phone_number = PhoneField(null=True, blank=True, unique=True)
    date_of_birth = models.DateField(null=True, blank= True)

    address_line_1 = models.CharField(max_length=40, null=True, blank=True)
    address_line_2 = models.CharField(max_length=40, null=True, blank=True)
    address_line_3 = models.CharField(max_length=40, null=True, blank=True)
    address_line_4 = models.CharField(max_length=40, null=True, blank=True)
    address_line_5 = models.CharField(max_length=40, null=True, blank=True)
    address_line_6 = models.CharField(max_length=40, null=True, blank=True)

    form_number = models.IntegerField(max_length=50, null=True, blank=True)
    registered_date = models.DateTimeField(null=True, blank= True)
    shop_number = models.CharField(max_length=50, null=True, blank=True)
    shop_name = models.CharField(max_length=50, null=True, blank=True)
    shop_address = models.CharField(max_length=50, null=True, blank=True)
    locality = models.CharField(max_length=50, null=True, blank=True)
    tehsil = models.CharField(max_length=50, null=True, blank=True)
    district = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.CharField(max_length=50, null=True, blank=True)
    shop_wall_length = models.IntegerField(max_length=50, null=True, blank=True)
    shop_wall_width = models.IntegerField(max_length=50, null=True, blank=True)
    serviced_4S = models.IntegerField(max_length=50, null=True, blank=True)
    serviced_2S = models.IntegerField(max_length=50, null=True, blank=True)
    serviced_CNG_LPG = models.IntegerField(max_length=50, null=True, blank=True)
    serviced_diesel = models.IntegerField(max_length=50, null=True, blank=True)
    spare_per_month = models.IntegerField(max_length=50, null=True, blank=True)
    genuine_parts_used = models.IntegerField(max_length=50, null=True, blank=True)
    sent_to_sap = models.BooleanField(default=False)
    image_url = models.FileField(upload_to=set_mechanic_image_path,
                                  max_length=255, null=True, blank=True,
                                  validators=[validate_image])
    last_transaction_date = models.DateTimeField(null=True, blank=True)
    total_accumulation_req = models.IntegerField(max_length=50, null=True, blank=True, default=0)
    total_redemption_req = models.IntegerField(max_length=50, null=True, blank=True, default=0)
    total_accumulation_points = models.IntegerField(max_length=50, null=True, blank=True, default=0)
    total_redemption_points = models.IntegerField(max_length=50, null=True, blank=True, default=0)
    is_active = models.BooleanField(default=True)
    is_inactive = models.BooleanField(default=False)

    def image_tag(self):
        return u'<img src="{0}/{1}" width="200px;"/>'.format(settings.S3_BASE_URL, self.image_url)
    image_tag.short_description = 'Member Image'
    image_tag.allow_tags = True

    form_status = models.CharField(max_length=15, choices=constants.FORM_STATUS_CHOICES,
                              default='Incomplete')
    sent_sms = models.BooleanField(default=False)
    download_detail = models.BooleanField(default=False)

    objects = user_manager.MemberManager()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        form_status=True
        for field in self._meta.fields:
            if field.name in constants.MANDATORY_MECHANIC_FIELDS and not getattr(self, field.name):
                form_status = False

        if not form_status:
            self.form_status='Incomplete'
        else:
            self.form_status='Complete'
            
        return super(Member, self).save(force_insert=force_insert, force_update=force_update,
                              using=using, update_fields=update_fields)

    class Meta:
        abstract = True
        verbose_name_plural = "Members"
        db_table = 'gm_member'

    def __unicode__(self):
        if self.permanent_id:
            return self.permanent_id
        return self.mechanic_id

class SparePartMasterData(BaseModel):
    '''details of Spare Part'''
    part_number = models.CharField(max_length=100, unique=True)
    part_model = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=50, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    segment_type = models.CharField(max_length=50, null=True, blank=True)
    supplier = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_sparepartmasterdata"
        verbose_name_plural = "Spare Parts Master Data"

    def __unicode__(self):
        return self.part_number
    
class SparePartUPC(BaseModel):
    '''details of Spare Part UPC'''
    unique_part_code = models.CharField(max_length=50, unique=True)
    is_used = models.BooleanField(default=False)
    is_used_by_retailer = models.BooleanField(default=False)  # added for retailer
    
    objects = user_manager.SparePartUPCManager()

    class Meta:
        abstract = True
        db_table = "gm_sparepartupc"
        verbose_name_plural = "Spare Part UPC"

    def __unicode__(self):
        return self.unique_part_code

class SparePartPoint(BaseModel):
    '''details of Spare Part points'''
    points = models.IntegerField(max_length=50, null=True, blank=True)
    price = models.FloatField(max_length=50, null=True, blank=True)
    MRP = models.FloatField(max_length=50, null=True, blank=True)
    valid_from =  models.DateTimeField(null=True, blank= True)
    valid_till =  models.DateTimeField(null=True, blank= True)
    territory = models.CharField(max_length=50, null=True, blank=True)
    
    objects = user_manager.SparePartPointManager()
    
    class Meta:
        abstract = True
        db_table = "gm_sparepartpoint"
        verbose_name_plural = "Spare Part Points"

    def __unicode__(self):
        return self.territory + ":" + str(self.points)

class AccumulationRequest(BaseModel):
    '''details of Accumulation request'''
    transaction_id = models.AutoField(primary_key=True)
    points = models.IntegerField(max_length=50)
    total_points = models.IntegerField(max_length=50)
    sent_to_sap = models.BooleanField(default=False)
    is_transferred = models.BooleanField(default=False)

    class Meta:
        abstract = True
        db_table = "gm_accumulationrequest"
        verbose_name_plural = "Accumulation Requests"

    def __unicode__(self):
        return str(self.transaction_id)
    
################# ACCUMULATION ADDED FOR RETAILER ##################
class AccumulationRequestRetailer(BaseModel):
    '''details of Accumulation request'''
    transaction_id = models.AutoField(primary_key=True)
    points = models.IntegerField(max_length=50)
    total_points = models.IntegerField(max_length=50)
    sent_to_sap = models.BooleanField(default=False)
    is_transferred = models.BooleanField(default=False)

    class Meta:
        abstract = True
        db_table = "gm_accumulationrequestretailer"
        verbose_name_plural = "Accumulation Requests Retailer"

    def __unicode__(self):
        return str(self.transaction_id)
################# END #################################

class Partner(BaseModel):
    '''details of RPs and LPs'''
    partner_id = models.CharField(max_length=50, unique=True, default=generate_partner_id)
    name = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    partner_type = models.CharField(max_length=12, choices=constants.PARTNER_TYPE, null=False, blank=False)

    class Meta:
        abstract = True
        db_table = "gm_partner"
        verbose_name_plural = "Partner"

    def __unicode__(self):
        return str(self.name) + ' ' + str(self.partner_id) + '(' + str(self.partner_type) + ')'

class ProductCatalog(BaseModel):
    '''details of Product Catalog'''
    product_id = models.CharField(max_length=50, unique=True)
    points = models.IntegerField(max_length=50, null=True, blank=True)
    price = models.IntegerField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    variation = models.CharField(max_length=50, null=True, blank=True)
    brand = models.CharField(max_length=50, null=True, blank=True)
    model = models.CharField(max_length=50, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    sub_category = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    image_url = models.FileField(upload_to=set_product_catalog_image_path,
                                  max_length=255, null=True, blank=True,
                                  validators=[validate_image])
    
    def image_tag(self):
        return u'<img src="{0}/{1}" width="200px;"/>'.format(settings.S3_BASE_URL, self.image_url)
    image_tag.short_description = 'Product Image'
    image_tag.allow_tags = True

    class Meta:
        abstract = True
        db_table = "gm_productcatalog"
        verbose_name_plural = "product catalog"
        
    def __unicode__(self):
        return str(self.product_id)

class RedemptionRequest(BaseModel):
    '''details of Redemption Request For Member'''
    delivery_address = models.CharField(max_length=50, null=True, blank=True)
    transaction_id = models.AutoField(primary_key=True)
    expected_delivery_date =  models.DateTimeField(null=True, blank= True)
    status = models.CharField(max_length=12, choices=constants.REDEMPTION_STATUS, default='Open')
    packed_by = models.CharField(max_length=50, null=True, blank=True)
    tracking_id = models.CharField(max_length=50, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    refunded_points = models.BooleanField(default=False)
    due_date =  models.DateTimeField(null=True, blank= True)
    resolution_flag = models.BooleanField(default=False)
    approved_date =  models.DateTimeField(null=True, blank= True)
    shipped_date =  models.DateTimeField(null=True, blank= True)
    delivery_date =  models.DateTimeField(null=True, blank= True)
    pod_number = models.CharField(max_length=50, null=True, blank=True)
    image_url = models.FileField(upload_to=set_redemption_pod_path,
                              max_length=255, null=True, blank=True,
                              validators=[validate_image])
    sent_to_sap = models.BooleanField(default=False)
    points = models.IntegerField(max_length=50)

    
    def image_tag(self):
        return u'<img src="{0}/{1}" width="200px;"/>'.format(settings.S3_BASE_URL, self.image_url)
    image_tag.short_description = 'Proof of Delivery'
    image_tag.allow_tags = True
    
    def clean(self, *args, **kwargs):
        if self.status=='Approved' and self.refunded_points:
            if self.member.total_points<self.product.points:
                raise ValidationError("Member now does not not have sufficient points to approve the request")
#         if self.status=='Packed' and (not self.partner or self.partner.partner_type not in ['Redemption','Logistics']):
#             raise ValidationError("Please assign a partner")
#         elif self.status=='Approved' and (not self.partner or self.partner.partner_type!='Redemption'):
#             raise ValidationError("Please assign a redemption partner")
        
        super(RedemptionRequest, self).clean(*args, **kwargs)

    class Meta:
        abstract = True
        db_table = "gm_redemptionrequest"
        verbose_name_plural = "Redemption Request"
        
    def __unicode__(self):
        return str(self.transaction_id)
    
    
################### add retailer redemption##############
class RedemptionRequestRetailer(BaseModel):
    '''details of Redemption Request For Retailer'''
    delivery_address = models.CharField(max_length=50, null=True, blank=True)
    transaction_id = models.AutoField(primary_key=True)
    expected_delivery_date =  models.DateTimeField(null=True, blank= True)
    status = models.CharField(max_length=12, choices=constants.REDEMPTION_STATUS, default='Open')
    packed_by = models.CharField(max_length=50, null=True, blank=True)
    tracking_id = models.CharField(max_length=50, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    refunded_points = models.BooleanField(default=False)
    due_date =  models.DateTimeField(null=True, blank= True)
    resolution_flag = models.BooleanField(default=False)
    approved_date =  models.DateTimeField(null=True, blank= True)
    shipped_date =  models.DateTimeField(null=True, blank= True)
    delivery_date =  models.DateTimeField(null=True, blank= True)
    pod_number = models.CharField(max_length=50, null=True, blank=True)
    image_url = models.FileField(upload_to=set_redemption_pod_path,
                              max_length=255, null=True, blank=True,
                              validators=[validate_image])
    sent_to_sap = models.BooleanField(default=False)
    points = models.IntegerField(max_length=50)

    
    def image_tag(self):
        return u'<img src="{0}/{1}" width="200px;"/>'.format(settings.S3_BASE_URL, self.image_url)
    image_tag.short_description = 'Proof of Delivery'
    image_tag.allow_tags = True
    
    def clean(self, *args, **kwargs):
        if self.status=='Approved' and self.refunded_points:
            if self.retailer.total_points<self.product.points:
                raise ValidationError("Retailer now does not not have sufficient points to approve the request")
#         if self.status=='Packed' and (not self.partner or self.partner.partner_type not in ['Redemption','Logistics']):
#             raise ValidationError("Please assign a partner")
#         elif self.status=='Approved' and (not self.partner or self.partner.partner_type!='Redemption'):
#             raise ValidationError("Please assign a redemption partner")
        
        super(RedemptionRequestRetailer, self).clean(*args, **kwargs)

    class Meta:
        abstract = True
        db_table = "gm_redemptionrequestretailer"
        verbose_name_plural = "Redemption Request Retailer"
        
    def __unicode__(self):
        return str(self.transaction_id)
###################### end add retailer redemption########
    
class WelcomeKit(BaseModel):
    '''details of welcome kit'''
    delivery_address = models.CharField(max_length=50, null=True, blank=True)
    transaction_id = models.AutoField(primary_key=True)
    expected_delivery_date =  models.DateTimeField(null=True, blank= True)
    due_date =  models.DateTimeField(null=True, blank= True)
    status = models.CharField(max_length=12, choices=constants.WELCOME_KIT_STATUS, default='Open')
    packed_by = models.CharField(max_length=50, null=True, blank=True)
    tracking_id = models.CharField(max_length=50, null=True, blank=True)
    resolution_flag = models.BooleanField(default=False)
    shipped_date =  models.DateTimeField(null=True, blank= True)
    delivery_date =  models.DateTimeField(null=True, blank= True)
    pod_number = models.CharField(max_length=50, null=True, blank=True)
    image_url = models.FileField(upload_to=set_welcome_kit_pod_path,
                              max_length=255, null=True, blank=True,
                              validators=[validate_image])

    def image_tag(self):
        return u'<img src="{0}/{1}" width="200px;"/>'.format(settings.S3_BASE_URL, self.image_url)
    image_tag.short_description = 'Proof of Delivery'
    image_tag.allow_tags = True

    def clean(self, *args, **kwargs):
        if self.status!='Open' and not self.partner:
            raise ValidationError("Please assign a partner")
        else:
            super(WelcomeKit, self).clean(*args, **kwargs)

    class Meta:
        abstract = True
        db_table = "gm_welcomekit"
        verbose_name_plural = "Welcome Kit Request"
    
    def __unicode__(self):
        return str(self.transaction_id)
    
class WelcomeKitRetailer(BaseModel):
    '''details of welcome kit for Retailer'''
    delivery_address = models.CharField(max_length=50, null=True, blank=True)
    transaction_id = models.AutoField(primary_key=True)
    expected_delivery_date =  models.DateTimeField(null=True, blank= True)
    due_date =  models.DateTimeField(null=True, blank= True)
    status = models.CharField(max_length=12, choices=constants.WELCOME_KIT_STATUS, default='Open')
    packed_by = models.CharField(max_length=50, null=True, blank=True)
    tracking_id = models.CharField(max_length=50, null=True, blank=True)
    resolution_flag = models.BooleanField(default=False)
    shipped_date =  models.DateTimeField(null=True, blank= True)
    delivery_date =  models.DateTimeField(null=True, blank= True)
    pod_number = models.CharField(max_length=50, null=True, blank=True)
    image_url = models.FileField(upload_to=set_welcome_kit_pod_path,
                              max_length=255, null=True, blank=True,
                              validators=[validate_image])

    def image_tag(self):
        return u'<img src="{0}/{1}" width="200px;"/>'.format(settings.S3_BASE_URL, self.image_url)
    image_tag.short_description = 'Proof of Delivery'
    image_tag.allow_tags = True

    def clean(self, *args, **kwargs):
        if self.status!='Open' and not self.partner:
            raise ValidationError("Please assign a partner")
        else:
            super(WelcomeKitRetailer, self).clean(*args, **kwargs)

    class Meta:
        abstract = True
        db_table = "gm_welcomekitretailer"
        verbose_name_plural = "Welcome Kit Request Retailer"
    
    def __unicode__(self):
        return str(self.transaction_id)
################# end welcome kit is added for retailer ##################
    
class CommentThread(BaseModel):
    '''details of activities done by service-desk user'''
    id = models.AutoField(primary_key=True)
    message = models.TextField(null=True, blank=True)
    is_edited = models.BooleanField(default=False)

    class Meta:
        abstract = True
        db_table = "gm_commentthread"
        verbose_name_plural = "Comment Thread"
    
    def __unicode__(self):
        return str(self.id)


################# comment is added for retailer ##################
class CommentThreadRetailer(BaseModel):
    '''details of activities done by service-desk user for Retailer'''
    id = models.AutoField(primary_key=True)
    message = models.TextField(null=True, blank=True)
    is_edited = models.BooleanField(default=False)

    class Meta:
        abstract = True
        db_table = "gm_commentthreadretailer"
        verbose_name_plural = "Comment Thread Retailer"
    
    def __unicode__(self):
        return str(self.id)
######################### retailer comment end####################

class DiscrepantAccumulation(BaseModel):
    ''' details of accumulation request with discrepancy'''
    
    class Meta:
        abstract = True
        db_table = "gm_discrepantaccumulation"
        verbose_name_plural = "Discrepant Request"

class LoyaltySLA(models.Model):
    '''SLA for welcomekit and redemption request'''
    status = models.CharField(max_length=12, choices=constants.LOYALTY_SLA_STATUS)
    action = models.CharField(max_length=12, choices=constants.LOYALTY_SLA_ACTION)
    reminder = Duration()
    resolution = Duration()
    member_resolution = Duration()
    
    def get_time_in_seconds(self, time , unit):
        if unit == 'days':
            total_time = time * 86400
        elif unit == 'hrs':
            total_time = time * 3600
        else:
            total_time = time * 60
        return total_time

    def clean(self, *args, **kwargs):
        resolution_time = self.get_time_in_seconds(self.resolution_time, self.resolution_unit)        
        reminder_time = self.get_time_in_seconds(self.reminder_time, self.reminder_unit)
        if (resolution_time > reminder_time):
            super(LoyaltySLA, self).clean(*args, **kwargs)
        else:
            raise ValidationError("Resolution time is greater than Reminder time")           

    class Meta:
        abstract = True
        db_table = "gm_loyaltysla"
        verbose_name_plural = "Loyalty SLA info"
        
    def __unicode__(self):
        return str(self.status)

class Territory(BaseModel):
    '''Territories under a brand'''
    territory = models.CharField(max_length=20, unique = True)
    
    class Meta:
        abstract = True
        db_table = "gm_territory"
        verbose_name_plural = "Territory info"

    def __unicode__(self):
        return self.territory


class State(BaseModel):
    '''States under a brand'''
    state_name = models.CharField(max_length=30, unique = True)
    state_code = models.CharField(max_length=10, unique = True)
    
    class Meta:
        abstract = True
        db_table = "gm_state"
        verbose_name_plural = "State info"

    def __unicode__(self):
        return self.state_name
    
class City(BaseModel):
    '''Cities under a brand'''
    city = models.CharField(max_length=50, unique = True)
    
    class Meta:
        abstract = True
        db_table = "gm_city"
        verbose_name_plural = "City info"

    def __unicode__(self):
        return self.city

############################### EPC MODELS ###################################################

class ECORelease(BaseModel):
    ''' details of ECO release'''
    eco_number  = models.CharField(max_length=20, null=True, blank=True)
    eco_release_date = models.DateField(max_length=20, null=True, blank=True)
    eco_description = models.CharField(max_length=40, null=True, blank=True)
    action = models.CharField(max_length=20, null=True, blank=True)
    parent_part = models.CharField(max_length=20, null=True, blank=True)

    add_part = models.CharField(max_length=20, null=True, blank=True)
    add_part_qty = models.FloatField(max_length=20, null=True, blank=True)
    add_part_rev = models.CharField(max_length=20, null=True, blank=True)
    add_part_loc_code = models.CharField(max_length=90, null=True, blank=True)
    
    del_part = models.CharField(max_length=20, null=True, blank=True)
    del_part_qty = models.FloatField(max_length=20, null=True, blank=True)
    del_part_rev = models.FloatField(max_length=20, null=True, blank=True)
    del_part_loc_code = models.CharField(max_length=90, null=True, blank=True)
    
    models_applicable = models.CharField(max_length=90, null=True, blank=True)
    serviceability = models.CharField(max_length=20, null=True, blank=True)
    interchangebility = models.CharField(max_length=20, null=True, blank=True)
    reason_for_change = models.CharField(max_length=90, null=True, blank=True)
    status = models.CharField(max_length=10, choices=constants.ECO_RELEASE_STATUS, default='Open')

    class Meta:
        abstract = True
        db_table = "gm_ecorelease"
        verbose_name_plural = "ECO Release"

class ECOImplementation(BaseModel):
    ''' details of ECO Implementation'''
    change_no = models.CharField(max_length=20, null=True, blank=True)
    change_date = models.DateField(max_length=20, null=True, blank=True)
    change_time = models.TimeField(max_length=20, null=True, blank=True)
    plant = models.CharField(max_length=20, null=True, blank=True)
    action = models.CharField(max_length=20, null=True, blank=True)
    
    parent_part = models.CharField(max_length=20, null=True, blank=True)
    added_part = models.CharField(max_length=20, null=True, blank=True)
    added_part_qty = models.FloatField(max_length=20, null=True, blank=True)
    deleted_part = models.CharField(max_length=20, null=True, blank=True)
    deleted_part_qty = models.FloatField(max_length=20, null=True, blank=True)
    
    chassis_number = models.CharField(max_length=20, null=True, blank=True)
    engine_number = models.CharField(max_length=20, null=True, blank=True)
    eco_number = models.CharField(max_length=20, null=True, blank=True)
    reason_code = models.CharField(max_length=20, null=True, blank=True)
    remarks = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=10, choices=constants.ECO_IMPLEMENTATION_STATUS, default='Open')
    
    class Meta:
        abstract = True
        db_table = "gm_ecoimplementation"
        verbose_name_plural = "ECO Implementation"

class BrandVertical(BaseModel):
    '''Stores the different vertical
    a brand can have'''
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_brandvertical"
        verbose_name_plural = "Brand Vertical"
    
    def __unicode__(self):
        return self.name


class BrandProductRange(BaseModel):
    '''Different range of product a brand provides'''
    sku_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    image_url = models.FileField(upload_to=set_brand_product_image_path,
                                  max_length=255, null=True, blank=True,
                                  validators=[validate_image])
    def image_tag(self):
        return u'<img src="{0}/{1}" width="200px;"/>'.format(settings.S3_BASE_URL, self.image_url)
    image_tag.short_description = 'Brand Product Image'
    image_tag.allow_tags = True

    class Meta:
        db_table = "gm_brandproductrange"
        abstract = True
        verbose_name_plural = "Product Range"
    
    def __unicode__(self):
        return self.sku_code
    
class BOMHeader(BaseModel):
    '''Details of  Header fields BOM'''
    sku_code = models.CharField(max_length=20, null=True, blank=True)
    plant = models.CharField(max_length=10, null=True, blank=True)
    bom_type = models.CharField(max_length=10, null=True, blank=True)
    bom_number = models.CharField(max_length=10, null=True, blank=True)
    valid_from = models.DateField(null=True, blank= True)
    valid_to = models.DateField(null=True, blank= True)
    created_on = models.DateField(null=True, blank= True)
    revision_number = models.IntegerField(default=0)
    eco_number = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_bomheader"
        verbose_name_plural = "Bills of Material "
    
    def __unicode__(self):
        return self.sku_code
        
class BOMPlate(BaseModel):
    '''Details of BOM Plates'''
    plate_id = models.CharField(max_length=50, unique=True)
    plate_txt = models.CharField(max_length=200, null=True, blank=True)
    plate_image = models.FileField(upload_to=set_plate_image_path,
                                  max_length=255, null=True, blank=True,
                                  validators=[validate_image])
    plate_image_with_part = models.FileField(upload_to=set_plate_with_part_image_path,
                                  max_length=255, null=True, blank=True,
                                  validators=[validate_image])
    def plate_image_tag(self):
        return u'<img src="{0}/{1}" width="200px;"/>'.format(settings.S3_BASE_URL, self.plate_image)
    plate_image_tag.short_description = 'Plate Image'
    plate_image_tag.allow_tags = True
    
    def plate_image_with_part_tag(self):
        return u'<img src="{0}/{1}" width="200px;"/>'.format(settings.S3_BASE_URL, self.plate_image_with_part)
    plate_image_with_part_tag.short_description = 'Plate with Part Image'
    plate_image_with_part_tag.allow_tags = True

    class Meta:
        db_table = "gm_bomplate"
        abstract = True
        verbose_name_plural = "BOM Plates"
    
    def __unicode__(self):
        return self.plate_id
        
class BOMPart(BaseModel):
    '''Details of  BOM Parts'''
    timestamp = models.DateTimeField(default=datetime.now)
    
    part_number = models.CharField(max_length=20, null=True, blank=True)
    revision_number = models.CharField(max_length=10, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_bompart"
        verbose_name_plural = "BOM Parts "
        
    def __unicode__(self):
        return self.part_number
        
class BOMPlatePart(BaseModel):
    '''Details of BOM Plates and part relation'''
    quantity = models.CharField(max_length=20, null=True, blank=True)
    valid_from = models.DateField(null=True, blank= True)
    valid_to = models.DateField(null=True, blank= True)
    uom = models.CharField(max_length=100, null=True, blank=True)
    serial_number = models.CharField(max_length=20, null=True, blank=True)
    change_number = models.CharField(max_length=12, null=True, blank=True)
    change_number_to = models.CharField(max_length=12, null=True, blank=True)
    item = models.CharField(max_length=10, null=True, blank=True)    
    item_id = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "gm_bomplatepart"
        verbose_name_plural = "BOM plate Parts"
        
class VisualisationUploadHistory(BaseModel):
    '''
        Upload history which has been saved along with status of
        approved or rejected
    '''
    sku_code = models.CharField(max_length=20)
    bom_number = models.CharField(max_length=10)
    plate_id = models.CharField(max_length=50)
    eco_number = models.CharField(max_length=20, null=True)
    status = models.CharField(max_length=10, choices=constants.SAVE_PLATE_PART_STATUS, default='Pending')

    class Meta:
        abstract = True
        db_table = "gm_visualisationuploadhistory"
        verbose_name_plural = "Visualisation Upload History"
        
class BOMVisualization(BaseModel):
    '''Details of BOM Plates coordinates'''
    x_coordinate  = models.IntegerField(default=0)
    y_coordinate  = models.IntegerField(default=0)
    z_coordinate  = models.IntegerField(default=0)
    serial_number = models.IntegerField(default=0)
    part_href = models.CharField(max_length=200)
    published_date = models.DateTimeField(null=True, blank=True)
    remarks = models.CharField(max_length=500, null=True, blank=True)
    is_published = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        abstract = True
        db_table = "gm_bomvisualization"
        verbose_name_plural = "BOM Visualization"
        
class ServiceCircular(models.Model):
    '''Save the service circular created for a product'''
    product_type = models.CharField(max_length=100, null=True, blank=True)
    type_of_circular = models.CharField(max_length=50, null=True, blank=True)
    change_no = models.CharField(max_length=50, null=True, blank=True)
    new_circular = models.CharField(max_length=50, null=True, blank=True)
    buletin_no = models.CharField(max_length=50, null=True, blank=True)
    circular_date = models.DateTimeField(null=True, blank=True)
    from_circular = models.CharField(max_length=50, null=True, blank=True)
    to_circular = models.CharField(max_length=50, null=True, blank=True)
    cc_circular = models.CharField(max_length=50, null=True, blank=True)
    circular_subject = models.CharField(max_length=50, null=True, blank=True)
    part_added = models.CharField(max_length=50, null=True, blank=True)
    circular_title = models.CharField(max_length=50, null=True, blank=True)
    part_deleted = models.CharField(max_length=50, null=True, blank=True)
    part_changed = models.CharField(max_length=50, null=True, blank=True)
    model_name = models.CharField(max_length=50, null=True, blank=True)
    sku_description = models.CharField(max_length=250, null=True, blank=True)
    
    class Meta:
        abstract = True
        db_table = "gm_servicecircular"

class ManufacturingData(models.Model):
    '''Manufacturing data of a product'''
    product_id = models.CharField(max_length=100, null=True, blank=True)
    material_number = models.CharField(max_length=100, null=True, blank=True)
    plant = models.CharField(max_length=100, null=True, blank=True)
    engine = models.CharField(max_length=100, null=True, blank=True)
    vehicle_off_line_date =  models.DateField(null=True, blank= True)
    is_discrepant = models.BooleanField(default=False)
    sent_to_sap = models.BooleanField(default=False)

    class Meta:
        abstract = True
        db_table = "gm_manufacturingdata"
        
        
#####################################IB models################################################

class Country(BaseModel):
    '''States under a brand'''
    name = models.CharField(max_length=30, unique = True)
    area_code = models.CharField(max_length=10, unique = True)
    
    class Meta:
        abstract = True
        db_table = "gm_country"

    def __unicode__(self):
        return self.name

class CountryDistributor(BaseModel):
    '''Details of Main Country Dealer'''
    distributor_id = models.CharField(
        max_length=25, blank=False, null=False, unique=True)
    fleet_enable = models.BooleanField(default=False)

    class Meta:
        abstract = True
        db_table = "gm_countrydistributor"

    def __unicode__(self):
        return self.distributor_id
   
class MainCountryDealer(BaseModel):
    '''Details of Main Country Dealer'''
    dealer_id = models.CharField(
        max_length=25, blank=False, null=False, unique=True)

    class Meta:
        abstract = True
        db_table = "gm_maincountrydealer"

    def __unicode__(self):
        return self.dealer_id

class FleetRider(BaseModel):
    '''Details of riders'''
    phone_number = PhoneField()
    is_active = models.BooleanField(default=False)

    class Meta:
        abstract = True
        db_table = "gm_fleetrider"

    def __unicode__(self):
        return self.phone_number

#######################################SFAREPORTS############################



class SfaReportNames(models.Model):

    name = models.CharField(max_length=50,blank=True,null=True)

    class Meta:
        abstract=True
        db_table = "gm_sfareportnames"
        verbose_name = "Reports"

    def __unicode__(self):
        return self.name


class NsmTarget(models.Model):
  
    month = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(12)], null=True)
    year =  models.IntegerField(validators=[MinValueValidator(2014)], null=True)
    target = models.DecimalField(max_digits=65, decimal_places=0, null=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
        db_table = "gm_sfa_nsm_target"
        verbose_name = "National Spares Manager Target"


class AsmTarget(models.Model):

    month = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(12)], null=True)
    year =  models.IntegerField(validators=[MinValueValidator(2014)], null=True)
    target = models.DecimalField(max_digits=65, decimal_places=0, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        db_table = "gm_sfa_asm_target"
        verbose_name = "Area Spares Manager Target"


class DistributorTarget(models.Model):
 
    month = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(12)], null=True)
    year =  models.IntegerField(validators=[MinValueValidator(2014)], null=True)
    target = models.DecimalField(max_digits=65, decimal_places=0, null=True)
    active = models.BooleanField(default=True)
 
    class Meta:
        abstract = True
        db_table = "gm_sfa_distributor_target"
        verbose_name = "Distributor Target"


class DsrTarget(models.Model):

    month = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(12)], null=True)
    year =  models.IntegerField(validators=[MinValueValidator(2014)], null=True)
    target = models.DecimalField(max_digits=65, decimal_places=0, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        db_table = "gm_sfa_dsr_target"
        verbose_name = "DSR Target"

class RetailerTarget(models.Model):

    month = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(12)], null=True)
    year =  models.IntegerField(validators=[MinValueValidator(2014)], null=True)
    target = models.DecimalField(max_digits=65, decimal_places=0, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        db_table = "gm_sfa_retailer_target"
        verbose_name = "Retailer Target"

################################SFA HIGHLIGHTS################################
class SfaHighlights(models.Model):

    name = models.CharField(max_length=50,blank=True,null=True)

    class Meta:
        abstract=True
        db_table = "gm_sfahighlights"
        verbose_name = "Highlights"

    def __unicode__(self):
        return self.name


class NsmHighlights(models.Model):

    month = models.DateTimeField(null=True,blank=True)
    year = models.DateTimeField(null=True,blank=True)

    class Meta:
        abstract = True
        db_table = "gm_sfa_nsm_highlights"
        verbose_name = "National Spares Manager Highlight"


class AsmHighlights(models.Model):

    month = models.DateTimeField(null=True,blank=True)
    year = models.DateTimeField(null=True,blank=True)

    class Meta:
        abstract = True
        db_table = "gm_sfa_asm_highlights"
        verbose_name = "Area Spares Manager Highlight"



class DistributorHighlights(models.Model):

    month = models.DateTimeField(null=True,blank=True)
    year = models.DateTimeField(null=True,blank=True)

    class Meta:
        abstract = True
        db_table = "gm_sfa_distributor_highlights"
        verbose_name = "Distributor Highlight"

class DsrHighlights(models.Model):

    month = models.DateTimeField(null=True,blank=True)
    year = models.DateTimeField(null=True,blank=True)

    class Meta:
        abstract = True
        db_table = "gm_sfa_dsr_highlights"
        verbose_name = "DistributorSalesRep Highlight"


class RetailerHighlights(models.Model):

    
    month = models.DateTimeField(null=True,blank=True)
    year = models.DateTimeField(null=True,blank=True)

    class Meta:
        abstract = True
        db_table = "gm_sfa_retailer_highlights"
        verbose_name = "Retailer Highlight"



def generate_asm_reports(request):
    #Get the asm targets
        pass
    
################################MECHANEED MODELS###############   

class Agency(BaseModel):
    '''details of Agency'''
    
    class Meta:
        abstract = True
        db_table = "md_agency"


class QualityCheck(BaseModel):
    '''details of QualityCheck'''

    class Meta:
        abstract = True
        db_table = "md_qualitycheck"


class FieldInterviewerSupervisor(BaseModel):
    '''details of FieldInterviewerSupervisor'''

    class Meta:
        abstract = True
        db_table = "md_fieldinterviewersupervisor"


class FieldInterviewer(BaseModel):
    '''details of FieldInterviewer'''

    class Meta:
        abstract = True
        db_table = "md_fieldinterviewer"

