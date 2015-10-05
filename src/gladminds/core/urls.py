from django.conf.urls import patterns, url, include
from gladminds.core.cron_jobs.taskqueue import SqsHandler
from gladminds.sqs_tasks import _tasks_map

from tastypie.api import Api
from django.conf import settings
from gladminds.core.apis import user_apis, preferences_apis, coupon_apis, product_apis,\
    audit_apis, dashboard_apis, service_desk_apis, loyalty_apis, part_change_apis,\
    service_circular
from gladminds.core.managers.sms_handler import SMSResources
from gladminds.core.apis.image_apis import upload_files
from gladminds.core.admin import brand_admin
from gladminds.core.services.loyalty.loyalty import loyalty


api_v1 = Api(api_name="v1")

api_v1.register(user_apis.UserProfileResource())
api_v1.register(user_apis.TerritoryResource())
api_v1.register(user_apis.StateResource())
api_v1.register(user_apis.CityResource())
api_v1.register(user_apis.BrandDepartmentResource())
api_v1.register(user_apis.DepartmentSubCategoriesResource())

api_v1.register(user_apis.CircleHeadResource())
api_v1.register(user_apis.RegionalManagerResource())
api_v1.register(user_apis.AreaSalesManagerResource())

api_v1.register(user_apis.ZonalServiceManagerResource())
api_v1.register(user_apis.AreaServiceManagerResource())
api_v1.register(user_apis.DealerResource())
api_v1.register(user_apis.AuthorizedServiceCenterResource())
api_v1.register(user_apis.ServiceAdvisorResource())

api_v1.register(user_apis.NationalSparesManagerResource())
api_v1.register(user_apis.AreaSparesManagerResource())
api_v1.register(user_apis.PartnerResource())
api_v1.register(user_apis.DistributorResource())
api_v1.register(user_apis.RetailerResource())
api_v1.register(user_apis.MemberResource())

api_v1.register(user_apis.ServiceDeskUserResource())

api_v1.register(user_apis.TransporterResource())
api_v1.register(user_apis.SupervisorResource())

api_v1.register(product_apis.ProductTypeResource())
api_v1.register(product_apis.ProductResource())
api_v1.register(product_apis.CustomerTempRegistrationResource())

api_v1.register(product_apis.SpareMasterResource())
api_v1.register(product_apis.ProductCatalogResource())
api_v1.register(product_apis.SparePartUPCResource())
api_v1.register(product_apis.SparePartPointResource())

api_v1.register(product_apis.ContainerTrackerResource())
api_v1.register(product_apis.ContainerIndentResource())
api_v1.register(product_apis.ContainerLRResource())

api_v1.register(coupon_apis.CouponDataResource())

api_v1.register(loyalty_apis.LoyaltySLAResource())
api_v1.register(loyalty_apis.AccumulationResource())
api_v1.register(loyalty_apis.DiscrepantAccumulationResource())
api_v1.register(loyalty_apis.RedemptionResource())

api_v1.register(service_desk_apis.FeedbackResource())
api_v1.register(service_desk_apis.ActivityResource())
api_v1.register(service_desk_apis.SLAResource())
api_v1.register(service_desk_apis.CommentsResource())

api_v1.register(preferences_apis.UserPreferenceResource())
api_v1.register(preferences_apis.BrandPreferenceResource())

api_v1.register(audit_apis.SMSLogResource())
api_v1.register(audit_apis.DataFeedLogResource())

api_v1.register(dashboard_apis.OverallStatusResource())
api_v1.register(dashboard_apis.FeedStatusResource())
api_v1.register(dashboard_apis.SMSReportResource())
api_v1.register(dashboard_apis.CouponReportResource())
api_v1.register(dashboard_apis.TicketStatusResource())

api_v1.register(part_change_apis.BrandProductRangeResource())
api_v1.register(part_change_apis.BrandVerticalResource())
api_v1.register(part_change_apis.BOMHeaderResource())
api_v1.register(part_change_apis.BOMPlatePartResource())
api_v1.register(part_change_apis.ECOReleaseResource())
api_v1.register(part_change_apis.ECOImplementationResource())
api_v1.register(part_change_apis.BOMVisualizationResource())
api_v1.register(part_change_apis.ManufacturingDataResource())

api_v1.register(service_circular.ServiceCircularResource())

from django.contrib.auth.decorators import login_required
from django.contrib import admin
admin.autodiscover()

api_v1.register(SMSResources())

