import csv
import logging
import os
import time
from datetime import datetime, timedelta

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.db.models import signals

from gladminds.core.services import message_template as templates
from gladminds.core import utils
from gladminds.bajajib import models
from gladminds.core.managers.audit_manager import sms_log
from gladminds.core.cron_jobs.queue_utils import send_job_to_queue
from gladminds.core.auth_helper import Roles
from gladminds.core.services.feed_resources import BaseFeed
logger = logging.getLogger("gladminds")

USER_GROUP = {'dealer': Roles.DEALERS,
              'ASC': Roles.ASCS,
              'SA':Roles.SERVICEADVISOR}

def load_feed():
    FEED_TYPE = settings.FEED_TYPE
    if FEED_TYPE is 'SAP':
        SAPFeed()

class SAPFeed(object):

    def import_to_db(self, feed_type=None, data_source=[], feed_remark=None):
        function_mapping = {
            'brand': BrandProductTypeFeed,
            'dealer': DealerAndServiceAdvisorFeed,
            'dispatch': ProductDispatchFeed,
            'purchase': ProductPurchaseFeed,
            'ASC': ASCFeed,
            'asc_sa': ASCAndServiceAdvisorFeed,
        }
        feed_obj = function_mapping[feed_type](data_source=data_source,
                                             feed_remark=feed_remark)
        return feed_obj.import_data()

class BrandProductTypeFeed(BaseFeed):

    def import_data(self):
        for product in self.data_source:
            try:
                product_type = models.ProductType(product_type=product['product_type'])
                product_type.save()
            except Exception as ex:
                logger.info(
                    "[Exception: BrandProductTypeFeed_product_type]: {0}".format(ex))
                continue


class DealerAndServiceAdvisorFeed(BaseFeed):

    def import_data(self):
        total_failed = 0
        for dealer in self.data_source:
            try:
                dealer_data = self.check_or_create_dealer(dealer_id=dealer['id'],
                                address=dealer['address'], cdms_flag=dealer['cdms_flag'])
                mobile_number_active = self.check_mobile_active(dealer, dealer_data)
                if mobile_number_active and dealer['status']=='Y':
                    raise ValueError(dealer['phone_number'] + ' is active under another dealer')
                try:
                    service_advisor = models.ServiceAdvisor.objects.select_related('user__user').get(
                                        service_advisor_id=dealer['service_advisor_id'])
                    if service_advisor.user.phone_number != dealer['phone_number']:
                        new_user=service_advisor.user
                        new_user.phone_number=dealer['phone_number']
                        new_user.save()
                        service_advisor.user=new_user
                        logger.info(
                        "[Info: DealerAndServiceAdvisorFeed_sa]: Updated phone number for {0}"
                        .format(dealer['service_advisor_id']))
                except ObjectDoesNotExist as odne:
                    logger.info(
                    "[Exception:  DealerAndServiceAdvisorFeed_sa]: {0}"
                    .format(odne))
                    sa_user = self.register_user(Roles.SERVICEADVISOR, username=dealer['service_advisor_id'],
                                                 first_name=dealer['name'],
                                                 phone_number=dealer['phone_number'])
                    service_advisor = models.ServiceAdvisor(
                                            service_advisor_id=dealer['service_advisor_id'], 
                                            dealer=dealer_data, user=sa_user)
                service_advisor.status = unicode(dealer['status'])
                service_advisor.save()
            except Exception as ex:
                total_failed += 1
                ex = "{0}".format(ex)
                logger.error(ex)
                self.feed_remark.fail_remarks(ex)
                continue

        return self.feed_remark

    def check_mobile_active(self, dealer, dealer_data):
        list_mobile = models.ServiceAdvisor.objects.active(dealer['phone_number'])
        list_active_mobile = list_mobile.exclude(dealer=dealer_data,
                                                 service_advisor_id=dealer['service_advisor_id'])
        if list_active_mobile:
            return True
        return False

def compare_purchase_date(date_of_purchase):
    valid_msg_days = models.Constant.objects.get(constant_name = "welcome_msg_active_days").constant_value
    valid_msg_days_delta = timedelta(days=int(valid_msg_days))
    purchased_days = datetime.now().date()-date_of_purchase
    if purchased_days <= valid_msg_days_delta:
        return True
    else:
        return False
    

