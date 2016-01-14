import json
import logging
from datetime import datetime, timedelta, date

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.contrib.sites.models import RequestSite


from tastypie.utils.urls import trailing_slash
from tastypie import fields,http, bundle
from tastypie.http import HttpBadRequest
from tastypie.authorization import Authorization
from tastypie.authorization import DjangoAuthorization
from tastypie.constants import ALL_WITH_RELATIONS, ALL
from tastypie.exceptions import ImmediateHttpResponse

from gladminds.core.apis.user_apis import UserResource
from gladminds.core.apis.authentication import AccessTokenAuthentication
from gladminds.core.apis.base_apis import CustomBaseModelResource
from gladminds.core.auth.access_token_handler import create_access_token, \
    delete_access_token
    
from gladminds.core import constants

from gladminds.core.model_fetcher import models
from gladminds.core.model_fetcher import get_model

from django.db import connections

LOG = logging.getLogger('gladminds')




class NsmTargetResource(CustomBaseModelResource):
        '''
            National Spares Manager Target Resource
        '''
        class Meta:
                queryset = models.NsmTarget.objects.all()
                resource_name = "national-spares-manager-target"
                authorization = Authorization()
                #authentication = AccessTokenAuthentication()
                allowed_methods = ['get', 'post', 'put']
                always_return_data = True

class AsmTargetResource(CustomBaseModelResource):
        '''
            Area Spares Manager Target Resource
        '''
        class Meta:
                queryset = models.AsmTarget.objects.all()
                resource_name = "area-spares-manager-target"
                authorization = Authorization()
                #authentication = AccessTokenAuthentication()
                allowed_methods = ['get', 'post', 'put']
                always_return_data = True

class DistributorTargetResource(CustomBaseModelResource):
        '''
            Distributor Target Resource
        '''
        class Meta:
                queryset = models.DistributorTarget.objects.all()
                resource_name = "distributor-target"
                authorization = Authorization()
                #authentication = AccessTokenAuthentication()
                allowed_methods = ['get', 'post', 'put']
                always_return_data = True

class DsrTargetResource(CustomBaseModelResource):
        '''
            DistributorSalesRep Target Resource
        '''
        class Meta:
                queryset = models.DsrTarget.objects.all()
                resource_name = "dsr-target"
                authorization = Authorization()
                #authentication = AccessTokenAuthentication()
                allowed_methods = ['get', 'post', 'put']
                always_return_data = True
                

class RetailerTargetResource(CustomBaseModelResource):
        '''
            Retailer Target Resource
        '''
        class Meta:
                queryset = models.RetailerTarget.objects.all()
                resource_name = "retailer-target"
                authorization = Authorization()
                #authentication = AccessTokenAuthentication()
                allowed_methods = ['get', 'post', 'put']
                always_return_data = True


class AsmHighlightsResource(CustomBaseModelResource):
        '''
            Area Spares Manager Highlights Resource
        '''
        class Meta:
                queryset = models.AsmHighlights.objects.all()
                resource_name = "area-spares-manager-highlights"
                authorization = Authorization()
                #authentication = AccessTokenAuthentication()
                allowed_methods = ['get', 'post', 'put']
                always_return_data = True

class NsmHighlightsResource(CustomBaseModelResource):
        '''
            Area Spares Manager Highlights Resource
        '''
        class Meta:
                queryset = models.NsmHighlights.objects.all()
                resource_name = "national-spares-manager-highlights"
                authorization = Authorization()
                #authentication = AccessTokenAuthentication()
                allowed_methods = ['get', 'post', 'put']
                always_return_data = True

class DistributorHighlightsResource(CustomBaseModelResource):
        '''
            Distributor Highlights Resource
        '''
        class Meta:
                queryset = models.DistributorHighlights.objects.all()
                resource_name = "distributor-highlights"
                authorization = Authorization()
                #authentication = AccessTokenAuthentication()
                allowed_methods = ['get', 'post', 'put']
                always_return_data = True

class RetailerHighlightsResource(CustomBaseModelResource):
        '''
            Retailer Highlights Resource
        '''
        class Meta:
                queryset = models.RetailerHighlights.objects.all()
                resource_name = "retailer-highlights"
                authorization = Authorization()
                #authentication = AccessTokenAuthentication()
                allowed_methods = ['get', 'post', 'put']
                always_return_data = True




class AsmProfileResource(CustomBaseModelResource):
    '''Extended user profile resource'''
    user = fields.ForeignKey(UserResource, 'user', null=True, blank=True, full=True)
    class Meta:
        queryset = models.AreaServiceManager.objects.all()
        resource_name = 'gm-asm'
        authorization = Authorization()
#         authorization = MultiAuthorization(DjangoAuthorization())
#         authentication = AccessTokenAuthentication()
        allowed_methods = ['get', 'post', 'put']
        filtering = {
                     "user":  ALL_WITH_RELATIONS,
                     #"phone_number": ALL,
                     #"state": ALL,
                     #"country": ALL,
                     #"pincode": ALL
                     }
        always_return_data = True 
#        ordering = ['user', 'phone_number']