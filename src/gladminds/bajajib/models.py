from django.db import models
from django.contrib.auth.models import User
from gladminds.core import base_models, constants
from gladminds.core.auth_helper import GmApps
import datetime
 
_APP_NAME = GmApps.BAJAJIB
 
try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now
 
class BrandProductCategory(base_models.BrandProductCategory):
    class Meta(base_models.BrandProductCategory.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Brand Categories"
 
 
class UserProfile(base_models.UserProfile):
    user = models.OneToOneField(User, primary_key=True,
                                        related_name='bajajib_users')
     
    class Meta(base_models.UserProfile.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Brand Users"

class Country(base_models.Country):
     
    class Meta(base_models.Country.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Country"

class CountryDistributor(base_models.CountryDistributor):
    user = models.OneToOneField(UserProfile, primary_key=True,
                                related_name='bajajib_registered_country_distributor')
    country = models.ForeignKey(Country)
     
    class Meta(base_models.CountryDistributor.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Country Distributor"

class MainCountryDealer(base_models.MainCountryDealer):
    user = models.OneToOneField(UserProfile, primary_key=True,
                                related_name='bajajib_registered_country_dealer')
    country = models.ForeignKey(Country)
     
    class Meta(base_models.MainCountryDealer.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Main Country Dealer"

class Dealer(base_models.Dealer):
    user = models.OneToOneField(UserProfile, primary_key=True,
                                related_name='bajajib_registered_dealer')
    country = models.ForeignKey(Country)
 
    class Meta(base_models.Dealer.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Dealer Data"
 
class ServiceAdvisor(base_models.ServiceAdvisor):
    user = models.OneToOneField(UserProfile, primary_key=True,
                            related_name='bajajib_service_advisor')
    dealer = models.ForeignKey(Dealer, null=True, blank=True)
 
    class Meta(base_models.ServiceAdvisor.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Service Advisor Data"
 
class ProductType(base_models.ProductType):
    brand_product_category = models.ForeignKey(
            BrandProductCategory, null=True, blank=True, related_name='bajajib_product_type')
 
    class Meta(base_models.ProductType.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Product Type"
 
 
class ProductData(base_models.ProductData):
    product_type = models.ForeignKey(ProductType, null=True, blank=True)
    country_distributor = models.ForeignKey(CountryDistributor)
    main_country_dealer = models.ForeignKey(MainCountryDealer, null=True, blank=True)
    dealer = models.ForeignKey(Dealer, null=True, blank=True)
    country_sku_code = models.CharField(max_length=20, null=True, blank=True)
    registration_number = models.CharField(max_length=10, null=True, blank=True)
 
    class Meta(base_models.ProductData.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Product Data"

class FleetRider(base_models.FleetRider):
    product = models.ForeignKey(ProductData)
 
    class Meta(base_models.FleetRider.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Fleet Rider"
 
 
class CouponData(base_models.CouponData):
    product = models.ForeignKey(ProductData, null=False, editable=False)
    service_advisor = models.ForeignKey(ServiceAdvisor, null=True, blank=True)
 
    class Meta(base_models.CouponData.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Coupon Information"
 
 
class ServiceAdvisorCouponRelationship(base_models.ServiceAdvisorCouponRelationship):
    unique_service_coupon = models.ForeignKey(CouponData, null=False)
    service_advisor = models.ForeignKey(ServiceAdvisor, null=False)
 
    class Meta(base_models.ServiceAdvisorCouponRelationship.Meta):
        app_label = _APP_NAME
        verbose_name_plural = 'Service Advisor And Coupon Relationship'
 
 
class UCNRecovery(base_models.UCNRecovery):
    user = models.ForeignKey(UserProfile, related_name='bajajib_ucn_recovery')
 
    class Meta(base_models.UCNRecovery.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "UCN recovery logs"
 
class OTPToken(base_models.OTPToken):
    user = models.ForeignKey(UserProfile, null=True, blank=True, related_name='bajajib_otp_token')
 
    class Meta(base_models.OTPToken.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "OTPs"
 
 
class MessageTemplate(base_models.MessageTemplate):
    country = models.ForeignKey(Country, null=True, blank=True)
 
    class Meta(base_models.MessageTemplate.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Message Template"
 
 
class EmailTemplate(base_models.EmailTemplate):
    country = models.ForeignKey(Country, null=True, blank=True)
 
    class Meta(base_models.EmailTemplate.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Email Template"
 
class SMSLog(base_models.SMSLog):
    country = models.ForeignKey(Country, null=True, blank=True)
 
    class Meta(base_models.SMSLog.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "SMS Log"
 
 
class EmailLog(base_models.EmailLog):
    country = models.ForeignKey(Country, null=True, blank=True)
 
    class Meta(base_models.EmailLog.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Email Log"
 
 
class DataFeedLog(base_models.DataFeedLog):
    country = models.ForeignKey(Country, null=True, blank=True)
 
    class Meta(base_models.DataFeedLog.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Feed Log"
 
 
class FeedFailureLog(base_models.FeedFailureLog):
    country = models.ForeignKey(Country, null=True, blank=True)
 
    class Meta(base_models.FeedFailureLog.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Feed Failure Log"
 
 
class VinSyncFeedLog(base_models.VinSyncFeedLog):
    country = models.ForeignKey(Country, null=True, blank=True)

    class Meta(base_models.VinSyncFeedLog.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Vin Sycn Feed"

class Constant(base_models.Constant):
    ''' contains all the constants'''
    country = models.ForeignKey(Country, null=True, blank=True)

    class Meta(base_models.Constant.Meta):
        app_label = _APP_NAME

class CustomerUpdateHistory(base_models.CustomerUpdateHistory):
    product = models.ForeignKey(ProductData)

    class Meta(base_models.CustomerUpdateHistory.Meta):
        app_label = _APP_NAME
      
      
'''Service desk for Uganda is added here'''

class ServiceType(base_models.ServiceType):
    class Meta(base_models.ServiceType.Meta):
        app_label = _APP_NAME

class Service(base_models.Service):
    service_type = models.ForeignKey(ServiceType)

    class Meta(base_models.Service.Meta):
        app_label = _APP_NAME

class ServiceDeskUser(base_models.ServiceDeskUser):
    user_profile = models.ForeignKey(UserProfile, null=True, blank=True)

    class Meta(base_models.ServiceDeskUser.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Service Desk Users"

class BrandDepartment(base_models.BrandDepartment):
    
    class Meta(base_models.BrandDepartment.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Brand Department"

class DepartmentSubCategories(base_models.DepartmentSubCategories):
    department = models.ForeignKey(BrandDepartment, null=True, blank=True)
    
    class Meta(base_models.DepartmentSubCategories.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Department Sub-categories"
        
class Feedback(base_models.Feedback):
    priority = models.CharField(max_length=12, choices=constants.PRIORITY, default='Low')
    reporter = models.ForeignKey(ServiceDeskUser, null=True, blank=True, related_name='bajajib_feedback_reporter')
    assignee = models.ForeignKey(ServiceDeskUser, null=True, blank=True, related_name='bajajib_feedback_assignee')
    previous_assignee = models.ForeignKey(ServiceDeskUser, null=True, blank=True, related_name='bajajib_previous_assignee')
    sub_department = models.ForeignKey(DepartmentSubCategories,null=True, blank=True) 
    
    class Meta(base_models.Feedback.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "user feedback"


class Activity(base_models.Activity):
    feedback = models.ForeignKey(Feedback, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, related_name="bajajib_activity_users")
    
    class Meta(base_models.Activity.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "user activity info"


class Comment(base_models.Comment):
    feedback_object = models.ForeignKey(Feedback,null=True, blank=True)

    class Meta(base_models.Comment.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "user comments"


class FeedbackEvent(base_models.FeedbackEvent):
    feedback = models.ForeignKey(Feedback, null=True, blank=True)
    user = models.ForeignKey(ServiceDeskUser, null=True, blank=True)
    activity = models.ForeignKey(Activity, null=True, blank=True)
     
    class Meta(base_models.FeedbackEvent.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "user feedback event "