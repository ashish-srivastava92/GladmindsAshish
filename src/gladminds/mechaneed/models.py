from django.db import models
from django.contrib.auth.models import User
from gladminds.core import base_models, constants
from gladminds.core.auth_helper import GmApps
import datetime
from gladminds.core.model_helpers import PhoneField
from gladminds.core.core_utils.utils import generate_agency_id, generate_qualitycheck_id


try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now
STATUS_CHOICES=constants.STATUS_CHOICES
 

_APP_NAME = GmApps.MECHANEED
 
try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now

 
class UserProfile(base_models.UserProfile):
    user = models.OneToOneField(User, primary_key=True,
                                        related_name='mechaneed_users')
    
     
    class Meta(base_models.UserProfile.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Brand Users"


class Agency(base_models.Agency):
    
    agency_id = models.CharField(max_length=255, null=True, blank=True, default=generate_agency_id)
    name = models.CharField(max_length=255, null=False)
    address = models.CharField(max_length=255, null=True, blank=True)
    address1 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    contactperson = models.CharField(max_length=255, null=False)
    phone_number = models.CharField(max_length=15, null=False, blank=False, unique=True)
                                                                                
    class Meta(base_models.Agency.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Agency"
    
    def __unicode__(self):
        return str(self.agency_id) + ' ' +str(self.name)

    
class QualityCheck(base_models.QualityCheck):
    '''details of QualityCheck'''
    user = models.ForeignKey(UserProfile, null=True, blank=True)
    agency = models.ForeignKey(Agency, null=True, blank=True)
    
    qualitycheck = models.CharField(max_length=50, unique=True, default=generate_qualitycheck_id)
    name = models.CharField(max_length=50, null=True, blank=True)
    phone_number = PhoneField(skip_check=True, null=True, blank=True)

    class Meta(base_models.QualityCheck.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Quality Check"
    
    def __unicode__(self):
        return str(self.agency) + ' ' +str(self.name)


class FieldInterviewerSupervisor(base_models.FieldInterviewerSupervisor):
    '''details of FieldInterviewerSupervisor'''
    user = models.ForeignKey(UserProfile, null=True, blank=True)
    qualitycheck_id = models.ForeignKey(QualityCheck, null=True, blank=True)
    agency = models.ForeignKey(Agency, null=True, blank=True)

    
    name = models.CharField(max_length=50, null=True, blank=True)
    phone_number = PhoneField(skip_check=True, null=True, blank=True)
    
    class Meta(base_models.FieldInterviewerSupervisor.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Field Interviewer Supervisor"
    
    def __unicode__(self):
        return str(self.qualitycheck_id) + ' ' + str(self.name)
        

class FieldInterviewer(base_models.FieldInterviewer):
    '''details of FieldInterviewer'''
    user = models.ForeignKey(UserProfile, null=True, blank=True)
    qualitycheck_id = models.ForeignKey(QualityCheck, null=True, blank=True)
    agency = models.ForeignKey(Agency, null=True, blank=True)
 
    name = models.CharField(max_length=50, null=True, blank=True)
    phone_number = PhoneField(skip_check=True, null=True, blank=True)
    
    class Meta(base_models.FieldInterviewer.Meta):
        app_label = _APP_NAME
        verbose_name_plural = "Field Interviewer"
    
    def __unicode__(self):
        return str(self.qualitycheck_id) + ' ' +str(self.name)

        