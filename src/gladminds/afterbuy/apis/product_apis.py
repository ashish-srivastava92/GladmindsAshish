import logging
import json
from django.http.response import HttpResponse
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.authorization import DjangoAuthorization
from tastypie import fields
from django.http.response import HttpResponseRedirect
from django.conf.urls import url
from gladminds.core.apis.base_apis import CustomBaseModelResource
from gladminds.afterbuy import models as afterbuy_models
from gladminds.settings import API_FLAG, BRAND_META
from tastypie.utils.urls import trailing_slash
from gladminds.afterbuy.apis.brand_apis import BrandResource
from gladminds.afterbuy import models as afterbuy_model
from gladminds.afterbuy.apis.user_apis import ConsumerResource
from django.forms.models import model_to_dict
from gladminds.core.apis.authorization import CustomAuthorization,\
    MultiAuthorization
from gladminds.core.apis.authentication import AccessTokenAuthentication
from gladminds.core.managers.mail import send_recycle_mail
from gladminds.afterbuy.apis.validations import ProductValidation
from django.conf import settings

logger = logging.getLogger("gladminds")


class ProductTypeResource(CustomBaseModelResource):
    class Meta:
        queryset = afterbuy_models.ProductType.objects.all()
        resource_name = "product-types"
        authentication = AccessTokenAuthentication()
        authorization = DjangoAuthorization()
        always_return_data = True


