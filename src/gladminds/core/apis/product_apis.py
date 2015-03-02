from tastypie.constants import ALL
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie import fields 
from gladminds.core.apis.base_apis import CustomBaseModelResource
from gladminds.core.model_fetcher import models
from gladminds.core.apis.authorization import MultiAuthorization
from gladminds.core.apis.authentication import AccessTokenAuthentication
from gladminds.core.apis.user_apis import DealerResource, PartnerResource


class ProductTypeResource(CustomBaseModelResource):
    class Meta:
        queryset = models.ProductType.objects.all()
        resource_name = "product-types"
        model_name = 'ProductType'
#         authentication = AccessTokenAuthentication()
#         authorization = MultiAuthorization(DjangoAuthorization())
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        always_return_data = True


class ProductResource(CustomBaseModelResource):
    product_type = fields.ForeignKey(ProductTypeResource, 'product_type',
                                     null=True, blank=True, full=True)
    dealer_id = fields.ForeignKey(DealerResource, 'dealer_id',
                                  null=True, blank=True, full=True)

    class Meta:
        queryset = models.ProductData.objects.all()
        resource_name = "products"
        model_name = 'ProductData'
        authentication = AccessTokenAuthentication()
        authorization = MultiAuthorization(Authorization())
        detail_allowed_methods = ['get']
        filtering = {
                     "product_id":  ALL,
                     "customer_id": ALL,
                     "customer_phone_number": ALL,
                     "customer_name": ALL,
                     "customer_address": ALL,
                     "purchase_date": ['gte', 'lte', 'isnull'],
                     "invoice_date": ['gte', 'lte']
                     }


class CustomerTempRegistrationResource(CustomBaseModelResource):
    product_data = fields.ForeignKey(ProductResource, 'product_data', null=True, blank=True, full=True)

    class Meta:
        queryset = models.CustomerTempRegistration.objects.all()
        resource_name = "customer-changes"
        model_name = 'CustomerTempRegistration'
        authentication = AccessTokenAuthentication()
        authorization = MultiAuthorization(DjangoAuthorization())
        detail_allowed_methods = ['get']
        always_return_data = True

class ProductCatalogResource(CustomBaseModelResource):
    partner = fields.ForeignKey(PartnerResource, 'partner', null=True, blank=True, full=True)
    
    class Meta:
        queryset = models.ProductCatalog.objects.all()
        resource_name = "product-catalogs"
        model_name = 'ProductCatalog'
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True

class SpareMasterResource(CustomBaseModelResource):
    product_type = fields.ForeignKey(ProductTypeResource, 'product_type', full=True)
    class Meta:
        queryset = models.SparePartMasterData.objects.all()
        resource_name = "spare-masters"
        model_name = 'SparePartMasterData'
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True

class SparePartPointResource(CustomBaseModelResource):
    part_number = fields.ForeignKey(SpareMasterResource, 'part_number', full=True)
    class Meta:
        queryset = models.SparePartPoint.objects.all()
        resource_name = "spare-points"
        model_name = 'SparePartPoint'
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True

class SparePartUPCResource(CustomBaseModelResource):
    part_number = fields.ForeignKey(SpareMasterResource, 'part_number', full=True)
    class Meta:
        queryset = models.SparePartUPC.objects.all()
        resource_name = "spare-upcs"
        model_name = 'SparePartUPC'
        authorization = Authorization()
        detail_allowed_methods = ['get', 'post', 'put']
        always_return_data = True
