import copy
import datetime

from django import forms
from django.contrib.admin import AdminSite, TabularInline
from django.contrib.auth.models import User, Group
from django.contrib.admin import ModelAdmin
from django.contrib.admin.views.main import ChangeList, ORDER_VAR
from django.contrib.admin import DateFieldListFilter
from django import forms

from gladminds.core.model_fetcher import get_model
from gladminds.core.services.loyalty.loyalty import loyalty
from gladminds.core import utils
from gladminds.core.auth_helper import GmApps, Roles
from gladminds.core.admin_helper import GmModelAdmin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.conf import settings
from gladminds.core.auth_helper import Roles
from gladminds.core import constants

from gladminds.core.models import Retailer,AreaSparesManager
from django.utils.html import mark_safe
from django.forms.widgets import TextInput
import logging, os

from django.contrib import messages, admin
from tastypie.validation import FormValidation


logger = logging.getLogger('gladminds')

class CoreAdminSite(AdminSite):
    pass


class UserProfileAdmin(GmModelAdmin):
    search_fields = ('user__username', 'phone_number')
    list_display = ('user', 'phone_number', 'status', 'address',
                    'state', 'country', 'pincode', 'date_of_birth', 'gender')
    readonly_fields = ('image_tag',)
    
class DealerAdmin(GmModelAdmin):
    search_fields = ('dealer_id',)
    list_display = ('dealer_id', 'get_user', 'get_profile_number', 'get_profile_address')


class AuthorizedServiceCenterAdmin(GmModelAdmin):
    search_fields = ('asc_id', 'dealer__dealer_id')
    list_display = ('asc_id', 'get_user', 'get_profile_number', 'get_profile_address', 'dealer', 'asm')

class ServiceAdvisorAdmin(GmModelAdmin):
    search_fields = ('service_advisor_id', 'dealer__dealer_id', 'asc__asc_id')
    list_display = ('service_advisor_id', 'get_user', 'get_profile_number', 'get_profile_address', 'dealer', 'asc', 'status')

class BrandProductCategoryAdmin(GmModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'description')

class ProductTypeAdmin(GmModelAdmin):
    search_fields = ('product_type',)
    list_display = ('id', 'product_type',\
                    'image_url', 'is_active')

class DispatchedProduct(get_model("ProductData")):
 
    class Meta:
        proxy = True

class ListDispatchedProduct(GmModelAdmin):
    search_fields = ('product_id', 'dealer_id__dealer_id')
    list_display = (
        'product_id', 'product_type', 'engine', 'UCN', 'dealer_id', "invoice_date")
    list_per_page = 50

    def queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        utils.get_search_query_params(request, self)
        query_set = self.model._default_manager.get_query_set()
        query_set = query_set.select_related('').prefetch_related('dealer_id', 'product_type')

        return query_set

    def UCN(self, obj):
        coupons = get_model("CouponData").objects.filter(product=obj.id)
        if coupons:
            return ' | '.join([str(ucn.unique_service_coupon) for ucn in coupons])
        else:
            return None
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(ListDispatchedProduct, self).get_form(request, obj, **kwargs)
        return form

    def changelist_view(self, request, extra_context=None):
        custom_search_mapping = {'Product Id' : 'product_id',
                                 'Dealer Id': 'dealer_id__dealer_id',}
        extra_context = {'custom_search': True, 'custom_search_fields': custom_search_mapping
                        }
        return super(ListDispatchedProduct, self).changelist_view(request, extra_context=extra_context)


class Couponline(TabularInline):
    model = get_model("CouponData")
    fields = ('unique_service_coupon', 'service_type', 'status', 'mark_expired_on', 'extended_date')
    extra = 0
    max_num = 0
    readonly_fields = ('unique_service_coupon','service_type', 'status', 'mark_expired_on', 'extended_date')


class ProductDataAdmin(GmModelAdmin):
    search_fields = ('product_id', 'customer_id', 'customer_phone_number',
                     'customer_name')
    list_display = ('product_id', 'customer_id', "UCN", 'customer_name',
                    'customer_phone_number', 'purchase_date')
    inlines = (Couponline,)
    list_per_page = 50

    def queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        utils.get_search_query_params(request, self)
        query_set = self.model._default_manager.get_query_set()
        query_set = query_set.select_related('')
        query_set = query_set.filter(purchase_date__isnull=False)
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            query_set = query_set.order_by(*ordering)
        return query_set

    def UCN(self, obj):
        coupons = get_model("CouponData").objects.filter(product=obj.id)
        if coupons:
            return ' | '.join([str(ucn.unique_service_coupon) for ucn in coupons])
        else:
            return None

    def service_type(self, obj):
        gm_coupon_data_obj = get_model("CouponData").objects.filter(product=obj.id)
        coupon_service_type = ''
        if gm_coupon_data_obj:
            coupon_service_type = " | ".join(
                [str(obj.service_type) for obj in gm_coupon_data_obj])
        return coupon_service_type
    
    def changelist_view(self, request, extra_context=None):
        custom_search_mapping = {'Product Id' : 'product_id',
                                 'Customer ID':'customer_id',
                                 'Customer Name': 'customer_name',
                                 'Customer Phone Number': 'customer_phone_number'}
        extra_context = {'custom_search': True, 'custom_search_fields': custom_search_mapping
                        }
        return super(ProductDataAdmin, self).changelist_view(request, extra_context=extra_context)


class CouponAdmin(GmModelAdmin):
    search_fields = (
        'unique_service_coupon', 'product__product_id', 'status')
    list_display = ('product', 'unique_service_coupon', 'actual_service_date',
                    'actual_kms', 'status', 'service_type','service_advisor', 'associated_with')
    exclude = ('order',)

    def suit_row_attributes(self, obj):
        class_map = {
            '1': 'success',
            '2': 'warning',
            '3': 'error',
            '4': 'info',
            '5': 'error',
            '6': 'warning'
        }
        css_class = class_map.get(str(obj.status))
        if css_class:
            return {'class': css_class}
    
    def associated_with(self, obj):
        if obj.service_advisor:
            sa = get_model("ServiceAdvisor").objects.filter(service_advisor_id=obj.service_advisor.service_advisor_id).select_related('dealer', 'authorizedservicecenter')[0]
            if sa.dealer:
                return sa.dealer.dealer_id + ' (D)'
            elif sa.asc:
                return sa.asc.asc_id + ' (A)'
            else:
                return None

    def changelist_view(self, request, extra_context=None):
        custom_search_mapping = {'Unique Service Coupon' : 'unique_service_coupon',
                                 'Product Id': 'product__product_id',
                                 'Status': 'status'}
        extra_context = {'custom_search': True, 'custom_search_fields': custom_search_mapping, 'created_date_search': True
                        }
        return super(CouponAdmin, self).changelist_view(request, extra_context=extra_context)

    def queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        if utils.get_search_query_params(request, self) and self.search_fields[0] == 'status':
            try:
                request.GET = request.GET.copy()
                search_value = str(constants.COUPON_STATUS[request.GET["q"].title()])
                request.GET["q"] = search_value
                request.META['QUERY_STRING'] = search_value
            except Exception:
                pass
        qs = self.model._default_manager.get_query_set()
        qs = qs.select_related('').prefetch_related('product')
        '''
            This if condition only for landing page
        '''
        if not request.GET.has_key('q') and not request.GET.has_key('_changelist_filters'):
            qs = qs.filter(status=4)
        return qs

    def get_changelist(self, request, **kwargs):
        return CouponChangeList