class ProductDispatchFeed(BaseFeed):

    def import_data(self):
        for product in self.data_source:
            try:
                product_data = models.ProductData.objects.get(product_id=product['vin'])
            except ObjectDoesNotExist as done:
                logger.info(
                    '[Info: ProductDispatchFeed_product_data]: {0}'.format(done))
                try:
                    dealer_data = self.check_or_create_country_distributor(dealer_id=product['dealer_id'])
                    product_data = models.ProductData(
                        product_id=product['vin'], invoice_date=product['invoice_date'], 
                        country_distributor=dealer_data, sku_code=product['product_type'])
                    product_data.save()
                    logger.info('[Successful: ProductDispatchFeed_product_data_save]:VIN-{0} UCN-{1}'.format(product['vin'], product['unique_service_coupon']))
                except Exception as ex:
                    ex = '''[Exception: ProductDispatchFeed_product_data_save]:{0} VIN - {1}'''.format(ex, product['vin'])
                    self.feed_remark.fail_remarks(ex)
                    logger.error(ex)
                    continue
            try:
                if not product['unique_service_coupon']:
                    continue
                valid_coupon = models.CouponData.objects.filter(unique_service_coupon=product['unique_service_coupon'])
                service_type_exists = models.CouponData.objects.filter(product__product_id=product['vin'], service_type=str(product['service_type']))
                if service_type_exists and not valid_coupon:
                    service_type_error = 'VIN already has coupon of service type {0}'.format(product['service_type'])
                    logger.error(service_type_error)
                    raise ValueError(service_type_error)
                elif not valid_coupon:
                    coupon_data = models.CouponData(unique_service_coupon=product['unique_service_coupon'],
                            product=product_data, valid_days=product['valid_days'],
                            valid_kms=product['valid_kms'], service_type=product['service_type'],
                            status=product['coupon_status'])
                    coupon_data.save()
                    logger.info('[Successful: ProductDispatchFeed_product_data_save]:VIN - {0} UCN - {1}'.format(product['vin'], product['unique_service_coupon']))
                    
                elif valid_coupon[0].product.product_id == product['vin'] and str(valid_coupon[0].service_type) == str(product['service_type']):
                    logger.info('UCN is already saved in database. VIN - {0} UCN - {1}'.format(product['vin'], product['unique_service_coupon']))
                    continue
                else:
                    coupon_exist_error = 'Coupon already registered for VIN {0}'.format(valid_coupon[0].product.product_id)
                    logger.error(coupon_exist_error)
                    raise ValueError(coupon_exist_error)
            except Exception as ex:   
                ex = '''[Error: ProductDispatchFeed_product_data_save]: VIN - {0} Coupon - {1} {2}'''.format(
                                        product['vin'], product['unique_service_coupon'], ex)
                self.feed_remark.fail_remarks(ex)
                logger.error(ex)
                continue

        return self.feed_remark

    def get_or_create_product_type(self, product_type=None):
        brand_list = [{
            'product_type': product_type,
            'product_name': product_type,
        }]
        obj_brand = BrandProductTypeFeed(data_source=brand_list)
        obj_brand.import_data()

class ProductPurchaseFeed(BaseFeed):

    def import_data(self):
        for product in self.data_source:
            try:
                product_data = models.ProductData.objects.get(product_id=product['vin'])
                if product_data.customer_id  and product_data.customer_id.find('T') != 0 and product_data.customer_id != product['sap_customer_id']:
                    raise ValueError('Permanent ID {0} already Exists! New ID {1}'.format(product_data.customer_id, product['sap_customer_id']))
                if product_data.customer_phone_number and product_data.customer_id == product['sap_customer_id']:
                    post_save.disconnect(
                        update_coupon_data, sender=models.ProductData)

                if not product_data.customer_id  or product_data.customer_id.find('T') == 0:
                    product_data.customer_id = product['sap_customer_id']
                    product_data.engine = product["engine"]
                    product_data.veh_reg_no =  product['veh_reg_no']
                
                product_purchase_date = product['product_purchase_date']
                product_data.purchase_date = product_purchase_date
                product_data.customer_phone_number = product['customer_phone_number']    
                product_data.customer_name = product['customer_name']
                product_data.customer_city = product['city']
                product_data.customer_state = product['state']
                product_data.customer_pincode = product['pin_no']
                product_data.save()
                
                post_save.connect(
                    update_coupon_data, sender=models.ProductData)

            except ObjectDoesNotExist as done:
                ex='[Info: ProductPurchaseFeed_product_data]: VIN- {0} :: {1}'''.format(product['vin'], done)
                logger.error(ex)
                self.feed_remark.fail_remarks(ex)
                vin_sync_feed = models.VinSyncFeedLog.objects.filter(product_id = product['vin'],ucn_count=-1)
                if vin_sync_feed:
                    vin_sync_feed=vin_sync_feed[0]
                    vin_sync_feed.sent_to_sap=False
                else:
                    vin_sync_feed=models.VinSyncFeedLog(product_id = product['vin'],ucn_count=-1) 
                vin_sync_feed.save()
            except Exception as ex:
                ex = '''[Exception: ProductPurchaseFeed_product_data]: VIN- {0} :: {1}'''.format(product['vin'], ex)
                self.feed_remark.fail_remarks(ex)
                logger.error(ex)
                continue

        return self.feed_remark


