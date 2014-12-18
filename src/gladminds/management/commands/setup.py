from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db.transaction import atomic
from django.contrib.auth.models import User, Permission, Group
from django.conf import settings
from gladminds.afterbuy.models import Consumer
from gladminds.core.auth_helper import AFTERBUY_GROUPS, add_user_to_group,\
    OTHER_GROUPS, Roles, GmApps, AFTERBUY_USER_MODELS, ALL_APPS
from django.contrib.contenttypes.models import ContentType
from gladminds.core.loaders.module_loader import get_model
from gladminds.management.commands.load_mech_data import Command as mech_cmd
from gladminds.management.commands.load_part_data import Command as part_cmd

_DEMO = GmApps.DEMO
_BAJAJ = GmApps.BAJAJ
_AFTERBUY = GmApps.AFTERBUY
_GM = GmApps.GM


_ALL_APPS = ALL_APPS

_AFTERBUY_ADMINS = [{'email':'karthik.rajagopalan@gladminds.co', 'username': 'karthik.rajagopalan', 'phone':'9741200991'},
                    {'email':'praveen.m@gladminds.co', 'username':'praveen.m', 'phone':'8867576306'}
                    ]

_AFTERBUY_SUPERADMINS = [{'email':'naveen.shankar@gladminds.co', 'username':'naveen.shankar', 'phone':'9880747576'},
                         {'email':'afterbuy@gladminds.co', 'username':'afterbuy', 'phone':'9999999999'}
                    ]

_BAJAJ_LOYALTY_SUPERADMINS = [('gladminds', '', 'gladminds!123'),
                              ('kumarashish@bajajauto.co.in', 'kumarashish@bajajauto.co.in',
                               'kumarashish!123')]
_BAJAJ_LOYALTY_NSM = [('rkrishnan@bajajauto.co.in', 'rkrishnan@bajajauto.co.in', 'rkrishnan!123', 'NSM002', 'south', 'Raghunath'),
                      ('rkrishnan@bajajauto.co.in', 'rkrishnan@bajajauto.co.in', 'rkrishnan!123', 'NSM002', 'west', 'Raghunath'),]
_BAJAJ_LOYALTY_ASM = [('spremnath@bajajauto.co.in', 'spremnath@bajajauto.co.in', 'spremnath!123', 'ASM004', 'PREM NATH', '+919176339712', 'Tamil Nadu'),
                      ('spremnath@bajajauto.co.in', 'spremnath@bajajauto.co.in', 'spremnath!123', 'ASM004', 'PREM NATH', '+919176339712', 'Karnataka')]

class Command(BaseCommand):

    def handle(self, *args, **options):
        call_command('syncdb', database=_DEMO, interactive=False)
        call_command('syncdb', database=_BAJAJ, interactive=False)
        call_command('syncdb', database=_AFTERBUY, interactive=False)
        call_command('syncdb', interactive=False)
        self.define_groups()
        self.create_admin(_DEMO)
        self.create_admin(_BAJAJ)
        self.create_admin(_GM)
        self.create_afterbuy_admins()
        self.create_bajaj_admins()
        self.set_afterbuy_permissions()
        self.upload_loyalty_user()
        self.upload_part_data()
        self.set_bajaj_permissions()

    def define_groups(self):
        for group in AFTERBUY_GROUPS:
            self.add_group(GmApps.AFTERBUY, group)

        for app in [GmApps.BAJAJ, GmApps.DEMO, GmApps.GM]:
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
    
    @atomic
    def create_bajaj_admins(self):
        from gladminds.bajaj.models import AreaSalesManager, NationalSalesManager
        for details in _BAJAJ_LOYALTY_SUPERADMINS:
            print "create loyalty superadmin", details
            self.create_user_profile(details, GmApps.BAJAJ, Roles.LOYALTYSUPERADMINS)
        for details in _BAJAJ_LOYALTY_NSM:
            print "create loyalty nsm", details
            profile_obj = self.create_user_profile(details, GmApps.BAJAJ, Roles.NSMS)
            try: 
                nsm_obj = NationalSalesManager.objects.get(user=profile_obj, nsm_id=details[3],
                                                           territory=details[4])
            except:
                nsm_obj = NationalSalesManager(user=profile_obj, nsm_id=details[3],
                                               name=details[5], email=details[0],
                                                           territory=details[4])
                nsm_obj.save()
        for details in _BAJAJ_LOYALTY_ASM:
            print "create loyalty asm", details
            profile_obj = self.create_user_profile(details, GmApps.BAJAJ, Roles.ASMS)
            if not AreaSalesManager.objects.filter(user=profile_obj, asm_id=details[3], state=details[6]).exists():
                asm_obj = AreaSalesManager(nsm=nsm_obj, user=profile_obj, asm_id=details[3],
                                             name=details[4], email=details[0],
                                             phone_number=details[5], state=details[6])
                asm_obj.save()

    def create_user_profile(self, details, app, group=None):
        users = User.objects.filter(username=details[0]).using(app)
        if len(users) > 0:
            admin = users[0]
        if len(users) == 0:
            admin = User.objects.using(app).create(username=details[0])
            admin.set_password(details[2])
            admin.is_staff = True
            admin.email = details[1]
            admin.save(using=app)
            if group:
                add_user_to_group(app, admin.id, group)
        user_profile_class = get_model('UserProfile', app)
        try:
            return user_profile_class.objects.get(user=admin.id)
        except:
            profile_obj = user_profile_class(user=admin)
            profile_obj.save()
            print "3333", profile_obj
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
        mech_data = mech_cmd()
        mech_data.handle()

    def upload_part_data(self):
        '''
        uploads parts data
        '''
        part_data = part_cmd()
        part_data.handle()

    def set_bajaj_permissions(self):
        brand = GmApps.BAJAJ
        for group in [Roles.ASMS, Roles.NSMS]:
            model_ids = []
            for model in ['Distributor', 'Retailer', 'Mechanic']:
                model_ids.append(ContentType.objects.get(app_label__in=['bajaj', 'auth'], model=model).id)
            permissions = Permission.objects.using(brand).filter(content_type__id__in=model_ids)
            group = Group.objects.using(brand).get(name=group)
            for permission in permissions:
                group.permissions.add(permission)
            model_ids = []
            for model in ['SparePartMasterData', 'SpareUPCData', 'SparePointData',
                          'AccumulationRequest']:
                model_ids.append(ContentType.objects.get(app_label__in=['bajaj', 'auth'], model=model).id)
            permissions = Permission.objects.using(brand).filter(content_type__id__in=model_ids,
                                                                 codename__contains='change_')
            for permission in permissions:
                group.permissions.add(permission)
            group.save(using=brand)
