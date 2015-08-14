import time
from integration.bajaj.base_integration import BrandResourceTestCase
from integration.bajaj.base import BaseTestCase
from integration.bajaj.test_brand_logic import Brand
from integration.bajaj.test_system_logic import System

from django.test import TestCase

from gladminds.bajaj import models
from django.test.client import Client
import logging
import json
logger = logging.getLogger('gladminds')

client = Client()


class CustomerRegistrationTest(BaseTestCase):
 
    def setUp(self):
        TestCase.setUp(self)
        BaseTestCase.setUp(self)
        self.brand = Brand(self)
        self.system = System(self)
        MSG_CUST_REG = "GCP_REG test.user@test.com TestUser"
        PHONE_NUMBER = "+TS{0}".format(int(time.time()))
        self.CUST_REG = {'text': MSG_CUST_REG, 'phoneNumber': PHONE_NUMBER}
 
        # iNVALID MESSAGE
        MSG_INVALID_CUST_REG = "GCP_REG test.user@test.com"
        self.INVALID_CUST_REG = {
            'text': MSG_INVALID_CUST_REG, 'phoneNumber': PHONE_NUMBER}
 
        # INVALID KEYWORD
        MSG_INVALID_CUST_REG_KEY = "REG test.user@test.com TestUser"
        self.INVALID_CUST_REG_KEY = {
            'text': MSG_INVALID_CUST_REG_KEY, 'phoneNumber': PHONE_NUMBER}
 
        # Already Register
        MSG_ALREADY_CUST_REG = "GCP_REG test.gladminds@test.com Test Gldaminds"
        self.ALREADY_CUST_REG = {
            'text': MSG_ALREADY_CUST_REG, 'phoneNumber': '+TS0000000001'}
 
    def test_customer_registration(self):
        brand = self.brand
        system = self.system
        response = brand.send_sms(url=self.MESSAGE_URL, message=self.CUST_REG)
        system.verify_result(input=response.status_code, output=200)
 
    def test_invalid_message(self):
        brand = self.brand
        system = self.system
        response = brand.send_sms(url=self.MESSAGE_URL, message=self.INVALID_CUST_REG)
        system.verify_result(input=response.status_code, output=400)
        response = brand.send_sms(url=self.MESSAGE_URL, message=self.INVALID_CUST_REG_KEY)
        system.verify_result(input=response.status_code, output=400)
 
    def test_already_registered_customer(self):
        brand = self.brand
        system = self.system
        response = brand.send_sms(url=self.MESSAGE_URL, message=self.ALREADY_CUST_REG)
        system.verify_result(input=response.status_code, output=200)


class CustomerServiceTest(BaseTestCase):
 
    def setUp(self):
        TestCase.setUp(self)
        BaseTestCase.setUp(self)
        self.brand = Brand(self)
        self.system = System(self)
        VALID_MSG_SERVICE = "SERVICE F0B18AE"
        VALID_PHONE_NUMBER = "+TS9800000011"
        self.vlid_service_message = {
            'text': VALID_MSG_SERVICE, 'phoneNumber': VALID_PHONE_NUMBER}
 
        # Invalid check customer id
        INVALID_MSG_SERVICE = "SERVICE 000000"
        self.inavlid_service_message = {
            'text': INVALID_MSG_SERVICE, 'phoneNumber': VALID_PHONE_NUMBER}
 
        # Invalid Phone Number
        INVALID_PHONE_NUMBER = "+TA0000000011"
        self.service_message_with_invalid_phone_number = {
            'text': VALID_MSG_SERVICE, 'phoneNumber': INVALID_PHONE_NUMBER}
 
    def test_valid_service(self):
        brand = self.brand
        system = self.system
        response = brand.send_sms(url=self.MESSAGE_URL, message=self.vlid_service_message)
        system.verify_result(input=response.status_code, output=200)
 
    def test_invalid_service(self):
        brand = self.brand
        system = self.system
        response = brand.send_sms(url=self.MESSAGE_URL, message=self.inavlid_service_message)
        system.verify_result(input=response.status_code, output=200)
        response = brand.send_sms(url=self.MESSAGE_URL, message=self.service_message_with_invalid_phone_number)
        system.verify_result(input=response.status_code, output=200)


