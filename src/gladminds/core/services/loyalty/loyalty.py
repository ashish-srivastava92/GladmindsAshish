'''Handlers for loyalty service logic'''

from gladminds.core.services.services import Services
import logging
import json
from datetime import datetime,timedelta
import StringIO
import csv
from django.http import HttpResponse
from django.conf import settings
from gladminds.core.auth_helper import Roles
from gladminds.core.managers.audit_manager import sms_log
from gladminds.core.model_fetcher import get_model
from gladminds.sqs_tasks import send_point, send_loyalty_sms
from gladminds.core import utils, constants
from gladminds.core.services.message_template import get_template
from gladminds.core.managers.mail import get_email_template, \
                       send_email_to_redemption_request_partner
from  gladminds.core.core_utils.date_utils import get_time_in_seconds
LOG = logging.getLogger('gladminds')

AUDIT_ACTION = 'SEND TO QUEUE'

LOG = logging.getLogger('gladminds')

class CoreLoyaltyService(Services):

    def __init__(self):
        Services.__init__(self)

    def save_comment(self, comment_type, message, transaction_id, user):
        '''Saves comment for welcome kit and redemption request'''
        redemption=welcome_kit=None
        if comment_type=='redemption':
            redemption = transaction_id
        elif comment_type=='welcome_kit':
            welcome_kit = transaction_id
        comment_thread = get_model('CommentThread')(user=user,
                                              message=message,
                                              welcome_kit=welcome_kit, 
                                              redemption=redemption)
        comment_thread.save(using=settings.BRAND)
        return comment_thread

    def get_mechanics_detail(self, request, choice, model_name):
        '''Fetches the details of the mechanics based on args'''
        kwargs={}
        if choice=='new':
            kwargs['download_detail'] = False
        if choice!='all':
            kwargs['form_status'] = 'Complete'
        if request.user.groups.filter(name=Roles.AREASPARESMANAGERS).exists():
            asm_state_list=get_model('AreaSparesManager').objects.get(user__user=request.user).state.all()
            kwargs['state__in'] = asm_state_list
        mechanics = get_model(model_name).objects.using(settings.BRAND).filter(**kwargs).select_related('state', 'registered_by_distributor')
        return mechanics
    
    def get_welcome_redemption_detail(self, request, choice, model_name):
        '''Fetches the details of the welcome/redemption based on args'''
        kwargs={}
        if choice!='all':
            kwargs['status'] = choice
        if request.user.groups.filter(name=Roles.AREASPARESMANAGERS).exists():
            asm_state_list=get_model('AreaSparesManager').objects.get(user__user=request.user).state.all()
            kwargs['member__state__in'] = asm_state_list
        elif request.user.groups.filter(name=Roles.RPS).exists():
            kwargs['packed_by'] = request.user.username
        elif request.user.groups.filter(name=Roles.LPS).exists():
            kwargs['partner__user'] = request.user
        welcome_kits = get_model(model_name).objects.using(settings.BRAND).filter(**kwargs).select_related('member__state', 'product')
        return welcome_kits
        
    def check_details(self, request, model, choice):
        '''Before download checks if there is any valid data to be download'''
        response = {'status': False}
        request_handler={'Member': 'get_mechanics_detail',
                         'WelcomeKit': 'get_welcome_redemption_detail',
                         'RedemptionRequest': 'get_welcome_redemption_detail'
                         }
        handler_funtion=getattr(self, request_handler[model])
        details = handler_funtion(request, choice, model)
        if details:
            response['status']=True
        return HttpResponse(json.dumps(response),
                            content_type='application/json')
        
    def download_member_detail(self, request, choice):
        '''Download list of new or all registered member'''
        file_name=choice+'_member_details_' + datetime.now().strftime('%d_%m_%y')
        headers=[]
        headers=headers+constants.DOWNLOAD_MECHANIC_FIELDS
        csvfile = StringIO.StringIO()
        csvwriter = csv.writer(csvfile)
        if not request.user.groups.filter(name__in=[Roles.RPS, Roles.LPS]).exists():  
            headers.append('form_status')
        csvwriter.writerow(headers)
        mechanics = self.get_mechanics_detail(request, choice, 'Member')
        for mechanic in mechanics:
            data=[]
            for field in headers:
                if field=='image_url':
                    image_url="{0}/{1}".format(settings.S3_BASE_URL, mechanic.image_url)
                    data.append(image_url)
                elif field=='state':
                    if mechanic.state:
                        data.append(mechanic.state.state_name)
                    else:
                        data.append(mechanic.state)
                elif field=='registered_by_distributor':
                    if mechanic.registered_by_distributor:
                        data.append(mechanic.registered_by_distributor.distributor_id)
                    else:
                        data.append(mechanic.registered_by_distributor)
                else:
                    data.append(getattr(mechanic, field))
            csvwriter.writerow(data)
        if choice in ['new','complete']:
            mechanics.using(settings.BRAND).update(download_detail=True)
        response = HttpResponse(csvfile.getvalue(), content_type='application/csv')
        response['Content-Disposition'] = 'attachment; filename={0}.csv'.format(file_name)
        LOG.error('[download_member_detail]: Download of mechanic data by user {0}'.format(request.user))
        return response

    def download_welcome_kit_detail(self, request, choice):
        '''Download list of new or all welcome kit'''
        file_name=choice+'_welcome_kit_details_' + datetime.now().strftime('%d_%m_%y')
        headers=constants.DOWNLOAD_WELCOME_KIT_FIELDS
        csvfile = StringIO.StringIO()
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)
        welcome_kits = self.get_welcome_redemption_detail(request, choice, 'WelcomeKit')
        for kit in welcome_kits:
            data=[]
            for field in headers:
                member=kit.member
                if field=='image_url':
                    image_url="{0}/{1}".format(settings.S3_BASE_URL, member.image_url)
                    data.append(image_url)
                elif field=='state':
                    data.append(member.state.state_name)
                elif field=='delivery_address':
                    data.append(kit.delivery_address)
                else:
                    data.append(getattr(member, field))
            csvwriter.writerow(data)
        response = HttpResponse(csvfile.getvalue(), content_type='application/csv')
        response['Content-Disposition'] = 'attachment; filename={0}.csv'.format(file_name)
        LOG.error('[download_welcome_kit]: Download of welcome kit data by user {0}'.format(request.user))
        return response

    def download_redemption_detail(self, request, choice):
        '''Download list of new or all redemption request'''
        file_name=choice+'_redemption_request_details_' + datetime.now().strftime('%d_%m_%y')
        headers=constants.DOWNLOAD_REDEMPTION_FIELDS
        csvfile = StringIO.StringIO()
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)
        redemptions = self.get_welcome_redemption_detail(request, choice, 'RedemptionRequest')
        for redemption in redemptions:
            data=[]
            for field in headers:
                member=redemption.member
                if field=='state':
                    data.append(member.state.state_name)
                elif field=='delivery_address':
                    data.append(redemption.delivery_address)
                elif field=='product':
                    data.append(redemption.product.product_id)
                else:
                    data.append(getattr(member, field))
            csvwriter.writerow(data)
        response = HttpResponse(csvfile.getvalue(), content_type='application/csv')
        response['Content-Disposition'] = 'attachment; filename={0}.csv'.format(file_name)
        LOG.error('[download_redemption_detail]: Download of redemption request data by user {0}'.format(request.user))
        return response


    def send_welcome_sms(self, mech):
        '''Send welcome sms to mechanics when registered'''
        phone_number=utils.get_phone_number_format(mech.phone_number)
        message=get_template('COMPLETE_FORM').format(
                        mechanic_name=mech.first_name,
                        member_id=mech.permanent_id)
        sms_log(settings.BRAND, receiver=phone_number, action=AUDIT_ACTION, message=message)
        self.queue_service(send_loyalty_sms, {'phone_number': phone_number,
                    'message': message, "sms_client": settings.SMS_CLIENT})
        LOG.error('[send_welcome_sms]:{0}:: {1}'.format(
                                    phone_number, message))

    def send_welcome_message(self, request):
        '''Send welcome sms to mechanics uploaded: one time use'''
        if settings.ENV in settings.IGNORE_ENV:
            return HttpResponse(json.dumps({'msg': 'SMS not allowed in ENV'}),
                                content_type='application/json')
        phone_list=[]
        mechanics = get_model('Member').objects.using(settings.BRAND).filter(sent_sms=False)
        for mech in mechanics:
            self.send_welcome_sms(mech)
            phone_list.append(mech.phone_number)
        mechanics.using(settings.BRAND).update(sent_sms=True)
        response = 'Message sent to {0} mechanics. phone numbers: {1}'.format(
                                len(phone_list), (', '.join(phone_list)))
        return HttpResponse(json.dumps({'msg': response}),
                            content_type='application/json')

    def send_welcome_kit_mail_to_partner(self, welcome_kit_obj):
        '''Send mail to GP and LP when welcome Kit is assigned to them'''
        data = get_email_template('ASSIGNEE_WELCOME_KIT_MAIL', settings.BRAND)
        data['newsubject'] = data['subject'].format(id = welcome_kit_obj.transaction_id)
        url_link='http://bajaj.gladminds.co'
        data['content'] = data['body'].format(id=welcome_kit_obj.transaction_id,
                              created_date = welcome_kit_obj.created_date,
                              member_id = welcome_kit_obj.member.mechanic_id,
                              member_name = welcome_kit_obj.member.first_name,
                              member_city = welcome_kit_obj.member.district,
                              member_state = welcome_kit_obj.member.state.state_name,
                        delivery_address = welcome_kit_obj.delivery_address,
                        url_link=url_link)
        partner_email_id=welcome_kit_obj.partner.user.user.email
        send_email_to_redemption_request_partner(data, partner_email_id)
        LOG.info('[send_welcome_kit_mail_to_partner]:{0}:: welcome kit request email sent'.format(
                                    partner_email_id))
        
    def send_welcome_kit_delivery(self, redemption_request):
        '''Send redemption request sms to mechanics'''
        member = redemption_request.member
        phone_number=utils.get_phone_number_format(member.phone_number)
        message=get_template('WELCOME_KIT_DELIVERY').format(
                        mechanic_name=member.first_name)
        sms_log(settings.BRAND, receiver=phone_number, action=AUDIT_ACTION, message=message)
        self.queue_service(send_loyalty_sms, {'phone_number': phone_number,
                    'message': message, "sms_client": settings.SMS_CLIENT})
        LOG.error('[send_request_status_sms]:{0}:: {1}'.format(
                                    phone_number, message))
        
    def initiate_welcome_kit(self, mechanic_obj):
        '''Saves the welcome kit request for processing'''
        welcome_kit=get_model('WelcomeKit').objects.filter(member=mechanic_obj)
        if not welcome_kit:
            delivery_address = ', '.join(filter(None, (mechanic_obj.shop_number,
                                                       mechanic_obj.shop_name,
                                                       mechanic_obj.shop_address)))
            partner=None
            packed_by=None
            partner_list = get_model('Partner').objects.using(settings.BRAND).all()
            if len(partner_list)==1:
                partner=partner_list[0]
                packed_by=partner.user.user.username
            date = self.set_date('Welcome Kit', 'Open')
            welcome_kit=get_model('WelcomeKit')(member=mechanic_obj,
                                        delivery_address=delivery_address,
                                        partner=partner,
                                        packed_by=packed_by,
                                        due_date=date['due_date'],
                                        expected_delivery_date=date['expected_delivery_date'])
            welcome_kit.save(using=settings.BRAND)
            self.send_welcome_kit_mail_to_partner(welcome_kit)
        else:
            welcome_kit=welcome_kit[0]
        return welcome_kit

    def send_mail_to_partner(self, redemption_obj):
        '''Send mail to GP and LP when redemption
           request is assigned to them'''
        data = get_email_template('ASSIGNEE_REDEMPTION_MAIL_DETAIL', settings.BRAND)
        data['newsubject'] = data['subject'].format(id = redemption_obj.transaction_id)
        url_link='http://bajaj.gladminds.co'
        data['content'] = data['body'].format(id=redemption_obj.transaction_id,
                              created_date = redemption_obj.created_date,
                              member_id = redemption_obj.member.mechanic_id,
                              member_name = redemption_obj.member.first_name,
                              member_city = redemption_obj.member.district,
                              member_state = redemption_obj.member.state.state_name,
                              product_id =  redemption_obj.product.product_id,
                              product_name =  redemption_obj.product.description,
                        delivery_address = redemption_obj.delivery_address,
                        url_link=url_link)
        partner_email_id=redemption_obj.partner.user.user.email
        send_email_to_redemption_request_partner(data, partner_email_id)
        LOG.error('[send_mail_to_partner]:{0}:: Redemption request email sent'.format(
                                    partner_email_id))

    def send_request_status_sms(self, redemption_request):
        '''Send redemption request sms to mechanics'''
        member = redemption_request.member
        phone_number=utils.get_phone_number_format(member.phone_number)
        message=get_template('REDEMPTION_PRODUCT_STATUS').format(
                        mechanic_name=member.first_name,
                        transaction_id=redemption_request.transaction_id,
                        product_name=redemption_request.product.description,
                        status=redemption_request.status.lower())
        sms_log(settings.BRAND, receiver=phone_number, action=AUDIT_ACTION, message=message)
        self.queue_service(send_loyalty_sms, {'phone_number': phone_number,
                    'message': message, "sms_client": settings.SMS_CLIENT})
        LOG.error('[send_request_status_sms]:{0}:: {1}'.format(
                                    phone_number, message))


    def register_redemption_request(self, mechanic, products):
        '''Saves the redemption request for processing'''
        transaction_ids=[]
        member = mechanic[0]
        delivery_address = ', '.join(filter(None, (member.shop_number,
                                                   member.shop_name,
                                                   member.shop_address)))
        for product in products:
            date = self.set_date('Redemption', 'Open')
            redemption_request=get_model('RedemptionRequest')(member=member,
                                        product=product,
                                        delivery_address=delivery_address,
                                        expected_delivery_date=date['expected_delivery_date'],
                                        due_date=date['due_date'],
                                        points=product.points)
            
            redemption_request.save(using=settings.BRAND)
            transaction_ids.append(str(redemption_request.transaction_id))
        transactions = (', '.join(transaction_ids))
        return transactions

    def update_points(self, mechanic, accumulate=0, redeem=0, refund_flag=False):
        '''Update the loyalty points of the user'''
        total_points = mechanic.total_points + accumulate - redeem
        mechanic.total_points = total_points
        if accumulate>0 and not refund_flag:
            mechanic.total_accumulation_req=mechanic.total_accumulation_req+1
            mechanic.total_accumulation_points=mechanic.total_accumulation_points+accumulate
            mechanic.last_transaction_date=datetime.now() 
        elif redeem>0 and not refund_flag:
            mechanic.total_redemption_req=mechanic.total_redemption_req+1
            mechanic.total_redemption_points=mechanic.total_redemption_points+redeem
            mechanic.last_transaction_date=datetime.now()
        mechanic.save(using=settings.BRAND)
        return total_points

    def check_point_balance(self, sms_dict, phone_number):
        '''send balance point of the user'''
        try:
            mechanic = get_model('Member').objects.using(settings.BRAND).filter(phone_number=utils.mobile_format(phone_number))
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
            sms_log(settings.BRAND, receiver=phone_number, action=AUDIT_ACTION, message=message)
            self.queue_service(send_point, {'phone_number': phone_number,
                    'message': message, "sms_client": settings.SMS_CLIENT})
        return {'status': True, 'message': message}

    def accumulate_point(self, sms_dict, phone_number):
        '''accumulate points with given upc'''
        unique_product_codes = set((sms_dict['upc'].upper()).split())
        valid_upc=[]
        valid_product_number=[]
        invalid_upcs_message=''
        try:
            if len(unique_product_codes)>constants.MAX_UPC_ALLOWED:
                message=get_template('MAX_ALLOWED_UPC').format(
                                        max_limit=constants.MAX_UPC_ALLOWED)
                raise ValueError('Maximum allowed upc exceeded')
            mechanic = get_model('Member').objects.using(settings.BRAND).filter(phone_number=utils.mobile_format(phone_number))
            if not mechanic:
                message=get_template('UNREGISTERED_USER')
                raise ValueError('Unregistered user')
            elif mechanic and  mechanic[0].form_status=='Incomplete':
                message=get_template('INCOMPLETE_FORM')
                raise ValueError('Incomplete user details')
            state_code= mechanic[0].state.state_code
            spares = get_model('SparePartUPC').objects.get_spare_parts(unique_product_codes)
            added_points=0
            spare_upc_part_map={}
            total_points=mechanic[0].total_points
            if spares:
                for spare in spares:
                    valid_product_number.append(spare.part_number)
                    if not spare_upc_part_map.has_key(spare.part_number):
                        spare_upc_part_map[spare.part_number]=[]
                    spare_upc_part_map[spare.part_number].append(spare.unique_part_code.upper())
                spare_points = get_model('SparePartPoint').objects.get_part_number(valid_product_number, state_code)
                if spare_points:
                    accumulation_log=get_model('AccumulationRequest')(member=mechanic[0],
                                                            points=0,total_points=0)
                    accumulation_log.save(using=settings.BRAND)
                    for spare_point in spare_points:
                        added_points=added_points+(len(spare_upc_part_map[spare_point.part_number]) * spare_point.points)
                        valid_upc.extend(spare_upc_part_map[spare_point.part_number])
                    total_points=self.update_points(mechanic[0],
                                    accumulate=added_points)

                    valid_spares = get_model('SparePartUPC').objects.get_spare_parts(valid_upc)
                    for spare in valid_spares:
                        accumulation_log.upcs.add(spare)
                    accumulation_log.points=added_points
                    accumulation_log.total_points=total_points
                    accumulation_log.save(using=settings.BRAND)
                    valid_spares.using(settings.BRAND).update(is_used=True)
            invalid_upcs = list(set(unique_product_codes).difference(valid_upc))
            if invalid_upcs:
                invalid_upcs_message=' Invalid Entry... {0} does not exist in our records.'.format(
                                              (', '.join(invalid_upcs)))
                used_upcs = get_model('SparePartUPC').objects.get_spare_parts(invalid_upcs, is_used=True)
                if used_upcs:
                    accumulation_requests = get_model('AccumulationRequest').objects.using(settings.BRAND).filter(upcs__in=used_upcs).prefetch_related('upcs').select_related('upcs')
                    accumulation_dict = {}
                    try:
                        for accumulation_request in accumulation_requests:
                            for upcs in  accumulation_request.upcs.values():
                                accumulation_dict[upcs['unique_part_code']] = accumulation_request    
                        for used_upc in used_upcs:
                            discrepant_accumulation_log = get_model('DiscrepantAccumulation')(new_member=mechanic[0], upc = used_upc,
                                                                         accumulation_request=accumulation_dict[used_upc])
                            discrepant_accumulation_log.save(using=settings.BRAND)
                    except Exception as ex:
                        LOG.error('[accumulate_point]:{0}:: {1}'.format(phone_number, ex))
            if len(unique_product_codes)==1 and invalid_upcs:
                message=get_template('SEND_INVALID_UPC')
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
            sms_log(settings.BRAND, receiver=phone_number, action=AUDIT_ACTION, message=message)
            self.queue_service(send_point, {'phone_number': phone_number,
                    'message': message, "sms_client": settings.SMS_CLIENT})
        return {'status': True, 'message': message}

    def redeem_point(self, sms_dict, phone_number):
        '''redeem points with given upc'''
        product_codes = sms_dict['product_id'].upper().split()
        try:
            mechanic = get_model('Member').objects.using(settings.BRAND).filter(phone_number=utils.mobile_format(phone_number))
            if not mechanic:
                message=get_template('UNREGISTERED_USER')
                raise ValueError('Unregistered user')
            elif mechanic and  mechanic[0].form_status=='Incomplete':
                message=get_template('INCOMPLETE_FORM')
                raise ValueError('Incomplete user details')
            elif mechanic and (mechanic[0].mechanic_id!=sms_dict['member_id'] and mechanic[0].permanent_id!=sms_dict['member_id']):
                message=get_template('INVALID_MEMBER_ID').format(mechanic_name=mechanic[0].first_name)
                raise ValueError('Invalid user-ID')
            products=get_model('ProductCatalog').objects.using(settings.BRAND).filter(product_id__in=product_codes)
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
            sms_log(settings.BRAND, receiver=phone_number, action=AUDIT_ACTION, message=message)
            self.queue_service(send_point, {'phone_number': phone_number,
                  'message': message, "sms_client": settings.SMS_CLIENT})
        return {'status': True, 'message': message}

    def set_date(self,action,status):
        '''Sets date of SLA based on action and status'''
        loyalty_sla_obj = get_model('LoyaltySLA').objects.using(settings.BRAND).get(action=action, status=status)
        total_seconds = get_time_in_seconds(loyalty_sla_obj.resolution_time, loyalty_sla_obj.resolution_unit)
        due_date = datetime.now() + timedelta(seconds=total_seconds)
        total_seconds = get_time_in_seconds(loyalty_sla_obj.member_resolution_time, loyalty_sla_obj.member_resolution_unit)
        expected_delivery_date = datetime.now() + timedelta(seconds=total_seconds)
        return {'due_date':due_date, 'expected_delivery_date':expected_delivery_date}
    
loyalty = CoreLoyaltyService()