class CouponChangeList(ChangeList):

    def get_ordering(self, request, queryset):
        '''
            This remove default ordering of django admin
            default ordering of django admin is primary key
        '''
        params = self.params
        ordering = list(self.model_admin.get_ordering(request)
                        or self._get_default_ordering())

        if ORDER_VAR in params:
            # Clear ordering and used params
            ordering = []
            order_params = params[ORDER_VAR].split('.')
            for p in order_params:
                try:
                    none, pfx, idx = p.rpartition('-')
                    field_name = self.list_display[int(idx)]
                    order_field = self.get_ordering_field(field_name)
                    if not order_field:
                        continue # No 'admin_order_field', skip it
                    ordering.append(pfx + order_field)
                except (IndexError, ValueError):
                    continue # Invalid ordering specified, skip it.

        ordering.extend(queryset.query.order_by)

        return ordering

class SMSLogAdmin(GmModelAdmin):
    search_fields = ('sender', 'receiver', 'action')
    list_display = (
        'created_date', 'action', 'message', 'sender', 'receiver')
    
    def suit_row_attributes(self, obj):
        class_map = {
            'success': 'success',
            'failed': 'error',
        }
        css_class = class_map.get(str(obj.status))
        if css_class:
            return {'class': css_class}
    
    def action(self, obj):
        return obj.action
    
    def has_add_permission(self, request):
        return False
    
class EmailLogAdmin(GmModelAdmin):
    search_fields = ('subject', 'sender', 'receiver')
    list_display = (
        'created_date', 'subject', 'message', 'sender', 'receiver', 'cc')

class FeedLogAdmin(GmModelAdmin):
    search_fields = ('status', 'data_feed_id', 'feed_type', 'action')
    list_display = ('timestamp', 'feed_type', 'action',
                    'total_data_count', 'success_data_count',
                    'failed_data_count', 'feed_remarks')

    def feed_remarks(self, obj):
        if obj.file_location:
            update_remark = ''
            update_remark = u'<a href="{0}" target="_blank">{1}</a>'.\
                                            format(obj.file_location, " Click for details")
            return update_remark
    feed_remarks.allow_tags = True

    def has_add_permission(self, request):
        return False

    def suit_row_attributes(self, obj):
        class_map = {
            'success': 'success',
            'failed': 'error',
        }
        css_class = class_map.get(str(obj.status))
        if css_class:
            return {'class': css_class}
        
    def changelist_view(self, request, extra_context=None):
        extra_context = {'created_date_search': True
                        }
        return super(FeedLogAdmin, self).changelist_view(request, extra_context=extra_context)

class ASCTempRegistrationAdmin(GmModelAdmin):
    search_fields = (
        'name', 'phone_number', 'email', 'dealer_id')

    list_display = (
        'name', 'phone_number', 'email', 'pincode',
        'address', 'timestamp', 'dealer_id')

class SATempRegistrationAdmin(GmModelAdmin):
    search_fields = (
        'name', 'phone_number')

    list_display = (
        'name', 'phone_number', 'status')

class CustomerTempRegistrationAdmin(GmModelAdmin):
    search_fields = (
        'product_data__product_id', 'new_customer_name', 'new_number', 'temp_customer_id', 'sent_to_sap')

    list_display = (
        'temp_customer_id', 'product_data', 'new_customer_name', 'new_number',
        'product_purchase_date', 'sent_to_sap', 'remarks')

    def suit_row_attributes(self, obj):
        class_map = {
            '1': 'success',
            '0': 'error'
        }
        css_class = class_map.get(str(obj.sent_to_sap))
        if css_class:
            return {'class': css_class}
        
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ('product_data',)
        form = super(CustomerTempRegistrationAdmin, self).get_form(request, obj, **kwargs)
        return form

class MessageTemplateAdmin(GmModelAdmin):
    search_fields = ('template_key', 'template')
    list_display = ('template_key', 'template', 'description')

class EmailTemplateAdmin(GmModelAdmin):
    search_fields = ('template_key', 'sender', 'receiver', 'subject')
    list_display = ('template_key', 'sender', 'receivers', 'subject')

    def receivers(self, obj):
        return ' | '.join(obj.receiver.split(','))

class SlaAdmin(GmModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
        'priority', ('response_time', 'response_unit'),
        ('reminder_time', 'reminder_unit'),
        ('resolution_time', 'resolution_unit'))
        }),
        )
    def response_time(self):
        return str(self.response_time) + ' ' + self.response_unit
    
    def reminder_time(self):
        return str(self.reminder_time) + ' ' + self.reminder_unit
    
    def resolution_time(self):
        return str(self.resolution_time) + ' ' + self.resolution_unit
    
    list_display = ('priority', response_time, reminder_time, resolution_time)

class ServiceAdmin(GmModelAdmin):
    list_display = ('service_type', 'name', 'description')
    readonly_fields = ('file_tag',)

class ServiceDeskUserAdmin(GmModelAdmin):
    list_display = ('user_profile', 'name', 'phone_number', 'email')

'''Admin View for loyalty'''
class NSMAdmin(GmModelAdmin):
    groups_update_not_allowed = [Roles.AREASPARESMANAGERS, Roles.NATIONALSPARESMANAGERS]
    search_fields = ('nsm_id', 'name', 'phone_number')
    list_display = ('nsm_id', 'name', 'email', 'phone_number','get_territory')

    def get_territory(self, obj):
        territories = obj.territory.all()
        if territories:
            return ' | '.join([str(territory.territory) for territory in territories])
        else:
            return None

    get_territory.short_description = 'Territory'

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ('nsm_id',)
        form = super(NSMAdmin, self).get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        obj.phone_number = utils.mobile_format(obj.phone_number)
        super(NSMAdmin, self).save_model(request, obj, form, change)

class ASMAdmin(GmModelAdmin):
    groups_update_not_allowed = [Roles.AREASPARESMANAGERS, Roles.NATIONALSPARESMANAGERS]
    search_fields = ('asm_id', 'nsm__name',
                     'phone_number')
    list_display = ('asm_id', 'name', 'email',
                     'phone_number', 'get_state', 'nsm')

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ('asm_id',)
        form = super(ASMAdmin, self).get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        obj.phone_number = utils.mobile_format(obj.phone_number)
        super(ASMAdmin, self).save_model(request, obj, form, change)

class DistributorAdmin(GmModelAdmin):
    groups_update_not_allowed = [Roles.AREASPARESMANAGERS, Roles.NATIONALSPARESMANAGERS]
    search_fields = ('distributor_id', 'asm__asm_id',
                     'phone_number', 'city')
    list_display = ('distributor_id', 'name', 'email',
                    'phone_number', 'city', 'asm', 'state')

    def queryset(self, request):
        query_set = self.model._default_manager.get_query_set()
        if request.user.groups.filter(name=Roles.AREASPARESMANAGERS).exists():
            asm_state_list=get_model("AreaSparesManager").objects.get(user__user=request.user).state.all()
            query_set=query_set.filter(state=asm_state_list)
        return query_set

    def changelist_view(self, request, extra_context=None):
        return super(DistributorAdmin, self).changelist_view(request)