class ProductServiceFeed(BaseFeed):

    def import_data(self):
        for redeem in self.data_source:
            try:
                closed_date = datetime.strptime(
                    redeem['closed_date'], '%d-%m-%Y %H:%M:%S')
                actual_service_date = datetime.strptime(
                    redeem['actual_service_date'], '%d-%m-%Y %H:%M:%S')
                coupon_data = models.CouponData.objects.filter(vin__vin=redeem['vin'], unique_service_coupon=redeem['unique_service_coupon']).update(
                    closed_date=closed_date, actual_service_date=actual_service_date, actual_kms=redeem['actual_kms'], status=2)
            except Exception as ex:
                continue


def update_coupon_data(sender, **kwargs):
    from gladminds.sqs_tasks import send_on_product_purchase
    instance = kwargs['instance']
    logger.info("triggered update_coupon_data")
    if instance.customer_phone_number:
        product_purchase_date = instance.purchase_date
        vin = instance.product_id
        coupon_data = models.CouponData.objects.filter(product=instance)
        for coupon in coupon_data:
            mark_expired_on = product_purchase_date + \
                timedelta(days=int(coupon.valid_days))
            coupon_object = models.CouponData.objects.get(
                product=instance, unique_service_coupon=coupon.unique_service_coupon)
            coupon_object.mark_expired_on = mark_expired_on
            coupon_object.extended_date = mark_expired_on
            coupon_object.save()
        
        try:
            customer_name=instance.customer_name
            customer_phone_number = utils.get_phone_number_format(instance.customer_phone_number)
            customer_id=instance.customer_id
            temp_customer_data = models.CustomerTempRegistration.objects.filter(product_data__product_id=vin)
            customer_id_replaced = False
            if temp_customer_data and not temp_customer_data[0].temp_customer_id == customer_id:
                customer_id_replaced = True
                message = templates.get_template('SEND_REPLACED_CUSTOMER_ID').format(
                    customer_name=customer_name, sap_customer_id=customer_id)
            elif instance.customer_id.find('T') == 0:
                message = templates.get_template('SEND_TEMPORARY_CUSTOMER_ID').format(
                    customer_name=customer_name, sap_customer_id=customer_id)
            else:
                if compare_purchase_date(product_purchase_date):
                    message = templates.get_template('SEND_CUSTOMER_ON_PRODUCT_PURCHASE').format(
                    customer_name=customer_name, sap_customer_id=customer_id)
                else:
                    message = templates.get_template('SEND_REPLACED_CUSTOMER_ID').format(
                    customer_name=customer_name, sap_customer_id=customer_id)
            sms_log(
                settings.BRAND, receiver=customer_phone_number, action='SEND TO QUEUE', message=message)
            send_job_to_queue(send_on_product_purchase, {"phone_number":customer_phone_number, "message":message, "sms_client":settings.SMS_CLIENT}) 

            if not customer_id_replaced:
                if str(vin).upper().startswith('VBK', 0, 3):
                    if str(vin).upper()[4] in ['U','G']:
                        message = templates.get_template('SEND_CUSTOMER_REGISTER_KTM_DUKE'
                                                     ).format(customer_name=instance.customer_name,
                                                              duke_android_url="http://tinyurl.com/com-ktm-ab",
                                                              duke_web_url="http://ktmdukeweb.gladminds.co")
                    elif str(vin).upper()[4]=='Y':
                        message = templates.get_template('SEND_CUSTOMER_REGISTER_KTM_RC'
                                                     ).format(customer_name=instance.customer_name,
                                                              rc_android_url="http://tinyurl.com/COM-KTM-RC",
                                                              rc_web_url="http://ktmrcweb.gladminds.co")
                    sms_log(settings.BRAND, receiver=instance.customer_phone_number, action='SEND TO QUEUE', message=message)
                    send_job_to_queue(send_on_product_purchase, {"phone_number":instance.customer_phone_number, "message":message, "sms_client":settings.SMS_CLIENT}) 
            
        except Exception as ex:
            logger.info("[Exception]: Signal-In Update Coupon Data %s" % ex)

