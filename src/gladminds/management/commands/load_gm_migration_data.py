import os
import json
import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.conf import settings

from gladminds.bajaj import models as common
from gladminds.bajaj.services.coupons import import_feed
from gladminds.core.auth_helper import ALL_APPS, Roles
from gladminds.core.model_fetcher import get_model


ALL_APPS = ALL_APPS + ['bajajib']
BASIC_FEED = import_feed.BaseFeed()
TODAY = datetime.datetime.now()

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        self.add_sms_template()
        self.add_email_template()
        self.add_constants()

    def add_group(self):
        '''Upload data of the groups'''
        print "Loading groups..."
        file_path = os.path.join(settings.PROJECT_DIR, 'template_data/group.json')
        groups = json.loads(open(file_path).read())
        Group.objects.all().delete()
        for group in groups:
            group = Group(id=group['fields']["id"],name=group['fields']["name"])
            group.save()
        print "Loaded groups..."

    def add_sms_template(self):
        '''Upload data of the SMS template'''
        print "Loading sms template..."
        file_path = os.path.join(settings.PROJECT_DIR, 'template_data/template.json')
        message_templates = json.loads(open(file_path).read())
        for app in ALL_APPS:
            mt = get_model('MessageTemplate', app)
            for message_temp in message_templates:
                fields = message_temp['fields']
                temp_obj=mt.objects.using(app).filter(template=fields['template'])
                if not temp_obj:
                    temp_obj = mt(id=message_temp['pk'], created_date=TODAY, template_key=fields['template_key']\
                               , template=fields['template'], description=fields['description'])
                    temp_obj.save(using=app)
            print "Loaded sms template..."
    
    def add_email_template(self):
        '''Upload data of the Email template'''
        print "Loading email template..."
        file_path = os.path.join(settings.PROJECT_DIR, 'template_data/email_template.json')
        email_templates = json.loads(open(file_path).read())
        for app in ALL_APPS:
            et = get_model('EmailTemplate', app)
            for email_temp in email_templates:
                fields = email_temp['fields']
                temp_obj=et.objects.using(app).filter(template_key=fields['template_key'])
                if not temp_obj:
                    temp_obj = et(id=email_temp['pk'], created_date=TODAY, template_key=fields['template_key']\
                               , sender=fields['sender'], receiver=fields['receiver'],\
                                subject=fields['subject'], body=fields['body'],\
                                description=fields['description'])
                    temp_obj.save(using=app)
            print "Loaded email template..."  
        
    def add_constants(self):
        '''Upload data of the Constants'''
        print "Loading constants.."
        file_path = os.path.join(settings.PROJECT_DIR, 'template_data/constant.json')
        constants = json.loads(open(file_path).read())
        for app in ALL_APPS:
            cons = get_model('Constant', app)
            for constant in constants:
                fields = constant['fields']
                temp_obj = cons.objects.using(app).filter(constant_name=fields['constant_name'])
                if not temp_obj:
                    temp_obj = cons(id=constant['pk'], created_date=TODAY, constant_name=fields['constant_name'],constant_value=fields['constant_value'])
                    temp_obj.save(using=app)
                    if 'country_name' in fields.keys():
                        country_obj = get_model('Country', app).objects.filter(name=fields['country_name'])
                        if not country_obj:
                            country_obj = get_model('Country', app)(name=fields['country_name'],
                                                                    area_code=fields['country_code'])
                            country_obj.save(using=app)
                        else:
                            country_obj = country_obj[0]

                        temp_obj.country = country_obj
                        temp_obj.save(using=app)
                             
            print "Loaded constants..."
