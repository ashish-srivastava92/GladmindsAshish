'''Handlers for service desk logic'''
import logging
import datetime
import json
import os
import sys

from django.conf import settings
from django.contrib.auth.models import User

from gladminds.core import utils
from gladminds.core.constants import FEEDBACK_STATUS, PRIORITY, FEEDBACK_TYPE, ALL,\
    DEMO_PRIORITY
from gladminds.core.managers.audit_manager import sms_log
from gladminds.core.services import message_template as templates
from gladminds.sqs_tasks import send_coupon, send_sms,\
    send_servicedesk_feedback_detail
from gladminds.core.managers.mail import send_feedback_received, \
     send_servicedesk_feedback, send_dealer_feedback
from gladminds.core.auth_helper import Roles
from gladminds.core.utils import get_list_from_set, create_context, \
    set_wait_time
from gladminds.core.cron_jobs.queue_utils import get_task_queue,\
    send_job_to_queue
from gladminds.core.core_utils.date_utils import convert_utc_to_local_time, \
    get_time_in_seconds
from gladminds.core.managers import mail
from django.db.transaction import atomic
from gladminds.core.model_fetcher import get_model

import uuid
from gladminds.core.model_fetcher import models

LOG = logging.getLogger('gladminds')

TEMP_ID_PREFIX = settings.TEMP_ID_PREFIX
__all__ = ['GladmindsTaskManager']
AUDIT_ACTION = 'SEND TO QUEUE'


class SDActions():
    PRIORITY = 'changed priority'
    STATUS = 'changed status'
    ASSIGNEE = 'changed assignee'
    COMMENT = "added comment"
    COMMENT_UPDATE = "updated comment"
    DUE_DATE = "changed due_date"


def get_feedbacks(user, status, priority, type, search=None):
    feedbacks = []
    if type == ALL or type is None:
        type_filter = get_list_from_set(FEEDBACK_TYPE)
    else:
        type_filter = [type]

    if priority == ALL or priority is None:
        priority_filter = get_list_from_set(DEMO_PRIORITY)
    else:
        priority_filter = [priority]

    if status is None or status == 'active':
        status_filter = ['Open', 'Pending', 'In Progress']
    else:
        if status == ALL:
            status_filter = get_list_from_set(FEEDBACK_STATUS)
        else:
            status_filter = [status]
    
    sa_id_list = []
    if user.groups.filter(name=Roles.DEALERS).exists():
        sa_list = get_model('ServiceAdvisor').objects.active_under_dealer(user)
        if sa_list:
            for sa in sa_list:
                sa_id_list.append(sa.service_advisor_id)
        sa_id_list.append(user)
        feedbacks = get_model('Feedback').objects.filter(reporter__name__in=sa_id_list, status__in=status_filter,
                                                       priority__in=priority_filter, type__in=type_filter
                                                    ).order_by('-created_date')
                                                    
    if user.groups.filter(name=Roles.DEALERADMIN).exists():
        dealers = get_model('Dealer').objects.all()
        for dealer in dealers:
            sa_id_list.append(dealer.dealer_id)
        sa_id_list.append(user)
    feedbacks = get_model('Feedback').objects.filter(reporter__name__in=sa_id_list, status__in=status_filter,
                                                       priority__in=priority_filter, type__in=type_filter
                                                    ).order_by('-created_date')    
        
    if user.groups.filter(name=Roles.ASCS).exists():
        sa_list = get_model('ServiceAdvisor').objects.active_under_asc(user)
        sa_id_list = []
        if sa_list:
            for sa in sa_list:
                sa_id_list.append(sa.service_advisor_id)
        sa_id_list.append(user)
        feedbacks = get_model('Feedback').objects.filter(reporter__name__in=sa_id_list, status__in=status_filter,
                                                       priority__in=priority_filter, type__in=type_filter
                                                    ).order_by('-created_date')
    if user.groups.filter(name=Roles.SDMANAGERS).exists():
        feedbacks = get_model('Feedback').objects.filter(status__in=status_filter, priority__in=priority_filter,
                                                   type__in=type_filter).order_by('-created_date')
    if user.groups.filter(name=Roles.SDOWNERS).exists():
        user_profile = get_model('UserProfile').objects.filter(user=user)
        servicedesk_user = get_model('ServiceDeskUser').objects.filter(user_profile=user_profile[0])
        feedbacks = get_model('Feedback').objects.filter(assignee=servicedesk_user[0], status__in=status_filter,
                                                   priority__in=priority_filter, type__in=type_filter).order_by('-created_date')

    return feedbacks


