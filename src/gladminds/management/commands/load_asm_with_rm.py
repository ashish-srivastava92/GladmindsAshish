import csv
import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from gladminds.core.model_fetcher import get_model
from gladminds.core.auth_helper import Roles
from django.contrib.auth.models import Group, User
APP='bajaj'
logger = logging.getLogger("gladminds")

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.upload_asc_with_rm_data()
    
    def register_user(self, group, username=None, phone_number=None,
                      first_name='', last_name='', email='', address='',
                      state='', pincode='', APP=APP):
        user_profile = get_model('UserProfile', APP)
        try:
            user_group = Group.objects.using(APP).get(name=group)
        except ObjectDoesNotExist as ex:
            user_group = Group.objects.using(APP).create(name=group)
            user_group.save(using=APP)
        if username:
            try:
                user_details = user_profile.objects.select_related('user').get(user__username=username)
            except ObjectDoesNotExist as ex:
                new_user = User(
                    username=username, first_name=first_name, last_name=last_name, email=email)
                if group =='customer':
                    password = settings.PASSWORD_POSTFIX
                else:
                    password = username + settings.PASSWORD_POSTFIX
                new_user.set_password(password)
                new_user.save(using=APP)
                new_user.groups.add(user_group)
                new_user.save(using=APP)
                logger.info(group + ' {0} registered successfully'.format(username))
                user_details = user_profile(user=new_user,
                                        phone_number=phone_number, address=address,
                                        state=state, pincode=pincode)
                user_details.save(using=APP)
            return user_details
        else:
            logger.info('{0} id is not provided.'.format(str(group)))
            raise Exception('{0} id is not provided.'.format(str(group)))   

    def upload_asc_with_rm_data(self):
        '''Uploads data of Dealers with their
           associated ASM and the RM'''
        print ''' Started uploading Area Service Manager data'''
        file_list = ['asm_data.csv']
        asm_list = []
        ASM = get_model('AreaSalesManager', APP)
        DEALER = get_model('Dealer', APP)
        RM = get_model('RegionalManager', APP)
        CH = get_model('CircleHead', APP)
        USER_PROFILE = get_model('UserProfile', APP)
        STATE = get_model('State', APP)
        
        for i in range(0, 1):
            with open(settings.PROJECT_DIR + '/upload_data/' + file_list[i], 'r') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                next(spamreader)
                for row_list in spamreader:
                    temp ={}
                    temp['state'] = row_list[0].strip()
                    temp['dealer_code'] = row_list[1].strip()
                    temp['dealer_name'] = row_list[2].strip()
                    temp['town'] = row_list[3].strip()  
                    temp['asm_name'] = row_list[4].strip()
                    temp['asm_email'] = row_list[5].strip()
                    temp['rm_name'] = row_list[6].strip()
                    temp['rm_email'] = row_list[7].strip()
                    temp['cr_name'] = row_list[8].strip()
                    temp['cr_email'] = row_list[9].strip()
                    asm_list.append(temp)                    
        
        for asm in asm_list:
            try:
                ch_object = CH.objects.using('bajaj').get(user__user__username=asm['cr_email'])
            except Exception as ex:
                cr_user_pro = self.register_user(Roles.CIRCLEHEADS,
                                                       username=asm['cr_email'],
                                                       email=asm['cr_email'],
                                                       first_name=asm['cr_name'])
                cr_object = CH(user=cr_user_pro)
                cr_object.save(using=APP)
                    
                
        for rm in asm_list:
            ch_object = CH.objects.using('bajaj').get(user__user__username=rm['cr_email'])
            try:
                rm_object = RM.objects.using('bajaj').get(user__user__username=rm['rm_email'])
            except Exception as ex:
                rm_user_pro = self.register_user(Roles.REGIONALMANAGERS,
                                                 username=rm['rm_email'],
                                                 email=rm['rm_email'],
                                                 first_name=rm['rm_name'])
                rm_object = RM(user=rm_user_pro, circle_head=ch_object)
                rm_object.save(using=APP)
                
        for asm in asm_list:
            rm_obj = RM.objects.using('bajaj').get(user__user__username=asm['rm_email'])
            try:
                asm_object = ASM.objects.using('bajaj').get(user__user__username=asm['asm_email'])
            except Exception as ex:
                try:
                    asm_user_pro = self.register_user(Roles.AREASALESMANAGERS,
                                                      username=asm['asm_email'],
                                                      email=asm['asm_email'],
                                                      first_name=asm['asm_name'])
                    asm_object = ASM(user=asm_user_pro, rm=rm_obj)
                    asm_object.save(using=APP)
                except Exception as ex:
                    print "Exception while creating area sales manager", ex, asm['asm_email']
                    
            if not asm_object.state.filter(state_name=asm['state']).exists():
                state_obj = STATE.objects.using('bajaj').get(state_name=asm['state'])
                asm_object.state.add(state_obj)
                asm_object.save(using=APP)
        
        for dealer in asm_list:
            asm_obj = ASM.objects.using('bajaj').get(user__user__username=dealer['asm_email'])
            try:
                dealer_obj = DEALER.objects.using('bajaj').get(dealer_id=dealer['dealer_code'])
                dealer_obj.sm = asm_obj
                dealer_obj.save()
            except Exception as ex:
                print "Creating dealer", ex
                