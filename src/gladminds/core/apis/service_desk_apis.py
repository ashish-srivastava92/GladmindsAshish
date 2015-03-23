from importlib import import_module
import json
import logging

from django.conf import settings
from django.conf.urls import url
from django.http.response import HttpResponse, HttpResponseBadRequest
from tastypie import fields
from tastypie.authentication import MultiAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.utils.urls import trailing_slash

from gladminds.core.apis.authentication import AccessTokenAuthentication
from gladminds.core.apis.authorization import MultiAuthorization,\
    ServiceDeskCustomAuthorization
from gladminds.core.apis.base_apis import CustomBaseModelResource
from gladminds.core.apis.user_apis import ServiceDeskUserResource, \
    DepartmentSubCategoriesResource, UserResource
from gladminds.core.model_fetcher import models
from django.db import connections
from gladminds.core.core_utils.utils import dictfetchall


LOG = logging.getLogger('gladminds')
    
class FeedbackResource(CustomBaseModelResource):
    '''
    Service Desk Feedback Resource
    '''
    reporter = fields.ForeignKey(ServiceDeskUserResource, 'reporter', full=True,
                                 null=True, blank=True)
    assignee = fields.ForeignKey(ServiceDeskUserResource, 'assignee', full=True,
                                 null=True, blank=True)
    previous_assignee = fields.ForeignKey(ServiceDeskUserResource, 'previous_assignee',
                                          full=True, null=True, blank=True)
    sub_department = fields.ForeignKey(DepartmentSubCategoriesResource, 'sub_department', null=True, blank=True, full=True)
    

    class Meta:
        queryset = models.Feedback.objects.all()
        resource_name = "feedbacks"
        model_name = "Feedback"
        authorization = MultiAuthorization(DjangoAuthorization(), ServiceDeskCustomAuthorization())
        authentication = MultiAuthentication(AccessTokenAuthentication())
        detail_allowed_methods = ['get']
        always_return_data = True
        filtering = {
                        "priority" : ALL,
                        "status": ALL,
                        "summary": ALL,
                        "created_date": ['gte', 'lte'],
                        "closed_date": ['gte', 'lte'],
                        "resolved_date": ['gte', 'lte'],
                        "assignee" : ALL_WITH_RELATIONS,
                        "due_date" : ALL,
                        "sub_department" : ALL_WITH_RELATIONS
                     }
        
        ordering = ['created_date']
        
    def prepend_urls(self):
        return [
                 url(r"^(?P<resource_name>%s)/add-ticket%s" % (self._meta.resource_name,trailing_slash()),
                                                        self.wrap_view('add_service_desk_ticket'), name="add_service_desk_ticket"),
                url(r"^(?P<resource_name>%s)/tat-report%s" % (self._meta.resource_name,trailing_slash()),
                                                        self.wrap_view('get_tat'), name="get_tat")]
         
    def add_service_desk_ticket(self, request, **kwargs):
        try:
            brand = settings.BRAND
            try:
                service_desk_view= getattr(import_module('gladminds.{0}.services.service_desk.servicedesk_views'.format(brand)), 'save_help_desk_data')
            except Exception as ex:
                service_desk_view= getattr(import_module('gladminds.core.services.service_desk.servicedesk_views'), 'save_help_desk_data')
            data = service_desk_view(request)
            return HttpResponse(content=json.dumps(data),
                                    content_type='application/json')
        except Exception as ex:
            LOG.error('Exception while saving data : {0}'.format(ex))
            return HttpResponseBadRequest()
    
    def get_tat(self, request, **kwargs):
        conn = connections[settings.BRAND]
        cursor = conn.cursor()
        cursor.execute("select sum(f2.dt) as sums ,count(*) as c , avg(f2.dt) as tat, YEAR(f1.created_date) as year, \
    MONTH(f1.created_date) as month from gm_feedback f1 inner join (select f2.id, TIMEDIFF(f2.resolved_date,f2.created_date)\
    as dt , f2.created_date from gm_feedback f2 where status= 'resolved') f2 on f2.id=f1.id group by \
    YEAR(f1.created_date), MONTH(f1.created_date)")
        details = dictfetchall(cursor)
        conn.close()
        result = []
        for data in details:
            tat ={}
            minutes, seconds = divmod(data['tat'], 60)
            tat['tat'] = minutes
            tat['month_of_year'] = str(data['year'])+"-"+ str(data['month'])
            result.append(tat)
        reports = {}
        reports['TAT'] = result
        return HttpResponse(content=json.dumps(reports),
                                    content_type='application/json')


class ActivityResource(CustomBaseModelResource):
    '''
    Service Desk Activities Resource 
    '''
    feedback = fields.ForeignKey(FeedbackResource, 'feedback', full=True,
                                 null=True, blank=True)
    user = fields.ForeignKey(UserResource, 'user', full=True,
                             null=True, blank=True)
    
    class Meta:
        queryset = models.Activity.objects.all()
        resource_name = 'feedback-activities'
        model_name = "Activity"
        detailed_allowed_methods = ['get']
        always_return_data = True
        filtering = {
                      "user" : ALL_WITH_RELATIONS,
                      "feedback" : ALL_WITH_RELATIONS
                     }
        ordering = ['created_date']
    
class SLAResource(CustomBaseModelResource):
    '''
    Service Desk SLA Resource
    '''    
    
    class Meta:
        queryset = models.SLA.objects.all()
        resource_name = 'slas'
        model_name = 'SLA'
        detailed_allowed_methods = ['get', 'post', 'put']
        always_return_data = True
        authorization = MultiAuthorization(DjangoAuthorization())
        filtering = {
                     "priority" : ALL
                     
                     }
        
        
        
        
        