from django.shortcuts import render_to_response
from django.conf import settings
from django.http.response import HttpResponseBadRequest

def send_sms(request):
    return render_to_response('mobile.html')

def view_wsdl(request, feed_type, show_indexes=False):
    WSDL_URL = {
                'coupon-redeem': settings.COUPON_WSDL,
                'customer-feed': settings.CUSTOMER_REGISTRATION_WSDL,
                'vin-sync': settings.VIN_SYNC_WSDL,
                'purchase-sync': settings.PURCHASE_SYNC_WSDL,
                }
    try:
        return render_to_response(WSDL_URL[feed_type], content_type = 'application/xml')
    except Exception as ex:
        return HttpResponseBadRequest()
