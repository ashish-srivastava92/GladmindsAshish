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
    country = models.ForeignKey(Country, null=True)
    # nex line is added after asking from Naveen that relation is mandatory B/W users
    main_country_dealer = models.ForeignKey(MainCountryDealer, null=True, blank=True)
 
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
