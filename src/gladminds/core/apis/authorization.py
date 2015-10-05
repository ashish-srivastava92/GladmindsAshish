from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized
from provider.oauth2.models import AccessToken
from django.conf import settings

from gladminds.afterbuy import models as afterbuy
from gladminds.core.auth_helper import Roles
import operator
from django.db.models.query_utils import Q
from gladminds.core.model_fetcher import get_model, models

class CustomAuthorization(Authorization):

    def read_list(self, object_list, bundle):
        user = bundle.request.user
        # This assumes a ``QuerySet`` from ``ModelResource``
        if len(object_list)>0:
            if hasattr(object_list[0], 'consumer'):
                return object_list.filter(consumer__user=user)
            elif hasattr(object_list[0], 'user'):
                return object_list.filter(user=user)
            elif hasattr(object_list[0], 'product'):
                return object_list.filter(product__consumer__user=user)
        else:
            return object_list

    def read_detail(self, object_list, bundle):
        if self.read_list(object_list, bundle):
            return True

    def create_detail(self, object_list, bundle):
        data = bundle.obj.__dict__
        try:
            access_token_container = bundle.request.GET.urlencode().split('access_token=')[1]
            key = access_token_container.split('&')[0]
        except:
            key = bundle.request.META.get('HTTP_ACCESS_TOKEN')
        if  (settings.ENV in settings.IGNORE_ENV and key in settings.HARCODED_TOKEN):
                return True
        try:
            authorization = AccessToken.objects.filter(token=key)[0]
        except:
            raise Unauthorized("You are not allowed to access that data.")
        user_id = int(authorization.user.id)
        if data.get('consumer_id'):
            try:
                update_obj = afterbuy.Consumer.objects.get(user=int(data['consumer_id']))
            except:
                raise Unauthorized("You are not allowed to access that data.")
            if user_id == update_obj.user.id:
                return True
            raise Unauthorized("You are not allowed to access that data.")
        if bundle.obj.__dict__.get('product_id'):
            try:
                update_obj = afterbuy.UserProduct.objects.get(id=int(data['product_id']))
            except Exception as ex:
                raise Unauthorized("You are not allowed to access that data.")
            if user_id == update_obj.consumer.user.id:
                return True
            raise Unauthorized("You are not allowed to access that data.")
        return True

    def update_detail(self, object_list, bundle):
        self.authorize_user(object_list, bundle)
        return True

    def delete_detail(self, object_list, bundle):
        self.authorize_user(object_list, bundle)
        return True

    def authorize_user(self, object_list, bundle):
        data = bundle.obj.__dict__
        klass = bundle.obj.__class__
        try:
            access_token_container = bundle.request.GET.urlencode().split('access_token=')[1]
            key = access_token_container.split('&')[0]
        except:
            key = bundle.request.META.get('HTTP_ACCESS_TOKEN')

        if (settings.ENV in settings.IGNORE_ENV and key in settings.HARCODED_TOKEN):
            return True
        try:
            authorization = AccessToken.objects.filter(token=key)[0]
        except:
            raise Unauthorized("You are not allowed to access that data.")
        user_id = int(authorization.user.id)
        klass = bundle.obj.__class__
        if klass._meta.module_name == 'consumer':
            if user_id == data['user_id']:
                update_obj = klass.objects.get(user__id=user_id)
                return True
            raise Unauthorized("You are not allowed to access that data.")
        if bundle.obj.__dict__.get('consumer_id'):
            try:
                update_obj = klass.objects.get(id=int(data['id']))
            except:
                raise Unauthorized("You are not allowed to access that data.")
            if user_id == update_obj.consumer.user.id:
                return True
            raise Unauthorized("You are not allowed to access that data.")
        if bundle.obj.__dict__.get('product_id'):
            try:
                update_obj = klass.objects.get(id=int(data['id']))
            except:
                raise Unauthorized("You are not allowed to access that data.")
            if user_id == update_obj.product.consumer.user.id:
                return True
            raise Unauthorized("You are not allowed to access that data.")