class SparePartMasterAdmin(GmModelAdmin):
    groups_update_not_allowed = [Roles.AREASPARESMANAGERS, Roles.NATIONALSPARESMANAGERS]
    search_fields = ('part_number', 'category',
                     'segment_type', 'supplier',
                     'product_type__product_type')
    list_display = ('part_number', 'description',
                    'product_type', 'category',
                    'segment_type',  'part_model', 'supplier')

class SparePartUPCAdmin(GmModelAdmin):
    groups_update_not_allowed = [Roles.AREASPARESMANAGERS, Roles.NATIONALSPARESMANAGERS]
    search_fields = ('part_number__part_number', 'unique_part_code', 'part_number__description')
    list_display = ('unique_part_code', 'part_number', 'get_part_description','is_used','is_used_by_retailer')

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ('is_used','is_used_by_retailer') #After Testing need to comment this line
        form = super(SparePartUPCAdmin, self).get_form(request, obj, **kwargs)
        return form

class SparePartPointAdmin(GmModelAdmin):
    groups_update_not_allowed = [Roles.AREASPARESMANAGERS, Roles.NATIONALSPARESMANAGERS]
    search_fields = ('part_number__part_number', 'points', 'territory')

    def changelist_view(self, request, extra_context={}):
        if request.user.is_superuser or request.user.groups.filter(name=Roles.LOYALTYSUPERADMINS).exists():
            self.list_display=('part_number', 'points', 'valid_from',
                    'valid_till', 'territory', 'price', 'MRP')
        else:
            self.list_display=('part_number', 'points', 'valid_from',
                    'valid_till', 'territory')
        return super(SparePartPointAdmin, self).changelist_view(request, extra_context=extra_context)
    
    def get_form(self, request, obj=None, **kwargs):
        if not request.user.is_superuser and not request.user.groups.filter(name=Roles.LOYALTYSUPERADMINS).exists():
            self.exclude = ('price', 'MRP')
        form = super(SparePartPointAdmin, self).get_form(request, obj, **kwargs)
        return form

class SparePartline(TabularInline):
    model = get_model("AccumulationRequest").upcs.through

class ProductCatalogAdmin(GmModelAdmin):
    groups_update_not_allowed = [Roles.AREASPARESMANAGERS, Roles.NATIONALSPARESMANAGERS]
    list_filter = ('is_active',)
    search_fields = ('partner__partner_id', 'product_id',
                    'brand', 'model', 'category',
                    'sub_category')

    list_display = ('partner', 'product_id', 'points', 'price',
                    'description', 'variation',
                    'brand', 'model', 'category',
                    'sub_category')
    readonly_fields = ('image_tag',)

class PartnerAdmin(GmModelAdmin):
    groups_update_not_allowed = [Roles.AREASPARESMANAGERS, Roles.NATIONALSPARESMANAGERS]
    list_filter = ('partner_type',)
    search_fields = ('partner_id', 'name', 'partner_type')

    list_display = ('partner_id', 'name' , 'address','partner_type')

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ('partner_id',)
        form = super(PartnerAdmin, self).get_form(request, obj, **kwargs)
        return form

class AccumulationRequestAdmin(GmModelAdmin):
    groups_update_not_allowed = [Roles.AREASPARESMANAGERS, Roles.NATIONALSPARESMANAGERS, Roles.LOYALTYADMINS, Roles.LOYALTYSUPERADMINS]
    search_fields = ('member__mechanic_id','member__permanent_id','upcs__unique_part_code')
    list_display = ( 'get_members_mechanic_id',  'get_mechanic_name', 'get_mechanic_district',
                     'get_asm', 'get_upcs', 'points',
                     'total_points', 'created_date')
    
    def get_upcs(self, obj):
        upcs = obj.upcs.all()
        if upcs:
            return ' | '.join([str(upc.unique_part_code) for upc in upcs])
        else:
            return None

    get_upcs.short_description = 'UPC'

    def queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        query_set = self.model._default_manager.get_query_set()
        if request.user.groups.filter(name=Roles.AREASPARESMANAGERS).exists():
            asm_state_list=get_model("AreaSparesManager").objects.get(user__user=request.user).state.all()
            query_set=query_set.filter(member__state=asm_state_list)
        return query_set

    def changelist_view(self, request, extra_context=None):
        extra_context = {'created_date_search': True
                        }
        return super(AccumulationRequestAdmin, self).changelist_view(request, extra_context=extra_context)
    
    
class AccumulationRequestRetailerAdmin(GmModelAdmin):
    groups_update_not_allowed = [Roles.AREASPARESMANAGERS, Roles.NATIONALSPARESMANAGERS, Roles.LOYALTYADMINS, Roles.LOYALTYSUPERADMINS]
    search_fields = ('retailer__retailer_id','retailer__retailer_permanent_id','upcs__unique_part_code','retailer__mobile','retailer__user__state')
    list_display = ( 'get_retailer_id',  'retailer_user_name', 'get_retailer_state',
                     'get_upcs', 'points', 'total_points', 'created_date')
    
    def get_retailer_id(self,obj):
        if obj.retailer.retailer_permanent_id:
            return obj.retailer.retailer_permanent_id
        return obj.retailer.retailer_id
    get_retailer_id.short_description = 'Retailer ID'
    
    def retailer_user_name(self, obj):
        return obj.retailer.retailer_name
    retailer_user_name.short_description = 'Retailer Name'
    
    def get_retailer_state(self, obj):
        return obj.retailer.user.state
    get_retailer_state.short_description = 'Retailer State'
    
    def get_upcs(self, obj):
        upcs = obj.upcs.all()
        if upcs:
            return ' | '.join([str(upc.unique_part_code) for upc in upcs])
        else:
            return None

    get_upcs.short_description = 'UPC'

    def queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        query_set = self.model._default_manager.get_query_set()
        if request.user.groups.filter(name=Roles.AREASPARESMANAGERS).exists():
            asm_state_list=get_model("AreaSparesManager").objects.get(user__user=request.user).state.all()
            state_list = []
            for state in asm_state_list:
                state_list.append(state.state_name)
            query_set=query_set.filter(retailer__user__state__in = state_list)
            
        return query_set
    
    def changelist_view(self, request, extra_context=None):
        extra_context = {'created_date_search': True
                        }
        return super(AccumulationRequestRetailerAdmin, self).changelist_view(request, extra_context=extra_context)


class MemberForm(forms.ModelForm):
    class Meta:
        model = get_model("Member")
    
    def __init__(self, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)
        for field in constants.MANDATORY_MECHANIC_FIELDS:
            self.fields[field].label = self.fields[field].label + ' * '
            
    def clean(self):
        self.cleaned_data = super(MemberForm, self).clean()
        if 'phone_number' in self.cleaned_data:
            retailer = get_model('Retailer').objects.filter(mobile=self.cleaned_data['phone_number'])
            if retailer:
                phone_number = self.cleaned_data['phone_number'].strip()
                if retailer[0].mobile[-10:] == phone_number[-10:]:
                    raise forms.ValidationError("Mobile number already exist.")
                
        return self.cleaned_data
            

