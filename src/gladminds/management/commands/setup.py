from datetime import datetime 
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db.transaction import atomic
from django.contrib.auth.models import User, Permission, Group
from django.conf import settings
from gladminds.afterbuy.models import Consumer
from gladminds.core.auth_helper import AFTERBUY_GROUPS, add_user_to_group,\
    OTHER_GROUPS, Roles, GmApps, AFTERBUY_USER_MODELS, ALL_APPS, ALL_BRANDS
from django.contrib.contenttypes.models import ContentType
from gladminds.core.model_fetcher import get_model
from gladminds.management.commands.load_state import Command as state_cmd
from gladminds.management.commands.load_mech_data import Command as mech_cmd
from gladminds.management.commands.load_part_data import Command as part_cmd
from gladminds.management.commands.load_asc_with_asm import Command as asm_cmd
from gladminds.management.commands.load_sbom_data import Command as sbom_cmd
from gladminds.management.commands.load_asm_with_rm import Command as sm_cmd


_DEMO = GmApps.DEMO
_BAJAJ = GmApps.BAJAJ
_AFTERBUY = GmApps.AFTERBUY
_GM = GmApps.GM
_BAJAJCV = GmApps.BAJAJCV
_DAIMLER = GmApps.DAIMLER
_PROBIKING = GmApps.PROBIKING
_BAJAJIB = GmApps.BAJAJIB
_MECHANEED = GmApps.MECHANEED

_ALL_APPS = ALL_APPS

_AFTERBUY_ADMINS = [{'email':'karthik.rajagopalan@gladminds.co', 'username': 'karthik.rajagopalan', 'phone':'9741200991'},
                    {'email':'praveen.m@gladminds.co', 'username':'praveen.m', 'phone':'8867576306'}
                    ]

_AFTERBUY_SUPERADMINS = [{'email':'naveen.shankar@gladminds.co', 'username':'naveen.shankar', 'phone':'9880747576'},
                         {'email':'afterbuy@gladminds.co', 'username':'afterbuy', 'phone':'9999999999'}
                    ]
_BAJAJ_LOYALTY_TERRITORY = ['North', 'South', 'East', 'West']
_BAJAJ_LOYALTY_SUPERADMINS = [('gladminds', '', 'gladminds!123', ''),
                              ('rkjena@bajajauto.co.in', 'rkjena@bajajauto.co.in', 'rkjena!123', 'Rajib Kumar Jena'),
                              ('ipattabhi@bajajauto.co.in', 'ipattabhi@bajajauto.co.in', 'ipattabhi!123', 'I Pattabhiramaswamy'),
                              ('adubey@bajajauto.co.in', 'adubey@bajajauto.co.in', 'adubey!123', 'Awadesh Dubey')]

_BAJAJ_LOYALTY_ADMINS = [('kumarashish@bajajauto.co.in', 'kumarashish@bajajauto.co.in','kumarashish!123', ''),
                         ('dhazarika@bajajauto.co.in', 'dhazarika@bajajauto.co.in','dhazarika!123', 'Debaranjan Hazarika'),]

_BAJAJ_LOYALTY_NSM = [('rkrishnan@bajajauto.co.in', 'rkrishnan@bajajauto.co.in', 'rkrishnan!123', 'NSM002', 'South', 'Raghunath'),
                      ('ssaha@bajajauto.co.in', 'ssaha@bajajauto.co.in', 'ssaha!123', 'NSM003', 'North', 'Sourav Saha')]

_BAJAJ_LOYALTY_ASM = [('prajurkar@bajajauto.co.in', 'prajurkar@bajajauto.co.in', 'spremnath!123', 'ASM004', 'PREM NATH', '+919176339712', 'Tamil Nadu'),
                      ('pgpooyath@bajajauto.co.in', 'pgpooyath@bajajauto.co.in', 'pgpooyath!123', 'ASM005', 'PRAVEEN G POOYATH', '+918111973444', 'Karnataka'),
                      ('abanerjee@bajajauto.co.in', 'abanerjee@bajajauto.co.in', 'abanerjee!123', 'ASM006', 'Abhijeet Banerjee', '', 'West Bengal'),
                      ('harpreetsingh@bajajauto.co.in', 'harpreetsingh@bajajauto.co.in', 'harpreetsingh!123', 'ASM007', 'HARPREET SINGH', '', 'Karnataka'),
                      ('rmishra@bajajauto.co.in', 'rmishra@bajajauto.co.in', 'rmishra!123', 'ASM008', 'RATNESH MISHRA', '', 'Karnataka'),
                      ('crnarendra@bajajauto.co.in', 'crnarendra@bajajauto.co.in', 'crnarendra!123', 'ASM009', 'CR NARENDRA', '', 'Karnataka'),
                      ('achinjain@bajajauto.co.in', 'achinjain@bajajauto.co.in', 'achinjain!123', 'ASM0010', 'ACHIN JAIN', '', 'Karnataka'),]

