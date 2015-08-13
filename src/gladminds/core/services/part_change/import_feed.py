import logging
from datetime import datetime

from django.conf import settings
from django.db import transaction

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
            except Exception as ex:
                ex="[Exception: ]: SBOMMainFeed {0}".format(ex)
                logger.error(ex)
                self.feed_remark[0].fail_remarks(ex)
        mail.send_epc_feed_received_mail(brand=settings.BRAND, template_name='SBOM_FEED')
        return self.feed_remark
    
class ECOReleaseFeed(BaseFeed):    

    def import_data(self):
        try:
            eco_release_obj_list=[]
            for eco_obj in self.data_source:
                if eco_obj['eco_release_date'] == "0000-00-00" or not eco_obj['eco_release_date']:
                    eco_release_date=None
                else:
                    eco_release_date=datetime.strptime(eco_obj['eco_release_date'], "%Y-%m-%d")
                eco_release_obj_list.append(get_model('ECORelease')(eco_number=eco_obj['eco_number'], eco_release_date=eco_release_date,
                                                    eco_description=eco_obj['eco_description'], action=eco_obj['action'], parent_part=eco_obj['parent_part'],
                                                    add_part=eco_obj['add_part'], add_part_qty=eco_obj['add_part_qty'], add_part_rev=eco_obj['add_part_rev'],
                                                    add_part_loc_code=eco_obj['add_part_loc_code'], del_part=eco_obj['del_part'], del_part_qty=eco_obj['del_part_qty'],
                                                    del_part_rev=eco_obj['del_part_rev'], del_part_loc_code=eco_obj['del_part_loc_code'], 
                                                    models_applicable=eco_obj['models_applicable'], serviceability=eco_obj['serviceability'], 
                                                    interchangebility=eco_obj['interchangebility'], reason_for_change=eco_obj['reason_for_change']))
            get_model('ECORelease').objects.bulk_create(eco_release_obj_list)
            mail.send_epc_feed_received_mail(brand=settings.BRAND, template_name='ECO_RELEASE_FEED')
        except Exception as ex:
            ex="[Exception: ]: ECOReleaseFeed {0}".format(ex)
            logger.error(ex)
            self.feed_remark.fail_remarks(ex)
        return self.feed_remark