class MemberAdmin(GmModelAdmin):
    list_filter = ('form_status',)
    form = MemberForm
    search_fields = ('mechanic_id', 'permanent_id',
                     'phone_number', 'first_name',
                     'state__state_name', 'district')
    list_display = ('get_mechanic_id','first_name', 'date_of_birth',
                    'phone_number', 'shop_name', 'district',
                    'state', 'pincode', 'registered_by_distributor', 'is_pt')
    readonly_fields = ('image_tag',)

    def suit_row_attributes(self, obj):
        class_map = {
            'Incomplete': 'error'
        }
        css_class = class_map.get(str(obj.form_status))
        if css_class:
            return {'class': css_class}
        
    def queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        query_set = self.model._default_manager.get_query_set()
        if request.user.groups.filter(name=Roles.AREASPARESMANAGERS).exists():
            asm_state_list=get_model("AreaSparesManager").objects.get(user__user=request.user).state.all()
            query_set=query_set.filter(state=asm_state_list)

        return query_set

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ('mechanic_id','form_status', 'sent_sms', 'total_points', 'sent_to_sap', 'permanent_id', 'download_detail')
        form = super(MemberAdmin, self).get_form(request, obj, **kwargs)
        return form

#     def save_model(self, request, obj, form, change):
#         if not (obj.phone_number == '' or (len(obj.phone_number) < 10)):
#             obj.phone_number=utils.mobile_format(obj.phone_number)
#         super(MemberAdmin, self).save_model(request, obj, form, change)

class CommentThreadInline(TabularInline):
    model = get_model("CommentThread")
    fields = ('created_date', 'user', 'message')
    extra = 0
    max_num = 0
    readonly_fields = ('created_date', 'user', 'message')


class RedemptionCommentForm(forms.ModelForm):
    extra_field = forms.CharField(label='comment', required=False, widget=forms.Textarea(attrs={'style':'resize: none;'}))

    def save(self, commit=True):
        extra_field = self.cleaned_data.get('extra_field', None)
        transaction_id = self.instance
        if extra_field:
            loyalty.save_comment('redemption', extra_field, transaction_id, self.current_user)
        return super(RedemptionCommentForm, self).save(commit=commit)
    
    class Meta:
        model = get_model("RedemptionRequest")

    
class RedemptionRequestAdmin(GmModelAdmin):
    readonly_fields = ('image_tag', 'transaction_id',)
    form = RedemptionCommentForm
    inlines = (CommentThreadInline,)
    list_filter = (
        ('created_date', DateFieldListFilter),
    )
    search_fields = ('member__phone_number', 'product__product_id', 'partner__partner_id', 'transaction_id')
    list_display = ('member',  'get_mechanic_name',
                     'delivery_address', 'get_mechanic_pincode',
                     'get_mechanic_district', 'get_mechanic_state',
                     'product','get_product_description', 'created_date','due_date',
                     'expected_delivery_date', 'status', 'partner')
    
    fieldsets = (
        (None, {
            'fields': (
            'transaction_id', 'delivery_address', 'expected_delivery_date', 'status',
            'tracking_id', 'due_date', 'approved_date', 'shipped_date',
            'delivery_date', 'pod_number', 'product', 'member',
            'partner', 'image_url', 'image_tag',
            'extra_field','points')
        }),
        )   
    

    def queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        query_set = self.model._default_manager.get_query_set()
        if request.user.groups.filter(name=Roles.RPS).exists():
            query_set=query_set.filter(is_approved=True, packed_by=request.user.username)
        elif request.user.groups.filter(name=Roles.LPS).exists():
            query_set=query_set.filter(status__in=constants.LP_REDEMPTION_STATUS, partner__user=request.user)
        elif request.user.groups.filter(name=Roles.AREASPARESMANAGERS).exists():
            asm_state_list=get_model("AreaSparesManager").objects.get(user__user=request.user).state.all()
            query_set=query_set.filter(member__state=asm_state_list)
        
        return query_set

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ('is_approved', 'packed_by', 'refunded_points', 'resolution_flag')
        form = super(RedemptionRequestAdmin, self).get_form(request, obj, **kwargs)
        form = copy.deepcopy(form)
        if request.user.groups.filter(name=Roles.RPS).exists():
            form.base_fields['status'].choices = constants.GP_REDEMPTION_STATUS
        elif request.user.groups.filter(name=Roles.LPS).exists():
            form.base_fields['status'].choices = constants.LP_REDEMPTION_STATUS
        else:
            form.base_fields['status'].choices = constants.REDEMPTION_STATUS
        form.current_user=request.user
        return form

    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data and obj.status!='Rejected':
            date = loyalty.set_date("Redemption", obj.status)
            obj.due_date = date['due_date']
            obj.expected_delivery_date = date['expected_delivery_date']
            obj.resolution_flag = False
        if 'status' in form.changed_data:
            if obj.status=='Approved':
                obj.is_approved=True
                partner=None
                packed_by=None
                partner_list = get_model("Partner").objects.all()
                if partner_list:
                    partner=partner_list[0]
                    packed_by=partner.user.user.username
                obj.partner=partner
                obj.packed_by=packed_by
                obj.approved_date=datetime.datetime.now()
            elif obj.status in ['Rejected', 'Open'] :
                obj.is_approved=False
                obj.packed_by=None
            elif obj.status=='Shipped':
                obj.shipped_date=datetime.datetime.now()
            elif obj.status=='Delivered':
                obj.delivery_date=datetime.datetime.now()
        if 'status' in form.changed_data:
            if obj.status=='Approved' and obj.refunded_points:
                loyalty.update_points(obj.member, redeem=obj.product.points, refund_flag=True)
                obj.refunded_points = False
            elif obj.status=='Rejected' and not obj.refunded_points:
                loyalty.update_points(obj.member, accumulate=obj.product.points, refund_flag=True)
                obj.refunded_points = True
        super(RedemptionRequestAdmin, self).save_model(request, obj, form, change)
        if 'status' in form.changed_data and obj.status in constants.STATUS_TO_NOTIFY:
            loyalty.send_request_status_sms(obj)
        if 'partner' in form.changed_data and obj.partner:
            loyalty.send_mail_to_partner(obj)

    def suit_row_attributes(self, obj):
        class_map = {
            'Rejected': 'error',
            'Approved': 'success',
            'Delivered': 'warning',
            'Packed': 'info',
            'Shipped': 'info',
        }
        css_class = class_map.get(str(obj.status))
        if css_class:
            return {'class': css_class}
        
        
class CommentThreadRetailerInline(TabularInline):
    model = get_model("CommentThreadRetailer")
    fields = ('created_date', 'user', 'message')
    extra = 0
    max_num = 0
    readonly_fields = ('created_date', 'user', 'message')

