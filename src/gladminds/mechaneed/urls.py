from django.conf.urls import patterns, url, include
from gladminds.mechaneed.admin import brand_admin
from gladminds.core import urls as core_urls
from gladminds.core.urls import api_v1

urlpatterns = patterns('',
    
    url(r'^admin/', include(brand_admin.urls)),
    url(r'', include(api_v1.urls)),
    
    url(r'', include(core_urls)),
)