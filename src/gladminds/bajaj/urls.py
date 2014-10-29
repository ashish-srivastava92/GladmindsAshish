from django.conf.urls import patterns, url, include
from django.conf import settings
from gladminds.bajaj.admin import brand_admin
from tastypie.api import Api
from gladminds.core import urls as core_urls
from gladminds.bajaj.apis import coupon_apis

api_v1 = Api(api_name="v1")
# api_v1.register(audit_api.AuditResources())
api_v1.register(coupon_apis.CouponDataResources())

urlpatterns = patterns('',
   
    url(r'^site-info/$', 'gladminds.bajaj.views.site_info', name='site_info'),
    url(r'', include(core_urls)),
    url(r'', include(brand_admin.urls)),
    url(r'', include(api_v1.urls))
)