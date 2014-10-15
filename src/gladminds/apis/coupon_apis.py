# from tastypie.constants import ALL_WITH_RELATIONS
# from tastypie.authorization import Authorization
# from tastypie import fields
# from gladminds.apis.baseresource import CustomBaseResource
# from gladminds.apis.product_apis import ProductDataResources
# from gladminds.core.base_models import CouponData, ServiceAdvisor,\
#     RegisteredDealer
#  
# class RegisteredDealerResources(CustomBaseResource):
#     class Meta:
#         queryset = RegisteredDealer.objects.all()
#         resource_name = "registereddealer"
#         authorization = Authorization()
#         detail_allowed_methods = ['get', 'post', 'delete', 'put']
#         always_return_data = True
#  
# class ServiceAdvisorResources(CustomBaseResource):
#     class Meta:
#         queryset = ServiceAdvisor.objects.all()
#         resource_name = "serviceadvisor"
#         authorization = Authorization()
#         detail_allowed_methods = ['get', 'post', 'delete', 'put']
#         always_return_data = True
#  
# class CouponDataResources(CustomBaseResource):
#     vin = fields.ForeignKey(ProductDataResources, 'vin', full=True)
#     sa_phone_number = fields.ForeignKey(ServiceAdvisorResources, 'sa_phone_number', full=True, null=True, blank=True)
#     servicing_dealer = fields.ForeignKey(RegisteredDealerResources, 'servicing_dealer', full=True,
#                                          null=True, blank=True)
#     class Meta:
#         queryset = CouponData.objects.all()
#         resource_name = "coupons"
#         authorization = Authorization()
#         detail_allowed_methods = ['get', 'post', 'delete', 'put']
#         always_return_data = True
#         filtering = {
#                         "servicing_dealer" : ALL_WITH_RELATIONS,
#                         "service_type" : ALL_WITH_RELATIONS,
#                         "status" : ALL_WITH_RELATIONS,
#                         "closed_date" : ['gte', 'lte'],
#                         "vin" : ALL_WITH_RELATIONS,
#                         "unique_service_coupon" : ALL_WITH_RELATIONS
#                      }