class RedemptionCommentRetailerForm(forms.ModelForm):
    extra_field = forms.CharField(label='comment', required=False, widget=forms.Textarea(attrs={'style':'resize: none;'}))

    def save(self, commit=True):
        extra_field = self.cleaned_data.get('extra_field', None)
        transaction_id = self.instance
        if extra_field:
            loyalty.save_comment_retailer('redemption', extra_field, transaction_id, self.current_user)
        return super(RedemptionCommentRetailerForm, self).save(commit=commit)
    
    class Meta:
        model = get_model("RedemptionRequestRetailer")

    
class RedemptionRequestRetailerAdmin(GmModelAdmin):
    readonly_fields = ('image_tag', 'transaction_id',)
    form = RedemptionCommentRetailerForm
    inlines = (CommentThreadRetailerInline,)
    list_filter = (
        ('created_date', DateFieldListFilter),
    )
    search_fields = ('product__product_id', 'partner__partner_id','retailer__user__state','retailer__retailer_id','retailer__retailer_permanent_id')

    list_display = ('get_retailer_id','get_retailer_name','delivery_address',
                    'get_retailer_pincode','get_retailer_district','get_retailer_state',
                    'get_product_id','get_product_description', 'created_date','due_date','expected_delivery_date',
                    'status', 'get_partner'
                     )
    
    fieldsets = (
        (None, {
            'fields': (
            'transaction_id', 'delivery_address', 'expected_delivery_date', 'status',
            'tracking_id', 'due_date', 'approved_date', 'shipped_date',
            'delivery_date', 'pod_number', 'product', 'retailer',
            'partner', 'image_url', 'image_tag',
            'extra_field', 'points')
        }),
        )   
    
    def get_retailer_id(self, obj):
        if obj.retailer.retailer_permanent_id:
            return obj.retailer.retailer_permanent_id
        return obj.retailer.retailer_id
    get_retailer_id.short_description = 'Retailer ID'
    
    def get_retailer_name(self, obj):
        return obj.retailer.retailer_name
    get_retailer_name.short_description = 'Retailer Name'
    
    def get_retailer_pincode(self, obj):
        return obj.retailer.user.pincode
    get_retailer_pincode.short_description = 'Pincode'
     
    def get_retailer_district(self, obj):
        return obj.retailer.district
    get_retailer_district.short_description = 'District'
     
    def get_retailer_state(self, obj):
        return obj.retailer.user.state
    get_retailer_state.short_description = 'State'
    
    def get_product_id(self, obj):
        return obj.product.product_id
    get_product_id.short_description = 'Product'
    
    def get_product_description(self, obj):
        return obj.product.description
    get_product_description.short_description = 'Product Description'
    
    def get_partner(self, obj):
        return obj.partner
    get_partner.short_description = 'Partner'
    

    def queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        query_set = self.model._default_manager.get_query_set()
        if request.user.groups.filter(name=Roles.RPS).exists():
            query_set=query_set.filter(is_approved=True, packed_by=request.user.username)
        elif request.user.groups.filter(name=Roles.LPS).exists():
            query_set=query_set.filter(status__in=constants.LP_REDEMPTION_STATUS, partner__user=request.user)
        elif request.user.groups.filter(name=Roles.AREASPARESMANAGERS).exists():
            asm_state_list=get_model("AreaSparesManager").objects.get(user__user=request.user).state.all()
            state_list = []
            for state in asm_state_list:
                state_list.append(state.state_name)
            query_set=query_set.filter(retailer__user__state__in = state_list)

        return query_set

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ('is_approved', 'packed_by', 'refunded_points', 'resolution_flag')
        form = super(RedemptionRequestRetailerAdmin, self).get_form(request, obj, **kwargs)
        form = copy.deepcopy(form)
        if request.user.groups.filter(name=Roles.RPS).exists():
            form.base_fields['status'].choices = constants.GP_REDEMPTION_STATUS
        elif request.user.groups.filter(name=Roles.LPS).exists():
            form.base_fields['status'].choices = constants.LP_REDEMPTION_STATUS
        else:
            form.base_fields['status'].choices = constants.REDEMPTION_STATUS
        form.current_user=request.user
        return form

    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data and obj.status!='Rejected':
            date = loyalty.set_date("Redemption", obj.status)
            obj.due_date = date['due_date']
            obj.expected_delivery_date = date['expected_delivery_date']
            obj.resolution_flag = False
        if 'status' in form.changed_data:
            if obj.status=='Approved':
                obj.is_approved=True
                partner=None
                packed_by=None
                partner_list = get_model("Partner").objects.all()
                if len(partner_list)==1:
                    partner=partner_list[0]
                    packed_by=partner.user.user.username
                obj.partner=partner
                obj.packed_by=packed_by
                obj.approved_date=datetime.datetime.now()
            elif obj.status in ['Rejected', 'Open'] :
                obj.is_approved=False
                obj.packed_by=None
            elif obj.status=='Shipped':
                obj.shipped_date=datetime.datetime.now()
            elif obj.status=='Delivered':
                obj.delivery_date=datetime.datetime.now()
        if 'status' in form.changed_data:
            if obj.status=='Approved' and obj.refunded_points:
                loyalty.update_points_retailer(obj.retailer, redeem=obj.product.points, refund_flag=True)
                obj.refunded_points = False
            elif obj.status=='Rejected' and not obj.refunded_points:
                loyalty.update_points_retailer(obj.retailer, accumulate=obj.product.points, refund_flag=True)
                obj.refunded_points = True
        super(RedemptionRequestRetailerAdmin, self).save_model(request, obj, form, change)
        if 'status' in form.changed_data and obj.status in constants.STATUS_TO_NOTIFY:
            loyalty.send_request_status_sms_retailer(obj)
        #### need to check the mail not sending #########
        if 'partner' in form.changed_data and obj.partner:
            loyalty.send_mail_to_partner_for_retailer(obj)

    def suit_row_attributes(self, obj):
        class_map = {
            'Rejected': 'error',
            'Approved': 'success',
            'Delivered': 'warning',
            'Packed': 'info',
            'Shipped': 'info',
        }
        css_class = class_map.get(str(obj.status))
        if css_class:
            return {'class': css_class}


class WelcomeKitCommentForm(forms.ModelForm):
    extra_field = forms.CharField(label='comment', required=False, widget=forms.Textarea(attrs={'style':'resize: none;'}))

    def save(self, commit=True):
        extra_field = self.cleaned_data.get('extra_field', None)
        transaction_id = self.instance
        if extra_field:
            loyalty.save_comment('welcome_kit', extra_field, transaction_id, self.current_user)
        return super(WelcomeKitCommentForm, self).save(commit=commit)
    
    class Meta:
        model = get_model("WelcomeKit")
       