def send_feedback_sms(template_name, phone_number, feedback_obj, comment_obj=None):
    created_date = convert_utc_to_local_time(feedback_obj.created_date)
    try:
        message = templates.get_template(template_name).format(
                                        type=feedback_obj.type,
                                        reporter=feedback_obj.reporter,
                                        message=feedback_obj.message,
                                        created_date=created_date,
                                        assign_to=feedback_obj.assign_to,
                                        priority=feedback_obj.priority)
        if comment_obj and template_name == 'SEND_MSG_TO_ASSIGNEE':
            message = message + 'Note :' + comment_obj.comments
    except Exception as ex:
        message = templates.get_template('SEND_INVALID_MESSAGE')
    finally:
        LOG.info("Send complain message received successfully with {0}".format(message))
        phone_number = utils.get_phone_number_format(phone_number)
        sms_log(settings.BRAND, receiver=phone_number, action=AUDIT_ACTION, message=message)
        send_job_to_queue(send_servicedesk_feedback_detail, {"phone_number":phone_number, "message":message, "sms_client":settings.SMS_CLIENT})
    return {'status': True, 'message': message}


def create_servicedesk_user(name, phone_number, email):
    user_profile = models.UserProfile.objects.filter(user__username=str(name))
    if len(user_profile) > 0:
        servicedesk_user = get_model('ServiceDeskUser').objects.filter(user_profile=user_profile[0])
        if servicedesk_user:
            servicedesk_user = servicedesk_user[0]
        else:
            servicedesk_user = get_model('ServiceDeskUser')(user_profile=user_profile[0], name=name)
            servicedesk_user.save(using=settings.BRAND)
    else:
        servicedesk_user = get_model('ServiceDeskUser')(name=name, phone_number=phone_number, email=email)
        servicedesk_user.save(using=settings.BRAND)

    return servicedesk_user


def create_feedback(sms_dict, phone_number, email, name, dealer_email, user, with_detail=False):
    ''' Save the feedback or complain from SA and sends SMS for successfully receive '''
    manager_obj = User.objects.get(groups__name=Roles.SDMANAGERS)
    try:
        servicedesk_user = create_servicedesk_user(name, phone_number, email)
        sub_category = get_model('DepartmentSubCategories').objects.get(id=sms_dict['sub-department'])
        
        if json.loads(sms_dict['sub-department-assignee']):
            sub_department_assignee = get_model('ServiceDeskUser').objects.filter(id=sms_dict['sub-department-assignee']) 
        
        else:
            sub_department_assignee = ''
             
        if len(sub_department_assignee)>0:
            gladminds_feedback_object = get_model('Feedback')(reporter=servicedesk_user,
                                                            type=sms_dict['type'],
                                                            summary=sms_dict['summary'], description=sms_dict['description'],
                                                            status="Open", created_date=datetime.datetime.now(), priority=sms_dict['priority'],
                                                            sub_department = sub_category, assignee=sub_department_assignee[0]
                                                            )
        else:
            gladminds_feedback_object = get_model('Feedback')(reporter=servicedesk_user,
                                                            type=sms_dict['type'],
                                                            summary=sms_dict['summary'], description=sms_dict['description'],
                                                            status="Open", created_date=datetime.datetime.now(), priority=sms_dict['priority'],
                                                            sub_department = sub_category                                                            
                                                            )
        gladminds_feedback_object.save(using=settings.BRAND)
        update_feedback_activities(gladminds_feedback_object, SDActions.STATUS, None,
                                   gladminds_feedback_object.status, user)
        if gladminds_feedback_object.assignee:
            date = set_due_date(sms_dict['priority'], gladminds_feedback_object)
            gladminds_feedback_object.due_date = date['due_date']
            gladminds_feedback_object.reminder_date = date['reminder_date'] 
            gladminds_feedback_object.save(using=settings.BRAND)

        if sms_dict['file_location']:
            file_obj = sms_dict['file_location']
            filename_prefix = gladminds_feedback_object.id
            filename_suffix = str(uuid.uuid4())
            ext = file_obj.name.split('.')[-1]
            file_obj.name = 'GM'+str(filename_prefix)+'_'+'_'+filename_suffix+'.'+ext
            destination = settings.SDFILE_DIR.format(settings.ENV)
            bucket = settings.SDFILE_BUCKET
            path = utils.upload_file(destination, bucket, file_obj, logger_msg="SDFile")
            gladminds_feedback_object.file_location = path
            gladminds_feedback_object.save(using=settings.BRAND)
        message = templates.get_template('SEND_RCV_FEEDBACK').format(type="feedback")
    except Exception as ex:
        LOG.error(ex)
        message = templates.get_template('SEND_INVALID_MESSAGE')
    finally:
        LOG.info("Send complain message received successfully with %s" % message)
        if phone_number:
            phone_number = utils.get_phone_number_format(phone_number)
            sms_log(settings.BRAND, receiver=phone_number, action=AUDIT_ACTION, message=message)
            LOG.info("[create_feedback]: {0}".format(settings.SMS_CLIENT))
            send_job_to_queue(send_servicedesk_feedback_detail, {"phone_number":phone_number, "message":message, "sms_client":settings.SMS_CLIENT})
        if dealer_email:
            context = utils.create_context('FEEDBACK_DETAIL_TO_DEALER', gladminds_feedback_object)
            send_dealer_feedback(context, dealer_email)
        context = utils.create_context('FEEDBACK_DETAIL_TO_ADIM', gladminds_feedback_object)
        send_feedback_received(context, manager_obj.email)
        context = utils.create_context('FEEDBACK_CONFIRMATION', gladminds_feedback_object)
        send_servicedesk_feedback(context, get_reporter_details(gladminds_feedback_object.reporter, "email"))
    return {'status': True, 'message': message}


