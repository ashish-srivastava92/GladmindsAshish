'''
this file contains all auth related code include group logic , etc
'''
from django.contrib.auth.models import Group, User
from django.conf import settings

ALL_APPS = settings.BRANDS + [settings.GM_BRAND]


class GmApps():
    AFTERBUY = 'afterbuy'
    BAJAJ = 'bajaj'
    BAJAJCV = 'bajajcv'
    DEMO = 'demo'
    GM = 'default'
    DAIMLER = 'daimler'
    PROBIKING = 'probiking'
    BAJAJIB = 'bajajib'
    MECHANEED = 'mechaneed'

ALL_BRANDS = [getattr(GmApps, x) for x in dir(GmApps) if (not x.startswith("__") and getattr(GmApps, x)
                                                          not in [GmApps.AFTERBUY, GmApps.GM])]


class Roles():
    SUPERADMINS = 'SuperAdmins'
    ADMINS = 'Admins'
    USERS = 'Users'
    CXOADMINS = 'CxoAdmins'

    SDESCALATION = 'EscalationAuthority'
    BRANDMANAGERS = 'BrandManagers'
    READONLY = 'ReadOnly'

    FSCSUPERADMINS = 'FscSuperAdmins'
    FSCADMINS = 'FscAdmins'
    DEALERS = 'Dealers'
    ASCS = 'AuthorisedServiceCenters'
    DASCS = 'DependentAuthorisedServiceCenters'
    SERVICEADVISOR = 'ServiceAdvisors'
    TRANSPORTER = 'Transporters'
    SUPERVISOR = 'Supervisors'
    CTSADMIN = 'CTSAdmins'
    
    SDSUPERADMINS = 'SdSuperAdmins'
    SDADMINS = 'SdAdmins'
    SDMANAGERS = 'SdManagers'
    SDOWNERS = 'SdOwners'
    DEALERADMIN = 'DealerAdmins' 
    SDREADONLY = 'SdReadOnly'
    AREASERVICEMANAGER = 'AreaServiceManagers'
    ZSM = 'ZonalServiceManagers' 
    AREASALESMANAGERS = 'AreaSalesManagers'
    REGIONALMANAGERS = 'RegionalManagers'
    CIRCLEHEADS = 'CircleHeads' 
    
    LOYALTYSUPERADMINS = 'LoyaltySuperAdmins'
    LOYALTYADMINS = 'LoyaltyAdmins'
    NATIONALSPARESMANAGERS = 'NationalSparesManagers'
    AREASPARESMANAGERS = 'AreaSparesManagers'
    DISTRIBUTORS = 'Distributors'
    RPS = 'RedemptionPartners'
    LPS = 'LogisticPartners'
    WELCOMEKITESCALATION = 'WelcomeKitEscalation'
    REDEEMESCALATION = 'RedemptionEscalation'

    COUNTRYDISTRIBUTOR = 'CountryDistributors'
    MAINCOUNTRYDEALER = 'MainCountryDealers'

    VISUALIZATIONADMIN = 'VisualizationAdmins'
    VISUALIZATIONSTAFF = 'VisualizationStaffs'
    VISUALIZATIONUSER = 'VisualizationUsers'
    
    DISTRIBUTORSTAFF = 'DistributorStaffs'
    DISTRIBUTORSALESREP = 'DisitrbutorSalesReps'
    
    RETAILERS = 'Retailers'
    
AFTERBUY_ADMIN_GROUPS = [Roles.SUPERADMINS, Roles.ADMINS]
AFTERBUY_GROUPS = [Roles.SUPERADMINS, Roles.ADMINS, Roles.USERS]
OTHER_GROUPS = [getattr(Roles,x) for x in dir(Roles) if not x.startswith("__")]

AFTERBUY_USER_MODELS = ['User', 'Consumer', 'UserProduct', 'ProductSupport', 'RegistrationCertificate',
                        'ProductInsuranceInfo', 'ProductWarrantyInfo', 'PollutionCertificate',
                        'License', 'Invoice', 'SellInformation', 'UserProductImages', 'UserPreference',
                        'UserNotification','Service']


def add_user_to_group(app, user_id, group_name):
    g = Group.objects.using(app).get(name=group_name)
    user = User.objects.using(app).get(id=user_id)
    if not user.groups.using(app).filter(name=group_name).exists():
        user.groups.add(g)
        user.save(using=app)
