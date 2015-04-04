from django.db import models
from django.contrib.auth.models import User
from gladminds.core import base_models, constants
from gladminds.core.auth_helper import GmApps
from django.conf import settings
from gladminds.core.model_helpers import validate_image, validate_file
 
_APP_NAME ='core'
 
 
class BrandProductCategory(base_models.BrandProductCategory):
    class Meta(base_models.BrandProductCategory.Meta):
        app_label = _APP_NAME


class UserProfile(base_models.UserProfile):
    user = models.OneToOneField(User, primary_key=True,
                                        related_name='core_users')
    
    class Meta(base_models.UserProfile.Meta):
        app_label = _APP_NAME


class Dealer(base_models.Dealer):
    user = models.OneToOneField(UserProfile, primary_key=True,
                                related_name='core_registered_dealer')

    class Meta(base_models.Dealer.Meta):
        app_label = _APP_NAME

class ZonalServiceManager(base_models.ZonalServiceManager):
    '''details of Zonal Service Manager'''
    user = models.ForeignKey(UserProfile, null=True, blank=True)
    
    class Meta(base_models.ZonalServiceManager.Meta):
        app_label = _APP_NAME 


class AreaServiceManager(base_models.AreaServiceManager):
    '''details of Area Service Manager'''
    user = models.ForeignKey(UserProfile, null=True, blank=True)
    zsm = models.ForeignKey(ZonalServiceManager, null=True, blank=True)
    
    class Meta(base_models.AreaServiceManager.Meta):
        app_label = _APP_NAME 


class AuthorizedServiceCenter(base_models.AuthorizedServiceCenter):
    user = models.OneToOneField(UserProfile, primary_key=True,
                                related_name='core_registered_asc')
    dealer = models.ForeignKey(Dealer, null=True, blank=True)
    asm = models.ForeignKey(AreaServiceManager, null=True, blank=True)
    

    class Meta(base_models.AuthorizedServiceCenter.Meta):
        app_label = _APP_NAME


class ServiceAdvisor(base_models.ServiceAdvisor):
    user = models.OneToOneField(UserProfile, primary_key=True,
                            related_name='core_service_advisor')
    dealer = models.ForeignKey(Dealer, null=True, blank=True)
    asc = models.ForeignKey(AuthorizedServiceCenter, null=True, blank=True)

    class Meta(base_models.ServiceAdvisor.Meta):
        app_label = _APP_NAME


class BrandDepartment(base_models.BrandDepartment):
    
    class Meta(base_models.BrandDepartment.Meta):
        app_label = _APP_NAME


class DepartmentSubCategories(base_models.DepartmentSubCategories):
    department = models.ForeignKey(BrandDepartment, related_name="department_sub_categories", null=True, blank=True)
    
    class Meta(base_models.DepartmentSubCategories.Meta):
        app_label = _APP_NAME


class ServiceDeskUser(base_models.ServiceDeskUser):
    user_profile = models.ForeignKey(UserProfile, null=True, blank=True)
    sub_department = models.ForeignKey(DepartmentSubCategories, related_name="sub_department_user", null=True, blank=True)
    
    class Meta(base_models.ServiceDeskUser.Meta):
        app_label = _APP_NAME


class Feedback(base_models.Feedback):
    priority = models.CharField(max_length=12, choices=constants.DEMO_PRIORITY, default='P3')
    reporter = models.ForeignKey(ServiceDeskUser, null=True, blank=True, related_name='core_feedback_reporter')
    assignee = models.ForeignKey(ServiceDeskUser, null=True, blank=True, related_name='core_feedback_assignee')
    previous_assignee = models.ForeignKey(ServiceDeskUser, null=True, blank=True, related_name='core_previous_assignee')
    sub_department = models.ForeignKey(DepartmentSubCategories,null=True, blank=True) 
    
    class Meta(base_models.Feedback.Meta):
        app_label = _APP_NAME


class Activity(base_models.Activity):
    feedback = models.ForeignKey(Feedback, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, related_name="core_activity_users")
    
    class Meta(base_models.Activity.Meta):
        app_label = _APP_NAME


