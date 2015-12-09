from datetime import datetime, timedelta
import logging

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from gladminds.core.model_fetcher import get_model
from gladminds.core.auth_helper import Roles


logger = logging.getLogger("gladminds")

class DealerManager(models.Manager):
    def active(self):
        return super(DealerManager, self).get_query_set().filter(user__user__is_active=1)

    def active_count(self):
        active_period = datetime.now() - timedelta(30)
        return super(DealerManager, self).get_query_set().filter(last_transaction_date__gte=active_period).count()

    def count(self):
        return super(DealerManager, self).get_query_set().all().count()

    def active_dealer(self, phone_number):
        return super(DealerManager, self).get_query_set().filter(user__phone_number=phone_number, user__status="Y")

class AuthorizedServiceCenterManager(models.Manager):
    def active_count(self):
        active_period = datetime.now() - timedelta(30)
        return super(AuthorizedServiceCenterManager, self).get_query_set().filter(last_transaction_date__gte=active_period).count()

    def count(self):
        return super(AuthorizedServiceCenterManager, self).get_query_set().all().count()


class ServiceAdvisorManager(models.Manager):
    def active(self, phone_number):
        return super(ServiceAdvisorManager, self).get_query_set().filter(user__phone_number=phone_number, status='Y')

    def count(self):
        return super(ServiceAdvisorManager, self).get_query_set().all().count()

    def active_count(self):
        return super(ServiceAdvisorManager, self).get_query_set().filter(status='Y').count()

    def active_under_dealer(self, dealer):
        return super(ServiceAdvisorManager, self).get_query_set().filter(dealer=dealer, status='Y')

    def active_under_asc(self, asc):
        return super(ServiceAdvisorManager, self).get_query_set().filter(asc=asc, status='Y')

    def get_dealer_asc_obj(self, reporter):
        service_advisor_obj = super(ServiceAdvisorManager, self).select_related('dealer, asc').get(user=reporter.user_profile)
        if service_advisor_obj.dealer:
            return service_advisor_obj.dealer.user
        else:
            return service_advisor_obj.asc.user


class CustomerTempRegistrationManager(models.Manager):
    def get_updated_customer_id(self, customer_id):
        if customer_id and customer_id.find('T') == 0:
            temp_customer_obj = super(CustomerTempRegistrationManager, self).get_query_set().filter(temp_customer_id=customer_id)
            if temp_customer_obj:
                customer_id = temp_customer_obj[0].product_data.customer_id
        return customer_id


class MemberManager(models.Manager):
    def get_mechanic(self, phone_number):
        return super(MemberManager, self).get_query_set().filter(user__phone_number=phone_number)


class SparePartUPCManager(models.Manager):
    
    def get_spare_parts(self, spare_product_codes,is_used=False):
        return super(SparePartUPCManager, self).get_query_set().filter(unique_part_code__in=spare_product_codes,is_used=is_used)

class SparePartPointManager(models.Manager):
    def get_part_number(self, valid_product_number, state):
        return super(SparePartPointManager, self).get_query_set().filter(part_number__in=valid_product_number, territory=state)
        

class RegisterUser():
    def register_user(self, group, username=None, phone_number=None,
                      first_name='', last_name='', email='', address='',
                      state='', pincode='', APP=None):
        user_profile = get_model('UserProfile', APP)
        logger.info('New {0} Registration with id - {1}'.format(group, username))
        try:
            user_group = Group.objects.using(APP).get(name=group)
        except ObjectDoesNotExist as ex:
            logger.info(
                "[Exception: new_ registration]: {0}"
                .format(ex))
            user_group = Group.objects.using(APP).create(name=group)
            user_group.save(using=APP)
        if username:
            try:
                user_details = user_profile.objects.select_related('user').get(user__username=username)
            except ObjectDoesNotExist as ex:
                logger.info(
                    "[Exception: new_ registration]: {0}"
                    .format(ex))    
                new_user = User(
                    username=username, first_name=first_name, last_name=last_name, email=email)
                if group =='customer':
                    password = settings.PASSWORD_POSTFIX
                elif len(username.split('@'))>1:
                    password = username.split('@')[0] + settings.ADMIN_PASSWORD_POSTFIX
                    new_user.is_staff = True
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
                user_details.save()
            return user_details
        else:
            logger.info('{0} id is not provided.'.format(str(group)))
            raise Exception('{0} id is not provided.'.format(str(group)))   