class Command(BaseCommand):

    def handle(self, *args, **options):
        call_command('syncdb', database=_DEMO, interactive=False)
        call_command('syncdb', database=_BAJAJ, interactive=False)
        call_command('syncdb', database=_AFTERBUY, interactive=False)
        call_command('syncdb', database=_BAJAJCV, interactive=False)
        call_command('syncdb', database=_DAIMLER, interactive=False)
        call_command('syncdb', database=_PROBIKING, interactive=False)
        call_command('syncdb', database=_BAJAJIB, interactive=False)
        call_command('syncdb', database=_MECHANEED, interactive=False)
        call_command('syncdb', interactive=False)
        self.define_groups()
        self.upload_state()
        self.create_admin(_DEMO)
        self.create_admin(_BAJAJ)
        self.create_admin(_GM)
        self.create_admin(_BAJAJCV)
        self.create_admin(_DAIMLER)
        self.create_admin(_PROBIKING)
        self.create_admin(_BAJAJIB)
        self.create_admin(_MECHANEED)
        self.create_afterbuy_admins()
        self.create_territory()
        self.create_loyalty_admins()
        self.set_afterbuy_permissions()
#         if settings.ENV not in ['prod', 'staging', 'qa']:
#             self.upload_loyalty_user()
#             self.upload_asm_user()
#             self.upload_part_data()
#             self.upload_sbom_data()
#             self.upload_asm_with_rm()
        for brand in ALL_BRANDS:
            self.set_brand_permissions(brand)
            
    def upload_state(self):
        '''
        Uploads state
        '''
        try:
            state_data = state_cmd()
            state_data.handle()
        except Exception as ex:
            print "[upload_state]: ", ex

    def define_groups(self):
        for group in AFTERBUY_GROUPS:
            self.add_group(GmApps.AFTERBUY, group)

        for app in [GmApps.BAJAJ, GmApps.DEMO, GmApps.GM, GmApps.DAIMLER, GmApps.BAJAJCV, GmApps.PROBIKING, GmApps.BAJAJIB, GmApps.MECHANEED]:
            for group in OTHER_GROUPS:
                self.add_group(app, group)

        for app in _ALL_APPS:
            ignore_list = []
            for ap in _ALL_APPS:
                if app != ap:
                    ignore_list.append(ap)
            Permission.objects.filter(content_type__app_label__in=ignore_list).using(app).delete()

    def add_group(self, app, group):
        group_count = Group.objects.filter(name=group).using(app).count()
        if group_count == 0:
            group_obj = Group(name=group)
            group_obj.save(using=app)

    def create_admin(self, app):
        name = settings.ADMIN_DETAILS[app]['user']
        password = settings.ADMIN_DETAILS[app]['password']

        user = User.objects.filter(username=name).using(app).count()
        if user == 0:
            admin = User.objects.using(app).create(username=name)
            admin.set_password(password)
            admin.is_superuser = True
            admin.is_staff = True
            admin.save(using=app)
            add_user_to_group(app, admin.id, Roles.SUPERADMINS)
    
    def create_afterbuy_admins(self):
        for details in _AFTERBUY_ADMINS:
            self.create_consumer(details, Roles.ADMINS)
        for details in _AFTERBUY_SUPERADMINS:
            self.create_consumer(details, Roles.SUPERADMINS)
            
    def create_territory(self):
        from gladminds.core.models import Territory
        for territory in _BAJAJ_LOYALTY_TERRITORY:
            try:
                territory_obj = Territory.objects.using(GmApps.BAJAJCV).get(territory=territory)
            except:
                territory_obj = Territory(territory=territory)
                territory_obj.save(using=GmApps.BAJAJCV)
        
    
    @atomic
    def create_loyalty_admins(self):
        from gladminds.core.models import AreaSparesManager, NationalSparesManager, Territory, State
        try:
            for details in _BAJAJ_LOYALTY_SUPERADMINS:
                print "create loyalty superadmin", details
                self.create_user_profile(details, GmApps.BAJAJCV, Roles.LOYALTYSUPERADMINS)
            for details in _BAJAJ_LOYALTY_NSM:
                print "create loyalty nsm", details
                profile_obj = self.create_user_profile(details, GmApps.BAJAJCV, Roles.NATIONALSPARESMANAGERS)
                try: 
                    nsm_obj = NationalSparesManager.objects.using(GmApps.BAJAJCV).get(user=profile_obj, nsm_id=details[3])
                except:
                    
                    nsm_obj = NationalSparesManager(created_date=datetime.now(),
                                                    user=profile_obj, nsm_id=details[3],
                                                   name=details[5], email=details[0])
                    nsm_obj.save(using=GmApps.BAJAJCV)
                    territory = Territory.objects.using(GmApps.BAJAJCV).get(territory=details[4])
                    nsm_obj.territory.add(territory)
                    nsm_obj.save(using=GmApps.BAJAJCV)
            for details in _BAJAJ_LOYALTY_ASM:
                print "create loyalty asm", details
                profile_obj = self.create_user_profile(details, GmApps.BAJAJCV, Roles.AREASPARESMANAGERS)
                if not AreaSparesManager.objects.using(GmApps.BAJAJCV).filter(user=profile_obj, asm_id=details[3]).exists():
                    state = State.objects.using(GmApps.BAJAJCV).get(state_name=details[6])
                    asm_obj = AreaSparesManager(nsm=nsm_obj, user=profile_obj, asm_id=details[3],
                                                 name=details[4], email=details[0],
                                                 phone_number=details[5])
                    asm_obj.save(using=GmApps.BAJAJCV)
                    asm_obj.state.add(state)
                    asm_obj.save(using=GmApps.BAJAJCV)
        except Exception as ex:
            print "[create_bajaj_admins]: ", ex
            
    def create_user_profile(self, details, app, group=None):
        users = User.objects.filter(username=details[0]).using(app)
        if len(users) > 0:
            admin = users[0]
        if len(users) == 0:
            admin = User.objects.using(app).create(username=details[0])
            admin.set_password(details[2])
            admin.is_staff = True
            admin.email = details[1]
            admin.first_name = details[3]
            admin.save(using=app)
            if group:
                add_user_to_group(app, admin.id, group)
        user_profile_class = get_model('UserProfile', app)
        try:
            return user_profile_class.objects.get(user=admin.id)
        except:
            profile_obj = user_profile_class(created_date=datetime.now(), user=admin)
            profile_obj.save()
            return profile_obj

    def create_consumer(self, details, group):
        app = GmApps.AFTERBUY
        username = details['username']
        phone = details['phone']
        email = details['email']
        password = settings.ADMIN_DETAILS[app]['password']

        user = User.objects.filter(username=username).using(app).count()
        if user == 0:
            admin = User.objects.using(app).create(username=username)
            admin.set_password(password)
            admin.is_superuser = True
            admin.is_staff = True
            admin.email = email
            admin.save(using=app)
            Consumer(user=admin, phone_number=phone, is_email_verified=True).save()
            add_user_to_group(app, admin.id, group)

    def set_afterbuy_permissions(self):
        model_ids = []
        for model in AFTERBUY_USER_MODELS:
            model_ids.append(ContentType.objects.get(app_label__in=['afterbuy', 'auth'], model=model).id)
        permissions = Permission.objects.using(GmApps.AFTERBUY).filter(content_type__id__in=model_ids)
        group = Group.objects.using(GmApps.AFTERBUY).get(name=Roles.USERS)
        for permission in permissions:
            group.permissions.add(permission)
        group.save(using=GmApps.AFTERBUY)

        permissions = Permission.objects.using(GmApps.AFTERBUY).all()
        group1 = Group.objects.using(GmApps.AFTERBUY).get(name=Roles.ADMINS)
        group2 = Group.objects.using(GmApps.AFTERBUY).get(name=Roles.SUPERADMINS)
        for permission in permissions:
            group1.permissions.add(permission)
            group2.permissions.add(permission)
        group1.save(using=GmApps.AFTERBUY)
        group2.save(using=GmApps.AFTERBUY)

    def upload_loyalty_user(self):
        '''
        Uploads distributor and mechanic data
        '''
        try:
            mech_data = mech_cmd()
            mech_data.handle()
        except Exception as ex:
            print "[upload_loyalty_user]: ", ex
    
    def upload_asm_user(self):
        '''
        Uploads distributor and mechanic data
        '''
        try:
            asm_data = asm_cmd()
            asm_data.handle()
        except Exception as ex:
            print "[upload_asm_user]: ", ex
    
    def upload_asm_with_rm(self):
        ''' Upload asm with rm data'''
        try:
            asm_data = sm_cmd()
            asm_data.handle()
        except Exception as ex:
            print "[Upload sales manager ]:", ex
    def upload_sbom_data(self):
        '''
        Uploads distributor and mechanic data
        '''
        try:
            sbom_data = sbom_cmd()
            sbom_data.handle()
        except Exception as ex:
            print "[upload_sbom_data]: ", ex

    def upload_part_data(self):
        '''
        uploads parts data
        '''
        try:
            part_data = part_cmd()
            part_data.handle()
        except Exception as ex:
            print "[upload_part_data]: ", ex
    
    def set_brand_permissions(self, brand):
        try:
            for group in [Roles.AREASPARESMANAGERS, Roles.NATIONALSPARESMANAGERS]:
                model_ids = []
                for model in ['Distributor', 'Retailer', 'Member']:
                    model_ids.append(ContentType.objects.get(app_label__in=[brand, 'auth'], model=model).id)
                permissions = Permission.objects.using(brand).filter(content_type__id__in=model_ids)
                group = Group.objects.using(brand).get(name=group)
                for permission in permissions:
                    group.permissions.add(permission)
                model_ids = []
                for model in ['SparePartMasterData', 'SparePartUPC', 'SparePartPoint',
                              'AccumulationRequest']:
                    model_ids.append(ContentType.objects.get(app_label__in=[brand, 'auth'], model=model).id)
                permissions = Permission.objects.using(brand).filter(content_type__id__in=model_ids,
                                                                     codename__contains='change_')
                for permission in permissions:
                    group.permissions.add(permission)
                group.save(using=brand)
        except Exception as ex:
            print "[set_brand_permissions]: ", ex