class Comment(base_models.Comment):
    feedback_object = models.ForeignKey(Feedback,null=True, blank=True)

    class Meta(base_models.Comment.Meta):
        app_label = _APP_NAME


class FeedbackEvent(base_models.FeedbackEvent):
    feedback = models.ForeignKey(Feedback, null=True, blank=True)
    user = models.ForeignKey(ServiceDeskUser, null=True, blank=True)
    activity = models.ForeignKey(Activity, null=True, blank=True)
     
    class Meta(base_models.FeedbackEvent.Meta):
        app_label = _APP_NAME


class ProductType(base_models.ProductType):
    brand_product_category = models.ForeignKey(
            BrandProductCategory, null=True, blank=True, related_name='core_product_type')

    class Meta(base_models.ProductType.Meta):
        app_label = _APP_NAME


class ProductData(base_models.ProductData):
    product_type = models.ForeignKey(ProductType, null=True, blank=True)
    dealer_id = models.ForeignKey(Dealer, null=True, blank=True)

    class Meta(base_models.ProductData.Meta):
        app_label = _APP_NAME


class CouponData(base_models.CouponData):
    product = models.ForeignKey(ProductData, null=False, editable=False)
    service_advisor = models.ForeignKey(ServiceAdvisor, null=True, blank=True)

    class Meta(base_models.CouponData.Meta):
        app_label = _APP_NAME


class ServiceAdvisorCouponRelationship(base_models.ServiceAdvisorCouponRelationship):
    unique_service_coupon = models.ForeignKey(CouponData, null=False)
    service_advisor = models.ForeignKey(ServiceAdvisor, null=False)

    class Meta(base_models.ServiceAdvisorCouponRelationship.Meta):
        app_label = _APP_NAME


class UCNRecovery(base_models.UCNRecovery):
    user = models.ForeignKey(UserProfile, related_name='core_ucn_recovery')

    class Meta(base_models.UCNRecovery.Meta):
        app_label = _APP_NAME


class OldFscData(base_models.OldFscData):
    product = models.ForeignKey(ProductData, null=True, blank=True)

    class Meta(base_models.OldFscData.Meta):
        app_label = _APP_NAME

class CDMSData(base_models.CDMSData):
    unique_service_coupon = models.ForeignKey(CouponData, null=True, editable=False)

    class Meta(base_models.CDMSData.Meta):
        app_label = _APP_NAME

class OTPToken(base_models.OTPToken):
    user = models.ForeignKey(UserProfile, null=True, blank=True, related_name='core_otp_token')

    class Meta(base_models.OTPToken.Meta):
        app_label = _APP_NAME


class MessageTemplate(base_models.MessageTemplate):

    class Meta(base_models.MessageTemplate.Meta):
        app_label = _APP_NAME


class EmailTemplate(base_models.EmailTemplate):

    class Meta(base_models.EmailTemplate.Meta):
        app_label = _APP_NAME


class ASCTempRegistration(base_models.ASCTempRegistration):

    class Meta(base_models.ASCTempRegistration.Meta):
        app_label = _APP_NAME


class SATempRegistration(base_models.SATempRegistration):

    class Meta(base_models.SATempRegistration.Meta):
        app_label = _APP_NAME


class CustomerTempRegistration(base_models.CustomerTempRegistration):
    product_data = models.ForeignKey(ProductData, null=True, blank=True)

    class Meta(base_models.CustomerTempRegistration.Meta):
        app_label = _APP_NAME

class CustomerUpdateFailure(base_models.CustomerUpdateFailure):
    '''stores data when phone number update exceeds the limit'''
    product_id = models.ForeignKey(ProductData, null=False, blank=False)
    
    class Meta(base_models.CustomerUpdateFailure.Meta):
        app_label = _APP_NAME
        
class CustomerUpdateHistory(base_models.CustomerUpdateHistory):
    '''Stores the updated values of registered customer'''
    temp_customer = models.ForeignKey(CustomerTempRegistration)

    class Meta(base_models.CustomerUpdateHistory.Meta):
        app_label = _APP_NAME