class WelcomeKitAdmin(GmModelAdmin):
    list_filter = ('status',)
    form = WelcomeKitCommentForm
    inlines = (CommentThreadInline,)
    search_fields = ('member__phone_number','member__mechanic_id', 'partner__partner_id', 'transaction_id')
    list_display = ('get_members_mechanic_id',  'get_mechanic_name',
                     'delivery_address', 'get_mechanic_pincode',
                     'get_mechanic_district', 'get_mechanic_state',
                     'created_date','due_date', 'expected_delivery_date', 'status', 'partner')
    readonly_fields = ('image_tag', 'transaction_id')
    fieldsets = (
    (None, {
        'fields': (
        'transaction_id', 'delivery_address',
        'expected_delivery_date', 'status',
        'tracking_id', 'due_date', 'shipped_date',
        'delivery_date', 'pod_number', 'member',
        'partner', 'image_url', 'image_tag',
        'extra_field')
    }),
    ) 
    
    def save_model(self, request, obj, form, change):
        if 'partner' in form.changed_data and obj.partner and obj.status in ['Accepted', 'Open']:
                obj.packed_by=obj.partner.user.user.username
        if 'status' in form.changed_data:
            if obj.status=='Shipped':
                obj.shipped_date=datetime.datetime.now()
            elif obj.status=='Delivered':
                obj.delivery_date=datetime.datetime.now()
        date = loyalty.set_date("Welcome Kit", obj.status)
        obj.due_date = date['due_date']
        obj.expected_delivery_date = date['expected_delivery_date']
        obj.resolution_flag = False
        super(WelcomeKitAdmin, self).save_model(request, obj, form, change)
        if 'status' in form.changed_data and obj.status=="Shipped":
            loyalty.send_welcome_kit_delivery(obj)
        if 'partner' in form.changed_data and obj.partner:
            loyalty.send_welcome_kit_mail_to_partner(obj)

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ('resolution_flag','packed_by')
        form = super(WelcomeKitAdmin, self).get_form(request, obj, **kwargs)
        form.current_user=request.user
        return form

    def suit_row_attributes(self, obj):
        class_map = {
            'Accepted': 'success',
            'Packed': 'info',
            'Shipped': 'info',
            'Delivered': 'warning'
        }
        css_class = class_map.get(str(obj.status))
        if css_class:
            return {'class': css_class}
        
    def queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        query_set = self.model._default_manager.get_query_set()
        if request.user.groups.filter(name=Roles.RPS).exists():
            query_set=query_set.filter(packed_by=request.user.username)
        elif request.user.groups.filter(name=Roles.LPS).exists():
            query_set=query_set.filter(status__in=constants.LP_REDEMPTION_STATUS, partner__user=request.user)
        elif request.user.groups.filter(name=Roles.AREASPARESMANAGERS).exists():
            asm_state_list=get_model("AreaSparesManager").objects.get(user__user=request.user).state.all()
            query_set=query_set.filter(member__state=asm_state_list)

        return query_set
    
    
class WelcomeKitCommentRetailerForm(forms.ModelForm):
    extra_field = forms.CharField(label='comment', required=False, widget=forms.Textarea(attrs={'style':'resize: none;'}))

    def save(self, commit=True):
        extra_field = self.cleaned_data.get('extra_field', None)
        transaction_id = self.instance
        if extra_field:
            loyalty.save_comment_retailer('welcome_kit', extra_field, transaction_id, self.current_user)
        return super(WelcomeKitCommentRetailerForm, self).save(commit=commit)
    
    class Meta:
        model = get_model("WelcomeKitRetailer")
       
class WelcomeKitRetailerAdmin(GmModelAdmin):
    list_filter = ('status',)
    form = WelcomeKitCommentRetailerForm
    inlines = (CommentThreadRetailerInline,)
    search_fields = ('retailer__retailer_id','retailer__retailer_permanent_id','partner__partner_id', 'transaction_id')
    list_display = ('get_retailer_retailer_id',  'get_retailer_name',
                     'delivery_address', 'get_retailer_pincode',
                    'get_retailer_district', 'get_retailer_state',
                    'created_date','due_date', 'expected_delivery_date', 'status', 'partner')
    readonly_fields = ('image_tag', 'transaction_id')
    fieldsets = (
    (None, {
        'fields': (
        'transaction_id', 'delivery_address',
        'expected_delivery_date', 'status',
        'tracking_id', 'due_date', 'shipped_date',
        'delivery_date', 'pod_number', 'retailer',
        'partner', 'image_url', 'image_tag',
        'extra_field')
    }),
    ) 
    
    def get_retailer_retailer_id(self,obj):
        if obj.retailer.retailer_permanent_id:
            return obj.retailer.retailer_permanent_id
        return obj.retailer.retailer_id
    get_retailer_retailer_id.short_description ="Retailer ID"
    
    def get_retailer_name(self,obj):
        return obj.retailer.retailer_name
    get_retailer_name.short_description ="Retailer Name"
    
    def get_retailer_pincode(self,obj):
        return obj.retailer.user.pincode
    get_retailer_pincode.short_description ="Pincode"
    
    def get_retailer_district(self,obj):
        return obj.retailer.district
    get_retailer_district.short_description ="District"
    
    def get_retailer_state(self,obj):
        return obj.retailer.user.state
    get_retailer_state.short_description ="State"

    
    def save_model(self, request, obj, form, change):
        if 'partner' in form.changed_data and obj.partner and obj.status in ['Accepted', 'Open']:
                obj.packed_by=obj.partner.user.user.username
        if 'status' in form.changed_data:
            if obj.status=='Shipped':
                obj.shipped_date=datetime.datetime.now()
            elif obj.status=='Delivered':
                obj.delivery_date=datetime.datetime.now()
        date = loyalty.set_date("Welcome Kit", obj.status)
        obj.due_date = date['due_date']
        obj.expected_delivery_date = date['expected_delivery_date']
        obj.resolution_flag = False
        super(WelcomeKitRetailerAdmin, self).save_model(request, obj, form, change)
        if 'status' in form.changed_data and obj.status=="Shipped":
            loyalty.send_welcome_kit_delivery_retailer(obj)
        ####### NEED TO CHECK WHY MAIL NOT GOING########################################
        if 'partner' in form.changed_data and obj.partner:
            loyalty.send_welcome_kit_mail_to_partner_retailer(obj)

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ('resolution_flag','packed_by')
        form = super(WelcomeKitRetailerAdmin, self).get_form(request, obj, **kwargs)
        form.current_user=request.user
        return form

    def suit_row_attributes(self, obj):
        class_map = {
            'Accepted': 'success',
            'Packed': 'info',
            'Shipped': 'info',
            'Delivered': 'warning'
        }
        css_class = class_map.get(str(obj.status))
        if css_class:
            return {'class': css_class}
        
    def queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        query_set = self.model._default_manager.get_query_set()
        if request.user.groups.filter(name=Roles.RPS).exists():
            query_set=query_set.filter(packed_by=request.user.username)
        elif request.user.groups.filter(name=Roles.LPS).exists():
            query_set=query_set.filter(status__in=constants.LP_REDEMPTION_STATUS, partner__user=request.user)
        elif request.user.groups.filter(name=Roles.AREASPARESMANAGERS).exists():
            asm_state_list=get_model("AreaSparesManager").objects.get(user__user=request.user).state.all()
            state_list = []
            for state in asm_state_list:
                state_list.append(state.state_name)
            query_set=query_set.filter(retailer__user__state__in = state_list)

        return query_set
#######################End of Welcome Kit added for Retailer#########################################################

