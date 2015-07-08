import json

from django.test.client import Client

from integration.bajaj.base import BaseTestCase
from test_constants import BRAND_PRODUCT_RANGE, BRAND_VERTICAL, BOM_HEADER, \
    BOM_PLATE_PART, ECO_RELEASE, ECO_IMPLEMENTATION, BOM_VISUALIZATION, \
    SBOM_REVIEW


client=Client(SERVER_NAME='bajaj')

class PartChangeTest(BaseTestCase):
    multi_db=True
    def setUp(self):
        TestCase.setUp(self)
        self.brand = Brand(self)
        self.system = System(self)
        BaseTestCase.setUp(self)
        self.create_user(username='bajaj', email='bajaj@gladminds.co', password='bajaj')
        self.access_token = self.brand.admin_login()


    def post(self, uri, data, access_token=None, content_type='application/json'):
        if access_token:
            uri = uri+'?access_token='+access_token
        resp = client.post(uri, data=json.dumps(data), content_type=content_type)
        return resp

    def get(self, uri, access_token, data=None, content_type='application/json'):
        resp = client.get(uri+'&&access_token='+access_token, content_type=content_type)
        return resp
    
    def user_login(self):
        self.create_user(username='user', email='asc@xyz.com', password='123', 
                        phone_number="+911234567890", brand='bajaj')
        data={"username": "user", "password": "123" }
        resp=self.post(uri='/v1/gm-users/login/', data=data)
        return json.loads(resp.content)['access_token']
    
    def test_get_brand_vertical(self):
        access_token = self.user_login()
        uri = '/v1/brand-verticals/'
        resp = self.post(uri, BRAND_VERTICAL, access_token)
        self.assertEquals(resp.status_code, 201)
        uri = '/v1/brand-verticals/?name=vertical2'
        resp = self.get(uri, access_token, content_type='application/json')
        self.assertEquals(resp.status_code, 200)
        
    def test_get_brand_product_range(self):
        access_token = self.user_login()
        uri = '/v1/brand-product-range/'
        resp = self.post(uri, data=BRAND_PRODUCT_RANGE, access_token=access_token)
        self.assertEquals(resp.status_code,201)
        uri = '/v1/brand-product-range/'
        resp = self.get(uri=uri, access_token=access_token)
        self.assertEquals(resp.status_code , 200)
        self.assertEquals(json.loads(resp.content)['objects'][0]['sku_code'], "112")
    
    def test_get_bom_header(self):
        access_token = self.user_login()
        uri = '/v1/bom-headers/'
        resp = self.post(uri, data=BOM_HEADER, access_token=access_token)
        self.assertEquals(resp.status_code, 201)
        uri = '/v1/bom-headers/?sku_code=112'
        resp = self.get(uri, access_token)
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(json.loads(resp.content)['objects'][0]['sku_code'], "112")
        self.assertEquals(json.loads(resp.content)['objects'][0]['bom_number'], "1232")
    
    def test_bom_plate_part(self):
        access_token = self.user_login()
        uri = '/v1/bom-plate-parts/'
        resp = self.post(uri, data=BOM_PLATE_PART, access_token=access_token)
        self.assertEquals(resp.status_code, 201)
        uri = '/v1/bom-plate-parts/?bom__sku_code=112'
        resp = self.get(uri, access_token=access_token)
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(json.loads(resp.content)['objects'][0]['plate']['plate_id'], "44")
        
    def test_eco_release(self):
        access_token = self.user_login()
        uri = '/v1/eco-releases/'
        resp = self.post(uri, data=ECO_RELEASE, access_token=access_token)
        self.assertEquals(resp.status_code, 201)
        uri = '/v1/eco-releases/1/?access_token='+access_token
        resp = client.get(uri, content_type='application/json')
        self.assertEquals(resp.status_code, 200)
        
    def test_eco_implementation(self):
        access_token = self.user_login()
        uri = '/v1/eco-implementations/'
        resp = self.post(uri, data=ECO_IMPLEMENTATION, access_token=access_token)
        self.assertEquals(resp.status_code, 201)
        uri = '/v1/eco-implementations/1/?access_token='+access_token
        resp = client.get(uri, content_type='application/json')
        self.assertEquals(resp.status_code, 200)
    
    def test_get_plates_image(self):
        access_token = self.user_login()
        uri = '/v1/bom-plate-parts/'
        resp = self.post(uri, data=BOM_PLATE_PART, access_token=access_token)
        self.assertEquals(resp.status_code, 201)
        uri = '/v1/bom-plate-parts/get-plates/?sku_code=112&&bom_number=211760'
        resp = self.get(uri, access_token=access_token)
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(json.loads(resp.content)[0]['plate_id'], "44")

    def test_get_sbom_details(self):
        access_token = self.user_login()
        uri = '/v1/bom-visualizations/'
        resp = self.post(uri, data=BOM_VISUALIZATION, access_token=access_token)
        self.assertEquals(resp.status_code, 201)
        uri = '/v1/bom-plate-parts/?plate__plate_id=44&&bom__bom_number=211760&&bom__sku_code=112'
        resp = self.get(uri, access_token=access_token)
        self.assertEquals(json.loads(resp.content)['objects'][0]['part']['part_number'], "15161069")
        self.assertEquals(resp.status_code, 200)

    def test_review_sbom(self):
        access_token = self.user_login()
        uri = '/v1/bom-visualizations/'
        resp = self.post(uri, data=BOM_VISUALIZATION, access_token=access_token)
        self.assertEquals(resp.status_code, 201)
        uri = '/v1/bom-visualizations/review-sbom/'
        resp = self.post(uri, data=SBOM_REVIEW, access_token=access_token)
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(json.loads(resp.content)['message'], "Success")
        
    def test_sbom_search_by_vin(self):
        access_token = self.access_token
        brnad.send_dispatch_feed()
        brand.send_sbom_data_feed()

        
        