class UserPreference(base_models.UserPreference):
    user = models.ForeignKey(UserProfile)

    class Meta(base_models.UserPreference.Meta):
        app_label = _APP_NAME
        unique_together = ("user", "key")


class SMSLog(base_models.SMSLog):

    class Meta(base_models.SMSLog.Meta):
        app_label = _APP_NAME


class EmailLog(base_models.EmailLog):

    class Meta(base_models.EmailLog.Meta):
        app_label = _APP_NAME


class DataFeedLog(base_models.DataFeedLog):

    class Meta(base_models.DataFeedLog.Meta):
        app_label = _APP_NAME


class FeedFailureLog(base_models.FeedFailureLog):

    class Meta(base_models.FeedFailureLog.Meta):
        app_label = _APP_NAME


class VinSyncFeedLog(base_models.VinSyncFeedLog):

    class Meta(base_models.VinSyncFeedLog.Meta):
        app_label = _APP_NAME


class AuditLog(base_models.AuditLog):
    user = models.ForeignKey(UserProfile)

    class Meta(base_models.AuditLog.Meta):
        app_label = _APP_NAME


class SLA(base_models.SLA):
    priority = models.CharField(max_length=12, choices=constants.DEMO_PRIORITY, unique=True)
    
    class Meta(base_models.SLA.Meta):
        app_label = _APP_NAME

class ServiceType(base_models.ServiceType):
    
    class Meta(base_models.ServiceType.Meta):
        app_label = _APP_NAME
    

class Service(base_models.Service):
    service_type = models.ForeignKey(ServiceType)

    class Meta(base_models.Service.Meta):
        app_label = _APP_NAME


class Constant(base_models.Constant):
    ''' contains all the constants'''
    
    class Meta(base_models.Constant.Meta):
        app_label = _APP_NAME
        
class BOMItem(base_models.BOMItem):
    '''Detaills of  Service Billing of Material'''
    class Meta(base_models.BOMItem.Meta):
        app_label = _APP_NAME

class BOMHeader(base_models.BOMHeader):
    '''Detaills of Header BOM'''
    class Meta(base_models.BOMHeader.Meta):
        app_label = _APP_NAME

class ECORelease(base_models.ECORelease):
    '''Detaills of ECO Release'''
    class Meta(base_models.ECORelease.Meta):
        app_label = _APP_NAME

#######################LOYALTY TABLES#################################
class Territory(base_models.Territory):
    '''List of territories'''
    
    class Meta(base_models.Territory.Meta):
        app_label = _APP_NAME

class State(base_models.State):
    ''' List of states mapped to territory'''
    territory = models.ForeignKey(Territory, null=True, blank=True)
 
    class Meta(base_models.State.Meta):
        app_label = _APP_NAME

class City(base_models.City):
    ''' List of cities mapped to states'''
    state = models.ForeignKey(State, null=True, blank=True)    
   
    class Meta(base_models.City.Meta):
        app_label = _APP_NAME

class NationalSparesManager(base_models.NationalSparesManager):
    '''details of National Spares Manager'''
    user = models.ForeignKey(UserProfile, null=True, blank=True)
    territory = models.ManyToManyField(Territory)

    class Meta(base_models.NationalSparesManager.Meta):
        app_label = _APP_NAME


class AreaSparesManager(base_models.AreaSparesManager):
    '''details of Area Spares Manager'''
    user = models.ForeignKey(UserProfile, null=True, blank=True)
    state = models.ManyToManyField(State)
    nsm = models.ForeignKey(NationalSparesManager, null=True, blank=True)

    class Meta(base_models.AreaSparesManager.Meta):
        app_label = _APP_NAME


class Distributor(base_models.Distributor):
    '''details of Distributor'''
    user = models.ForeignKey(UserProfile, null=True, blank=True)
    asm = models.ForeignKey(AreaSparesManager, null=True, blank=True)
    state = models.ForeignKey(State, null=True, blank=True)
    
    class Meta(base_models.Distributor.Meta):
        app_label = _APP_NAME


