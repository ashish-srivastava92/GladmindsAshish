import logging
from tastypie.constants import ALL
from tastypie.authorization import Authorization
from tastypie import fields
from django.http.response import HttpResponseRedirect
from django.conf.urls import url
from django.contrib.auth.models import User
from gladminds.core.apis.base_apis import CustomBaseModelResource
from gladminds.afterbuy import models as afterbuy_models
from gladminds.settings import API_FLAG, COUPON_URL
from tastypie.utils.urls import trailing_slash
from gladminds.afterbuy.apis.brand_apis import BrandResource
from gladminds.afterbuy.apis.user_apis import ConsumerResource

logger = logging.getLogger("gladminds")

class ProductTypeResource(CustomBaseModelResource):
    class Meta:
        queryset = afterbuy_models.ProductType.objects.all()
        resource_name = "types"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'delete', 'put']
        always_return_data = True

class UserProductResource(CustomBaseModelResource):
    consumer = fields.ForeignKey(ConsumerResource, 'consumer', null=True, blank=True, full=True)
    brand = fields.ForeignKey(BrandResource, 'brand', null=True, blank=True, full=True)
    type = fields.ForeignKey(ProductTypeResource, 'type', null=True, blank=True, full=True)
    
    class Meta:
        queryset = afterbuy_models.UserProduct.objects.all()
        resource_name = "products"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'delete','put']
        always_return_data = True

    def prepend_urls(self):
        return [
                url(r"^(?P<resource_name>%s)/(?P<product_id>[\d]+)/coupons%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_product_coupons'), name="get_product_coupons" )
        ]
        
    def get_product_coupons(self, request, **kwargs):
        port = request.META['SERVER_PORT']
        product_id = kwargs.get('product_id')
        try:
            if product_id:
                product_info = afterbuy_models.UserProduct.objects.get(id=product_id)
                brand_product_id = product_info.brand_product_id
                if not API_FLAG:
                    return HttpResponseRedirect('http://'+COUPON_URL+':'+port+'/v1/coupons/?product='+brand_product_id)
                else:
                    return HttpResponseRedirect('http://'+COUPON_URL+'/v1/coupons/?product='+brand_product_id)
        except Exception as ex:
            logger.error('Invalid details')


class ProductInsuranceInfoResource(CustomBaseModelResource):
    product = fields.ForeignKey(UserProductResource, 'product', null=True, blank=True, full=True)
    class Meta:
        queryset = afterbuy_models.ProductInsuranceInfo.objects.all()
        resource_name = "insurances"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'delete', 'put']
        always_return_data = True
        filtering = {
                     "product" : ALL
                     }
    
    
class InvoiceResource(CustomBaseModelResource):
    product = fields.ForeignKey(UserProductResource, 'product', null=True, blank=True, full=True)
    class Meta:
        queryset = afterbuy_models.Invoice.objects.all()
        resource_name = "invoices"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'delete', 'put']
        always_return_data = True
        filtering = {
                     "product" : ALL
                     }
        
class LicenseResource(CustomBaseModelResource):
    product = fields.ForeignKey(UserProductResource, 'product', full=True, null=True)
    class Meta:
        queryset = afterbuy_models.License.objects.all()
        resource_name = 'licenses'
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'delete' ,'put']
        always_return_data =True
        filtering = {
                     "product" : ALL
                     }

class RegistrationCertificateResource(CustomBaseModelResource):
    product = fields.ForeignKey(UserProductResource, 'product', full=True, null=True)
    class Meta:
        queryset = afterbuy_models.RegistrationCertificate.objects.all()
        resource_name = 'registrations'
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'delete' ,'put']
        always_return_data =True
        filtering = {
                     "product" : ALL
                     }

class PollutionCertificateResource(CustomBaseModelResource):
    product = fields.ForeignKey(UserProductResource, 'product', full=True, null=True)
    class Meta:
        queryset = afterbuy_models.PollutionCertificate.objects.all()
        resource_name = 'pollution'
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'delete' ,'put']
        always_return_data =True
        filtering = {
                     "product" : ALL
                     }
        

class SupportResource(CustomBaseModelResource):
    brand = fields.ForeignKey(BrandResource, 'brand', full=True, null=True)
    brand_product_category = fields.ForeignKey(BrandResource, 'brand_product_category', full=True, null=True)
    class Meta:
        queryset = afterbuy_models.Support.objects.all()
        resource_name = 'support'
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'delete' ,'put']
        always_return_data =True
        filtering = {
                     "brand" : ALL
                     }
        
