from integration.base_integration import GladmindsResourceTestCase
from django.test.client import Client

from gladminds.aftersell.models import common as afterbuy_common


class TestSaveFormRegistration(GladmindsResourceTestCase):

    def setUp(self):
        self.client = Client()
        pass

    def _test_asc_registration(self):
        data = {
                    u'name': u'TestASCUser',
                    u'address': u'TestASCUser Address',
                    u'pincode': u'111111',
                    u'password': u'password',
                    u'phone_number': u'9999999999',
                    u'email': u'TestASCUser@TestASCUser.com'
                }

        response = self.client.post('/save/asc', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(afterbuy_common.ASCSaveForm.objects.count(), 1)
        self.assertEqual(afterbuy_common
                         .ASCSaveForm.objects.all()[0].phone_number,
                          data['phone_number'])

    def test_fail_registration_mail(self):
        data = {
                    u'name': u'TestASCUser',
                    u'address': u'TestASCUser Address',
                    u'pincode': u'111111',
                    u'password': u'password',
                    u'phone_number': u'9999999999',
                    u'email': u'TestASCUser@TestASCUser.com'
                }

        response = self.client.post('/save/asc', data=data)
        self.assertEqual(response.status_code, 200)
        
        