class LoyaltySlaAdmin(GmModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
        'status','action',
        ('reminder_time', 'reminder_unit'),
        ('resolution_time', 'resolution_unit'), 
        ('member_resolution_time','member_resolution_unit'))
        }),
        )    
    def reminder_time(self):
        return str(self.reminder_time) + ' ' + self.reminder_unit
    
    def resolution_time(self):
        return str(self.resolution_time) + ' ' + self.resolution_unit
    
    def member_resolution_time(self):
        return str(self.member_resolution_time) + ' ' + self.member_resolution_unit

    list_display = ('status','action', reminder_time, resolution_time, member_resolution_time)
    
class ConstantAdmin(GmModelAdmin):
    search_fields = ('constant_name',  'constant_value')
    list_display = ('constant_name',  'constant_value',)
    
########################These are added for Brand movement category detail in retailer#######################################
class NameTopTwoMechFromCounterInline(TabularInline):
    model = get_model('NameTopTwoMechFromCounter')
    extra = 1
    fields = ('retailer','Name_of_mechanic','mobile_no_mechanic', 'Name_of_reborer','mobile_no_reborer')
    
class BrandMovementDetailRetailerInline(TabularInline):
    model = get_model('BrandMovementDetailRetailer')
    extra = 1
    fields = ('retailer','category_name','top_2selling_parts_from_counter', 'description','top_2competitor_brands')

class BrandMovementDetailCategoryRetailerAdmin(GmModelAdmin):
    groups_update_not_allowed = [Roles.NATIONALSPARESMANAGERS,Roles.AREASPARESMANAGERS]
    search_fields = ('category_name',)
    list_display = ('category_name',)
    inlines = (BrandMovementDetailRetailerInline,)
    
class SellingPartsRetailerAdmin(GmModelAdmin):
    groups_update_not_allowed = [Roles.NATIONALSPARESMANAGERS,Roles.AREASPARESMANAGERS]
    search_fields = ('part_name',)
    list_display = ('part_name',)
    inlines = (BrandMovementDetailRetailerInline,)


    
###############################################################

class RetailerForm(forms.ModelForm):
    
    class Meta:
        model = get_model('Retailer')
        exclude = ['approved', 'rejected_reason',  'retailer_code', 'retailer_permanent_id','retailer_id','form_status']

    def clean(self):
        self.cleaned_data = super(RetailerForm, self).clean()
        if 'mobile' in self.cleaned_data:
            mechanic = get_model('Member').objects.filter(phone_number=self.cleaned_data['mobile'])
            if mechanic:
                if mechanic[0].phone_number[-10:] == self.cleaned_data['mobile'][-10:]:
                    raise forms.ValidationError("Mobile number already exist.")
        
        return self.cleaned_data
        
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(RetailerForm, self).__init__(*args, **kwargs)
        self.fields['profile'].widget = TextInput(attrs={'placeholder': 'Retailer'})