class CouponCheckAndClosure(BrandResourceTestCase):

    def setUp(self):
        '''
            Test Case Checking coupon validation can be done only from
            registered dealer's number
        '''
        BrandResourceTestCase.setUp(self)
        self.brand = Brand(self)
        brand = self.brand
        self.system = System(self)
        self.create_user(username='gladminds', email='gladminds@gladminds.co', password='gladminds', brand='bajaj')
        self.create_user(username='bajaj', email='bajaj@gladminds.co', password='bajaj', brand='bajaj')
        brand.send_service_advisor_feed()
        brand.send_dispatch_feed()
        brand.send_purchase_feed()
        self.product_obj = brand.get_product_obj(product_id='12345678901232792')

    def test_simple_inprogress_from_unused(self):
        brand = self.brand
        system = self.system
        create_sms_dict = {'kms': 450, 'service_type': 1, 'sap_customer_id': '29122701'}
        brand.check_coupon(create_sms_dict, "1111111111")
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9217')
        system.verify_result(input=coupon_status.status, output=4)

#     Need to find out how to write this test case because it creates cyclic dependency.
#     def test_validate_dealer(self):
#         self.assertEqual(models.ServiceAdvisor.objects.count(), 1, "Service Advisor Obj is not created as required")
#         obj = GladmindsResources()
#         self.assertEqual(obj.validate_dealer("9999999999").phone_number, u"9999999999", "validate dealer")
#         sa_obj = models.ServiceAdvisor.objects.filter(service_advisor_id='DEALER001SA001')
#         sa_dealer_rel = models.ServiceAdvisorDealerRelationship.objects.filter(service_advisor_id = sa_obj[0])[0]
#         sa_dealer_rel.status = 'N'
#         sa_dealer_rel.save()

    def test_coupon_exceed(self):
        brand = self.brand
        system = self.system
        create_sms_dict = {'kms': 12050, 'service_type': 3, 'sap_customer_id': '29122701'}
        brand.check_coupon(create_sms_dict, '1111111111')
        system.verify_result(input=models.CouponData.objects.filter(unique_service_coupon='USC9217')[0].status, output=5)
        system.verify_result(input=models.CouponData.objects.filter(unique_service_coupon='USC9227')[0].status, output=5)
        system.verify_result(input=models.CouponData.objects.filter(unique_service_coupon='USC9237')[0].status, output=4)
  
    def test_invalid_ucn_or_sap_id(self):
        brand = self.brand
        create_sms_dict = {'kms': 450, 'service_type': 1, 'sap_customer_id': '29122701'}
        brand.check_coupon(create_sms_dict, "1111111111")
        data = 'C {0} {1}'.format('29122701', 'USC9227')
        sms_dict = {'text': data, 'phoneNumber': '1111111111'}
        response = brand.send_sms(url=self.MESSAGE_URL, message=sms_dict)
        result = json.loads(response.content)
        self.assertFalse(result['status'])

    def test_coupon_logic_1(self):
        '''
            If we have check coupon with this message
            and 1 service is unused.
            then 1 is in-progress and 2 is in unused state
        '''
        brand = self.brand
        system = self.system
        create_sms_dict = {'kms': 450, 'service_type': 2, 'sap_customer_id': '29122701'}
        brand.check_coupon(create_sms_dict, '1111111111')
  
        '''In-progress Coupon'''
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9227')
        system.verify_result(input=coupon_status.status, output=4)
     
        '''Unused Coupon'''
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9217')
        system.verify_result(input=coupon_status.status, output=1)
 
    def test_coupon_logic_2(self):
        '''
            If we have check coupon with this message
            check SAP001 600 2.
            Then then 1 is exceed and 2 is in unused state
        '''
        brand = self.brand
        system = self.system
 
        create_sms_dict = {'kms': 2600, 'service_type': 1, 'sap_customer_id': '29122701'}
        brand.check_coupon(create_sms_dict, '1111111111')
 
        '''Exceed Coupon'''
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9217')
        system.verify_result(input=coupon_status.status, output=5)
 
        '''Unused Coupon'''
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9227')
        system.verify_result(input=coupon_status.status, output=1)
 
    def test_coupon_logic_3(self):
        '''
            Initial state
            coupon 1 is in inprogress and valid in b/w (1 - 2000)
            coupon 2 is in unused and valid in b/w (2001 - 8000)
            Check command returns service type 1
        '''
        brand = self.brand
        system = self.system
  
        create_sms_dict = {'kms': 1100, 'service_type': 1, 'sap_customer_id': '29122701'}
        brand.check_coupon(create_sms_dict, '1111111111')
  
        '''in_progess_coupon status should be 4'''
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9217')
        system.verify_result(input=coupon_status.status, output=4)
        
        create_sms_dict = {'kms': 1100, 'service_type': 2, 'sap_customer_id': '29122701'}
        brand.check_coupon(create_sms_dict, '1111111111')
  
        '''Coupon should be in unused State'''
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9227')
        system.verify_result(input=coupon_status.status, output=1)
  
    def test_coupon_logic_4(self):
        '''
            Initial state
            coupon 1 is in in-progress and valid in b/w (400 - 500)
            coupon 2 is in unused and valid in b/w (900 - 1000)
            If we have check coupon with this message
            check SAP001 2100 2
            Mark 1 service as exceed limit
            And make 2 service as inprogress
        '''
        brand = self.brand
        system = self.system
  
        sms_dict = {'kms': 450, 'service_type': 1, 'sap_customer_id': '29122701'}
        brand.check_coupon(sms_dict, '1111111111')
        
        '''in_progess_coupon status should be 4'''
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9217')
        system.verify_result(input=coupon_status.status, output=4)
  
        sms_dict = {'kms': 2200, 'service_type': 2, 'sap_customer_id': '29122701'}
        brand.check_coupon(sms_dict, '1111111111')
  
        '''in_progess_coupon status should be 4'''
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9217')
        system.verify_result(input=coupon_status.status, output=5)
  
        '''Coupon should be in unused State'''
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9227')
        system.verify_result(input=coupon_status.status, output=4)
  
    def test_coupon_logic_5(self):
        '''
            Initial state
            coupon 1 is in unused and valid in b/w (400 - 500)
            coupon 2 is in unused and valid in b/w (900 - 1000)
            coupon 3 is in unused and valid in b/w (1400 - 1500)
            If we have check coupon with this message
            check SAP001 1100 1
            Mark 1 as exceed limit
            Mark 2 as exceed limit
            Mark 3 as in progress
 
            check SAP001 450 1
            Mark 1 as in progress
            Mark 2 as unused
            Mark 3 as unused
        '''
        
        brand = self.brand
        system = self.system
 
        sms_dict = {'kms': 9200, 'service_type': 2, 'sap_customer_id': '29122701'}
        
        brand.check_coupon(sms_dict, '1111111111')
               
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9217')
        system.verify_result(input=coupon_status.status, output=5)
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9227')
        system.verify_result(input=coupon_status.status, output=5)
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9237')
        system.verify_result(input=coupon_status.status, output=1)
 
        sms_dict = {'kms': 900, 'service_type': 1, 'sap_customer_id': '29122701'}
        brand.check_coupon(sms_dict, '1111111111')
        
        
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9217')
        system.verify_result(input=coupon_status.status, output=4)
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9227')
        system.verify_result(input=coupon_status.status, output=1)
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9237')
        system.verify_result(input=coupon_status.status, output=1)
  
        '''
            Initial state
            coupon 1 is in progress
            coupon 2 is in unused and valid in b/w (900 - 1000)
            coupon 3 is in unused and valid in b/w (1400 - 1500)
            If we have check coupon with this message
            check SAP001 1550 1
            Mark 1 as exceed limit
            Mark 2 as exceed limit
            Mark 3 as exceed limit
        '''
        sms_dict = {'kms': 15050, 'service_type': 3, 'sap_customer_id': '29122701'}
        brand.check_coupon(sms_dict, '1111111111')
  
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9217')
        system.verify_result(input=coupon_status.status, output=5)
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9227')
        system.verify_result(input=coupon_status.status, output=5)
        coupon_status = brand.check_coupon_status(unique_service_coupon='USC9237')
        system.verify_result(input=coupon_status.status, output=5)


class BrandData(BrandResourceTestCase, BaseTestCase):
 
    def setUp(self):
        TestCase.setUp(self)
        BaseTestCase.setUp(self)
        self.brand = Brand(self)
        self.system = System(self)
        self.PHONE_NUMBER = "+TS0000000000"
        self.VALID_BRAND_ID = {
            'text': "BRAND BRAND001", 'phoneNumber': self.PHONE_NUMBER}
        self.INVALID_BRAND_ID = {
            'text': "BRAND BRAN", 'phoneNumber': self.PHONE_NUMBER}
 
    '''
    TestCase for getting all products associated with the brand for a customer
    '''
 
    def test_get_all_products_of_a_brand(self):
        brand = self.brand
        system = self.system
        response = brand.send_sms(url=self.MESSAGE_URL, message=self.VALID_BRAND_ID)
        system.verify_result(input=response.status_code, output=200)
 
    def test_get_all_brand(self):
        brand = self.brand
        system = self.system
        response = brand.send_sms(url=self.MESSAGE_URL, message=self.INVALID_BRAND_ID)
        system.verify_result(input=response.status_code, output=200)