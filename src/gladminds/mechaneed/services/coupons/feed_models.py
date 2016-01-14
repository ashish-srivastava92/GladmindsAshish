from django.views.decorators.csrf import csrf_exempt
from spyne.application import Application
from spyne.decorator import srpc
from spyne.model.complex import Array
from spyne.model.complex import ComplexModel
from spyne.model.complex import Iterable
from spyne.model.primitive import Integer, Decimal, Date, Time
from spyne.model.primitive import Unicode, Mandatory, Boolean
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from spyne.server.wsgi import WsgiApplication
from spyne.service import ServiceBase
from spyne.util.wsgi_wrapper import WsgiMounter

from gladminds.bajajib.services.coupons.import_feed import SAPFeed
from gladminds.core.soap_authentication import AuthenticationService
import logging
from django.conf import settings
import json
from gladminds.core import utils
from gladminds.core.managers.feed_log_remark import FeedLogWithRemark
from gladminds.core.managers.audit_manager import feed_failure_log


logger = logging.getLogger("gladminds")


pattern = r'(\d{4})-(\d{2})-(\d{2})(\d{2})(\d{2})(\d{2})'
date_pattern = r'(\d{4})-(\d{2})-(\d{2})'
time_pattern = r'(\d{2}):(\d{2}):(\d{2})'
tns = settings.IB_WSDL_TNS
SUCCESS = "SUCCESS"
FAILED = "FAILURE"


class AuthenticationModel(ComplexModel):
    __namespace__ = tns
    UserName = Unicode(min_occurs=1, nillable=False)
    Password = Unicode(min_occurs=1, nillable=False)

class BrandModel(ComplexModel):
    __namespace__ = tns
    BRAND_ID = Unicode
    BRAND_NAME = Unicode
    PRODUCT_TYPE = Unicode
    PRODUCT_NAME = Unicode
    TIMESTAMP = Unicode(pattern=pattern)


class BrandModelList(ComplexModel):
    __namespace__ = tns
    BrandData = Array(BrandModel)


class DealerModel(ComplexModel):
    __namespace__ = tns
    KUNNR = Unicode
    ADDRESS = Unicode
    SER_ADV_ID = Unicode
    SER_ADV_NAME = Unicode
    SER_ADV_MOBILE = Unicode
    ACTIVE_FLAG = Unicode
    TIMESTAMP = Unicode(pattern=pattern)
    CDMS_FLAG = Boolean

class DealerModelList(ComplexModel):
    __namespace__ = tns
    DealerData = Array(DealerModel)
    
class ASCModel(ComplexModel):
    __namespace__ = tns
    ASC_ID = Unicode
    ASC_NAME = Unicode
    ASC_MOBILE = Unicode
    ASC_EMAIL = Unicode
    ASC_ADDRESS = Unicode
    KUNNAR = Unicode


class ASCModelList(ComplexModel):
    __namespace__ = tns
    ASCData = Array(ASCModel)    


class ProductDispatchModel(ComplexModel):
    __namespace__ = tns
    CHASSIS = Unicode
    PRODUCT_TYPE = Unicode
    VEC_DIS_DT = Date
    KUNNR = Unicode
    UCN_NO = Unicode(default=None)
    DAYS_LIMIT_FROM = Decimal
    DAYS_LIMIT_TO = Decimal
    KMS_FROM = Decimal
    KMS_TO = Decimal
    SERVICE_TYPE = Unicode
    #UCN_Status = Unicode
    TIMESTAMP = Unicode(pattern=pattern)
#     SKU_CODE = Unicode
#     ENGINE = Unicode

class ProductDispatchModelList(ComplexModel):
    __namespace__ = tns
    ProductDispatchData = Array(ProductDispatchModel)


class ProductPurchaseModel(ComplexModel):
    __namespace__ = tns
    CHASSIS = Unicode
    CUSTOMER_ID = Unicode
    CUST_MOBILE = Unicode
    CUSTOMER_NAME = Unicode
    CITY = Unicode
    STATE = Unicode
    PIN_NO = Unicode
    VEH_SL_DT = Date
    VEH_REG_NO = Unicode
    VEH_SL_DLR = Unicode
    KUNNR = Unicode
    TIMESTAMP = Unicode(pattern=pattern)
    ENGINE = Unicode


class ProductPurchaseModelList(ComplexModel):
    __namespace__ = tns
    ProductPurchaseData = Array(ProductPurchaseModel)

class BrandService(ServiceBase):
    __namespace__ = tns

    @srpc(BrandModelList, AuthenticationModel,  _returns=Unicode)
    def postBrand(ObjectList, Credential):
        try:
            brand_list = []
            for brand in ObjectList.BrandData:
                brand_list.append({
                    'brand_id': brand.BRAND_ID,
                    'brand_name': brand.BRAND_NAME,
                    'product_type': brand.PRODUCT_TYPE,
                    'product_name': brand.PRODUCT_NAME,
                })
            save_to_db(feed_type='brand', data_source=brand_list)
            return SUCCESS
        except Exception as ex:
            return FAILED


class DealerService(ServiceBase):
    __namespace__ = tns

    @srpc(DealerModelList, AuthenticationModel, _returns=Unicode)
    def postDealer(ObjectList, Credential):
        dealer_list = []
        feed_remark = FeedLogWithRemark(len(ObjectList.DealerData),
                                        feed_type='Dealer Feed',
                                        action='Received', status=True)
        for dealer in ObjectList.DealerData:
            try:
                dealer_list.append({
                    'id': dealer.KUNNR,
                    'address': dealer.ADDRESS,
                    'service_advisor_id': dealer.SER_ADV_ID,
                    'name': dealer.SER_ADV_NAME,
                    'phone_number': utils.mobile_format(dealer.SER_ADV_MOBILE),
                    'status': dealer.ACTIVE_FLAG,
                    'cdms_flag':dealer.CDMS_FLAG
                })
            except Exception as ex:
                ex = "DealerService: {0}  Error on Validating {1}".format(dealer, ex)
                feed_remark.fail_remarks(ex)
                logger.error(ex)
        feed_remark = save_to_db(feed_type='dealer', data_source=dealer_list,
                              feed_remark=feed_remark)

        feed_remark.save_to_feed_log()
        return get_response(feed_remark)
    
