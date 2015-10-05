import logging
import os
import json
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from django.db import transaction
from django.conf import settings
from django.test.client import Client
from gladminds.bajaj import models
from gladminds.bajaj.services.coupons import import_feed, export_feed

client = Client(SERVER_NAME='bajaj')

logger = logging.getLogger('gladminds')

class Brand(object):
    def __init__(self, tester):
        self.tester = tester

    def send_purchase_feed(self):
        file_path = os.path.join(settings.BASE_DIR, 'tests/integration/bajaj/test_data/product_purchase_feed.xml')
        self.post_feed(file_path)

    def send_purchase_feed_with_diff_cust_num(self):
        file_path = os.path.join(settings.BASE_DIR, 'tests/integration/bajaj/test_data/purchase_feed_with_diff_cust_num.xml')
        self.post_feed(file_path)

    def check_for_auth(self):
        file_path = os.path.join(settings.BASE_DIR, 'tests/integration/bajaj/test_data/feeds_for_testing_auth.xml')
        self.post_feed(file_path)

    def send_as_feed_without_id(self):
        file_path = os.path.join(settings.BASE_DIR, 'tests/integration/bajaj/test_data/without_sa_id_sa_feed.xml')
        xml_data = open(file_path, 'r').read()
        with transaction.atomic():
            response = self.tester.client.post('/api/v1/feed/?wsdl', data=xml_data,content_type='text/xml')
            self.tester.assertEqual(200, response.status_code)

        response_content = response.content
        xml_parser = ET.fromstring(response_content)
        with transaction.atomic():
            status = xml_parser.findall('*//{http://api.gladmindsplatform.co/api/v1/bajaj/feed/}postDealerResult')[0].text
            self.tester.assertEqual(status, 'SUCCESS')

    def send_sa_upate_mobile_feed(self):
        file_path = os.path.join(settings.BASE_DIR, 'tests/integration/bajaj/test_data/sa_update_mobile_feed.xml')
        self.post_feed(file_path)

    def send_dispatch_feed(self):
        file_path = os.path.join(settings.BASE_DIR, 'tests/integration/bajaj/test_data/product_dispatch_feed.xml')
        self.post_feed(file_path)

    def send_dispatch_feed_without_ucn(self):
        file_path = os.path.join(settings.BASE_DIR, 'tests/integration/bajaj/test_data/product_dispatch_feed_without_ucn.xml')
        self.post_feed(file_path)

    def send_asc_feed(self):
        file_path = os.path.join(settings.BASE_DIR, 'tests/integration/bajaj/test_data/asc_feed.xml')
        self.post_feed(file_path)

    def send_service_advisor_feed(self):
        file_path = os.path.join(settings.BASE_DIR, 'tests/integration/bajaj/test_data/service_advisor_feed.xml')
        self.post_feed(file_path)

    def send_service_advisor_feed_with_new_status(self):
        file_path = os.path.join(settings.BASE_DIR, 'tests/integration/bajaj/test_data/service_advisor_feed_2.xml')
        self.post_feed(file_path)
    
    def send_container_tracker_feed(self):
        file_path = os.path.join(settings.BASE_DIR, 'tests/integration/bajaj/test_data/container_tracker.xml')
        self.post_feed(file_path)
        
    def send_manufacture_data_feed(self):
        file_path = os.path.join(settings.BASE_DIR, 'tests/integration/bajaj/test_data/manufacture_data.xml')
        self.post_feed(file_path)
    
    def send_sbom_data_feed(self):
        file_path = os.path.join(settings.BASE_DIR, 'tests/integration/bajaj/test_data/bom_feed.xml')
        self.post_feed(file_path)

    def post_feed(self, file_path):
        xml_data = open(file_path, 'r').read()
        response = client.post('/api/v1/feed/?wsdl', data=xml_data, content_type='text/xml')
        self.tester.assertEqual(200, response.status_code)

    def send_sms(self, **kwargs):
        response = client.post(kwargs['url'], kwargs['message'])
        return response

    def check_coupon_status(self, **kwargs):
        coupon_status = models.CouponData.objects.get(unique_service_coupon=kwargs['unique_service_coupon'])
        return coupon_status

    def get_coupon_obj(self, **kwargs):
        coupon_obj = models.CouponData(**kwargs)
        coupon_obj.save()
        return coupon_obj

    def get_product_obj(self, **kwargs):
        product_data = models.ProductData.objects.get(**kwargs)
        return product_data

    def check_asc_feed_saved_to_database(self):
        self.send_asc_feed()
        asc = models.AuthorizedServiceCenter.objects.get(asc_id='ASC001')
        self.tester.assertEquals('ASC001', asc.asc_id)

    def check_coupon(self, data, phone_number):
        data = 'A {1} {0} {2}'.format(data['kms'], data['sap_customer_id'], data['service_type'])
        create_sms_dict = {'text': data, 'phoneNumber': phone_number}
        response = self.send_sms(url='/v1/messages', message=create_sms_dict)
        self.tester.assertEqual(200, response.status_code)

    def check_service_feed_saved_to_database(self):
        self.tester.assertEquals(3, models.Dealer.objects.count())
        dealer_data = models.Dealer.objects.all()[0]
        self.tester.assertEquals(u"GMDEALER031", dealer_data.dealer_id)
        service_advisors = models.ServiceAdvisor.objects.filter(service_advisor_id='GMDEALER001SA31')
        self.tester.assertEquals(1, len(service_advisors))
        self.tester.assertEquals(u"GMDEALER001SA31", service_advisors[0].service_advisor_id)

    def check_service_advisor_dealer_relationship_saved_to_database(self):
        sa_dealer_rel_data = models.ServiceAdvisor.objects.all()
        self.tester.assertEquals(3, len(sa_dealer_rel_data))
        self.tester.assertEquals(3, models.ServiceAdvisor.objects.count())
        sa_obj_1 = models.ServiceAdvisor.objects.filter(service_advisor_id='GMDEALER001SA31')
        dealer_obj_1 = models.Dealer.objects.filter(dealer_id='GMDEALER031')
        sa_dealer_rel_obj_1 = models.ServiceAdvisor.objects.get(service_advisor_id=sa_obj_1[0], dealer_id=dealer_obj_1[0])
        self.tester.assertEquals('Y', sa_dealer_rel_obj_1.status)
        sa_obj_2 = models.ServiceAdvisor.objects.filter(service_advisor_id='GMDEALER001SA32')
        dealer_obj_2 = models.Dealer.objects.filter(dealer_id='GMDEALER032')
        sa_dealer_rel_obj_2 = models.ServiceAdvisor.objects.get(service_advisor_id=sa_obj_2[0], dealer_id=dealer_obj_2[0])
        self.tester.assertEquals('Y', sa_dealer_rel_obj_2.status)
 
    def check_data_saved_to_database(self):
        sa_obj_1 = models.ServiceAdvisor.objects.filter(service_advisor_id='GMDEALER001SA31')
        self.tester.assertEquals('+911111111111', sa_obj_1[0].user.phone_number)
        dealer_obj_1 = models.Dealer.objects.filter(dealer_id='GMDEALER031')
        sa_dealer_rel_obj_1 = models.ServiceAdvisor.objects.get(service_advisor_id=sa_obj_1[0], dealer_id=dealer_obj_1[0])
        self.tester.assertEquals('N', sa_dealer_rel_obj_1.status)
        sa_obj_2 = models.ServiceAdvisor.objects.filter(service_advisor_id='GMDEALER001SA32')
        dealer_obj_2 = models.Dealer.objects.filter(dealer_id='GMDEALER032')
        sa_dealer_rel_obj_2 = models.ServiceAdvisor.objects.get(service_advisor_id=sa_obj_2[0], dealer_id=dealer_obj_2[0])
        self.tester.assertEquals('Y', sa_dealer_rel_obj_2.status)
 
    def coupon_data_saved_to_database(self):
        self.tester.assertEqual(models.CouponData.objects.count(), 3, "Three coupon created")
        coupon_data = models.CouponData.objects.filter(unique_service_coupon='USC9217')[0]
        self.tester.assertEquals(u"USC9217", coupon_data.unique_service_coupon)
        coupon_data.status = 2
        coupon_data.closed_date = datetime.now()
        coupon_data.actual_service_date = datetime.now()
        coupon_data.save()
 
        today = datetime.now()
        start_date = today - timedelta(days=1)
        end_date = today
        redeem_obj = export_feed.ExportCouponRedeemFeed()
        feed_export_data = redeem_obj.export_data(start_date=start_date, end_date=end_date)
 
        self.tester.assertEqual(len(feed_export_data[0]), 1, "Not accurate length of feeds log")
        self.tester.assertEqual(feed_export_data[0][0]["GCP_UCN_NO"], u'USC9217', "Not accurate UCN")
 
    def check_product_data_saved_to_database(self):
        self.tester.assertEquals(1, models.ProductData.objects.count())
        product_data = models.ProductData.objects.all()[0]
        self.tester.assertEquals(u"12345678901232792", product_data.product_id)
        self.tester.assertEquals(3, models.CouponData.objects.count())
        coupon_data = models.CouponData.objects.all()[0]
        self.tester.assertEquals(u"USC9217", coupon_data.unique_service_coupon)
 
    def service_advisor_database_upadted(self):
        sa_obj_1 = models.ServiceAdvisor.objects.filter(service_advisor_id='GMDEALER001SA31')
        dealer_obj_1 = models.Dealer.objects.filter(dealer_id='GMDEALER031')
        self.tester.assertEquals('+911234555555', sa_obj_1[0].user.phone_number)
        sa_dealer_rel_obj_2 = models.ServiceAdvisor.objects.get(service_advisor_id=sa_obj_1[0], dealer_id=dealer_obj_1[0])
        self.tester.assertEquals('N', sa_dealer_rel_obj_2.status)
        sa_obj_2 = models.ServiceAdvisor.objects.filter(service_advisor_id='GMDEALER001SA32')
        dealer_obj_2 = models.Dealer.objects.filter(dealer_id='GMDEALER032')
        self.tester.assertEquals('+914444455555', sa_obj_2[0].user.phone_number)
        dealer_obj_3 = models.Dealer.objects.filter(dealer_id='GMDEALER034')
        sa_obj_3 = models.ServiceAdvisor.objects.filter(service_advisor_id='GMDEALER001SA33')
        self.tester.assertEquals(1, len(sa_obj_3))
        self.tester.assertEquals(0, len(dealer_obj_3))
    
    def admin_login(self):
        data=json.dumps({"username": "bajaj", "password": "bajaj"})
        resp=client.post('/v1/gm-users/login/', data=data, content_type='application/json')
        return json.loads(resp.content)['access_token']
    
    def tranporter_login(self):
        data=json.dumps({"username": "15346", "password": "15346@123"})
        resp=client.post('/v1/gm-users/login/', data=data, content_type='application/json')
        return json.loads(resp.content)['access_token']
    
    def register_circle_head(self, access_token, data):
        uri = '/v1/circle-heads/register/?access_token='+access_token
        response = client.post(uri, data=json.dumps(data), content_type='application/json')
        return response
    
    def get_circle_head(self, access_token):
        uri = '/v1/circle-heads/?access_token='+access_token
        response = client.get(uri, content_type='application/json')
        return response
    
    def update_circle_head(self, access_token, user_id, new_data):
        uri = '/v1/circle-heads/update/'+str(user_id)+'/?access_token='+access_token
        response = client.post(uri, data=json.dumps(new_data), content_type='application/json')
        return response
    
    def register_regional_sales_manager(self,access_token, data):
        uri = '/v1/regional-sales-managers/register/?access_token='+access_token
        response = client.post(uri, data=json.dumps(data), content_type='application/json')
        return response
    
    def get_container_indent(self, access_token):
        uri = '/v1/container-indents/?access_token='+access_token
        response = client.get(uri, content_type='application/json')
        response_data=json.loads(response.content)['objects']
        return response_data

    def get_container_lr(self, access_token):
        uri = '/v1/container-lrs/?access_token='+access_token
        response = client.get(uri, content_type='application/json')
        response_data=json.loads(response.content)['objects']
        return response_data
    
    def submit_container_indent(self, access_token, indent_id):
        data=json.dumps({"status": "Inprogress",  "modified_date": "2015-07-02"})
        uri = '/v1/container-indents/submit/'+indent_id+'/?access_token='+access_token
        resp=client.put(uri, data=data, content_type='application/json')     
    
    def get_indent_count(self, access_token):
        uri = '/v1/container-indents/count/?access_token='+access_token
        response = client.get(uri, content_type='application/json')
        response_data=json.loads(response.content)
        return response_data

    def save_container_lr(self, access_token, transaction_id, status):
        data=json.dumps({"status":status, "modified_date": "2015-03-05",
                         "seal_no":"123", "container_no":"723389"})
        uri = '/v1/container-lrs/save/'+transaction_id+'/?access_token='+access_token
        resp=client.put(uri, data=data, content_type='application/json')  

    def get_manufaturing_data(self, access_token):
        uri = '/v1/manufacturing-details/?access_token='+access_token
        response = client.get(uri, content_type='application/json')
        response_data=json.loads(response.content)
        return response_data['objects']

    def search_sbom_data(self, access_token, parameter, value):
        data = {'parameter': parameter, 'value': value}
        if parameter=='revision':
            data['sku_code']='00DH15ZZ'
        uri = '/v1/bom-plate-parts/search-sbom/'
        response = client.get(uri, data=data, access_token=access_token)
        response_data= json.loads(response.content)
        return response_data['objects']
