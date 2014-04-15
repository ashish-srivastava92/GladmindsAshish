from integration.base_integration import GladmindsResourceTestCase
from django.test.utils import override_settings
from gladminds.tasks import send_service_detail, expire_service_coupon
from datetime import datetime, timedelta
from unit.base_unit import GladmindsUnitTestCase


class TestCelery(GladmindsResourceTestCase):
    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='django')
    
    def test_send_sms(self):
        result = send_service_detail.delay(phone_number='99999999', message='Test Message')
        self.assertTrue(result.successful())
        
    @override_settings(SMS_CLIENT = "MOCK_FAIL")
    def test_send_sms_fail(self):
        result = send_service_detail.delay(phone_number='99999999', message='Test Message')
        self.assertFalse(result.successful())
        


class TestCronjobs(GladmindsUnitTestCase):
    
    def setUp(self):
        brand_obj = self.get_brand_obj(brand_id='brand001', brand_name='bajaj')
        product_type_obj = self.get_product_type_obj(brand_id=brand_obj, product_name='DISCO120', product_type='BIKE')
        dealer_obj = self.get_delear_obj(dealer_id='DEALER001')
        customer_obj = self.get_customer_obj(phone_number='9999999')
        product_obj = self.get_product_obj(vin="VINXXX001", producttype_data=product_type_obj, dealer_data = dealer_obj\
                                           , customer_phone_number = customer_obj, sap_customer_id='SAP001')
        service_advisor = self.get_service_advisor_obj(dealer_data = dealer_obj, service_advisor_id = 'SA001Test'\
                                                 ,name='UMOTO', phone_number='+914444861111', status='Y')
        self.get_dealer_service_advisor_obj(dealer_data=dealer_obj, service_advisor_id=service_advisor, status='Y')
        service_advisor1 = self.get_service_advisor_obj(dealer_data = dealer_obj, service_advisor_id = 'SA002Test'\
                                                 ,name='UMOTOR', phone_number='+919999999999', status='Y')
        self.get_dealer_service_advisor_obj(dealer_data=dealer_obj, service_advisor_id=service_advisor1, status='Y')
        self.get_coupon_obj(unique_service_coupon='COUPON005', product_data=product_obj, valid_days=30\
                                         , valid_kms=500, service_type = 1, mark_expired_on = datetime.now()+timedelta(days=1), status=1)
        customer_obj1 = self.get_customer_obj(phone_number='8888888')
        product_obj1 = self.get_product_obj(vin="VINXXX002", producttype_data=product_type_obj, dealer_data = dealer_obj\
                                           , customer_phone_number = customer_obj1, sap_customer_id='SAP002')
        self.get_coupon_obj(unique_service_coupon='COUPON004', actual_service_date=datetime.now()-timedelta(days=10), product_data=product_obj1, valid_days=30\
                                         , valid_kms=500, service_type = 1, mark_expired_on = datetime.now()-timedelta(days=1), status=4)
        self.get_coupon_obj(unique_service_coupon='COUPON006', actual_service_date=datetime.now()-timedelta(days=40), product_data=product_obj, valid_days=30\
                                         , valid_kms=3000, service_type = 2, mark_expired_on = datetime.now()-timedelta(days=1), status=4)
        self.get_coupon_obj(unique_service_coupon='COUPON007', product_data=product_obj, valid_days=30\
                                         , valid_kms=6000, service_type = 3, mark_expired_on = datetime.now()-timedelta(days=1), status=1)
    
    def test_expire_service_coupon(self):
        expire_service_coupon()
        self.assertEqual(self.filter_coupon_obj('COUPON004').status, 4)
        self.assertEqual(self.filter_coupon_obj('COUPON005').status, 1)
        self.assertEqual(self.filter_coupon_obj('COUPON006').status, 3)
        self.assertEqual(self.filter_coupon_obj('COUPON007').status, 3)
        