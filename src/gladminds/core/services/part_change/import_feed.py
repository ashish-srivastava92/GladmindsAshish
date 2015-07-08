import logging
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from gladminds.core.model_fetcher import get_model
from gladminds.core.auth_helper import Roles
from gladminds.core.services.feed_resources import BaseFeed
from gladminds.core.managers import mail
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
            'sbom_main': SBOMMainFeed,
            'eco_release': ECOReleaseFeed,
            'eco_implementation':ECOImplementationFeed,
            'manufacture_data': ManufactureDataFeed,
        }
        feed_obj = function_mapping[feed_type](data_source=data_source,
                                             feed_remark=feed_remark)
        return feed_obj.import_data()

    
class SBOMMainFeed(BaseFeed):
  
    def import_data(self):
        bom_header_obj = 0
        for bom in self.data_source[1]:
            try:
                bom_header_obj = get_model('BOMHeader')(sku_code=bom['sku_code'],
                                                        plant=bom['plant'],
                                                        bom_type=bom['bom_type'],
                                                        bom_number=bom['bom_number_header'],
                                                        created_on=bom['created_on'],
                                                        valid_from=bom['valid_from_header'],
                                                        valid_to=bom['valid_to_header'])
                bom_header_obj.save(using=settings.BRAND) 
            except Exception as ex:
                ex="[Exception: ]: SBOMMainFeed {0}".format(ex)
                logger.error(ex)
                self.feed_remark[1].fail_remarks(ex)

        for bom in self.data_source[0]:
            try:
                bom_plate_obj = get_model('BOMPlate')(plate_id=bom['plate_id'], plate_txt=bom['plate_txt'])
                bom_plate_obj.save(using=settings.BRAND)
                
                bom_part_obj = get_model('BOMPart')(part_number=bom['part_number'], revision_number=bom['revision_number'])
                bom_part_obj.save(using=settings.BRAND)

                bomplatepart_obj = get_model('BOMPlatePart')(quantity=bom['quantity'], uom=bom['uom'],
                                                            change_number_to=bom['change_number_to'],
                                                            change_number=bom['change_number'],
                                                            valid_from=bom['valid_from'], valid_to=bom['valid_to'], 
                                                            serial_number=bom['serial_number'],
                                                            item=bom['item'], item_id=bom['item_id'])

                bomplatepart_obj.bom = bom_header_obj
                bomplatepart_obj.part = bom_part_obj
                bomplatepart_obj.plate = bom_plate_obj
                bomplatepart_obj.save(using=settings.BRAND)
                mail.send_epc_feed_received_mail(brand=settings.BRAND, template_name='SBOM_FEED')
            except Exception as ex:
                ex="[Exception: ]: SBOMMainFeed {0}".format(ex)
                logger.error(ex)
                self.feed_remark[0].fail_remarks(ex)

        return self.feed_remark
    
class ECOReleaseFeed(BaseFeed):    

    def import_data(self):
        for eco_obj in self.data_source:
            try:
                if eco_obj['eco_release_date'] == "0000-00-00" or not eco_obj['eco_release_date']:
                    eco_release_date=None
                else:
                    eco_release_date=datetime.strptime(eco_obj['eco_release_date'], "%Y-%m-%d")
                eco_release_obj = get_model('ECORelease')(eco_number=eco_obj['eco_number'], eco_release_date=eco_release_date,
                                                    eco_description=eco_obj['eco_description'], action=eco_obj['action'], parent_part=eco_obj['parent_part'],
                                                    add_part=eco_obj['add_part'], add_part_qty=eco_obj['add_part_qty'], add_part_rev=eco_obj['add_part_rev'],
                                                    add_part_loc_code=eco_obj['add_part_loc_code'], del_part=eco_obj['del_part'], del_part_qty=eco_obj['del_part_qty'],
                                                    del_part_rev=eco_obj['del_part_rev'], del_part_loc_code=eco_obj['del_part_loc_code'], 
                                                    models_applicable=eco_obj['models_applicable'], serviceability=eco_obj['serviceability'], 
                                                    interchangebility=eco_obj['interchangebility'], reason_for_change=eco_obj['reason_for_change'])
                eco_release_obj.save()
                mail.send_epc_feed_received_mail(brand=settings.BRAND, template_name='ECO_RELEASE_FEED')
            except Exception as ex:
                ex="[Exception: ]: ECOReleaseFeed {0}".format(ex)
                logger.error(ex)
                self.feed_remark.fail_remarks(ex)
        return self.feed_remark

