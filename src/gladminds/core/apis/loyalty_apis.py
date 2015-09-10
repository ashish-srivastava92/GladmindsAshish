import json
import logging

from django.conf.urls import url
from django.http.response import HttpResponse
from django.db.models.aggregates import Count
from django.db import transaction
from django.forms.models import model_to_dict
from django.db.models.query_utils import Q

from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.utils.urls import trailing_slash
from tastypie import fields
from tastypie.authorization import Authorization

from gladminds.core.apis.base_apis import CustomBaseModelResource
from gladminds.core.model_fetcher import models, get_model
from gladminds.core import constants
from gladminds.core.apis.authentication import AccessTokenAuthentication
from gladminds.core.apis.authorization import MultiAuthorization,\
    LoyaltyCustomAuthorization
from gladminds.core.auth_helper import Roles
from gladminds.core.apis.user_apis import MemberResource, AreaSparesManagerResource, PartnerResource,UserResource
from gladminds.core.apis.product_apis import ProductCatalogResource,\
    SparePartUPCResource
logger = logging.getLogger("gladminds")

class LoyaltySLAResource(CustomBaseModelResource):
    class Meta:
        queryset = models.LoyaltySLA.objects.all()
        resource_name = "loyalty-slas"
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True

class ProductResource(CustomBaseModelResource):
    partner = fields.ForeignKey(PartnerResource, 'partner', null=True, blank=True, full=True)
    
    class Meta:
        queryset = models.ProductCatalog.objects.all()
        resource_name = "product-catalogs"
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        
class RedemptionResource(CustomBaseModelResource):
    member = fields.ForeignKey(MemberResource, 'member', full=True)
    product_catalog = fields.ForeignKey(ProductCatalogResource, 'product', full=True)
    partner = fields.ForeignKey(PartnerResource, 'partner', null=True, blank=True, full=True)    

    class Meta:
        queryset = get_model('RedemptionRequest').objects.all()
        resource_name = "redemption-requests"
        authentication = AccessTokenAuthentication()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        args = constants.LOYALTY_ACCESS
        authorization = MultiAuthorization(Authorization(), LoyaltyCustomAuthorization(query_field=args['query_field']))
        filtering = {
                     "member": ALL_WITH_RELATIONS,
                     "resolution_flag":ALL,
                     "status":ALL,
                     "created_date" : ALL
                     }
        ordering = ["created_date", "status", "member"]
    
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(RedemptionResource, self).build_filters(filters)
        
        if 'member_id' in filters:
            query = filters['member_id']
            qset = (
                    Q(member__mechanic_id=query)|
                    Q(member__permanent_id=query)
                      )
            orm_filters.update({'custom':  qset})
        return orm_filters  
                     
            
    def apply_filters(self, request, applicable_filters):
        if 'custom' in applicable_filters:
            custom = applicable_filters.pop('custom')
        else:
            custom = None
        
        semi_filtered = super(RedemptionResource, self).apply_filters(request, applicable_filters)
        
        return semi_filtered.filter(custom) if custom else semi_filtered

    def prepend_urls(self):
        return [
                url(r"^(?P<resource_name>%s)/members-details/(?P<status>[a-zA-Z.-]+)%s" % (self._meta.resource_name,trailing_slash()),
                                                        self.wrap_view('pending_redemption_request'), name="pending_redemption_request"),
                url(r"^(?P<resource_name>%s)/count%s" % (self._meta.resource_name,trailing_slash()),
                                                        self.wrap_view('count_redemption_request'), name="count_redemption_request"),
                ]

    def get_filter_query(self, user, query):
        if not user.is_superuser:
            user_group = user.groups.values()[0]['name']
            q_user = self._meta.args['query_field'][user_group]['user']
            if user.groups.filter(name=Roles.NATIONALSPARESMANAGERS).exists():
                nsm_territory_list=models.NationalSparesManager.objects.get(user__user=user).territory.all()
                query[q_user] = nsm_territory_list
            elif user.groups.filter(name=Roles.AREASPARESMANAGERS).exists():
                asm_state_list=models.AreaSparesManager.objects.get(user__user=user).state.all()
                query[q_user] = asm_state_list
            elif user.groups.filter(name=Roles.DISTRIBUTORS).exists():
                distributor_city =  models.Distributor.objects.get(user__user=user).city
                query[q_user] = str(distributor_city)
            else:
                query[q_user] = user.username
        return query

    ''' returns a dict having Count of redemption request within sla, above sla and total count'''
    def count_redemption_request (self, request, **kwargs):
        data = []
        query = {}
        try:
            self.is_authenticated(request)
            query =self.get_filter_query(request.user, query)
            redemption_requests = models.RedemptionRequest.objects.values('status', 'resolution_flag').annotate(count= Count('status')).filter(**query)   
            redemption_report = {}
            for status in dict(constants.REDEMPTION_STATUS).keys():
                redemption_report[status]={'total_count':0, 'above_sla_count':0, 'within_sla_count':0}
            for redemption in redemption_requests:
                redemption_status=redemption['status']
                if redemption['resolution_flag']:
                    count=redemption['count']
                    redemption_report[redemption_status]['above_sla_count']=count
                else:
                    count=redemption['count']
                    redemption_report[redemption_status]['within_sla_count']=count
                redemption_report[redemption_status]['total_count']=redemption_report[redemption_status]['total_count']+count
        except Exception as ex:
            logger.error('redemption request count requested by {0}:: {1}'.format(request.user, ex))
            data = {'status': 0, 'message': 'could not retrieve the count of redemption request'}
        return HttpResponse(json.dumps(redemption_report), content_type="application/json")

    ''' List of Members with pending redemption request'''
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

       
class AccumulationResource(CustomBaseModelResource):
    member = fields.ForeignKey(MemberResource, 'member', full=True) 
    asm = fields.ForeignKey(AreaSparesManagerResource, 'asm', null=True, blank=True, full=True)
    upcs = fields.ManyToManyField(SparePartUPCResource, 'upcs', full=True)
    
    class Meta:
        queryset = models.AccumulationRequest.objects.all()
        resource_name = "accumulations"
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        detail_allowed_methods = ['get', 'post']
        always_return_data = True
        filtering = {
                     "member":ALL_WITH_RELATIONS,
                     "asm" : ALL_WITH_RELATIONS,
                     "upcs" : ALL_WITH_RELATIONS,
                     "created_date" : ALL
                     }
    
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(AccumulationResource, self).build_filters(filters)
        
        if 'member_id' in filters:
            query = filters['member_id']
            qset = (
                    Q(member__mechanic_id=query)|
                    Q(member__permanent_id=query)
                      )
            orm_filters.update({'custom':  qset})
        return orm_filters  
                     
            
    def apply_filters(self, request, applicable_filters):
        if 'custom' in applicable_filters:
            custom = applicable_filters.pop('custom')
        else:
            custom = None
        
        semi_filtered = super(AccumulationResource, self).apply_filters(request, applicable_filters)
        
        return semi_filtered.filter(custom) if custom else semi_filtered
    
    def alter_list_data_to_serialize(self, request, data):
        part_numbers = []
        for object in data['objects']:
            if object.data.has_key('upcs'):
                for upc in object.data['upcs']:            
                    part_numbers.append(upc.data['part_number'].data['id'])
        
        points = models.SparePartPoint.objects.filter(part_number__in=part_numbers).values('part_number__id', 'points')

        for object in data['objects']:
            if object.data.has_key('upcs'):
                for upc in object.data['upcs']:
                    part_number = upc.data['part_number'].data['id']
                    upc_mapping = filter(lambda point: point['part_number__id']==part_number, points)
                    upc.data['part_number'].data['point'] = upc_mapping[0]['points']
                    
        return data


class WelcomeKitResource(CustomBaseModelResource):
    member = fields.ForeignKey(MemberResource, 'member')
    partner = fields.ForeignKey(PartnerResource, 'partner', null=True, blank=True, full=True)
    
    class Meta:
        queryset = models.WelcomeKit.objects.all()
        resource_name = "welcome-kits"
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
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
        authentication = AccessTokenAuthentication()
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
        authentication = AccessTokenAuthentication()
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
                from_mechanic = models.Member.objects.get(mechanic_id= request.POST['from'])
                to_mechanic = models.Member.objects.get(mechanic_id= request.POST['to'])
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