class MultiAuthorization(Authorization):
    def __init__(self, *args, **kwargs):
        self.authorizers = args

    def read_list(self, object_list, bundle):
        for authorizer in self.authorizers:
            if object_list is []:
                return []
            object_list = authorizer.read_list(object_list, bundle)
        return object_list

    def read_detail(self, object_list, bundle):
        for authorizer in self.authorizers:
            klass = authorizer.read_detail(object_list, bundle)
            if klass is False:
                raise Unauthorized("You are not allowed to access that resource.")
        return True

    def create_list(self, object_list, bundle):
        for authorizer in self.authorizers:
            if object_list is []:
                return []
            object_list = authorizer.create_list(object_list, bundle)
        return object_list

    def create_detail(self, object_list, bundle):
        for authorizer in self.authorizers:
            klass = authorizer.create_detail(object_list, bundle)
            if klass is False:
                raise Unauthorized("You are not allowed to access that resource.")
        return True

    def update_list(self, object_list, bundle):
        for authorizer in self.authorizers:
            if object_list is []:
                return []
            object_list = authorizer.update_list(object_list, bundle)
        return object_list

    def update_detail(self, object_list, bundle):
        for authorizer in self.authorizers:
            klass = authorizer.update_detail(object_list, bundle)
            if klass is False:
                raise Unauthorized("You are not allowed to access that resource.")
        return True

    def delete_list(self, object_list, bundle):
        for authorizer in self.authorizers:
            if object_list is []:
                return []
            object_list = authorizer.delete_list(object_list, bundle)
        return object_list

    def delete_detail(self, object_list, bundle):
        for authorizer in self.authorizers:
            klass = authorizer.delete_detail(object_list, bundle)
            if klass is False:
                raise Unauthorized("You are not allowed to access that resource.")
        return True


class LoyaltyCustomAuthorization(Authorization):

    def __init__(self, query_field=None):
        self.query_field = query_field

    @staticmethod
    def get_filter_query(user, q_user, query): 
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
    
    ''' filter the object list based on query defined for specific Role'''
    def read_list(self, object_list, bundle):           
        klass_name = bundle.obj.__class__._meta.module_name
        user = bundle.request.user
        if not user.is_superuser:
            query = {}
            user_group = user.groups.values()[0]['name']
            q_user = self.query_field[user_group]['user']
            if klass_name=="member" and self.query_field[user_group].has_key('area'):
                q_user = self.query_field[user_group]['area']
                 
            query = self.get_filter_query(user, q_user, query)
            object_list = object_list.filter(**query)
        return object_list

class ServiceDeskCustomAuthorization(Authorization):
    def get_sa_under_dealer(self, dealer_id):
        sa_obj = get_model('ServiceAdvisor').objects.filter(dealer__user__user_id=dealer_id).values('user__user_id')
        sa_list = []
        for sa in sa_obj:
            sa_list.append(int(sa['user__user_id']))
        sa_list.append(dealer_id)

        return sa_list
    
    def read_list(self, object_list, bundle):
        if bundle.request.user.groups.filter(name__in=[Roles.SDMANAGERS, Roles.DEALERADMIN]):
            object_list = object_list.all()
        elif bundle.request.user.groups.filter(name=Roles.SDOWNERS):
            object_list = object_list.filter(assignee__user_profile__user_id=int(bundle.request.user.id))
        elif bundle.request.user.groups.filter(name=Roles.DEALERS):
            sa_list = self.get_sa_under_dealer(bundle.request.user.id)
            object_list = object_list.filter(reporter__user_profile__user_id__in=sa_list)
        else:
            object_list = []
        return object_list
    
    def read_detail(self, object_list, bundle):
        if bundle.request.user.groups.filter(name=Roles.SDOWNERS):
            if bundle.obj.assignee.user_profile.user.id != bundle.request.user.id:
                return False 
        elif bundle.request.user.groups.filter(name=Roles.DEALERS):
            sa_list = self.get_sa_under_dealer(bundle.request.user.id)
            if bundle.obj.reporter.user_profile.user.id not in sa_list:
                return False
        return True
    
