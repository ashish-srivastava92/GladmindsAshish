#from tastypie.constants import ALL
from gladminds.core.apis.base_apis import CustomBaseModelResource
from gladminds.core.model_fetcher import models
from tastypie.authorization import Authorization
from tastypie import fields
from gladminds.core.apis.user_apis import UserProfileResource, UserResource
from gladminds.core.apis.product_apis import ProductTypeResource
from django.conf.urls import url
from django.http.response import HttpResponse
import json
from django.forms.models import model_to_dict
from django.db.models.query_utils import Q
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.utils.urls import trailing_slash
from gladminds.core.apis.authorization import MultiAuthorization,\
    LoyaltyCustomAuthorization
import logging
from django.db import transaction
from gladminds.core.auth_helper import Roles
import operator
from django.db.models.aggregates import Count, Sum
from celery.worker.state import total_count
import itertools

logger = logging.getLogger("gladminds")

class TerritoryResource(CustomBaseModelResource):
    
    class Meta:
        queryset = models.Territory.objects.all()
        resource_name = "territories"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'put', 'delete']
        always_return_data = True

class StateResource(CustomBaseModelResource):
    territory = fields.ForeignKey(TerritoryResource, 'territory')
    
    class Meta:
        queryset = models.State.objects.all()
        resource_name = "states"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        always_return_data = True
        filtering = {
                     "state_name":ALL, 
                     }
        
class CityResource(CustomBaseModelResource):    
    state = fields.ForeignKey(StateResource, 'state')
    
    class Meta:
        queryset = models.City.objects.all()
        resource_name = "cities"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        always_return_data = True


class NSMResource(CustomBaseModelResource):
    class Meta:
        queryset = models.NationalSalesManager.objects.all()
        resource_name = "nsms"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        
        
class ASMResource(CustomBaseModelResource):
    class Meta:
        queryset = models.AreaSalesManager.objects.all()
        resource_name = "asms"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        
class PartnerResource(CustomBaseModelResource):
    class Meta:
        queryset = models.Partner.objects.all()
        resource_name = "partners"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True


class DistributorResource(CustomBaseModelResource):
    user = fields.ForeignKey(UserProfileResource, 'user', null=True, blank=True, full=True)
    asm = fields.ForeignKey(ASMResource, 'asm', null=True, blank=True, full=True)
    class Meta:
        queryset = models.Distributor.objects.all()
        resource_name = "distributors"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True


class RetailerResource(CustomBaseModelResource):
    class Meta:
        queryset = models.Retailer.objects.all()
        resource_name = "retailers"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True

class SpareMasterResource(CustomBaseModelResource):
    product_type = fields.ForeignKey(ProductTypeResource, 'product_type', full=True)
    class Meta:
        queryset = models.SparePartMasterData.objects.all()
        resource_name = "spare-masters"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True

class SparePartPointResource(CustomBaseModelResource):
    part_number = fields.ForeignKey(SpareMasterResource, 'part_number', full=True)
    class Meta:
        queryset = models.SparePartPoint.objects.all()
        resource_name = "spare-points"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True

class LoyaltySLAResource(CustomBaseModelResource):
    class Meta:
        queryset = models.LoyaltySLA.objects.all()
        resource_name = "slas"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True

class ProductResource(CustomBaseModelResource):
    partner = fields.ForeignKey(PartnerResource, 'partner', null=True, blank=True, full=True)
    
    class Meta:
        queryset = models.ProductCatalog.objects.all()
        resource_name = "product-catalogs"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True
    
class MemberResource(CustomBaseModelResource):
    distributor = fields.ForeignKey(DistributorResource, 'registered_by_distributor', null=True, blank=True, full=True) 
    preferred_retailer = fields.ForeignKey(RetailerResource, 'preferred_retailer', null=True, blank=True, full=True)
    state = fields.ForeignKey(StateResource, 'state',)
    
    class Meta:
        queryset = models.Mechanic.objects.all()
        resource_name = "members"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        filtering = {
                     "state":ALL_WITH_RELATIONS,
                     "locality":ALL,
                     "district":ALL,
                     }
        