class ASCService(ServiceBase):
    __namespace__ = tns

    @srpc(ASCModelList, AuthenticationModel, _returns=Unicode)
    def postASC(ObjectList, Credential):
        asc_list = []
        feed_remark = FeedLogWithRemark(len(ObjectList.ASCData),
                                        feed_type='ASC Feed',
                                        action='Received', status=True)
        for asc_element in ObjectList.ASCData:
            try:
                asc_list.append({
                    'asc_id': asc_element.ASC_ID,
                    'name': asc_element.ASC_NAME,
                    'phone_number': utils.mobile_format(asc_element.ASC_MOBILE),
                    'address': asc_element.ASC_ADDRESS,
                    'email': asc_element.ASC_EMAIL,
                    'dealer_id': asc_element.KUNNAR
                })
            except Exception as ex:
                ex = "ASCService: {0}  Error on Validating {1}".format(asc_element, ex)
                feed_remark.fail_remarks(ex)
                logger.error(ex)
        feed_remark = save_to_db(feed_type='ASC', data_source=asc_list,
                              feed_remark=feed_remark)
        feed_remark.save_to_feed_log()
        return get_response(feed_remark)    


class ProductDispatchService(ServiceBase):
    __namespace__ = tns

    @srpc(ProductDispatchModelList, AuthenticationModel, _returns=Unicode)
    def postProductDispatch(ObjectList, Credential):
        feed_remark = FeedLogWithRemark(len(ObjectList.ProductDispatchData),
                                        feed_type='Dispatch Feed',
                                        action='Received', status=True)
        product_dispatch_list = []
        for product in ObjectList.ProductDispatchData:
            try:
                product_dispatch_list.append({
                    'vin': product.CHASSIS,
                    'product_type': product.PRODUCT_TYPE,
                    'invoice_date': product.VEC_DIS_DT,
                    'dealer_id': product.KUNNR,
                    'unique_service_coupon': product.UCN_NO,
                    'valid_days': product.DAYS_LIMIT_TO,
                    'valid_kms': product.KMS_TO,
                    'service_type': product.SERVICE_TYPE,
                    'coupon_status': settings.DEFAULT_COUPON_STATUS,
#                     'sku_code':product.SKU_CODE
#                     'engine':product.ENGINE,
                })
            except Exception as ex:
                ex = "ProductDispatchService: {0}  Error on Validating {1}".format(product, ex)
                feed_remark.fail_remarks(ex)
                logger.error(ex)

        feed_remark = save_to_db(
            feed_type='dispatch', data_source=product_dispatch_list,
                                        feed_remark=feed_remark)
        feed_remark.save_to_feed_log()
        return get_response(feed_remark)


class ProductPurchaseService(ServiceBase):
    __namespace__ = tns

    @srpc(ProductPurchaseModelList, AuthenticationModel, _returns=Unicode)
    def postProductPurchase(ObjectList, Credential):
        feed_remark = FeedLogWithRemark(len(ObjectList.ProductPurchaseData),
                                        feed_type='Purchase Feed',
                                        action='Received', status=True)
        product_purchase_list = []
        for product in ObjectList.ProductPurchaseData:
            try:
                product_purchase_list.append({
                    'vin': product.CHASSIS,
                    'sap_customer_id': product.CUSTOMER_ID,
                    'customer_phone_number': utils.mobile_format(product.CUST_MOBILE),
                    'customer_name': product.CUSTOMER_NAME,
                    'city': product.CITY,
                    'state': product.STATE,
                    'pin_no': product.PIN_NO,
                    'product_purchase_date': product.VEH_SL_DT,
                    'engine': product.ENGINE,
                    'veh_reg_no': product.VEH_REG_NO
                })
            except Exception as ex:
                ex = "ProductPurchaseService: {0}  Error on Validating {1}".format(product, ex)
                feed_remark.fail_remarks(ex)
                logger.error(ex)

        feed_remark = save_to_db(
            feed_type='purchase', data_source=product_purchase_list,
                                                 feed_remark=feed_remark)
        feed_remark.save_to_feed_log()
        return get_response(feed_remark)

def get_response(feed_remark):
    if feed_remark.failed_feeds > 0:
        remarks = feed_remark.remarks.elements()
        for remark in remarks:
            feed_failure_log(brand=settings.BRAND, feed_type=feed_remark.feed_type, reason=remark)
        return FAILED
    else:
        return SUCCESS

def save_to_db(feed_type=None, data_source=[], feed_remark=None):
    sap_obj = SAPFeed()
    return sap_obj.import_to_db(feed_type=feed_type, data_source=data_source,
                                 feed_remark=feed_remark)


def _on_method_call(ctx):
    if ctx.in_object is None:
        raise ArgumentError("Request doesn't contain data")
    auth_obj = AuthenticationService(
                                username=ctx.in_object.Credential.UserName,
                                password=ctx.in_object.Credential.Password)
    auth_obj.authenticate()

BrandService.event_manager.add_listener('method_call', _on_method_call)
DealerService.event_manager.add_listener('method_call', _on_method_call)
ProductDispatchService.event_manager.add_listener(
    'method_call', _on_method_call)
ProductPurchaseService.event_manager.add_listener(
    'method_call', _on_method_call)