def get_feedback(feedback_id, user):
    if user.groups.filter(name=Roles.SDOWNERS).exists():
        user_profile = get_model('UserProfile').objects.filter(user=user)
        servicedesk_user = get_model('ServiceDeskUser').objects.filter(user_profile=user_profile[0])
        return get_model('Feedback').objects.get(id=feedback_id, assignee=servicedesk_user[0])
    else:
        return get_model('Feedback').objects.get(id=feedback_id)

def get_servicedesk_users(designation):
    users = User.objects.filter(groups__name__in=designation)
    if len(users) > 0:
        user_list = get_model('UserProfile').objects.filter(user__in=users)
        return get_model('ServiceDeskUser').objects.filter(user_profile__in=user_list)
    else:
        LOG.info("No user with designation SDO exists")
        return None

def get_comments(feedback_id):
    comments = get_model('Comment').objects.filter(feedback_object_id=feedback_id)
    return comments


def set_due_date(priority, feedback_obj):
    '''
    Set all the dates as per SLA definition
    due_date = created_date + resolution_time
    reminder_date = due_date - reminder_time
    '''
    created_date = feedback_obj.created_date
    sla_obj = get_model('SLA').objects.get(priority=priority)
    total_seconds = get_time_in_seconds(sla_obj.resolution_time, sla_obj.resolution_unit)
    due_date = created_date + datetime.timedelta(seconds=total_seconds)
    total_seconds = get_time_in_seconds(sla_obj.reminder_time, sla_obj.reminder_unit)
    reminder_date = due_date - datetime.timedelta(seconds=total_seconds)
    return {'due_date':due_date, 'reminder_date':reminder_date}


def get_reporter_details(reporter, value="phone_number"):
    if value == "email":
        if reporter.email:
            return reporter.email
        else:
            return reporter.user_profile.user.email
    else:
        if reporter.phone_number:
            return reporter.phone_number
        else:
            return reporter.user_profile.phone_number


def send_mail_to_reporter(reporter_email_id, feedback_obj, template):
    context = create_context(template, feedback_obj)
    mail.send_email_to_initiator_when_due_date_is_changed(context, reporter_email_id)


def send_mail_to_dealer(feedback_obj, email_id, template):
    context = create_context(template, feedback_obj)
    mail.send_email_to_dealer_after_issue_assigned(context, email_id)


def update_feedback_activities(feedback, action, original_value, new_value, user):
    feedback_activity = get_model('Activity')(feedback=feedback, action=action, original_value=original_value,
                                        new_value=new_value, user=user)
    feedback_activity.save(using=settings.BRAND)


def get_dealer_asc_email(feedback_obj):
    user = feedback_obj.reporter.user_profile.user
    if user.groups.filter(name=Roles.SERVICEADVISOR).exists():
        dealer_asc_obj = get_model('ServiceAdvisor').objects.get_dealer_asc_obj(feedback_obj.reporter)
    else:
        dealer_asc_obj = get_model('UserProfile').objects.get(user=feedback_obj.reporter.user_profile.user)

    return dealer_asc_obj 


