from django.shortcuts import render_to_response
# from gladminds.models import Customer,Product,Service


def send_sms(request):
    return render_to_response('mobile.html')


def views_coupon_redeem_wsdl(request, document_root, show_indexes=False):
    return render_to_response("coupon_redeem.wsdl", content_type = 'application/xml')
