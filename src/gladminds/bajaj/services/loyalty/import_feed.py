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
from gladminds.bajaj import models
from gladminds.core.managers.audit_manager import feed_log, sms_log
from gladminds.core.cron_jobs.queue_utils import send_job_to_queue

logger = logging.getLogger("gladminds")
USER_GROUP = {'dealer': 'dealers', 'ASC': 'ascs', 'SA':'sas', 'customer':"customer"}

class LoyaltyFeed(object):

    def import_to_db(self, feed_type=None, data_source=[], feed_remark=None):
        function_mapping = {
            'part_master': PartMasterFeed,
            'part_upc': PartUPCFeed,
            'part_point': PartPointFeed,
            'distributor': DistributorFeed,
            'mechanic': MechanicFeed
        }
        feed_obj = function_mapping[feed_type](data_source=data_source,
                                             feed_remark=feed_remark)
        return feed_obj.import_data()

class BaseFeed(object):

    def __init__(self, data_source=None, feed_remark=None):
        self.data_source = data_source
        self.feed_remark = feed_remark


class PartMasterFeed(BaseFeed):

    def import_data(self):
        total_failed = 0
        for spare in self.data_source:
            try:
                part_data = models.SparePartMasterData.objects.get(part_number=spare['part_number'])
            except ObjectDoesNotExist as done:
                logger.info(
                    '[Info: PartMasterFeed_part_data]: {0}'.format(done))
                try:
                    spare_type_object = models.ProductType.objects.filter(product_type=spare['part_type'])
                    if not spare_type_object:
                        spare_type_object = models.ProductType(product_type=spare['part_type'])
                        spare_type_object.save()
                    else:
                        spare_type_object = spare_type_object[0]
                    spare_object = models.SparePartMasterData(
                                                product_type=spare_type_object,
                                                part_number = spare['part_number'],
                                                part_model = spare['part_model'],
                                                description = spare['description'],
                                                category = spare['category'],
                                                segment_type = spare['segment'],
                                                supplier = spare['supplier']
                                    )
                    spare_object.save()
                except Exception as ex:
                    total_failed += 1
                    ex = "[PartMasterFeed]: part-{0} :: {1}".format(spare['part_number'], ex)
                    logger.error(ex)
                    self.feed_remark.fail_remarks(ex)
                    continue
        return self.feed_remark


class PartUPCFeed(BaseFeed):

    def import_data(self):
        total_failed = 0
        for spare in self.data_source:
            try:
                part_data = models.SparePartMasterData.objects.get(part_number=spare['part_number'])
                spare_object = models.SparePartUPC(
                                            part_number=part_data,
                                            unique_part_code = spare['UPC'])
                spare_object.save()
            except Exception as ex:
                total_failed += 1
                ex = "[PartUPCFeed]: part-{0} , UPC-{1} :: {2}".format(spare['part_number'],
                                                            spare['UPC'], ex)
                logger.error(ex)
                self.feed_remark.fail_remarks(ex)
                continue

        return self.feed_remark

class PartPointFeed(BaseFeed):

    def import_data(self):
        total_failed = 0
        for spare in self.data_source:
            try:
                part_data = models.SparePartMasterData.objects.get(part_number=spare['part_number'])
                spare_object = models.SparePartPoint.objects.filter(part_number=part_data,
                                                     territory=spare['territory'])
                if not spare_object:
                    spare_object = models.SparePartPoint(part_number = part_data,
                                              points = spare['points'],
                                              price = spare['price'],
                                              MRP = spare['mrp'],
                                              valid_from = spare['valid_from'],
                                              valid_till = spare['valid_to'],
                                              territory = spare['territory'])
                    spare_object.save()
                else:
                    raise ValueError('Points of the part already exists for the territory: ' + spare['territory'])
            except Exception as ex:
                total_failed += 1
                ex = "[PartPointFeed]: part-{0} :: {1}".format(spare['part_number'], ex)
                logger.error(ex)
                self.feed_remark.fail_remarks(ex)
                continue

        return self.feed_remark

class DistributorFeed(BaseFeed):

    def import_data(self):
        total_failed = 0
        for distributor in self.data_source:
            try:
                dist_object = models.Distributor.objects.filter(distributor_id=distributor['id'])
                if not dist_object:
                    password=distributor['id']+'@123'
                    dist_user_object = User.objects.using(settings.BRAND).create(username=distributor['id'])
                    dist_user_object.set_password(password)
                    dist_user_object.email = distributor['email']
                    dist_user_object.first_name = distributor['name']
                    dist_user_object.save(using=settings.BRAND)
                    dist_user_pro_object = models.UserProfile(user=dist_user_object,
                                                phone_number=distributor['mobile'],
                                                address=distributor['city'])
                    dist_user_pro_object.save()
                    asm_object = models.AreaSalesManager.objects.get(asm_id=distributor['asm_id'])
                    dist_object = models.Distributor(distributor_id=distributor['id'],
                                              asm=asm_object,
                                              user=dist_user_pro_object,
                                              name=distributor['name'],
                                              email=distributor['email'],
                                              phone_number=distributor['mobile'],
                                              city=distributor['city'])
                    dist_object.save()
                else:
                    raise ValueError('Distributor ID already exists')
            except Exception as ex:
                total_failed += 1
                ex = "[DistributorFeed]: id-{0} :: {1}".format(distributor['id'], ex)
                logger.error(ex)
                self.feed_remark.fail_remarks(ex)
                continue

        return self.feed_remark

class MechanicFeed(BaseFeed):

    def import_data(self):
        total_failed = 0
        for mechanic in self.data_source:
            try:
                mech_object = models.Mechanic.objects.filter(phone_number=mechanic['mobile'])
                if not mech_object:
                    mech_id = utils.generate_temp_id('TME')
                    if mechanic['dist_id']:
                        dist_object = models.Distributor.objects.get(distributor_id=mechanic['dist_id'])
                    mech_object = models.Mechanic(registered_by_distributor=dist_object,
                                    mechanic_id=mech_id,
                                    first_name = mechanic['first_name'],
                                    last_name = mechanic['last_name'],
                                    date_of_birth=mechanic['dob'],
                                    phone_number=mechanic['mobile'],
                                    shop_name =  mechanic['shop_name'],
                                    state =  mechanic['state'],
                                    pincode =  mechanic['pincode'],
                                    )
                    mech_object.save()
                else:
                    raise ValueError('Mechanic number already exists')
            except Exception as ex:
                total_failed += 1
                ex = "[MechanicFeed]: id-{0} :: {1}".format(mechanic['mobile'], ex)
                logger.error(ex)
                self.feed_remark.fail_remarks(ex)
                continue

        return self.feed_remark