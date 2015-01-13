from tastypie.constants import ALL
from tastypie.authorization import Authorization
from tastypie import fields 
from gladminds.bajaj.models import ProductData, ProductType
from gladminds.core.apis.base_apis import CustomBaseModelResource
from gladminds.core.apis.user_apis import DealerResources


class ProductTypeDataResources(CustomBaseModelResource):
    class Meta:
        queryset = ProductType.objects.all()
        resource_name = "product-types"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        always_return_data = True


class ProductDataResources(CustomBaseModelResource):
    product_type = fields.ForeignKey(ProductTypeDataResources, 'product_type',
                                     null=True, blank=True, full=True)
    dealer_id = fields.ForeignKey(DealerResources, 'dealer_id',
                                  null=True, blank=True, full=True)

    class Meta:
        queryset = ProductData.objects.all()
        resource_name = "products"
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
                     "product_id":  ALL,
                     "customer_id": ALL,
                     "customer_phone_number": ALL,
                     "customer_name": ALL,
                     "customer_address": ALL,
                     "purchase_date": ['gte', 'lte'],
                     "invoice_date": ['gte', 'lte']
                     }

