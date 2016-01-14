import json
import logging
from datetime import datetime
from gladminds.core.managers.audit_manager import feed_log, feed_failure_log
from gladminds.bajajib import models
from django.conf import settings

from gladminds.core import utils
from gladminds.core.model_fetcher import get_model
from gladminds.core.managers.feed_log_remark import FeedLogWithRemark
from gladminds.bajajib.services.coupons.feed_models import save_to_db
from gladminds.core.services.feed_resources import BaseExportFeed

logger = logging.getLogger("gladminds")

class ExportCouponRedeemFeed(BaseExportFeed):
    
    def export_data(self, start_date=None, end_date=None):
        results = models.CouponData.objects.filter(sent_to_sap=0,
                            status=2).select_related('product_id')
        items = []
        total_failed = 0
        item_batch = {
            'TIMESTAMP': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
        self.feed_remark = FeedLogWithRemark(len(results), feed_type='Coupon Redemption Feed', action='Send', status=True)
        for redeem in results:
            try:
                #added the condition only for the previous coupons with no servicing dealer details
                if redeem.service_advisor:
                    if redeem.service_advisor.dealer:
                        servicing_dealer = redeem.service_advisor.dealer.dealer_id
                    else:
                        servicing_dealer = redeem.service_advisor.asc.asc_id
                else:
                    servicing_dealer = redeem.product.dealer_id.dealer_id
                
                item = {
                        "CHASSIS": redeem.product.product_id,
                        "GCP_KMS": redeem.actual_kms,
                        "GCP_KUNNR": servicing_dealer,
                        "GCP_UCN_NO": redeem.unique_service_coupon,
                        "PRODUCT_TYPE": redeem.product.sku_code,
                        "SERVICE_TYPE": str(redeem.service_type),
                        "SER_AVL_DT": redeem.actual_service_date.date().strftime("%Y-%m-%d"),
                    }                        
                items.append(item)
            except Exception as ex:
                logger.error("[ExportCouponRedeemFeed]: error fetching from db {0}".format(ex))
                total_failed = total_failed + 1
                self.feed_remark.fail_remarks(ex)
        logger.info("[ExportCouponRedeemFeed]: processed coupon")
        return items, item_batch, total_failed

    def export(self, brand, items=None, item_batch=None, total_failed_on_feed=0):
        logger.info(
            "[ExportCouponRedeemFeed]: Export {0}".format(self.feed_type))
        client = self.get_client()
        total_failed = total_failed_on_feed
        export_status = False
        for item in items:
            export_status = False
            logger.info("[ExportCouponRedeemFeed]: Sending coupon - {0}"\
                        .format(item))
            try:            
                result = client.service.MI_GCP_UCN_Sync(
                    ITEM=[item], ITEM_BATCH=item_batch)
                logger.info("[ExportCouponRedeemFeed]: Response from SAP: {0}".format(result))
                if result[1]['I_STATUS'] == 'SUCCESS':
                    try:
                        coupon = models.CouponData.objects.get(unique_service_coupon=item['GCP_UCN_NO'])
                        coupon.sent_to_sap = True
                        coupon.save()
                        export_status = True
                        logger.info("[ExportCouponRedeemFeed]: Sent coupon - {0}".format(item['GCP_UCN_NO']))
                    except Exception as ex:
                        total_failed = total_failed + 1
                        logger.error("[ExportCouponRedeemFeed]: Error:: {0} - {1}".format(item['GCP_UCN_NO'], ex))
                        self.feed_remark.fail_remarks(ex)
                else:
                    total_failed = total_failed + 1
                    logger.error("[ExportCouponRedeemFeed]: {0}:: Success not received from SAP".format(item['GCP_UCN_NO']))
            except Exception as ex:
                total_failed = total_failed + 1
                logger.error("[ExportCouponRedeemFeed]: Error:: {0} - {1}".format(item['GCP_UCN_NO'], ex))
                self.feed_remark.fail_remarks(ex)
        feed_log(brand, feed_type=self.feed_type, total_data_count=len(items)\
                 + total_failed_on_feed, failed_data_count=total_failed,\
                 success_data_count=len(items) + total_failed_on_feed - total_failed,\
                 action='Sent', status=export_status)

class ExportASCRegistrationFeed(BaseExportFeed):
    def export_data(self, asc_phone_number=None):
        asc_form_obj = models.ASCTempRegistration.objects\
            .get(phone_number=asc_phone_number, status=1)

        item_batch = {
            'TIMESTAMP': asc_form_obj.timestamp.strftime("%Y-%m-%dT%H:%M:%S")}

        item = {
            "ASC_NAME": asc_form_obj.name,
            "ASC_MOBILE": asc_form_obj.phone_number,
            "ASC_EMAIL": asc_form_obj.email,
            "ASC_ADDRESS": asc_form_obj.address,
            "ASC_ADDRESS_PINCODE": asc_form_obj.pincode,
            "KUNNAR": "hardcoded",
        }
        return {"item": item, "item_batch": item_batch}

    def export(self, items=None, item_batch=None, total_failed_on_feed=0):
        logger.info(
            "Export {2}: Item:{0} and Item_batch: {1}"\
            .format(items, item_batch, self.feed_type))
        client = self.get_client()

        result = client.service.postASC(
            ITEM=[items], ITEM_BATCH=item_batch)
        if not result[1]['I_STATUS'] == 'SUCCESS':
            raise
        return

class ExportCustomerRegistrationFeed(BaseExportFeed):
    
    def export_data(self, start_date=None, end_date=None):
        results = models.CustomerTempRegistration.objects.filter(sent_to_sap=False).select_related('product_data')
        items = []
        total_failed = 0
        item_batch = {
            'TIME_STAMP': datetime.now().strftime("%Y%m%d%H%M%S")}
        for redeem in results:
            try:
                item = {
                    "CHASSIS": redeem.product_data.product_id,
                    "KUNNR": redeem.product_data.dealer_id.dealer_id,
                    "CUSTOMER_ID" : redeem.temp_customer_id,
                    "ENGINE" : redeem.product_data.engine,
                    "VEH_SL_DT": redeem.product_purchase_date.date().strftime("%Y-%m-%d"),
                    "CUSTOMER_NAME": redeem.new_customer_name,
                    "CUST_MOBILE": redeem.new_number,
                    
                }
                items.append(item)
            except Exception as ex:
                logger.error("[ExportCustomerRegistrationFeed]: error fetching from db {0}".format(ex))
                total_failed = total_failed + 1
        return items, item_batch, total_failed

    def export(self, brand, items=None, item_batch=None, total_failed_on_feed=0):
        logger.info(
            "[ExportCustomerRegistrationFeed]: Export {0}".format(self.feed_type))
        client = self.get_client()
        total_failed = total_failed_on_feed
        for item in items:
            export_status = False
            logger.info("[ExportCustomerRegistrationFeed]: Sending customer - {0}"\
                        .format(item['CUSTOMER_ID']))
            try:
#                 if settings.ENV in ['prod']:
#                     result = client.service.SI_GCPCstID_sync(
#                         item_custveh=[{"item": item}], item=item_batch)
#                 else:
                result = client.service.SI_CstID_sync(
                    item_custveh=[{"item": item}], item=item_batch)
                logger.info("[ExportCustomerRegistrationFeed]: Response from SAP: {0}".format(result))
                if result[0]['item'][0]['STATUS'] == 'SUCCESS':
                    try:
                        temp_customer_object = models.CustomerTempRegistration.objects.get(temp_customer_id=item['CUSTOMER_ID'])
                        temp_customer_object.sent_to_sap = True
#                         if settings.ENV in ['prod']:
#                             if result[2]:
#                                 temp_customer_object.remarks = result[2]['item'][0]['REMARKS']
#                             else: 
#                                 temp_customer_object.tagged_sap_id = result[1]['item'][0]['PARTNER']
                        temp_customer_object.save()
                        export_status = True
                        logger.info("[ExportCustomerRegistrationFeed]: Sent customer ID - {0}".format(item['CUSTOMER_ID']))
                    except Exception as ex:
                        total_failed = total_failed + 1
                        logger.error("[ExportCustomerRegistrationFeed]: Error:: {0} - {1}".format(item['CUSTOMER_ID'], ex))
                else:
                    total_failed = total_failed + 1
                    logger.error("[ExportCustomerRegistrationFeed]: Success not received from SAP".format(item['CUSTOMER_ID']))
            except Exception as ex:
                total_failed = total_failed + 1
                logger.error("[ExportCustomerRegistrationFeed]:  Error:: {0} - {1}".format(item['CUSTOMER_ID'], ex))
        feed_log(brand, feed_type=self.feed_type, total_data_count=len(items)\
                 + total_failed_on_feed, failed_data_count=total_failed,\
                 success_data_count=len(items) + total_failed_on_feed - total_failed,\
                 action='Sent', status=export_status)

class ExportUnsyncProductFeed(BaseExportFeed):

    def export(self, data=None):
        data_source = []
        message="some error occurred, please try again later."
        logger.info(
            "[ExportUnsyncProductFeed]: Export {1}: Items:{0}"\
            .format(data, self.feed_type))
        client = self.get_client()

        logger.info("[ExportUnsyncProductFeed]: sending product details: {0}"\
                    .format(data['vin']))
        
        result = client.service.SI_GCPONL_Sync(
                DT_ONL=[{"CHASSIS": data['vin'],"DEALER": data['current_user'].username}])
        try:
            logger.info("[ExportUnsyncProductFeed]: Response from SAP: {0}".format(result))
            
            if len(result)>1:
                return_code = result[1][0]['RETURN_CODE']
                ucn_count = len(result[0])
            else:
                return_code = result[0][0]['RETURN_CODE']
                ucn_count=0
            
            if return_code:
                vin_sync_feed = models.VinSyncFeedLog(product_id = data['vin'], dealer_asc_id=data['current_user'].username,
                                                      status_code=return_code, ucn_count=ucn_count)
                vin_sync_feed.save()
                if return_code.upper() == 'S':
                    message='The Chassis was found in the main database. Please try after sometime.'
                    for results in result[0]:
                        try:
                            valid_dict = {
                                     1 : {
                                          "valid_days": 365,
                                          "valid_kms": 2000
                                             },
                                     2 : {
                                          "valid_days": 730,
                                          "valid_kms": 8000,
                                             },
                                     3 : {
                                          "valid_days": 730,
                                          "valid_kms": 15000,
                                             }
                                    }
                            
                            results['DAYS_LIMIT_TO'] = valid_dict[int(results['SERV_TYP'])]['valid_days']
                            results['KMS_TO'] = valid_dict[int(results['SERV_TYP'])]['valid_kms']
                            data_source.append(utils.create_dispatch_feed_data(results))
                            feed_remark = FeedLogWithRemark(len(data_source),
                                            feed_type='VIN sync Feed',
                                            action='Sent', status=True)
                        except Exception as ex:
                            ex = "[ExportUnsyncProductFeed]: ProductDispatchService: {0}  Error on Validating {1}".format(result, ex)
                            feed_remark.fail_remarks(ex)
                            logger.error(ex)
                    feed_remark = save_to_db(feed_type='dispatch', data_source=data_source,
                                        feed_remark=feed_remark)
                    feed_remark.save_to_feed_log()
                    if feed_remark.failed_feeds > 0:
                        remarks = feed_remark.remarks.elements()
                        for remark in remarks:
                            feed_failure_log(brand=settings.BRAND, feed_type='VIN sync Feed', reason=remark)
                            logger.info('[ExportUnsyncProductFeed]: ' + json.dumps(feed_remark.remarks))
                        raise ValueError('dispatch feed failed!')
                        logger.info('[ExportUnsyncProductFeed]: dispatch feed completed')
                        
                else:
                    message='This Chassis is not available in Main database, please type the correct chassis number'
        except Exception as ex:
            logger.error("[ExportUnsyncProductFeed]: Failed to send the details to sap")
            logger.error(ex)
        return message
    
class ExportPurchaseSynFeed(BaseExportFeed):
    
    def export_data(self, start_date=None, end_date=None):
        results = models.VinSyncFeedLog.objects.filter(sent_to_sap=False, ucn_count=-1)
        items = []
        total_failed = 0
        item_batch = {'I_STAMP': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
        for sync_feed in results:
            try:
                item = {
                    "CHASSIS": sync_feed.product_id,
                }
                items.append(item)
            except Exception as ex:
                logger.error("[ExportPurchaseSynFeed]: error fetching from db {0}".format(ex))
                total_failed = total_failed + 1
        return items, item_batch, total_failed

    def export(self, brand, items=None, item_batch=None, total_failed_on_feed=0):
        logger.info(
            "Export {2}: Items:{0} and Item_batch: {1}"\
            .format(items, item_batch, self.feed_type))
        client = self.get_client()
        total_failed = total_failed_on_feed
        for item in items:
            export_status = False
            logger.info("[ExportPurchaseSynFeed]: Sending chassis - {0}"\
                        .format(item['CHASSIS']))
            try:
                result = client.service.SI_PurchFeed_Sync(
                                DT_Item=[item],
                                DT_STAMP=[{"Item_Stamp":item_batch}])
                logger.info("[ExportPurchaseSynFeed]: Response from SAP: {0}".format(result))
                if result['STATUS'] == 'SUCCESS':
                    try:
                        vin_sync_feed = models.VinSyncFeedLog.objects.get(product_id = item['CHASSIS'])
                        vin_sync_feed.status_code = result['STATUS']
                        vin_sync_feed.sent_to_sap = True
                        vin_sync_feed.save()
                        export_status = True
                        logger.info("[ExportPurchaseSynFeed]: Sent the VIN {0} to sap".format(item['CHASSIS']))
                    except Exception as ex:
                        total_failed = total_failed + 1
                        logger.error("[ExportPurchaseSynFeed]: Error:: {0} - {1}".format(item['CHASSIS'], ex))
                else:
                    total_failed = total_failed + 1
                    logger.error("[ExportPurchaseSynFeed]:Success not received from SAP {0}".format(item['CHASSIS']))
            except Exception as ex:
                total_failed = total_failed + 1
                logger.error("[ExportPurchaseSynFeed]: Error:: {0} - {1}".format(item['CHASSIS'], ex))
        feed_log(brand, feed_type=self.feed_type, total_data_count=len(items)\
                 + total_failed_on_feed, failed_data_count=total_failed,\
                 success_data_count=len(items) + total_failed_on_feed - total_failed,\
                 action='Sent', status=export_status)
        
class ExportCTSFeed(BaseExportFeed):
    def export_data(self, brand=None):
        items = []
        total_failed = 0
        item_batch = {
            'ITIMESTAMP': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
        
        cts_objs = get_model('ContainerLR', brand).objects.filter(zib_indent_num__status='Inprogress',sent_to_sap=0).select_related('transporter', 'zib_indent_num')
                
        for cts_obj in cts_objs:
            try:
                item = {
                    "Indent_Num": cts_obj.zib_indent_num.indent_num,
                    "Consigment_Id": cts_obj.consignment_id,
                    "Truck_No": cts_obj.truck_no,
                    "Transporter_Id": cts_obj.transporter.transporter_id,
                    "Transaction_Id": cts_obj.transaction_id,
                    "Container_No": cts_obj.container_no,
                    "Seal_No": cts_obj.seal_no,            
                }
                items.append(item)
            except Exception as ex:
                logger.error("[ExportCTSFeed]: error fetching from db {0}".format(ex))
                total_failed = total_failed + 1

        return items, item_batch, total_failed

    def export(self, brand=None, items=None, item_batch=None, total_failed_on_feed=0):
        client = self.get_client()
        total_failed = total_failed_on_feed
        export_status = False
        for item in items:
            logger.error("[ExportCTSFeed]: sending CTS:{0}".format(item['Transaction_Id']))
            try:
                result = client.service.SI_CTS_Sync(
                    DT_CTS_Item={'Item':[item]}, DT_STAMP={'Item_STAMP':item_batch})
                logger.info("[ExportCTSFeed]: Response from SAP: {0}".format(result))                
                if result[0]['STATUS'] == 'SUCCESS':
                    try:
                        cts = get_model('ContainerLR', brand).objects.get(transaction_id=item['Transaction_Id'])
                        cts.sent_to_sap = True
                        cts.save(using=brand)
                        export_status = True
                    except Exception as ex:
                        logger.error("[ExportCTSFeed]: Error in sending CTS:{0}::{1}".format(item['Transaction_Id'], ex))
                else:
                    total_failed = total_failed + 1
                    logger.error("[ExportCTSFeed]: {0}:: Not received success from sap".format(item['Transaction_Id']))
            except Exception as ex:
                logger.error("[ExportCTSFeed]: Error in sending CTS :{0}::{1}".format(item['Transaction_Id'], ex))
        
        feed_log(brand, feed_type=self.feed_type,
                 total_data_count=len(items)+ total_failed_on_feed, 
                 failed_data_count=total_failed,
                 success_data_count=len(items) + total_failed_on_feed - total_failed,
                 action='Sent', status=export_status)
