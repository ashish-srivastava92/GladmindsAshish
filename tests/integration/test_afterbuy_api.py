''' Test Case for testing out the Afterbuy Api
'''
from integration import base_integration
from django.test.client import Client
from test_constants import AFTERBUY_PRODUCTS
import json

client  =  Client(SERVER_NAME='afterbuy')

class TestAfterbuyApi(base_integration.GladmindsResourceTestCase):
    def setUp(self):
        super(TestAfterbuyApi, self).setUp()

    def test_user_registration(self):
        create_mock_data = {'name': 'saurav','phone_number':'7760814041','email_id':'srv.sngh@gmail.com','password':'123'}
        uri = '/afterbuy/v1/consumers/registration/'
        resp = client.post(uri, format='json', data=create_mock_data)
        self.assertEquals(200, resp.status_code)
 
    def test_user_login(self):
        login_data = {'phone_number':'7760814041', 'password':'123'}
        uri = '/afterbuy/v1/consumers/login/'
        resp = client.post(uri, format='json', data=login_data)
        self.assertEquals(200, resp.status_code)
         
        # Checking login by email id
        login_data = {'email_id':'srv.sngh@gmail.com', 'password':'123'}
        uri = '/afterbuy/v1/consumers/login/'
        resp = client.post(uri, format='json', data=login_data)
        self.assertEquals(200, resp.status_code)
        
    def test_user_emailid_exists(self):
        create_mock_data = {'email_id':'srv.sngh@gmail.com'}
        uri = '/afterbuy/v1/consumers/authenticate-email/'
        resp = client.post(uri, format='json', data=create_mock_data)
        self.assertEquals(200, resp.status_code)
        
        
    def test_user_send_otp(self):
        create_mock_data = {'phone_number':'7760814041'}
        uri = '/afterbuy/v1/consumers/send-otp/'
        resp = client.post(uri, format='json', data=create_mock_data)
        self.assertEquals(200, resp.status_code)
        
    def test_change_user_password(self):
        create_mock_data = {'phone_number':'7760814041', 'password': '1234'}
        uri = '/afterbuy/v1/consumers/forgot-password/'
        resp = client.post(uri, format='json', data=create_mock_data)
        self.assertEquals(200, resp.status_code)
#         
    def test_fetch_user_detail(self):
        self.test_user_registration()
        create_mock_data = {'email_id':'srv.sngh@gmail.com'}
        uri = '/afterbuy/v1/consumers/1/details/'
        resp = client.get(uri, format='json', data=create_mock_data)
        self.assertEquals(200, resp.status_code)
        
    def test_add_product(self):
        self.test_user_registration()
                
    def test_fetch_user_products(self):
        self.test_user_registration()
        create_mock_data = {'email_id':'srv.sngh@gmail.com'}
        uri = '/afterbuy/v1/consumers/1/products/'
        resp = client.get(uri, format='json', data=create_mock_data)
        self.assertEquals(200, resp.status_code)

    def test_product_api(self):
        #Checking post api
        json_data = json.dumps(AFTERBUY_PRODUCTS)
        resp = client.post('/afterbuy/v1/products/', json_data, content_type='application/json')
        self.assertEquals(resp.status_code,201)
        
        #Checking get api
        resp = client.get('/afterbuy/v1/products/1/')
        self.assertEquals(resp.status_code,200)
        self.assertEqual(self.deserialize(resp)['nick_name'], "aaa")
        self.assertEqual(len(self.deserialize(resp)), 17)
        
        #Cheking put api
        json_data = json.dumps({"nick_name":"bbb"})
        resp = client.put('/afterbuy/v1/products/1/',json_data, content_type='application/json')
        self.assertEquals(resp.status_code, 200)
        resp = client.get('/afterbuy/v1/products/1/')
        self.assertEqual(self.deserialize(resp)['nick_name'], "bbb")
        
        