import copy
import datetime
from django import forms
from django.contrib.admin import AdminSite, TabularInline
from django.contrib.auth.models import User, Group
from django.contrib.admin import ModelAdmin
from django.contrib.admin.views.main import ChangeList, ORDER_VAR
from django.contrib.admin import DateFieldListFilter
from django import forms

from gladminds.bajajib import models
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

class BajajibAdminSite(AdminSite):
    pass


class UserProfileAdmin(GmModelAdmin):
    search_fields = ('user__username', 'phone_number',)
    list_display = ('user', 'phone_number', 'status', 'address',
                    'state', 'country', 'pincode', 'date_of_birth', 'gender')
    readonly_fields = ('image_tag',)

class CountryDistributorAdmin(GmModelAdmin):
    search_fields = ('distributor_id',)
    list_display = ('distributor_id', 'get_user', 'get_profile_number', 'country')
    
class MainCountryDealerAdmin(GmModelAdmin):
    search_fields = ('dealer_id',)
    list_display = ('dealer_id', 'get_user', 'get_profile_number', 'country')
    
class DealerAdmin(GmModelAdmin):
    search_fields = ('dealer_id',)
    list_display = ('dealer_id', 'get_user', 'get_profile_number', 'get_profile_address')

class ServiceAdvisorAdmin(GmModelAdmin):
    search_fields = ('service_advisor_id', 'dealer__dealer_id')
    list_display = ('service_advisor_id', 'get_user', 'get_profile_number', 'get_profile_address', 'dealer', 'status')

class BrandProductCategoryAdmin(GmModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'description')

class ProductTypeAdmin(GmModelAdmin):
    search_fields = ('product_type',)
    list_display = ('id', 'product_type',\
                    'image_url', 'is_active')

class DispatchedProduct(models.ProductData):

    class Meta:
        proxy = True

class ListDispatchedProduct(GmModelAdmin):
    search_fields = ('product_id', 'dealer_id__dealer_id')
    list_display = (
        'product_id', 'sku_code', 'engine', 'UCN', 'dealer', "invoice_date")
    list_per_page = 50

    def queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        utils.get_search_query_params(request, self)
        query_set = self.model._default_manager.get_query_set()
        query_set = query_set.select_related('').prefetch_related('dealer', 'product_type')

        return query_set

    def UCN(self, obj):
        coupons = models.CouponData.objects.filter(product=obj.id)
        if coupons:
            return ' | '.join([str(ucn.unique_service_coupon) for ucn in coupons])
        else:
            return None
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(ListDispatchedProduct, self).get_form(request, obj, **kwargs)
        return form

    def changelist_view(self, request, extra_context=None):
        custom_search_mapping = {'Product Id' : 'product_id',
                                 'Dealer Id': 'dealer__dealer_id',}
        extra_context = {'custom_search': True, 'custom_search_fields': custom_search_mapping
                        }
        return super(ListDispatchedProduct, self).changelist_view(request, extra_context=extra_context)


class Couponline(TabularInline):
    model = models.CouponData
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
        coupons = models.CouponData.objects.filter(product=obj.id)
        if coupons:
            return ' | '.join([str(ucn.unique_service_coupon) for ucn in coupons])
        else:
            return None

    def service_type(self, obj):
        gm_coupon_data_obj = models.CouponData.objects.filter(product=obj.id)
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
            sa = models.ServiceAdvisor.objects.filter(service_advisor_id=obj.service_advisor.service_advisor_id).select_related('dealer', 'authorizedservicecenter')[0]
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
    
    def queryset(self, request):
        query_set = self.model._default_manager.get_query_set()
        if request.user.groups.filter(name=Roles.CTSADMIN).exists():
            query_set=query_set.filter(feed_type__in=['ContainerTracker Feed', 'CTS Feed'])
        return query_set
        
    def changelist_view(self, request, extra_context=None):
        extra_context = {'created_date_search': True
                        }
        return super(FeedLogAdmin, self).changelist_view(request, extra_context=extra_context)

class MessageTemplateAdmin(GmModelAdmin):
    search_fields = ('template_key', 'template')
    list_display = ('template_key', 'template', 'description')

class EmailTemplateAdmin(GmModelAdmin):
    search_fields = ('template_key', 'sender', 'receiver', 'subject')
    list_display = ('template_key', 'sender', 'receivers', 'subject')

    def receivers(self, obj):
        return ' | '.join(obj.receiver.split(','))

class ConstantAdmin(GmModelAdmin):
    search_fields = ('constant_name',  'constant_value')
    list_display = ('constant_name',  'constant_value',)
    
    def save_model(self, request, obj, form, change):
        constant_data = models.Constant.objects.filter(constant_name=obj.constant_name,country_id=obj.country_id)
        if constant_data:
            self.message_user(request, "Record not added. The constant is already defined for the country specified.",
                                level=messages.ERROR)
        else:
            super(ConstantAdmin, self).save_model(request, obj, form, change)
                        
class FleetRiderAdmin(GmModelAdmin):
    search_fields = ('product',  'phone_number', 'rider_name')
    list_display = ('product',  'phone_number', 'rider_name')
    
class CountryAdmin(GmModelAdmin):
    search_fields = ('name',  'area_code')
    list_display = ('name',  'area_code',)

class ServiceDeskUserAdmin(GmModelAdmin):
    list_display = ('user_profile', 'name', 'phone_number', 'email')
    
class ServiceAdmin(GmModelAdmin):
    list_display = ('service_type', 'name', 'description')
    readonly_fields = ('file_tag',)

def get_admin_site_custom(brand):
    brand_admin = BajajibAdminSite(name=brand)
    
    brand_admin.register(User, UserAdmin)
    brand_admin.register(Group, GroupAdmin)
    brand_admin.register(get_model("UserProfile", brand), UserProfileAdmin)
    brand_admin.register(get_model("Country", brand), CountryAdmin)
    
    brand_admin.register(get_model("CountryDistributor", brand), CountryDistributorAdmin)
    brand_admin.register(get_model("MainCountryDealer", brand), MainCountryDealerAdmin)
    
    brand_admin.register(get_model("Dealer", brand), DealerAdmin)
    brand_admin.register(get_model("ServiceAdvisor", brand), ServiceAdvisorAdmin)
    
    brand_admin.register(get_model("BrandProductCategory", brand), BrandProductCategoryAdmin)
    brand_admin.register(get_model("ProductType", brand), ProductTypeAdmin)
    brand_admin.register(DispatchedProduct, ListDispatchedProduct)
    brand_admin.register(get_model("ProductData", brand), ProductDataAdmin)
    brand_admin.register(get_model("CouponData", brand), CouponAdmin)
    
    brand_admin.register(get_model("SMSLog", brand), SMSLogAdmin)
    brand_admin.register(get_model("EmailLog", brand), EmailLogAdmin)
    brand_admin.register(get_model("DataFeedLog", brand), FeedLogAdmin)
    brand_admin.register(get_model("FeedFailureLog", brand))
    
    brand_admin.register(get_model("EmailTemplate", brand), EmailTemplateAdmin)
    brand_admin.register(get_model("MessageTemplate", brand), MessageTemplateAdmin)
    brand_admin.register(get_model("Constant", brand), ConstantAdmin)
    
    brand_admin.register(get_model("FleetRider", brand), FleetRiderAdmin)
    
    brand_admin.register(get_model("ServiceDeskUser", brand), ServiceDeskUserAdmin)
    brand_admin.register(get_model("Service", brand), ServiceAdmin)
    brand_admin.register(get_model("ServiceType", brand))

    return brand_admin

brand_admin = get_admin_site_custom(GmApps.BAJAJIB)
