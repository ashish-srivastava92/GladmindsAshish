import copy
import datetime
from django import forms
from django.contrib.admin import AdminSite, TabularInline
from django.contrib.auth.models import User, Group
from django.contrib.admin import ModelAdmin
from django.contrib.admin.views.main import ChangeList, ORDER_VAR
from django.contrib.admin import DateFieldListFilter
from django import forms

from gladminds.mechaneed import models
from gladminds.core.model_fetcher import get_model
from gladminds.core.services.loyalty.loyalty import loyalty
from gladminds.core import utils
from gladminds.core.auth_helper import GmApps, Roles
from gladminds.core.admin_helper import GmModelAdmin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.conf import settings
from gladminds.core.auth_helper import Roles
from gladminds.core import constants

class MechaneedAdminSite(AdminSite):
    pass


class UserProfileAdmin(GmModelAdmin):
    search_fields = ('user__username', 'phone_number',)
    list_display = ('user', 'phone_number', 'status', 'address',
                    'state', 'country', 'pincode', 'date_of_birth', 'gender')
    readonly_fields = ('image_tag',)

class AgencyAdmin(GmModelAdmin):
    search_fields = ('name','city','phone_number','contactperson')
                     
    list_display = ('name','contactperson','phone_number','city','address')
                     
    
class QualityCheckAdmin(GmModelAdmin):
    search_fields = ('agency', 'qualitycheck','phone_number')
                     
    list_display = ('agency', 'qualitycheck','name', 'phone_number',)
                     


class FieldInterviewerSupervisorAdmin(GmModelAdmin):
    search_fields = ('agency', 'qualitycheck_id','phone_number')
                     
    list_display = ('agency','qualitycheck_id','name', 'phone_number',)
                     

class FieldInterviewerAdmin(GmModelAdmin):
    search_fields = ('agency', 'qualitycheck_id','phone_number')
                     
    list_display = ('agency','qualitycheck_id', 'name', 'phone_number',)
                     

def get_admin_site_custom(brand):
    brand_admin = MechaneedAdminSite(name=brand)
    
    brand_admin.register(User, UserAdmin)
    brand_admin.register(Group, GroupAdmin)
    brand_admin.register(get_model("UserProfile", brand), UserProfileAdmin)
    
    brand_admin.register(get_model("Agency", brand), AgencyAdmin)
    brand_admin.register(get_model("QualityCheck", brand), QualityCheckAdmin)
    brand_admin.register(get_model("FieldInterviewerSupervisor", brand), FieldInterviewerSupervisorAdmin)
    brand_admin.register(get_model("FieldInterviewer", brand), FieldInterviewerAdmin)

     

    return brand_admin

brand_admin = get_admin_site_custom(GmApps.MECHANEED)