@atomic
def modify_feedback(feedback_obj, data, user, host):
    try:
        status = get_list_from_set(FEEDBACK_STATUS)
        comment_object = None
        assign_status = False
        pending_status = False
        reporter_email_id = get_reporter_details(feedback_obj.reporter, "email")
        reporter_phone_number = get_reporter_details(feedback_obj.reporter)
        previous_status = feedback_obj.status
        dealer_asc_obj = get_dealer_asc_email(feedback_obj)
        
        # check if status is pending
        if feedback_obj.status == status[4]:
            pending_status = True
     
        if feedback_obj.assignee:
            assign_number = feedback_obj.assignee.user_profile.phone_number
        else:
            assign_number = None
        assign = feedback_obj.assignee
        
        if data['status'] == status[0] and previous_status == (status[1] or status[2]):
            feedback_obj.fcr = False
    
        if feedback_obj.due_date:
            due_date = convert_utc_to_local_time(feedback_obj.due_date)
            feedback_obj.due_date = data['due_date']
            feedback_obj.due_date = datetime.datetime.strptime(data['due_date'], '%Y-%m-%d %H:%M:%S')
            feedback_obj.save(using=settings.BRAND)
            if due_date != feedback_obj.due_date:
                update_feedback_activities(feedback_obj, SDActions.DUE_DATE, due_date, feedback_obj.due_date, user)
                if reporter_email_id:
                    send_mail_to_reporter(reporter_email_id, feedback_obj, 'DUE_DATE_MAIL_TO_INITIATOR')
                else:
                    LOG.info("Reporter emailId not found.")
                    
                    if dealer_asc_obj.user.email:
                        send_mail_to_dealer(feedback_obj, dealer_asc_obj.user.email, 'DUE_DATE_MAIL_TO_DEALER')
                    else:
                        LOG.info("Dealer / Asc emailId not found.")
                if reporter_phone_number:
                    send_sms('INITIATOR_FEEDBACK_DUE_DATE_CHANGE', reporter_phone_number,
                     feedback_obj)
        
        if feedback_obj.priority:
            priority = feedback_obj.priority
            feedback_obj.priority = data['Priority']
            feedback_obj.save(using=settings.BRAND)
            if priority != feedback_obj.priority:
                due_date = feedback_obj.due_date
                date = set_due_date(data['Priority'], feedback_obj)
                feedback_obj.due_date = date['due_date']
                feedback_obj.reminder_date = date['reminder_date'] 
                feedback_obj.save(using=settings.BRAND)
                update_feedback_activities(feedback_obj, SDActions.PRIORITY, priority, feedback_obj.priority, user)
                update_feedback_activities(feedback_obj, SDActions.DUE_DATE, due_date, feedback_obj.due_date, user)
                if due_date != convert_utc_to_local_time(feedback_obj.due_date):
                    if reporter_email_id:
                        send_mail_to_reporter(reporter_email_id, feedback_obj, 'DUE_DATE_MAIL_TO_INITIATOR')
                else:
                    LOG.info("Reporter emailId not found.")
                    if dealer_asc_obj.user.email:
                        send_mail_to_dealer(feedback_obj, dealer_asc_obj.user.email, 'DUE_DATE_MAIL_TO_DEALER')
                    else:
                        LOG.info("Dealer / Asc emailId not found.")
                if reporter_phone_number:
                    send_sms('INITIATOR_FEEDBACK_DUE_DATE_CHANGE', reporter_phone_number,
                     feedback_obj)
            
        if assign is None:
            assign_status = True
        if data['assign_to'] == '':
            feedback_obj.status = data['status']
            feedback_obj.priority = data['Priority']
            feedback_obj.assignee = None
         
        else:
            if json.loads(data.get('reporter_status')):
                feedback_obj.previous_assignee = feedback_obj.assignee
                feedback_obj.assign_to_reporter = True
                feedback_obj.assignee = feedback_obj.reporter
                
            else:
                if data['assign_to'] :
                    servicedesk_user = get_model('ServiceDeskUser').objects.filter(user_profile__user__username=str(data['assign_to']))
                    feedback_obj.assignee = servicedesk_user[0]
                    feedback_obj.assign_to_reporter = False
            feedback_obj.status = data['status']
            feedback_obj.priority = data['Priority']
    
        # check if status is pending
        if data['status'] == status[4]:
            feedback_obj.pending_from = datetime.datetime.now()
        
        # check if status is progress
        if data['status'] == status[3]:
            if previous_status == 'Pending':
                feedback_obj.assignee = feedback_obj.previous_assignee
        
        # check if status is closed
        if data['status'] == status[1]:
            feedback_obj.closed_date = datetime.datetime.now()
        feedback_obj.save(using=settings.BRAND)
    
        if assign_status and feedback_obj.assignee:
            feedback_obj.previous_assignee = feedback_obj.assignee
            feedback_obj.assignee_created_date = datetime.datetime.now()
            date = set_due_date(data['Priority'], feedback_obj)
            feedback_obj.due_date = date['due_date']
            feedback_obj.reminder_date = date['reminder_date'] 
            feedback_obj.save(using=settings.BRAND)
            update_feedback_activities(feedback_obj, SDActions.STATUS, None, data['status'], user)
            context = create_context('INITIATOR_FEEDBACK_MAIL_DETAIL',
                                     feedback_obj)
            if reporter_email_id:
                mail.send_email_to_initiator_after_issue_assigned(context,
                                                             reporter_email_id)
            else:
                LOG.info("Reporter emailId not found.")
                if dealer_asc_obj.user.email:
                    context = create_context('INITIATOR_FEEDBACK_MAIL_DETAIL_TO_DEALER',
                                     feedback_obj)
                    mail.send_email_to_dealer_after_issue_assigned(context,
                                                             dealer_asc_obj.user.email)
                else:
                    LOG.info("Dealer / Asc emailId not found.")
            if reporter_phone_number:
                send_sms('INITIATOR_FEEDBACK_DETAILS', reporter_phone_number,
                     feedback_obj)
    
        if data['comments']:
            comment_object = get_model('Comment')(
                                            comment=data['comments'],
                                            user=user, created_date=datetime.datetime.now(),
                                            modified_date=datetime.datetime.now(),
                                            feedback_object=feedback_obj)
            comment_object.save(using=settings.BRAND)
            update_feedback_activities(feedback_obj, SDActions.COMMENT, None, data['comments'], user)
    
    # check if status is resolved
        if feedback_obj.status == status[2]:
            if previous_status == status[0]:
                feedback_obj.fcr = True
            servicedesk_obj_all = User.objects.filter(groups__name=Roles.SDMANAGERS)
            feedback_obj.resolved_date = datetime.datetime.now()
            feedback_obj.resolved_date = datetime.datetime.now()
            feedback_obj.root_cause = data['rootcause']
            feedback_obj.resolution = data['resolution']
            feedback_obj.save(using=settings.BRAND)
            comments = get_model('Comment').objects.filter(feedback_object=feedback_obj.id).order_by('-created_date')
            if reporter_email_id:
                context = create_context('INITIATOR_FEEDBACK_RESOLVED_MAIL_DETAIL',
                                      feedback_obj, comments[0])
                mail.send_email_to_initiator_after_issue_resolved(context,
                                                              feedback_obj, host, reporter_email_id)
            else:
                LOG.info("Reporter emailId not found.")
                if dealer_asc_obj.user.email:
                    context = create_context('FEEDBACK_RESOLVED_MAIL_TO_DEALER',
                                     feedback_obj)
                    mail.send_email_to_dealer_after_issue_assigned(context,
                                                             dealer_asc_obj.user.email)
                else:
                    LOG.info("Dealer / Asc emailId not found.")
    
            context = create_context('TICKET_RESOLVED_DETAIL_TO_BAJAJ',
                                     feedback_obj)
            mail.send_email_to_brand_after_issue_resolved(context)
            context = create_context('TICKET_RESOLVED_DETAIL_TO_MANAGER',
                                     feedback_obj)
            mail.send_email_to_manager_after_issue_resolved(context, servicedesk_obj_all[0])
            if reporter_phone_number:
                send_sms('INITIATOR_FEEDBACK_STATUS', reporter_phone_number,
                     feedback_obj)
        
        if previous_status != feedback_obj.status:
            update_feedback_activities(feedback_obj, SDActions.STATUS, previous_status, feedback_obj.status, user)
            
        if pending_status:
            set_wait_time(feedback_obj)
     
        if feedback_obj.assignee:
            if assign_number != feedback_obj.assignee.user_profile.phone_number:
                update_feedback_activities(feedback_obj, SDActions.ASSIGNEE, assign_number,
                                           feedback_obj.assignee.user_profile.phone_number, user)
                context = create_context('ASSIGNEE_FEEDBACK_MAIL_DETAIL',
                                          feedback_obj)
                mail.send_email_to_assignee(context, feedback_obj.assignee.user_profile.user.email)
                send_sms('SEND_MSG_TO_ASSIGNEE',
                         feedback_obj.assignee.user_profile.phone_number,
                         feedback_obj, comment_object)
        return True

    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        error = "{0} {1} {2}".format(exc_type, fname, exc_tb.tb_lineno)
        LOG.error('Exception while modifying ticket details : {0} {1}'.format(ex, error))
        return False
