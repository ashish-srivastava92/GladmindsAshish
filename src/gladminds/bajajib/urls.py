from django.conf.urls import patterns, url, include
from gladminds.bajajib.admin import brand_admin
from gladminds.core import urls as core_urls
from gladminds.core.urls import api_v1

urlpatterns = patterns('',
    url(r'^ussd/sms/','gladminds.bajajib.services.feed_views.send_sms', name='send_sms'),
    url(r'^admin/', include(brand_admin.urls)),
    url(r'', include(api_v1.urls)),
    url(r'^site-info/$', 'gladminds.bajajib.views.site_info', name='site_info'),
    
    
    
    url(r'^aftersell/servicedesk/helpdesk$', 'gladminds.bajajib.services.service_desk.servicedesk_views.service_desk', name='enable_servicedesk'),
    url(r'^aftersell/servicedesk/$', 'gladminds.bajajib.services.service_desk.servicedesk_views.get_servicedesk_tickets', name='get_servicedesk_tickets'),
    #url(r'^aftersell/helpdesk$', 'gladminds.bajajib.services.service_desk.servicedesk_views.get_helpdesk', name='get_helpdesk'),
    url(r'^aftersell/feedbackdetails/(?P<feedback_id>\d+)/$', 'gladminds.bajajib.services.service_desk.servicedesk_views.modify_servicedesk_tickets', name='modify_servicedesk_tickets'),
    url(r'^aftersell/feedbackdetails/(?P<feedback_id>\d+)/comments/(?P<comment_id>\d+)/$', 'gladminds.bajajib.services.service_desk.servicedesk_views.modify_feedback_comments', name='modify_feedback_comments'),
    url(r'^aftersell/feedbackresponse/(?P<feedback_id>\d+)/$', 'gladminds.bajajib.services.service_desk.servicedesk_views.get_feedback_response', name='get_feedback_response'),
    url(r'^aftersell/servicedesk/save-feedback/$', 'gladminds.bajajib.services.service_desk.servicedesk_views.save_feedback', name='save_feedback'),
    
    
    
    url(r'^api/v1/feed/\?wsdl$', 'gladminds.bajajib.webservice.all_service'),
    url(r'^api/v1/feed/$', 'gladminds.bajajib.webservice.all_service'),

    url(r'^api/v1/(?P<feed_type>[a-zA-Z0-9-]+)/$', 'gladminds.bajajib.services.feed_views.view_wsdl'),

    url(r'^aftersell/users/(?P<users>[a-zA-Z0-9]+)$', 'gladminds.bajajib.views.views.users'),
    url(r'^aftersell/sa/(?P<id>[a-zA-Z0-9]+)/$', 'gladminds.bajajib.views.views.get_sa_under_asc'),
    url(r'^aftersell/reports/reconciliation$', 'gladminds.bajajib.views.views.reports'),
    url(r'^coupon/report/(?P<role>[a-zA-Z0-9.-]+)/$', 'gladminds.bajajib.views.views.get_active_asc_report'),
    url(r'^aftersell/register/(?P<menu>[a-zA-Z0-9]+)$', 'gladminds.bajajib.views.views.register'),
    url(r'^aftersell/exceptions/(?P<exception>[a-zA-Z0-9]+)$', 'gladminds.bajajib.views.views.exceptions'),
    url(r'^aftersell/feeds/vin-sync/$', 'gladminds.bajajib.views.views.vin_sync_feed'),
    url(r'^aftersell/asc/self-register/$', 'gladminds.bajajib.views.views.save_asc_registration'),
    
    
    url(r'^aftersell/(?P<provider>[a-zA-Z]+)/login/$', 'gladminds.bajajib.views.views.auth_login', name='user_login'),
    url(r'^aftersell/provider/logout$', 'gladminds.bajajib.views.views.user_logout', name='user_logout'),
    url(r'^aftersell/provider/redirect$', 'gladminds.bajajib.views.views.redirect_user'),
    url(r'^aftersell/users/otp/generate$', 'gladminds.bajajib.views.views.generate_otp', name='generate_otp'),
    url(r'^aftersell/users/otp/validate', 'gladminds.bajajib.views.views.validate_otp', name='validate_otp'),
    url(r'^aftersell/users/otp/update_pass', 'gladminds.bajajib.views.views.update_pass', name='update_pass'),
    url(r'^aftersell/provider/change-password$', 'gladminds.bajajib.views.views.change_password', name='change_password'),
    url(r'', include(core_urls)),
)