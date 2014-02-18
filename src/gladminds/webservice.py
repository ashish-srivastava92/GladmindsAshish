from spyne.application import Application
from spyne.decorator import srpc
from spyne.service import ServiceBase
from spyne.model.primitive import Integer,DateTime,Decimal
from spyne.model.primitive import Unicode
from spyne.model.complex import Iterable
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import WsgiMounter

tns = 'gladminds.webservice'
success = "success"
failed = "failed"

class BrandService(ServiceBase):
    @srpc(Unicode, Unicode, Unicode,Unicode, _returns=Unicode)
    def postBrand(BRAND_ID, BRAND_NAME, PRODUCT_TYPE, PRODUCT_NAME):
        try:
            brand_data = {
                'brand_id':BRAND_ID, 
                'brand_name': BRAND_NAME, 
                'product_type': PRODUCT_TYPE, 
                'product_name': PRODUCT_NAME
            }
            return success
        except Exception as ex:
            print "BrandService: {0}".format(ex)
            return failed
            
class DealerService(ServiceBase):
    @srpc(Unicode, Unicode, Unicode,Unicode, Unicode, _returns=Unicode)
    def postDealer(DEALER_ID, ADDRESS, SER_ADV_ID, SER_ADV_NAME, SER_ADV_MOBILE):
        try:
            dealer_data = {
                'dealer_id' : DEALER_ID,
                'address' : ADDRESS,
                'service_advisor_id' : SER_ADV_ID,
                'name' : SER_ADV_NAME,
                'phone_number': SER_ADV_MOBILE
            }
            return success
        except Exception as ex:
            print "DealerService: {0}".format(ex)
            return failed 

class ProductDispatchService(ServiceBase):
    @srpc(Unicode, Unicode, DateTime, Unicode, Unicode, Decimal, Decimal, Decimal, Decimal, Unicode, _returns=Unicode)
    def postProductDispatch(CHASSIS, PRODUCT_TYPE, VEC_DIS_DT, DEALER_ID, UCN_NO, DAYS_LIMIT_FROM, DAYS_LIMIT_TO, KMS_FROM, KMS_TO, SERVICE_TYPE):
        try:
            product_dispatch_data = {
                    'vin' : CHASSIS,
                    'product_type': PRODUCT_TYPE,
                    'invoice_date': VEC_DIS_DT,
                    'dealer_id' : DEALER_ID,
                    'unique_service_coupon' : UCN_NO,
                    'valid_days' : DAYS_LIMIT_TO,
                    'valid_kms' : KMS_TO,
                    'service_type' : SERVICE_TYPE
                }
            return success
        except Exception as ex:
            print "ProductDispatchService: {0}".format(ex)
            return failed

class ProductPurchaseService(ServiceBase):
    @srpc(Unicode, Unicode, Unicode, Unicode, Unicode, Unicode, Unicode, DateTime, _returns=Unicode)
    def postProductPurchase(CHASSIS, CUSTOMER_ID, CUST_MOBILE, CUSTOMER_NAME, CITY, STATE, PIN_NO, PRODUCT_PURCHASE_DATE):
        try:
            product_purchase_data = {
                    'vin' : CHASSIS,
                    'sap_customer_id' : CUSTOMER_ID,
                    'customer_phone_number' : CUST_MOBILE,
                    'customer_name' : CUSTOMER_NAME,
                    'city' : CITY,
                    'state' : state,
                    'pin_no' : PIN_NO,
                    'product_purchase_date' : PRODUCT_PURCHASE_DATE,
            }
            return success
        except Exception as ex:
            print "ProductPurchaseService: {0}".format(ex)
            return  failed
            

brand_app = Application([BrandService],
    tns=tns,
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

dealer_app = Application([DealerService],
    tns=tns,
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

dispatch_app = Application([ProductDispatchService],
    tns=tns,
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

purchase_app = Application([ProductPurchaseService],
    tns=tns,
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)