class RedemptionResource(CustomBaseModelResource):
    member = fields.ForeignKey(MemberResource, 'member')
    product = fields.ForeignKey(ProductResource, 'product')
    partner = fields.ForeignKey(PartnerResource, 'partner', null=True, blank=True, full=True)
    
    class Meta:
        queryset = models.RedemptionRequest.objects.all()
        resource_name = "redemption-requests"
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        args = {
                'display_field' : {
                                    Roles.ASMS:[],
                                    Roles.NSMS:[],
                                    Roles.RPS:[],
                                    Roles.LPS:[]
                                   },
                'query_field' : {
                                  Roles.RPS:{
                                             'query':[Q(is_approved=True)],
                                             'user_name':'packed_by' 
                                             },
                                  Roles.LPS : {
                                                'query':[Q(status__in=['Shipped','Delivered'])],
                                                'user':'partner__user'
                                              },
                                  Roles.DEALERS:{
                                                 'user':'registered_by_distributor__user', 
                                                 'area':'member__registered_by_distributor__city'
                                                 }, 
                                  Roles.ASMS : {
                                                'user':'member__registered_by_distributor__asm__user__user',
                                                'area':'member__state__state_name'
                                               },
                                }
                }
        
        authorization = MultiAuthorization(Authorization(), LoyaltyCustomAuthorization
                                           (display_field=args['display_field'], query_field=args['query_field']))
        filtering = {
                     "member": ALL_WITH_RELATIONS,
                     "resolution_flag":ALL,
                     }
 
    def prepend_urls(self):
        return [
                url(r"^(?P<resource_name>%s)/members-details/(?P<status>[a-zA-Z.-]+)%s" % (self._meta.resource_name,trailing_slash()),
                                                        self.wrap_view('pending_redemption_request'), name="pending_redemption_request"),
                url(r"^(?P<resource_name>%s)/count%s" % (self._meta.resource_name,trailing_slash()),
                                                        self.wrap_view('count_redemption_request'), name="count_redemption_request"),
                url(r"^(?P<resource_name>%s)/points%s" % (self._meta.resource_name,trailing_slash()),
                                                        self.wrap_view('points_redemption_request'), name="points_redemption_request"),
                ]


    ''' returns a dict having Count of redemption request within sla, above sla and total count'''
    def count_redemption_request (self, request, **kwargs):
        data = {}
        query = {}
        try:
            user_group = request.user.groups.values()[0]['name']
            if not request.user.groups.filter(name=Roles.RPS).exists():
                q_user = self._meta.args['query_field'][user_group]['user']
                query[q_user] = request.user
            else:
                q_user = self._meta.args['query_field'][user_group]['user_name']
                query[q_user] = request.user.username
                query['is_approved']= True
               
            total = models.RedemptionRequest.objects.values('status').annotate(total_count= Count('status')).filter(**query)   
            query['resolution_flag'] = False
            within_sla_count = models.RedemptionRequest.objects.values('status').annotate(within_sla_count= Count('status')).filter(**query)
            query['resolution_flag'] = True        
            overdue_count = models.RedemptionRequest.objects.values('resolution_flag').annotate(above_sla_count= Count('status')).filter(**query)        
        
            for a,b,c in itertools.izip_longest(total, within_sla_count, overdue_count):    
                if not type(b):
                    a['within_sla_count']= b['within_sla_count']            
                if not type(c):
                    a['above_sla_count']= c['above_sla_count']   
                a.setdefault('total_count', 0)
                a.setdefault('within_sla_count', 0)
                a.setdefault('above_sla_count', 0)                                     
                data[a['status']]= a
        except Exception as ex:
            logger.error('redemption request count requested by {0}:: {1}'.format(request.user, ex))
            data = {'status': 0, 'message': 'could not retrieve the count of redemption request'}
        return HttpResponse(json.dumps(data), content_type="application/json")


    def points_redemption_request (self, request, **kwargs):
        data = {}
        query = {}
        try:
            user_group = request.user.groups.values()[0]['name']
            q_user = self._meta.args['query_field'][user_group]['user']
            area = self._meta.args['query_field'][user_group]['area']
            query[q_user] = request.user
            total_points_list = models.RedemptionRequest.objects.filter(**query).values(area).annotate(Sum('points'))   
            data = total_points_list
        except Exception as ex:
            logger.error('redemption request points requested by {0}:: {1}'.format(request.user, ex))
            data = {'status': 0, 'message': 'could not retrieve the points of redemption request'}
        return HttpResponse(json.dumps(data), content_type="application/json")


    ''' List of mechanics with pending redemption request'''
    def pending_redemption_request(self,request, **kwargs):
        status = kwargs['status']
        redemptionrequests = models.RedemptionRequest.objects.filter(~Q(status=status)).select_related('member')
        requests  = []
        if request.method == 'GET':
            for redemptionrequest in redemptionrequests: 
                redemption_dict = model_to_dict(redemptionrequest.member,exclude=['expected_delivery_date','due_date','image_url'])
                redemption_dict['due_date'] = redemptionrequest.member.modified_date.strftime('%Y-%m-%dT%H:%M:%S')
                redemption_dict['registered_date'] = redemptionrequest.member.registered_date.strftime('%Y-%m-%dT%H:%M:%S')
                redemption_dict['date_of_birth'] = redemptionrequest.member.date_of_birth.strftime('%Y-%m-%dT%H:%M:%S')
                redemption_dict['image_url'] = str(redemptionrequest.member.image_url)
                requests.append(redemption_dict)
            return HttpResponse(json.dumps(requests), content_type="application/json")
        else: 
            return HttpResponse(json.dumps({"message":"method not allowed"}), content_type="application/json",status=401)
    
        