class UserProductResource(CustomBaseModelResource):
    consumer = fields.ForeignKey(ConsumerResource, 'consumer', null=True, blank=True, full=True)
    brand = fields.ForeignKey(BrandResource, 'brand', null=True, blank=True, full=True)
    product_type = fields.ForeignKey(ProductTypeResource, 'product_type', null=True, blank=True, full=True)

    class Meta:
        queryset = afterbuy_models.UserProduct.objects.all()
        resource_name = "products"
        authentication = AccessTokenAuthentication()
        authorization = MultiAuthorization(DjangoAuthorization(), CustomAuthorization())
        validation = ProductValidation()
        always_return_data = True
        filtering = {
                     "consumer": ALL,
                     "product_type": ALL,
                     "brand": ALL_WITH_RELATIONS,
                     "is_deleted": ALL
                     }

    def dehydrate(self, bundle):
        insurance = afterbuy_models.ProductInsuranceInfo.objects.filter(product=bundle.data['id'])
        invoice = afterbuy_models.Invoice.objects.filter(product=bundle.data['id'])
        license = afterbuy_models.License.objects.filter(product=bundle.data['id'])
        registrations = afterbuy_models.RegistrationCertificate.objects.filter(product=bundle.data['id'])
        pollution = afterbuy_models.PollutionCertificate.objects.filter(product=bundle.data['id'])
        product_support = afterbuy_models.ProductSupport.objects.filter(product=bundle.data['id'])
        sell_information = afterbuy_models.SellInformation.objects.filter(product=bundle.data['id'])
        brand_id = bundle.data['brand'].data['id']
        support = afterbuy_models.Support.objects.filter(brand=int(brand_id))
        product_image = afterbuy_models.UserProductImages.objects.filter(product=bundle.data['id'])
        bundle.data['insurance'] = [model_to_dict(c) for c in insurance]
        bundle.data['invoice'] = [model_to_dict(c) for c in invoice]
        bundle.data['license'] = [model_to_dict(c) for c in license]
        bundle.data['registrations'] = [model_to_dict(c) for c in registrations]
        bundle.data['pollution'] = [model_to_dict(c) for c in pollution]
        bundle.data['support'] = [model_to_dict(c) for c in support]
        bundle.data['product_image'] = [model_to_dict(c) for c in product_image]
        bundle.data['product_support'] = [model_to_dict(c) for c in product_support]
        bundle.data['sell_information'] = [model_to_dict(c) for c in sell_information]
        return bundle

    def prepend_urls(self):
        return [
                url(r"^(?P<resource_name>%s)/(?P<product_id>[\d]+)/coupons%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_product_coupons'), name="get_product_coupons" ),
                url(r"^(?P<resource_name>%s)/(?P<product_id>[\d]+)/recycle%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('mail_products_details'), name="mail_products_details" )
        ]

    def get_product_coupons(self, request, **kwargs):
        port = request.META['SERVER_PORT']
        product_id = kwargs.get('product_id')
        access_token = request.META['QUERY_STRING'] 
        try:
            if product_id:
                product_info = afterbuy_models.UserProduct.objects.get(id=product_id)
                brand_product_id = product_info.brand_product_id
                if not API_FLAG:
                    return HttpResponseRedirect('http://'+BRAND_META[settings.BRAND]['base_url']+':'+port+'/v1/coupons/?product__product_id='+brand_product_id+'&'+access_token)
                else:
                    return HttpResponseRedirect('http://'+BRAND_META[settings.BRAND]['base_url']+'/v1/coupons/?product__product_id='+brand_product_id+'&'+access_token)
        except Exception as ex:
            logger.error('Invalid details')

    def mail_products_details(self, request, **kwargs):
        try:
            product_id = kwargs['product_id']
            product_info = afterbuy_models.UserProduct.objects.get(id=product_id)
            email_id = product_info.consumer.user.email
            try:
                afterbuy_model.Consumer.objects.get(user__email=email_id, is_email_verified=True)
                send_recycle_mail(email_id, data=product_info)
                data = {'status': 1, 'message': 'email sent successfully'}
            except Exception as ex:
                data = {'status': 0, 'message': 'email_id not active'}
        except Exception as ex:
            logger.error('Invalid details')  
            data = {'status': 0, 'message': 'email not sent'}
        return HttpResponse(json.dumps(data), content_type="application/json")


class ProductInsuranceInfoResource(CustomBaseModelResource):
    product = fields.ForeignKey(UserProductResource, 'product', null=True, blank=True, full=True)

    class Meta:
        queryset = afterbuy_models.ProductInsuranceInfo.objects.all()
        resource_name = "insurances"
        authorization = MultiAuthorization(DjangoAuthorization(), CustomAuthorization())
        authentication = AccessTokenAuthentication()
        always_return_data = True
        filtering = {
                     "product": ALL,
                     "is_expired": ALL,
                     "expiry_date": ALL
                     }


class InvoiceResource(CustomBaseModelResource):
    product = fields.ForeignKey(UserProductResource, 'product', null=True, blank=True, full=True)

    class Meta:
        queryset = afterbuy_models.Invoice.objects.all()
        resource_name = "invoices"
        authorization = MultiAuthorization(DjangoAuthorization(), CustomAuthorization())
        authentication = AccessTokenAuthentication()
        always_return_data = True
        filtering = {
                     "product": ALL
                     }


class LicenseResource(CustomBaseModelResource):
    product = fields.ForeignKey(UserProductResource, 'product', full=True, null=True)

    class Meta:
        queryset = afterbuy_models.License.objects.all()
        resource_name = 'licenses'
        authorization = MultiAuthorization(DjangoAuthorization(), CustomAuthorization())
        authentication = AccessTokenAuthentication()
        always_return_data =True
        filtering = {
                     "product" : ALL
                     }


class RegistrationCertificateResource(CustomBaseModelResource):
    product = fields.ForeignKey(UserProductResource, 'product', full=True, null=True)

    class Meta:
        queryset = afterbuy_models.RegistrationCertificate.objects.all()
        resource_name = 'registrations'
        authorization = MultiAuthorization(DjangoAuthorization(), CustomAuthorization())
        authentication = AccessTokenAuthentication()
        always_return_data = True
        filtering = {
                     "product": ALL
                     }


class PollutionCertificateResource(CustomBaseModelResource):
    product = fields.ForeignKey(UserProductResource, 'product', full=True, null=True)

    class Meta:
        queryset = afterbuy_models.PollutionCertificate.objects.all()
        resource_name = 'pollution'
        authentication = AccessTokenAuthentication()
        authorization = MultiAuthorization(DjangoAuthorization(), CustomAuthorization())
        always_return_data = True
        filtering = {
                     "product": ALL
                     }


class SupportResource(CustomBaseModelResource):
    brand = fields.ForeignKey(BrandResource, 'brand', full=True, null=True)
    brand_product_category = fields.ForeignKey(BrandResource, 'brand_product_category', full=True, null=True)

    class Meta:
        queryset = afterbuy_models.Support.objects.all()
        resource_name = 'support'
        authentication = AccessTokenAuthentication()
        authorization = DjangoAuthorization()
        always_return_data = True
        filtering = {
                     "brand": ALL,
                     "brand_product_category": ALL
                     }


class ProductSupportResource(CustomBaseModelResource):
    product = fields.ForeignKey(UserProductResource, 'product', full=True, null=True)

    class Meta:
        queryset = afterbuy_models.ProductSupport.objects.all()
        resource_name = 'product-support'
        authentication = AccessTokenAuthentication()
        authorization = MultiAuthorization(DjangoAuthorization(), CustomAuthorization())
        always_return_data = True
        filtering = {
                     "product": ALL,
                     }


class SellInformationResource(CustomBaseModelResource):
    product = fields.ForeignKey(UserProductResource, 'product', full=True, null=True)

    class Meta:
        queryset = afterbuy_models.SellInformation.objects.all()
        resource_name = 'sell-information'
        authentication = AccessTokenAuthentication()
        authorization = MultiAuthorization(DjangoAuthorization(), CustomAuthorization())
        always_return_data = True
        filtering = {
                     "product": ALL,
                     }


class UserProductImagesResource(CustomBaseModelResource):
    product = fields.ForeignKey(UserProductResource, 'product', full=True, null=True)

    class Meta:
        queryset = afterbuy_models.UserProductImages.objects.all()
        resource_name = 'product-images'
        authentication = AccessTokenAuthentication()
        authorization = MultiAuthorization(DjangoAuthorization(), CustomAuthorization())
        always_return_data = True
        filtering = {
                     "product": ALL,
                     }


class InterestResource(CustomBaseModelResource):

    class Meta:
        queryset = afterbuy_model.Interest.objects.all()
        resource_name = "interests"
        authentication = AccessTokenAuthentication()
        authorization = DjangoAuthorization()
        always_return_data = True
