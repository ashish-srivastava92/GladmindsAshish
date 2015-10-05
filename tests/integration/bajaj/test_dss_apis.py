import logging
import json
from django.test import TestCase
from django.utils import unittest

from integration.bajaj.base import BaseTestCase
from integration.bajaj.test_brand_logic import Brand
from integration.bajaj.test_system_logic import System
from gladminds.core.auth_helper import Roles
from test_constants import CIRCLE_HEAD, RM_DATA

logger = logging.getLogger('gladminds')

class CircleHeadResourceTest(BaseTestCase):
    multi_db=True
    
    def setUp(self):
        TestCase.setUp(self)
        self.brand = Brand(self)
        self.system = System(self)
        BaseTestCase.setUp(self)
        self.create_user(username='bajaj', email='bajaj@gladminds.co', password='bajaj', is_superuser=True)
        self.access_token = self.brand.admin_login()
        
    def test_registration_of_circle_head(self):
        '''
           Test the API to register a Circle head
        '''
        brand = self.brand
        system = self.system
        admin_access_token=self.access_token
        resp = brand.register_circle_head(admin_access_token,CIRCLE_HEAD)
        self.assertEquals(resp.status_code,200)
        response_data=json.loads(resp.content)['status']
        system.verify_result(input=response_data, output=1)
        resp = brand.get_circle_head(admin_access_token)
        system.verify_result(input= json.loads(resp.content)['objects'][0]["user"]["user"]["email"], output=CIRCLE_HEAD["email"])
        
        
    def test_get_circle_head_list(self):
        '''
           Test the API to get list of all Circle heads
           Admin sees all the Circle heads
        '''
        brand = self.brand
        system = self.system
        admin_access_token=self.access_token
        ch_registration = brand.register_circle_head(admin_access_token,CIRCLE_HEAD)
        response = brand.get_circle_head(admin_access_token)
        self.assertEquals(response.status_code,200)
        circle_head_data = json.loads(response.content)['objects']
        system.verify_result(input=len(circle_head_data), output=1)
        
    def test_update_circle_head(self):
        '''
           Test the API to update a Circle head
        '''
        brand = self.brand
        system = self.system
        admin_access_token=self.access_token
        ch_registration = brand.register_circle_head(admin_access_token,CIRCLE_HEAD)
        user_id_of_ch = 2
        new_detail = {"phone_number":"1234512345","name":"chtesting1","email":"testing1@abc.com"}
        response = brand.update_circle_head(admin_access_token, user_id_of_ch, new_detail)
        self.assertEquals(response.status_code,200)
        status = json.loads(response.content)['status']
        system.verify_result(input=status, output=1)
        ch_data = brand.get_circle_head(admin_access_token)
        system.verify_result(input= json.loads(ch_data.content)['objects'][0]["user"]["user"]["email"], output=new_detail["email"])
        

class RegionalSalesManagerResourceTest(BaseTestCase):
    multi_db=True
    
    def setUp(self):
        TestCase.setUp(self)
        self.brand = Brand(self)
        self.system = System(self)
        BaseTestCase.setUp(self)
        self.create_user(username='bajaj', email='bajaj@gladminds.co', password='bajaj', is_superuser=True)
        self.access_token = self.brand.admin_login()
        
    def test_registration_of_regional_sales_manager(self):
        '''
           Test the API to register a Regional Sales manager
        '''
        brand = self.brand
        system = self.system
        admin_access_token=self.access_token
        ch_registration = brand.register_circle_head(admin_access_token, CIRCLE_HEAD)
        resp = brand.register_regional_sales_manager(admin_access_token, RM_DATA)
        self.assertEquals(resp.status_code,200)
        response_data=json.loads(resp.content)['status']
        system.verify_result(input=response_data, output=1)


        