class ContainerIndentCustomAuthorization(Authorization):

    def get_indents_query(self, object_list, bundle):
        query_set=[]
        if bundle.request.user.groups.filter(name=Roles.TRANSPORTER):
            query_set = get_model('ContainerLR').objects.filter(transporter__user__user_id=bundle.request.user.id)
            
        elif bundle.request.user.groups.filter(name=Roles.SUPERVISOR):
            supervisor = get_model('Supervisor').objects.get(user__user_id=bundle.request.user.id)
            query_set = get_model('ContainerLR').objects.filter(Q(submitted_by=supervisor.supervisor_id) | Q(submitted_by=None) 
                                                                        & Q(transporter=supervisor.transporter))
        return query_set
        
    def read_list(self, object_list, bundle):
        query_set = self.get_indents_query(object_list, bundle)
        if query_set:
            submitted_indents=query_set.values_list('zib_indent_num_id', flat=True)
            object_list = object_list.filter(id__in=submitted_indents)
        return object_list

class ContainerLRCustomAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        if bundle.request.user.groups.filter(name=Roles.TRANSPORTER):
            object_list = object_list.filter(transporter__user__user_id=int(bundle.request.user.id))
        elif bundle.request.user.groups.filter(name=Roles.SUPERVISOR):
            supervisor = get_model('Supervisor').objects.get(user__user_id=bundle.request.user.id)
            object_list = object_list.filter(Q(submitted_by=supervisor.supervisor_id) | Q(submitted_by=None) 
                                                                        & Q(transporter=supervisor.transporter))
        return object_list

class CTSCustomAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        if bundle.request.user.groups.filter(name=Roles.TRANSPORTER):
            object_list = object_list.filter(transporter__user__user_id=int(bundle.request.user.id))
        elif bundle.request.user.groups.filter(name=Roles.SUPERVISOR):
            supervisor = get_model('Supervisor').objects.get(user__user_id=bundle.request.user.id)
            
            object_list = object_list.filter(Q(transporter=supervisor.transporter)
                                             & (Q(submitted_by=supervisor.supervisor_id) | Q(submitted_by=None)))
        return object_list


class ZSMCustomAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        if bundle.request.user.groups.filter(name=Roles.ZSM):
            object_list = object_list.filter(zsm__user__user_id=int(bundle.request.user.id))
        elif bundle.request.user.groups.filter(name=Roles.AREASERVICEMANAGER):
            object_list = object_list.filter(user__user_id=int(bundle.request.user.id))
        return object_list
    
class RMCustomAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        if bundle.request.user.groups.filter(name=Roles.REGIONALMANAGERS):
            object_list = object_list.filter(rm__user__user_id=int(bundle.request.user.id))
        elif bundle.request.user.groups.filter(name=Roles.AREASALESMANAGERS):
            object_list = object_list.filter(user__user_id=int(bundle.request.user.id))
        return object_list

class DealerCustomAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        if bundle.request.user.groups.filter(name=Roles.ZSM):
            object_list = object_list.filter(asm__zsm__user__user_id=int(bundle.request.user.id))
        elif bundle.request.user.groups.filter(name=Roles.AREASERVICEMANAGER):
            object_list = object_list.filter(asm__user__user_id=int(bundle.request.user.id))
        elif bundle.request.user.groups.filter(name=Roles.REGIONALMANAGERS):
            object_list = object_list.filter(sm__rm__user__user_id=int(bundle.request.user.id))
        elif bundle.request.user.groups.filter(name=Roles.AREASALESMANAGERS):
            object_list = object_list.filter(sm__user__user_id=int(bundle.request.user.id))
        return object_list
