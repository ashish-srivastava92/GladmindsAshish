import time
from django.core import management
from tastypie.test import ResourceTestCase

class GladmindsResourceTestCase(ResourceTestCase):
    
    def setUp(self):
        super(GladmindsResourceTestCase, self).setUp()
        management.call_command('loaddata', 'etc/testdata/template.json', verbosity=0)
        management.call_command('loaddata', 'etc/testdata/customer.json', verbosity=0)
        management.call_command('loaddata', 'etc/testdata/brand.json', verbosity=0)
        management.call_command('loaddata', 'etc/testdata/producttype.json', verbosity=0)
        management.call_command('loaddata', 'etc/testdata/dealer.json', verbosity=0)
        management.call_command('loaddata', 'etc/testdata/serviceadvisor.json', verbosity=0)
        management.call_command('loaddata', 'etc/testdata/product.json', verbosity=0)
        management.call_command('loaddata', 'etc/testdata/coupon.json', verbosity=0)
        self.MESSAGE_URL = "/v1/messages"
    
    def assertSuccessfulHttpResponse(self, resp, msg=None):
        """
        Ensures the response is returning status between 200 and 299,
         both inclusive 
        """
        return self.assertTrue(resp.status_code >= 200 
                               and resp.status_code <= 299, msg) 
        

class CustomerRegistrationTest(GladmindsResourceTestCase):
    def setUp(self):
        super(CustomerRegistrationTest, self).setUp()
        MSG_CUST_REG = "GCP_REG test.user@test.com Test User"
        PHONE_NUMBER = "+TS{0}".format(int(time.time()))
        self.CUST_REG = {'text': MSG_CUST_REG, 'phoneNumber': PHONE_NUMBER}
        
        #iNVALID MESSAGE
        MSG_INVALID_CUST_REG = "GCP_REG test.user@test.com"
        self.INVALID_CUST_REG = {'text': MSG_INVALID_CUST_REG, 'phoneNumber': PHONE_NUMBER}
    
        #INVALID KEYWORD
        MSG_INVALID_CUST_REG_KEY = "REG test.user@test.com Test User"
        self.INVALID_CUST_REG_KEY = {'text': MSG_INVALID_CUST_REG_KEY, 'phoneNumber': PHONE_NUMBER}
        
        #Already Register
        MSG_ALREADY_CUST_REG = "GCP_REG test.gladminds@test.com Test Gldaminds"
        self.ALREADY_CUST_REG = {'text': MSG_ALREADY_CUST_REG, 'phoneNumber': '+TS0000000001'}
        

    def test_customer_registration(self):
       resp = self.api_client.post(uri=self.MESSAGE_URL, data = self.CUST_REG)
       self.assertHttpOK(resp)
        
    def test_invalid_message(self):
        resp = self.api_client.post(uri=self.MESSAGE_URL, data = self.INVALID_CUST_REG)
        self.assertHttpBadRequest(resp)
         
        resp = self.api_client.post(uri=self.MESSAGE_URL, data = self.INVALID_CUST_REG_KEY)
        self.assertHttpBadRequest(resp)
        
    def test_customer_registration(self):
       resp = self.api_client.post(uri=self.MESSAGE_URL, data = self.CUST_REG)
       self.assertHttpOK(resp)
       
    def test_already_registered_customer(self):
        resp = self.api_client.post(uri=self.MESSAGE_URL, data = self.ALREADY_CUST_REG)
        self.assertHttpOK(resp)
            
class CustomerServiceTest(GladmindsResourceTestCase):
     
     def setUp(self):
         super(CustomerServiceTest, self).setUp()
         VALID_MSG_SERVICE = "SERVICE F0B18AE"
         VALID_PHONE_NUMBER = "+TS9800000011"
         self.MSG_SVC = {'text': VALID_MSG_SERVICE, 'phoneNumber': VALID_PHONE_NUMBER}
         
         #Invalid check customer id
         INVALID_MSG_SERVICE = "SERVICE 000000"
         self.IN_MSG_SVC = {'text': INVALID_MSG_SERVICE, 'phoneNumber': VALID_PHONE_NUMBER}
         
         #Invalid Phone Number
         INVALID_PHONE_NUMBER = "+TA0000000011"
         self.IN_PH_MSG_SVC = {'text': VALID_MSG_SERVICE, 'phoneNumber': INVALID_PHONE_NUMBER}
    
     def test_valid_service(self):
        resp = self.api_client.post(uri=self.MESSAGE_URL, data = self.MSG_SVC)
        self.assertHttpOK(resp)
    
     def test_invalid_service(self):
        resp = self.api_client.post(uri=self.MESSAGE_URL, data = self.IN_MSG_SVC)
        self.assertHttpOK(resp)
        
        resp = self.api_client.post(uri=self.MESSAGE_URL, data = self.IN_PH_MSG_SVC)
        self.assertHttpOK(resp)
        
    
class CouponCheckAndClosure(GladmindsResourceTestCase):
    def setUp(self):
        super(CouponCheckAndClosure, self).setUp()
        self.MSG_CHECK_COUPON = "CHECK TESTVECHILEID00002 50 2"
        self.PHONE_NUMBER = "+SA0000000000"
        self.CHECK_COUPON = {'text': self.MSG_CHECK_COUPON, 'phoneNumber': self.PHONE_NUMBER}
        self.INVALID_PHONE_NUMBER="+0000000000"
        self.CHECK_INVALID_COUPON={'text': self.MSG_CHECK_COUPON, 
                                   'phoneNumber': self.INVALID_PHONE_NUMBER}
        self.VALID_COUPON="CHECK TESTVECHILEID00002 50 3"
        self.CHECK_VALID_COUPON = {'text': self.VALID_COUPON, 'phoneNumber': self.PHONE_NUMBER}
    
    '''
    Test Case Checking coupon validation can be done only from 
    registered dealer's number
    '''
    def test_check_coupon_sa(self):
       resp = self.api_client.post(uri=self.MESSAGE_URL, data=self.CHECK_COUPON)
       self.assertHttpOK(resp)
       resp = self.api_client.post(uri=self.MESSAGE_URL, data=self.CHECK_INVALID_COUPON)
       self.assertHttpUnauthorized(resp)
       
    def test_valid_coupon(self):
        resp = self.api_client.post(uri=self.MESSAGE_URL, data=self.CHECK_VALID_COUPON)
        self.assertHttpOK(resp)
       

    
       
       
       