class RetailerAdmin(GmModelAdmin):
    groups_update_not_allowed = [Roles.NATIONALSPARESMANAGERS,Roles.AREASPARESMANAGERS]
    form = RetailerForm
    search_fields = ('retailer_name', 'retailer_town', 'billing_code','territory','mobile')
    list_display = ('retailer_code', 'retailer_billing_code', 'retailer_user_name',
                    'user_territory', 'town', 'pincode', 'user_mobile',
                    'user_email', 'distributor_name', 'Status')
    exclude = []
    inlines = (NameTopTwoMechFromCounterInline, BrandMovementDetailRetailerInline)
    
    
    def suit_cell_attributes(self, obj, column):
        if column == 'status':
            return {'width': '500px'}
    
    def get_form(self, request, obj=None, **kwargs):
        ModelForm = super(RetailerAdmin, self).get_form(request, obj, **kwargs)
        class ModelFormMetaClass(ModelForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return ModelForm(*args, **kwargs)
        return ModelFormMetaClass
    
    def get_actions(self, request):
        #in case of administrator only, grant him the approve retailer option
        if self.param.groups.filter(name__in =['SuperAdmins', 'Admins', 'SFAAdmins', 'AreaSparesManagers']).exists():
            self.actions.append('approve')
        actions = super(RetailerAdmin, self).get_actions(request)
        return actions
    
    def queryset(self, request):
        query_set = self.model._default_manager.get_query_set()
        if request.user.groups.filter(name=Roles.AREASPARESMANAGERS).exists():
            asm_state_list=AreaSparesManager.objects.get(user__user__username=request.user).state.all()
            state_list = []
            for state in asm_state_list:
                state_list.append(state.state_name)
            query_set=query_set.filter(user__state__in = state_list)
        return query_set

    def changelist_view(self, request, extra_context=None):
        self.param = request.user
        return super(RetailerAdmin, self).changelist_view(request)
    
#      def approve(self, request, queryset):
#         queryset.update(approved=constants.STATUS['APPROVED'])
#         for retailer in queryset:
#             try:
#                 send_email(sender = constants.FROM_EMAIL_ADMIN, receiver = retailer.email, 
#                        subject = constants.APPROVE_RETAILER_SUBJECT, body = '',
#                        message = constants.APPROVE_RETAILER_MESSAGE)
#             except Exception as e:
#                 logger.error('Mail is not sent. Exception occurred ',e)
#     approve.short_description = 'Approve Selected Retailers'

    def Status(self, obj):
        return obj.status
    Status.short_description = 'Status'
    
    def retailer_billing_code(self, obj):
        return obj.billing_code
    retailer_billing_code.short_description = 'Retailer billing code'
    
    def retailer_user_name(self, obj):
        return obj.retailer_name
    retailer_user_name.short_description = 'retailer name'
    
    def user_territory(self, obj):
        return obj.territory
    user_territory.short_description = 'territory'
    
    def town(self,obj):
        return obj.retailer_town
    town.short_description = 'Town/ City'
    
    def pincode(self, obj):
        return obj.user.pincode
    
    def city(self, obj):
        return obj.retailer_town
    
    def phone(self, obj):
        return obj.user.phone_number
    
    def user_mobile(self, obj):
        return obj.mobile
    user_mobile.short_description = 'mobile'

    def user_email(self, obj):
        return obj.email
    user_email.short_description = 'email'

    def distributor_code(self, obj):
        return obj.distributor.distributor_id
    distributor_code.short_description = 'Distributor Code'
    
    def distributor_name(self, obj):
        return obj.distributor.name
    distributor_name.short_description = 'Distributor Name'
    
    def save_model(self, request, obj, form, change):
        form_status=True
        form_data = form.cleaned_data
        
        for field in form_data:
            if field in constants.MANDATORY_RETAILER_FIELDS and not form_data.get(field):
                form_status = False
                
        if form_status == False:
            obj.form_status='Incomplete'
            obj.save()
        else:
            obj.form_status='Complete'
            obj.save()
        
        if request.user.groups.filter(name__in=[Roles.DISTRIBUTORS,Roles.DISTRIBUTORSALESREP,Roles.SUPERADMINS]).exists():
            obj.approved = constants.STATUS['WAITING_FOR_APPROVAL']
            try:
                retailer = Retailer.objects.filter().order_by("-id")[0]
                obj.retailer_code = str(int(retailer.retailer_code) + \
                                        constants.RETAILER_SEQUENCE_INCREMENT)
            except:
                obj.retailer_code = str(constants.RETAILER_SEQUENCE)
                
                
            super(RetailerAdmin, self).save_model(request, obj, form, change)
            
#     def status(self, obj):
#         #Added retailer by distributor/distributorstaff must be approved by the ASM/admin
#         #he can also be rejected on some conditions
#         if obj.approved == constants.STATUS['APPROVED']:
#             return 'Approved'
#         elif obj.approved == constants.STATUS['WAITING_FOR_APPROVAL'] :
#             if self.param.groups.filter(name__in = \
#                                     ['SuperAdmins', 'Admins','SFAAdmins', 'AreaSparesManagers']).exists():
# 
#                 
# #                 <a href="" class="btn btn-info" data-toggle="modal" data-target="#downloadModal">Download welcome kit details</a>
#                 #reject_button = "<a  class='btn btn-success' data-toggle='modal'  href=\"/admin/retailer/approve_retailer/retailer_id/"+str(obj.id)+"\">Approve</a>&nbsp;<input type=\"button\"  class='btn btn-danger' data-toggle='modal'  id=\"button_reject\" value=\"Reject\" onclick=\"popup_reject(\'"+str(obj.id)+"\',\'"+obj.retailer_name+"\',\'"+obj.email+"\',\'"+obj.distributor.name+"\'); return false;\">"
#                 reject_button = "<a  class='btn btn-success' data-toggle='modal'  href=\"/admin/retailer/approve_retailer/retailer_id/"+str(obj.id)+"\">Approve</a>&nbsp;<input type=\"button\"  class='btn btn-danger' data-toggle='modal'  id=\"button_reject\" value=\"Reject\" onclick=\"popup_reject(\'"+str(obj.id)+"\',\'"+obj.retailer_name+"\',\'"+obj.email+"\'); return false;\">"
#                 #reject_button = "<input type=\"button\" id=\"button_reject\" value=\"Reject\" onclick=\"popup_reject(); return false;\">"
#                 return mark_safe(reject_button)
#             else:
#                 return 'Waiting for approval'
#         elif obj.approved == constants.STATUS['REJECTED'] :
#             if self.param.groups.filter(name__in =['SuperAdmins', 'Admins', 'AreaSparesManagers']).exists():
#                 return 'Rejected'
#             else:
#                 if self.param.groups.filter(name__in =['Distributors', 'DistributorStaffs']).exists():
#                     rejected_reason = "<input type=\"button\" value=\"Rejected Reason\" onclick=\"popup_rejected_reason(\'"+str(obj.id)+"\',\'"+obj.retailer_name+"\',\'"+obj.rejected_reason+"\'); return false;\">"
#                     return mark_safe(rejected_reason)
#     status.allow_tags = True
##################### ENDRETAILER###########################

def get_admin_site_custom(brand):
    brand_admin = CoreAdminSite(name=brand)
    
    brand_admin.register(User, UserAdmin)
    brand_admin.register(Group, GroupAdmin)
    brand_admin.register(get_model("UserProfile", brand), UserProfileAdmin)
    
    if brand not in ['core']:
        brand_admin.register(get_model("Dealer", brand), DealerAdmin)
        brand_admin.register(get_model("AuthorizedServiceCenter", brand), AuthorizedServiceCenterAdmin)
        brand_admin.register(get_model("ServiceAdvisor", brand), ServiceAdvisorAdmin)
        
        brand_admin.register(get_model("BrandProductCategory", brand), BrandProductCategoryAdmin)
        brand_admin.register(get_model("ProductType", brand), ProductTypeAdmin)
        brand_admin.register(DispatchedProduct, ListDispatchedProduct)
        brand_admin.register(get_model("ProductData", brand), ProductDataAdmin)
        brand_admin.register(get_model("CouponData", brand), CouponAdmin)
        
        brand_admin.register(get_model("ASCTempRegistration", brand), ASCTempRegistrationAdmin)
        brand_admin.register(get_model("SATempRegistration", brand), SATempRegistrationAdmin)
        brand_admin.register(get_model("CustomerTempRegistration", brand), CustomerTempRegistrationAdmin)
        
    brand_admin.register(get_model("SMSLog", brand), SMSLogAdmin)
    brand_admin.register(get_model("EmailLog", brand), EmailLogAdmin)
    brand_admin.register(get_model("DataFeedLog", brand), FeedLogAdmin)
    brand_admin.register(get_model("FeedFailureLog", brand))
    
    brand_admin.register(get_model("NationalSparesManager", brand), NSMAdmin)
    brand_admin.register(get_model("AreaSparesManager", brand), ASMAdmin)
    brand_admin.register(get_model("Distributor", brand), DistributorAdmin)
    brand_admin.register(get_model("Member", brand), MemberAdmin)
    
    brand_admin.register(get_model("SparePartMasterData", brand), SparePartMasterAdmin)
    brand_admin.register(get_model("SparePartUPC", brand), SparePartUPCAdmin)
    brand_admin.register(get_model("SparePartPoint", brand), SparePartPointAdmin)
    brand_admin.register(get_model("AccumulationRequest", brand), AccumulationRequestAdmin)
    brand_admin.register(get_model("LoyaltySLA", brand), LoyaltySlaAdmin)
    
    brand_admin.register(get_model("Partner", brand), PartnerAdmin)
    brand_admin.register(get_model("ProductCatalog", brand), ProductCatalogAdmin)
    brand_admin.register(get_model("RedemptionRequest", brand), RedemptionRequestAdmin)
    brand_admin.register(get_model("WelcomeKit", brand), WelcomeKitAdmin)
    
    brand_admin.register(get_model("EmailTemplate", brand), EmailTemplateAdmin)
    brand_admin.register(get_model("MessageTemplate", brand), MessageTemplateAdmin)
    brand_admin.register(get_model("SLA", brand), SlaAdmin)
    brand_admin.register(get_model("ServiceDeskUser", brand), ServiceDeskUserAdmin)
    brand_admin.register(get_model("Service", brand), ServiceAdmin)
    brand_admin.register(get_model("ServiceType", brand))
    brand_admin.register(get_model("Constant", brand), ConstantAdmin)
    brand_admin.register(get_model("Feedback", brand))
    brand_admin.register(get_model("Territory", brand))
    brand_admin.register(get_model("BrandDepartment", brand))
    brand_admin.register(get_model("DepartmentSubCategories", brand))
    
    brand_admin.register(get_model("Retailer", brand), RetailerAdmin)
    brand_admin.register(get_model("AccumulationRequestRetailer", brand), AccumulationRequestRetailerAdmin)
    brand_admin.register(get_model("RedemptionRequestRetailer", brand), RedemptionRequestRetailerAdmin)
    brand_admin.register(get_model("WelcomeKitRetailer", brand), WelcomeKitRetailerAdmin)
    brand_admin.register(get_model("BrandMovementDetailCategoryRetailer", brand), BrandMovementDetailCategoryRetailerAdmin)
    brand_admin.register(get_model("SellingPartsRetailer", brand), SellingPartsRetailerAdmin)
    
    
    return brand_admin

brand_admin = get_admin_site_custom("core")