class ECOImplementationFeed(BaseFeed):

    def import_data(self):
        for eco_obj in self.data_source:
            try:
                if eco_obj['change_date'] == "0000-00-00" or not eco_obj['change_date']:
                    change_date=None
                else:
                    change_date=datetime.strptime(eco_obj['change_date'], "%Y-%m-%d")
                eco_implementation_obj = get_model('ECOImplementation')(change_no=eco_obj['change_no'],change_date=change_date,
                                                           change_time=eco_obj['change_time'],plant=eco_obj['plant'],
                                                           action=eco_obj['action'],parent_part=eco_obj['parent_part'],
                                                           added_part=eco_obj['added_part'],added_part_qty=eco_obj['added_part_qty'],
                                                           deleted_part=eco_obj['deleted_part'],deleted_part_qty=eco_obj['deleted_part_qty'],
                                                           chassis_number=eco_obj['chassis_number'],engine_number=eco_obj['engine_number'],
                                                           eco_number=eco_obj['eco_number'],reason_code=eco_obj['reason_code'],
                                                           remarks=eco_obj['remarks']
                                                           )
                eco_implementation_obj.save()
                self.modify_sbom_data(eco_implementation_obj)
                mail.send_epc_feed_received_mail(brand=settings.BRAND, template_name='ECO_RELEASE_FEED')
                
            except Exception as ex:
                ex="[Exception: ]: ECOImplementationFeed {0}".format(ex)
                logger.error(ex)
                self.feed_remark.fail_remarks(ex)
        return self.feed_remark
    
    def modify_sbom_data(self, eco_implementation_obj):
        try:
            eco_release_obj  = get_model('ECORelease').objects.get(eco_number=eco_implementation_obj.eco_number)
            bom_header = get_model('BOMHeader').objects.get(sku_code=eco_release_obj.models_applicable)
            bom_plate = get_model('BOMPlate').objects.get(plate_id=eco_implementation_obj.parent_part)
            if eco_implementation_obj.added_part:
                try:
                    bom_part = get_model('BOMPart').objects.get(part_number=eco_implementation_obj.added_part)
                except Exception as ex:
                    ex="[Exception: ]: while adding new part {0}".format(ex)
                    logger.error(ex)
                    bom_part = get_model('BOMPart')(part_number=eco_implementation_obj.added_part)
                    bom_part.save(using=settings.BRAND)
                bom_plate_part = get_model('BOMPlatePart')(bom=bom_header, plate=bom_plate, part=bom_part,
                                                                   quantity=eco_implementation_obj.added_part_qty,
                                                                   valid_from=eco_implementation_obj.change_date,
                                                                   valid_to='9999-12-31',
                                                                   change_number=eco_implementation_obj.change_no)
                bom_plate_part.save(using=settings.BRAND)
                bom_plate_part.bom.bom_number=bom_header.bom_number
                bom_plate_part.plate.plate_id=eco_implementation_obj.parent_part
                bom_plate_part.save(using=settings.BRAND)
            if eco_implementation_obj.deleted_part:
                try:
                    bom_part = get_model('BOMPart').objects.get(part_number=eco_implementation_obj.deleted_part)
                    bom_plate_part = get_model('BOMPlatePart').objects.filter(bom__bom_number=bom_header.bom_number,
                                                                              plate__plate_id=eco_implementation_obj.parent_part,
                                                                              part=bom_part)
                    if len(bom_plate_part) > 0:
                        bom_plate_part.update(valid_to=eco_implementation_obj.change_date)
                except Exception as ex:
                    ex="[Exception] : while deleting a part {0}".format(ex)
                    logger.error(ex)
        except ObjectDoesNotExist as odne:
            ex = "[Exception]: modify sbom data {0}".format(odne)
            logger.error(ex)
        return
    
class ManufactureDataFeed(BaseFeed):    

    def import_data(self):
        for data_obj in self.data_source:
            try:
                is_discrepant=False
                manufacture_data_obj = get_model('ManufacturingData').objects.filter(
                                                            product_id=data_obj['product_id'],
                                                            is_discrepant=is_discrepant)
                if manufacture_data_obj:
                    if self.all_values_same(manufacture_data_obj.values(), data_obj):
                        continue
                    is_discrepant=True
                manufacture_data_obj = get_model('ManufacturingData')(product_id=data_obj['product_id'],
                                           material_number=data_obj['material_number'],
                                           plant=data_obj['plant'], engine=data_obj['engine'],
                                           vehicle_off_line_date=data_obj['vehicle_off_line_date'],
                                           is_discrepant=is_discrepant)
                manufacture_data_obj.save()
            except Exception as ex:
                ex="[Exception: ]: ManufactureDataFeed {0}".format(ex)
                logger.error(ex)
                self.feed_remark.fail_remarks(ex)
        return self.feed_remark
    
    def all_values_same(self,manufacture_data_obj, data_obj):
        for key, value in data_obj.items():
            active = filter(lambda active: active[key] == value, manufacture_data_obj)
            if not active:
                return False
        return True      
