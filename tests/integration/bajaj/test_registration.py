from django.test import TestCase
from django.test.client import Client
from integration.bajaj.base import BaseTestCase
from integration.bajaj.test_brand_logic import Brand
from integration.bajaj.test_system_logic import System

client  =  Client(SERVER_NAME='bajaj')

class TestDealerRegistration(BaseTestCase):
    multi_db=True
    
    def setUp(self):
        self.client = Client(SERVER_NAME='bajaj')
        BaseTestCase.setUp(self)
        self.system = System(self)

    def test_new_dealer(self):
        dealer = self.system
        dealer.dealer_login()


class TestCustomerRegistration(BaseTestCase):
    multi_db=True
    
    def setUp(self):
        TestCase.setUp(self)
        BaseTestCase.setUp(self)
        self.brand = Brand(self)
        brand = self.brand
        self.system = System(self)
        self.client = Client(SERVER_NAME='bajaj')
        self.create_user(username='gladminds', email='gladminds@gladminds.co', password='gladminds')
        self.create_user(username='bajaj', email='bajaj@gladminds.co', password='bajaj', brand='bajaj')
        brand.send_dispatch_feed()
        '''This both feed will create product data, product type ,brand database'''

    def test_temp_customer_registration(self):
        dealer = self.system
        dealer.dealer_login()
        dealer.register_customer()

    def test_update_cutomer_mobile(self):
        dealer = self.system
        brand = self.brand
        brand.send_purchase_feed()
        product_obj = dealer.get_product_details(product_id='12345678901232792')
        dealer.verify_result(input=product_obj.customer_phone_number, output='+917777777777')
        brand.send_purchase_feed_with_diff_cust_num()
        product_obj = dealer.get_product_details(product_id='12345678901232792')
        dealer.verify_result(input=product_obj.customer_phone_number, output='+918888888888')
 
    def test_asc_registration_by_self(self):
        dealer = self.system
        dealer.dealer_login()
        dealer.check_asc_exists('test_asc','test_asc','dealer')
 
    def test_asc_registration_by_dealer(self):
        dealer = self.system
        dealer.check_asc_exists('test_asc','test_asc','self')