class SparePartUPCResource(CustomBaseModelResource):
    part_number = fields.ForeignKey(SpareMasterResource, 'part_number', full=True)
    class Meta:
        queryset = models.SparePartUPC.objects.all()
        resource_name = "spare-upcs"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        
class AccumulationResource(CustomBaseModelResource):
    member = fields.ForeignKey(MemberResource, 'member', full=True) 
    asm = fields.ForeignKey(ASMResource, 'asm', null=True, blank=True, full=True)
    upcs = fields.ManyToManyField(SparePartUPCResource, 'upcs', full=True)
    
    class Meta:
        queryset = models.AccumulationRequest.objects.all()
        resource_name = "accumulations"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post']
        always_return_data = True
        filtering = {
                     "member":ALL_WITH_RELATIONS,
                     }

class WelcomeKitResource(CustomBaseModelResource):
    member = fields.ForeignKey(MemberResource, 'member')
    partner = fields.ForeignKey(PartnerResource, 'partner', null=True, blank=True, full=True)
    
    class Meta:
        queryset = models.WelcomeKit.objects.all()
        resource_name = "welcome-kits"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True

class CommentThreadResource(CustomBaseModelResource):
    redemption = fields.ForeignKey(RedemptionResource, 'redemption', null=True, blank=True, full=True)
    welcome_kit = fields.ForeignKey(WelcomeKitResource, 'welcome_kit', null=True, blank=True, full=True)
    user = fields.ForeignKey(UserResource, 'user')
    
    class Meta:
        queryset = models.CommentThread.objects.all()
        resource_name = "comment-threads"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True

class DiscrepantAccumulationResource(CustomBaseModelResource):
    upc = fields.ForeignKey(SparePartUPCResource,'upc', null=True, blank=True, full=True)
    new_member = fields.ForeignKey(MemberResource,'new_member')
    accumulation_request = fields.ForeignKey(AccumulationResource, 'accumulation_request')
     
    class Meta:
        queryset = models.DiscrepantAccumulation.objects.all()
        resource_name = "accumulation-discrepancies"
        authorization = Authorization()
        detail_allowed_methods = ['get']
        always_return_data = True

    def prepend_urls(self):
        return [
              url(r"^(?P<resource_name>%s)/transfer-points%s" % (self._meta.resource_name,trailing_slash()),
                                                     self.wrap_view('transfer_points'), name="transfer_points")
                ]

    
    def transfer_points(self,request, **kwargs):
        try:
            with transaction.atomic():
                upc = request.POST['upc']
                upc_obj = models.SparePartUPC.objects.get(unique_part_code=upc)
                points = models.SparePartPoint.objects.get(part_number=upc_obj.part_number).points
                from_mechanic = models.Mechanic.objects.get(mechanic_id= request.POST['from'])
                to_mechanic = models.Mechanic.objects.get(mechanic_id= request.POST['to'])
                self.update_points(from_mechanic, redeem=points)
                self.update_points(to_mechanic, accumulate=points)
                 
                accumulation_log = models.AccumulationRequest(member=to_mechanic,points=points,
                                                              total_points=to_mechanic.total_points,is_transferred=True)            
                accumulation_log.save()
                accumulation_log.upcs.add(upc_obj)
                data = {'status':1, 'message': 'Successfully transfered'}
        except Exception as ex:
            logger.error('[transfer_point]:{0}:: {1}'.format(upc, ex))
            data = {'status': 0, 'message': 'could not transfer points'}
        return HttpResponse(json.dumps(data), content_type="application/json")   
    
    def update_points(self, mechanic, accumulate=0, redeem=0):
        '''Update the loyalty points of the user'''
        total_points = mechanic.total_points + accumulate -redeem
        mechanic.total_points = total_points
        mechanic.save()