class Retailer(base_models.Retailer):
    '''details of retailer'''

    class Meta(base_models.Retailer.Meta):
        app_label = _APP_NAME

class Member(base_models.Member):
    '''details of Member'''
    registered_by_distributor = models.ForeignKey(Distributor, null=True, blank=True)
    preferred_retailer = models.ForeignKey(Retailer, null=True, blank=True)
    state = models.ForeignKey(State)


    class Meta(base_models.Member.Meta):
        app_label = _APP_NAME

class SparePartMasterData(base_models.SparePartMasterData):
    '''details of Spare Part'''
    product_type = models.ForeignKey(ProductType, null=True, blank=True)

    class Meta(base_models.SparePartMasterData.Meta):
        app_label = _APP_NAME


class SparePartUPC(base_models.SparePartUPC):
    '''details of Spare Part UPC'''
    part_number = models.ForeignKey(SparePartMasterData)

    class Meta(base_models.SparePartUPC.Meta):
        app_label = _APP_NAME

class SparePartPoint(base_models.SparePartPoint):
    '''details of Spare Part points'''
    part_number = models.ForeignKey(SparePartMasterData)

    class Meta(base_models.SparePartPoint.Meta):
        app_label = _APP_NAME


class AccumulationRequest(base_models.AccumulationRequest):
    '''details of Accumulation request'''
    member = models.ForeignKey(Member)
    upcs = models.ManyToManyField(SparePartUPC)
    asm = models.ForeignKey(AreaSparesManager, null=True, blank=True)

    class Meta(base_models.AccumulationRequest.Meta):
        app_label = _APP_NAME

class Partner(base_models.Partner):
    '''details of RPs and LPs'''
    user = models.ForeignKey(UserProfile, null=True, blank=True)

    class Meta(base_models.Partner.Meta):
        app_label = _APP_NAME

class ProductCatalog(base_models.ProductCatalog):
    '''details of Product Catalog'''
    partner = models.ForeignKey(Partner, null=True, blank=True)

    class Meta(base_models.ProductCatalog.Meta):
        app_label = _APP_NAME

class RedemptionRequest(base_models.RedemptionRequest):
    '''details of Redemption Request'''
    product = models.ForeignKey(ProductCatalog)
    member = models.ForeignKey(Member)
    partner = models.ForeignKey(Partner, null=True, blank=True)

    class Meta(base_models.RedemptionRequest.Meta):
        app_label = _APP_NAME

class WelcomeKit(base_models.WelcomeKit):
    '''details of welcome kit'''
    member = models.ForeignKey(Member)
    partner = models.ForeignKey(Partner, null=True, blank=True)

    class Meta(base_models.WelcomeKit.Meta):
        app_label = _APP_NAME

class CommentThread(base_models.CommentThread):
    '''details of activities done by service-desk user'''
    welcome_kit = models.ForeignKey(WelcomeKit, null=True, blank=True)
    redemption = models.ForeignKey(RedemptionRequest, null=True, blank=True)
    user = models.ForeignKey(User, related_name="core_comments_user")

    class Meta(base_models.CommentThread.Meta):
        app_label = _APP_NAME

class DateDimension(base_models.DateDimension):
    '''
    Date dimension table
    '''
    class Meta(base_models.DateDimension.Meta):
        app_label = _APP_NAME


class CouponFact(base_models.CouponFact):
    '''Coupon Fact Table for reporting'''
    date = models.ForeignKey(DateDimension)

    class Meta(base_models.CouponFact.Meta):
        app_label = _APP_NAME
        unique_together = ("date", "data_type")
        
class LoyaltySLA(base_models.LoyaltySLA):

    class Meta(base_models.LoyaltySLA.Meta):
        app_label = _APP_NAME
        unique_together = ("status", "action")

class DiscrepantAccumulation(base_models.DiscrepantAccumulation):
    upc = models.ForeignKey(SparePartUPC)
    new_member = models.ForeignKey(Member)
    accumulation_request = models.ForeignKey(AccumulationRequest)
     
    class Meta(base_models.DiscrepantAccumulation.Meta):
        app_label = _APP_NAME