class ECOImplementationFeed(BaseFeed):

    def import_data(self):
        try:
            eco_implementation_list=[]
            eco_number_list=[]
            plate_list=[]
            added_part_list=[]
            for eco_obj in self.data_source:
                if eco_obj['change_date'] == "0000-00-00" or not eco_obj['change_date']:
                    change_date=None
                else:
                    change_date=datetime.strptime(eco_obj['change_date'], "%Y-%m-%d")
                
                eco_implementation_list.append(get_model('ECOImplementation')(change_no=eco_obj['change_no'],change_date=change_date,
                                                           change_time=eco_obj['change_time'],plant=eco_obj['plant'],
                                                           action=eco_obj['action'],parent_part=eco_obj['parent_part'],
                                                           added_part=eco_obj['added_part'],added_part_qty=eco_obj['added_part_qty'],
                                                           deleted_part=eco_obj['deleted_part'],deleted_part_qty=eco_obj['deleted_part_qty'],
                                                           chassis_number=eco_obj['chassis_number'],engine_number=eco_obj['engine_number'],
                                                           eco_number=eco_obj['eco_number'],reason_code=eco_obj['reason_code'],
                                                           remarks=eco_obj['remarks']
                                                           ))
                eco_number_list.append(eco_obj['eco_number'])
                plate_list.append(eco_obj['parent_part'])
                added_part_list.append(eco_obj['added_part'])
            eco_implementation_obj = get_model('ECOImplementation').objects.bulk_create(eco_implementation_list)
            feed_remark = self.modify_sbom_data(eco_implementation_obj, set(eco_number_list), set(plate_list), set(added_part_list), self.feed_remark)
            mail.send_epc_feed_received_mail(brand=settings.BRAND, template_name='ECO_RELEASE_FEED')
            self.feed_remark=feed_remark
        except Exception as ex:
            ex="[Exception: ]: ECOImplementationFeed {0}".format(ex)
            logger.error(ex)
            self.feed_remark.fail_remarks(ex)
        return self.feed_remark
    
    
    def modify_sbom_data(self, data_source, eco_number_list, plate_list, part_list, feed_remark):
        try:
            with transaction.atomic():
                sku_code_list=[]
                eco_sku={}
                eco_release = get_model('ECORelease').objects.filter(eco_number__in=eco_number_list)
                for eco_release_obj in eco_release:
                    sku_code_list.append(eco_release_obj.models_applicable)
                    eco_sku[eco_release_obj.eco_number]=eco_release_obj.models_applicable
                bom_header = get_model('BOMHeader').objects.filter(sku_code__in=sku_code_list)
                if not bom_header:
                    raise ValueError('Invalid sku codes')
                bom_header_create=[]
                for eco_number in eco_number_list:
                    revision_number=0
                    eco_number_exist=filter(lambda bom_obj: bom_obj.eco_number == eco_number, bom_header)
                    if not eco_number_exist:
                        sku_data=filter(lambda bom_obj: bom_obj.sku_code == eco_sku[str(eco_number)], bom_header)
                        for sku in sku_data:
                            if sku.revision_number>revision_number:
                                revision_number=sku.revision_number
                        bom_header_create.append(get_model('BOMHeader')(sku_code=sku_data[0].sku_code,
                                                            bom_number=sku_data[0].bom_number,
                                                            revision_number=revision_number+1,
                                                            eco_number=eco_number))
                get_model('BOMHeader').objects.bulk_create(bom_header_create)
                
                bom_plates = get_model('BOMPlate').objects.filter(plate_id__in=plate_list).values_list("plate_id", flat=True)
                new_plates=plate_list.difference(set(bom_plates))
                insert_plate_data=[]
                for plate in new_plates:
                    insert_plate_data.append(get_model('BOMPlate')(plate_id=plate))
                get_model('BOMPlate').objects.bulk_create(insert_plate_data)
                        
                bom_parts = get_model('BOMPart').objects.filter(part_number__in=part_list).values_list("part_number", flat=True)
                new_parts=part_list.difference(set(bom_parts))
                insert_part_data=[]
                for part in new_parts:
                    insert_part_data.append(get_model('BOMPart')(part_number=part, revision_number=0))
                get_model('BOMPart').objects.bulk_create(insert_part_data)
                
                bom_header = get_model('BOMHeader').objects.filter(sku_code__in=sku_code_list)
                bom_plates = get_model('BOMPlate').objects.filter(plate_id__in=plate_list)
                bom_parts = get_model('BOMPart').objects.filter(part_number__in=part_list)
                
                bom_plate_part_list=[]
                for eco_implementation_obj in data_source:
                    bom_obj = filter(lambda bom_obj: eco_implementation_obj.eco_number == bom_obj.eco_number, bom_header)
                    plate_obj = filter(lambda plate_obj: eco_implementation_obj.parent_part == plate_obj.plate_id, bom_plates)
                    if eco_implementation_obj.added_part:
                        part_obj = filter(lambda part_obj: eco_implementation_obj.added_part == part_obj.part_number, bom_parts)
                        bom_plate_part_list.append(get_model('BOMPlatePart')(bom=bom_obj[0], plate=plate_obj[0], part=part_obj[0],
                                                                       quantity=eco_implementation_obj.added_part_qty,
                                                                       valid_from=eco_implementation_obj.change_date,
                                                                       valid_to='9999-12-31',
                                                                       change_number=eco_implementation_obj.change_no))
                    if eco_implementation_obj.deleted_part:
                        part_obj = filter(lambda part_obj: eco_implementation_obj.deleted_part == part_obj.part_number, bom_parts)
                        if part_obj:
                            bom_plate_part = get_model('BOMPlatePart').objects.filter(bom=bom_obj[0],
                                                                                plate=plate_obj[0], part=part_obj[0])
                            if len(bom_plate_part) > 0:
                                bom_plate_part.update(valid_to=eco_implementation_obj.change_date)
                get_model('BOMPlatePart').objects.bulk_create(bom_plate_part_list)
        except Exception as done:
            ex = "[Exception]: modify sbom data {0}".format(done)
            logger.error(ex)
            feed_remark.fail_remarks(ex)
        return feed_remark
    
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