urlpatterns = patterns('',
    url(r'', include(api_v1.urls)),
    url(r'^$', 'gladminds.core.views.home'),
    url(r'^admin/', include(brand_admin.urls)),
    url(r'api/doc/', include('gladminds.core.api_docs.swagger_urls', namespace='tastypie_swagger')),
    url(r'^login/$', 'gladminds.core.views.auth_login'),
    url(r'^logout/$', 'gladminds.core.views.user_logout'),
    url(r'^services/$', 'gladminds.core.views.home'),

    url(r'^api/v1/feed/\?wsdl$', 'gladminds.core.webservice.all_service'),
    url(r'^api/v1/feed/$', 'gladminds.core.webservice.all_service'),
    
    url(r'^add/servicedesk-user/$', 'gladminds.core.services.service_desk.servicedesk_views.add_servicedesk_user', name='add_servicedesk_user'),
    url(r'^aftersell/users/(?P<users>[a-zA-Z0-9]+)$', 'gladminds.core.views.users'),
    url(r'^aftersell/sa/(?P<id>[a-zA-Z0-9]+)/$', 'gladminds.core.views.get_sa_under_asc'),
    url(r'^aftersell/reports/reconciliation$', 'gladminds.core.views.reports'),
    url(r'^asc/report/$', 'gladminds.core.views.get_active_asc_report'),
    url(r'^aftersell/servicedesk/save-feedback/$', 'gladminds.core.services.service_desk.servicedesk_views.save_feedback', name='save_feedback'),
    
    url(r'^aftersell/servicedesk/get-subcategories/$', 'gladminds.core.services.service_desk.servicedesk_views.get_subcategories', name='get_subcategories'),
    url(r'^aftersell/servicedesk/get-brand-users/$', 'gladminds.core.services.service_desk.servicedesk_views.get_brand_users', name='get_brand_users'),

    url(r'^aftersell/register/(?P<menu>[a-zA-Z0-9]+)$', 'gladminds.core.views.register'),
    url(r'^aftersell/exceptions/(?P<exception>[a-zA-Z0-9]+)$', 'gladminds.core.views.exceptions'),
    url(r'^aftersell/asc/self-register/$', 'gladminds.core.views.save_asc_registration'),

    url(r'^aftersell/(?P<provider>[a-zA-Z]+)/login/$', 'gladminds.core.views.auth_login', name='user_login'),
    url(r'^aftersell/provider/logout$', 'gladminds.core.views.user_logout', name='user_logout'),
    url(r'^aftersell/provider/redirect$', 'gladminds.core.views.redirect_user'),
    url(r'^aftersell/users/otp/generate$', 'gladminds.core.views.generate_otp', name='generate_otp'),
    url(r'^aftersell/users/otp/validate', 'gladminds.core.views.validate_otp', name='validate_otp'),
    url(r'^aftersell/users/otp/update_pass', 'gladminds.core.views.update_pass', name='update_pass'),
    url(r'^aftersell/provider/change-password$', 'gladminds.core.views.change_password', name='change_password'),

    url(r'^aftersell/servicedesk/helpdesk$', 'gladminds.core.services.service_desk.servicedesk_views.service_desk', name='enable_servicedesk'),
    url(r'^aftersell/servicedesk/$', 'gladminds.core.services.service_desk.servicedesk_views.get_servicedesk_tickets', name='get_servicedesk_tickets'),
    url(r'^aftersell/helpdesk$', 'gladminds.core.services.service_desk.servicedesk_views.get_helpdesk', name='get_helpdesk'),
    url(r'^aftersell/feedbackdetails/(?P<feedback_id>\d+)/$', 'gladminds.core.services.service_desk.servicedesk_views.modify_servicedesk_tickets', name='modify_servicedesk_tickets'),
    url(r'^aftersell/feedbackdetails/(?P<feedback_id>\d+)/comments/(?P<comment_id>\d+)/$', 'gladminds.core.services.service_desk.servicedesk_views.modify_feedback_comments', name='modify_feedback_comments'),
    url(r'^aftersell/feedbackresponse/(?P<feedback_id>\d+)/$', 'gladminds.core.services.service_desk.servicedesk_views.get_feedback_response', name='get_feedback_response'),
    url(r'^aftersell/servicedesk/save-feedback/$', 'gladminds.core.services.service_desk.servicedesk_views.save_feedback', name='save_feedback'),

    url(r'^v1/upload', upload_files),
    # Tasks URL
    url(r'^tasks-view/$', 'gladminds.core.views.sqs_tasks_view'),
    url(r'^trigger-tasks', 'gladminds.core.views.trigger_sqs_tasks'),
    url(r'^tasks', SqsHandler.as_view(task_map=_tasks_map)),
    url(r'^sms/','gladminds.bajaj.services.feed_views.send_sms', name='send_sms'),
    url(r'^demo-sbom-upload/','gladminds.bajaj.services.feed_views.demo_sbom_upload', name='demo_sbom_upload'),

    url(r'^welcome', loyalty.send_welcome_message, name='send_welcome_message'),
    url(r'^check-detail/(?P<model>[a-zA-Z0-9]+)/(?P<choice>[a-zA-Z0-9]+)$', loyalty.check_details, name='check_details'),
    url(r'^member-download/(?P<choice>[a-zA-Z0-9]+)$', loyalty.download_member_detail, name='download_member_detail'),
    url(r'^kit-download/(?P<choice>[a-zA-Z0-9]+)$', loyalty.download_welcome_kit_detail, name='download_welcome_kit_detail'),
    url(r'^redemption-download/(?P<choice>[a-zA-Z0-9]+)$', loyalty.download_redemption_detail, name='download_redemption_detail'),
    url(r'^accumulation-download/(?P<choice>[a-zA-Z0-9]+)$', loyalty.download_accumulation_detail, name='download_accumulation_detail'),
    url(r'^loyalty/(?P<report_choice>[a-zA-Z]+)/$', 'gladminds.core.views.get_loyalty_reports'),
    url(r'^powerrewards/$', 'gladminds.core.views.get_loyalty_login'),
)
