'''Handlers for loyalty logic'''

import logging
import json

from django.conf import settings
from django.http.response import HttpResponse
from gladminds.core.managers.audit_manager import sms_log
from gladminds.bajaj import models
from gladminds.sqs_tasks import send_point, send_loyalty_sms
from gladminds.core import utils, constants
from gladminds.core.services.loyalty.loyalty import CoreLoyaltyService
from gladminds.core.services.message_template import get_template
from datetime import datetime

LOG = logging.getLogger('gladminds')

AUDIT_ACTION = 'SEND TO QUEUE'


class LoyaltyService(CoreLoyaltyService):
    '''Class for loyalty service'''

    def send_request_status_sms(self, redemption_request):
        '''Send redemption request sms to mechanics'''
        member = redemption_request.member
        phone_number=utils.get_phone_number_format(member.phone_number)
        message=get_template('REDEMPTION_PRODUCT_STATUS').format(
                        mechanic_name=member.first_name,
                        transaction_id=redemption_request.transaction_id,
                        status=redemption_request.status.lower())
        sms_log(receiver=phone_number, action=AUDIT_ACTION, message=message)
        self.queue_service(send_loyalty_sms, {'phone_number': phone_number,
                    'message': message, "sms_client": settings.SMS_CLIENT})

    def send_welcome_sms(self, mech):
        '''Send welcome sms to mechanics when registered'''
        phone_number=utils.get_phone_number_format(mech.phone_number)
        message=get_template('WELCOME_MESSAGE').format(
                        mechanic_name=mech.first_name)
        sms_log(receiver=phone_number, action=AUDIT_ACTION, message=message)
        self.queue_service(send_loyalty_sms, {'phone_number': phone_number,
                    'message': message, "sms_client": settings.SMS_CLIENT})

    def send_welcome_message(self, request):
        '''Send welcome sms to mechanics uploaded: one time use'''
        if settings.ENV in settings.IGNORE_ENV:
            return HttpResponse(json.dumps({'msg': 'SMS not allowed in ENV'}),
                                content_type='application/json')
        phone_list=[]
        mechanics = models.Mechanic.objects.filter(sent_sms=False)
        for mech in mechanics:
            self.send_welcome_sms(mech)
            phone_list.append(mech.phone_number)
        mechanics.update(sent_sms=True)
        response = 'Message sent to {0} mechanics. phone numbers: {1}'.format(
                                len(phone_list), (', '.join(phone_list)))
        return HttpResponse(json.dumps({'msg': response}),
                            content_type='application/json')

    def register_redemption_request(self, mechanic, products):
        '''Saves the redemption request for processing'''
        transaction_ids=[]
        member = mechanic[0]
        delivery_address = ', '.join(filter(None, (member.shop_number,
                                                   member.shop_name,
                                                   member.shop_address)))
        for product in products:
            redemption_request=models.RedemptionRequest(member=member,
                                        product=product,
                                        delivery_address=delivery_address)
            redemption_request.save()
            transaction_ids.append(str(redemption_request.transaction_id))
        transactions = (', '.join(transaction_ids))
        return transactions

    def update_points(self, mechanic, accumulate=0, redeem=0):
        '''Update the loyalty points of the user'''
        total_points = mechanic.total_points + accumulate -redeem
        mechanic.total_points = total_points
        mechanic.save()
        return total_points

    def check_point_balance(self, sms_dict, phone_number):
        '''send balance point of the user'''
        try:
            mechanic = models.Mechanic.objects.filter(phone_number=utils.mobile_format(phone_number))
            if not mechanic:
                message=get_template('UNREGISTERED_USER')
                raise ValueError('Unregistered user')
            elif mechanic and  mechanic[0].form_status=='Incomplete':
                message=get_template('INCOMPLETE_FORM')
                raise ValueError('Incomplete user details')

            total_points=mechanic[0].total_points
            today = datetime.now().strftime('%d/%m/%Y')
            message=get_template('SEND_BALANCE_POINT').format(
                            mechanic_name=mechanic[0].first_name,
                            total_points=total_points,
                            today=today)

        except Exception as ex:
            LOG.error('[check_point_balance]:{0}:: {1}'.format(
                                            phone_number, ex))
        finally:
            phone_number = utils.get_phone_number_format(phone_number)
            sms_log(receiver=phone_number, action=AUDIT_ACTION, message=message)
            self.queue_service(send_point, {'phone_number': phone_number,
                    'message': message, "sms_client": settings.SMS_CLIENT})
        return {'status': True, 'message': message}

    def accumulate_point(self, sms_dict, phone_number):
        '''accumulate points with given upc'''
        unique_product_codes = set((sms_dict['ucp'].upper()).split())
        valid_ucp=[]
        valid_product_number=[]
        invalid_upcs_message=''
        try:
            if len(unique_product_codes)>constants.MAX_UCP_ALLOWED:
                message=get_template('MAX_ALLOWED_UCP').format(
                                        max_limit=constants.MAX_UCP_ALLOWED)
                raise ValueError('Maximum allowed ucp exceeded')
            mechanic = models.Mechanic.objects.filter(phone_number=utils.mobile_format(phone_number))
            if not mechanic:
                message=get_template('UNREGISTERED_USER')
                raise ValueError('Unregistered user')
            elif mechanic and  mechanic[0].form_status=='Incomplete':
                message=get_template('INCOMPLETE_FORM')
                raise ValueError('Incomplete user details')
            spares = models.SparePartUPC.objects.get_spare_parts(unique_product_codes)
            added_points=0
            total_points=mechanic[0].total_points
            if spares:
                accumulation_log=models.AccumulationRequest(member=mechanic[0],
                                                        points=0,total_points=0)
                accumulation_log.save()
                for spare in spares:
                    valid_product_number.append(spare.part_number)
                    valid_ucp.append(spare.unique_part_code)
                    accumulation_log.upcs.add(spare)
                spare_points = models.SparePartPoint.objects.get_part_number(valid_product_number)
                for spare_point in spare_points:
                    added_points=added_points+spare_point.points
                total_points=self.update_points(mechanic[0],
                                    accumulate=added_points)
                accumulation_log.points=added_points
                spares.update(is_used=True)
                accumulation_log.total_points=total_points
                accumulation_log.save()
            invalid_upcs = list(set(unique_product_codes).difference(valid_ucp))
            if invalid_upcs:
                invalid_upcs_message=' Invalid Entry... {0} does not exist in our records.'.format(
                                              (', '.join(invalid_upcs)))
            if len(unique_product_codes)==1 and invalid_upcs:
                message=get_template('SEND_INVALID_UCP')
            else:
                message=get_template('SEND_ACCUMULATED_POINT').format(
                                mechanic_name=mechanic[0].first_name,
                                added_points=added_points,
                                total_points=total_points,
                                invalid_upcs=invalid_upcs_message)

        except Exception as ex:
            LOG.error('[accumulate_point]:{0}:: {1}'.format(phone_number, ex))
        finally:
            phone_number = utils.get_phone_number_format(phone_number)
            sms_log(receiver=phone_number, action=AUDIT_ACTION, message=message)
            self.queue_service(send_point, {'phone_number': phone_number,
                    'message': message, "sms_client": settings.SMS_CLIENT})
        return {'status': True, 'message': message}

    def redeem_point(self, sms_dict, phone_number):
        '''redeem points with given upc'''
        product_codes = sms_dict['product_id'].upper().split()
        try:
            mechanic = models.Mechanic.objects.filter(phone_number=utils.mobile_format(phone_number))
            if not mechanic:
                message=get_template('UNREGISTERED_USER')
                raise ValueError('Unregistered user')
            elif mechanic and  mechanic[0].form_status=='Incomplete':
                message=get_template('INCOMPLETE_FORM')
                raise ValueError('Incomplete user details')
            elif mechanic and mechanic[0].mechanic_id!=sms_dict['member_id']:
                message=get_template('INVALID_MEMBER_ID').format(mechanic_name=mechanic[0].first_name)
                raise ValueError('Invalid user-ID')
            products=models.ProductCatalog.objects.filter(product_id__in=product_codes)
            redeem_points=0
            if len(products)==len(product_codes):
                for product in products:
                    redeem_points=redeem_points+product.points
                left_points=mechanic[0].total_points-redeem_points
                if left_points>=0:
                    total_points=self.update_points(mechanic[0],
                                            redeem=redeem_points)
                    transaction_ids = self.register_redemption_request(mechanic,
                                                            products)
                    message=get_template('SEND_REDEEM_POINT').format(
                                    mechanic_name=mechanic[0].first_name,
                                    transaction_id=transaction_ids,
                                    total_points=total_points)
                else:
                    if len(products)==1:
                        message=get_template('SEND_INSUFFICIENT_POINT_SINGLE').format(
                                        mechanic_name=mechanic[0].first_name,
                                        total_points=mechanic[0].total_points,
                                        shortage_points=abs(left_points))
                    else:
                        message=get_template('SEND_INSUFFICIENT_POINT_MULTIPLE').format(
                                        mechanic_name=mechanic[0].first_name,
                                        shortage_points=abs(left_points))
            else:
                message=get_template('INVALID_PRODUCT_ID')
        except Exception as ex:
            LOG.error('[redeem_point]:{0}:: {1}'.format(phone_number, ex))
        finally:
            phone_number = utils.get_phone_number_format(phone_number)
            sms_log(receiver=phone_number, action=AUDIT_ACTION, message=message)
            self.queue_service(send_point, {'phone_number': phone_number,
                  'message': message, "sms_client": settings.SMS_CLIENT})
        return {'status': True, 'message': message}

LoyaltyService = LoyaltyService()