post_save.connect(update_coupon_data, sender=models.ProductData)

class ASCFeed(BaseFeed):
    def import_data(self):
        for asc in self.data_source:
            asc_data = models.AuthorizedServiceCenter.objects.filter(asc_id=asc['asc_id'])
            if not asc_data:
                dealer_data = None
                if asc['dealer_id']:
                    dealer_data = self.check_or_create_dealer(dealer_id=asc['dealer_id'])
                try:
                    asc_obj = self.register_user(Roles.ASCS, username=asc['asc_id'],
                                                address=asc['address'])
                    asc_data = models.AuthorizedServiceCenter(user=asc_obj,asc_id=asc['asc_id'],
                                    dealer=dealer_data)
                    asc_data.save()
                except Exception as ex:
                    ex = "[Exception: ASCFeed_dealer_data]: {0}".format(ex)
                    logger.error(ex)
                    self.feed_remark.fail_remarks(ex)
            else:
                ex = "[Exception: ASCFeed_dealer_data] asc_id {0} already exists".format(asc['asc_id'])
                logger.error(ex)
        return self.feed_remark
    
class ASCAndServiceAdvisorFeed(BaseFeed):

    def import_data(self):
        total_failed = 0
        for asc in self.data_source:
            try:
                asc_data = models.AuthorizedServiceCenter.objects.get(asc_id=asc['id'])
            except ObjectDoesNotExist as ex:
                asc_obj = self.register_user(Roles.ASCS, username=asc['id'])
                asc_data = models.AuthorizedServiceCenter(user=asc_obj,asc_id=asc['id'])
            try:
                mobile_number_active = self.check_mobile_active(asc, asc_data)
                if mobile_number_active and asc['status']=='Y':
                    raise ValueError(asc['phone_number'] + ' is active under another dealer')
                try:
                    service_advisor = models.ServiceAdvisor.objects.select_related('user__user').get(
                                        service_advisor_id=asc['service_advisor_id'])
                    if service_advisor.user.phone_number != asc['phone_number']:
                        service_advisor.user.phone_number = asc['phone_number']
                        logger.info(
                        "[Info: DealerAndServiceAdvisorFeed_sa]: Updated phone number for {0}"
                        .format(asc['service_advisor_id']))
                except ObjectDoesNotExist as odne:
                    logger.info(
                    "[Exception:  DealerAndServiceAdvisorFeed_sa]: {0}"
                    .format(odne))
                    sa_user = self.register_user(Roles.SERVICEADVISOR, username=asc['service_advisor_id'],
                                                 first_name=asc['name'],
                                                 phone_number=asc['phone_number'])
                    service_advisor = models.ServiceAdvisor(
                                            service_advisor_id=asc['service_advisor_id'], 
                                            asc=asc_data, user=sa_user)
                service_advisor.status = unicode(asc['status'])
                service_advisor.save()
            except Exception as ex:
                total_failed += 1
                ex = "{0}".format(ex)
                logger.error(ex)
                self.feed_remark.fail_remarks(ex)
                continue

        return self.feed_remark

    def check_mobile_active(self, asc, asc_data):
        list_mobile = models.ServiceAdvisor.objects.active(asc['phone_number'])
        list_active_mobile = list_mobile.exclude(asc=asc_data,
                                                 service_advisor_id=asc['service_advisor_id'])
        if list_active_mobile:
            return True
        return False
