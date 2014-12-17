import logging
import datetime
import json
from gladminds.bajaj import models as models
from gladminds.core.exceptions import DataNotFoundError
from gladminds.core.utils import create_context, get_list_from_set, set_wait_time
from gladminds.core.core_utils.date_utils import get_start_and_end_date, convert_utc_to_local_time, \
    get_time_in_seconds
from gladminds.core.managers import mail
from gladminds.core.constants import FEEDBACK_STATUS, PRIORITY, FEEDBACK_TYPE, \
    TIME_FORMAT
from django.contrib.auth.models import Group, User
from gladminds.sqs_tasks import send_sms
from gladminds.core.auth_helper import Roles

logger = logging.getLogger('gladminds')

def get_feedback(feedback_id, user):
    if user.groups.filter(name=Roles.SDOWNERS).exists():
        user_profile = models.UserProfile.objects.filter(user=user)
        servicedesk_user = models.ServiceDeskUser.objects.filter(user_profile=user_profile[0])
        return models.Feedback.objects.get(id=feedback_id, assignee=servicedesk_user[0])
    else:
        return models.Feedback.objects.get(id=feedback_id)

def get_servicedesk_users(designation):
    users = User.objects.filter(groups__name=designation)
    if len(users)>0:
        user_list = models.UserProfile.objects.filter(user__in=users)
        return models.ServiceDeskUser.objects.filter(user_profile__in=user_list)
    else:
        logger.info("No user with designation SDO exists")
        return None

def get_comments(feedback_id):
    comments = models.Comment.objects.filter(feedback_object_id=feedback_id)
    return comments

def set_due_date(priority, feedback_obj):
    '''
    Set all the dates as per SLA definition
    due_date = created_date + resolution_time
    reminder_date = due_date - reminder_time
    '''
    created_date = feedback_obj.created_date
    sla_obj = models.SLA.objects.get(priority=priority)
    total_seconds = get_time_in_seconds(sla_obj.resolution_time, sla_obj.resolution_unit)
    due_date = created_date + datetime.timedelta(seconds=total_seconds)
    total_seconds = get_time_in_seconds(sla_obj.reminder_time, sla_obj.reminder_unit)
    reminder_date = due_date-datetime.timedelta(seconds=total_seconds)
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

def update_feedback_activities(feedback):
    
def save_update_feedback(feedback_obj, data, user, host):
    status = get_list_from_set(FEEDBACK_STATUS)
    comment_object = None
    assign_status = False
    pending_status = False
    reporter_email_id = get_reporter_details(feedback_obj.reporter,"email")
    reporter_phone_number = get_reporter_details(feedback_obj.reporter)
    previous_status = feedback_obj.status
    
    #check if status is pending
    if feedback_obj.status == status[4]:
        pending_status = True
 
    if feedback_obj.assignee:
        assign_number = feedback_obj.assignee.user_profile.phone_number
    else:
        assign_number = None
    assign = feedback_obj.assignee
    
    if feedback_obj.due_date:
        due_date = convert_utc_to_local_time(feedback_obj.due_date)
        feedback_obj.due_date = data['due_date']
        feedback_obj.due_date = datetime.datetime.strptime(data['due_date'], '%Y-%m-%d %H:%M:%S')
        feedback_obj.save()
        if due_date != feedback_obj.due_date:
            if reporter_email_id:
                send_mail_to_reporter(reporter_email_id, feedback_obj, 'DUE_DATE_MAIL_TO_INITIATOR')
            else:
                logger.info("Reporter emailId not found.")
                dealer_asc_obj = models.ServiceAdvisor.objects.get_dealer_asc_obj(feedback_obj.reporter)
                if dealer_asc_obj.user.user.email:
                    send_mail_to_dealer(feedback_obj, dealer_asc_obj.user.user.email, 'DUE_DATE_MAIL_TO_DEALER')
                else:
                    logger.info("Dealer / Asc emailId not found.")

            send_sms('INITIATOR_FEEDBACK_DUE_DATE_CHANGE', reporter_phone_number,
                 feedback_obj)
    
    if feedback_obj.priority:
        priotity = feedback_obj.priority
        feedback_obj.priority = data['Priority']
        feedback_obj.save()
        if priotity != feedback_obj.priority:
            due_date = feedback_obj.due_date
            date = set_due_date(data['Priority'], feedback_obj)
            feedback_obj.due_date = date['due_date']
            feedback_obj.reminder_date = date['reminder_date'] 
            feedback_obj.save()
            if due_date != convert_utc_to_local_time(feedback_obj.due_date):
                if reporter_email_id:
                    send_mail_to_reporter(reporter_email_id, feedback_obj, 'DUE_DATE_MAIL_TO_INITIATOR')
            else:
                logger.info("Reporter emailId not found.")
                dealer_asc_obj = models.ServiceAdvisor.objects.get_dealer_asc_obj(feedback_obj.reporter)
                if dealer_asc_obj.user.user.email:
                    send_mail_to_dealer(feedback_obj, dealer_asc_obj.user.user.email, 'DUE_DATE_MAIL_TO_DEALER')
                else:
                    logger.info("Dealer / Asc emailId not found.")
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
                servicedesk_user = models.ServiceDeskUser.objects.filter(user_profile__phone_number=data['assign_to'])
                feedback_obj.assignee = servicedesk_user[0]
                feedback_obj.assign_to_reporter = False
        feedback_obj.status = data['status']
        feedback_obj.priority = data['Priority']

    #check if status is pending
    if data['status'] == status[4]:
        feedback_obj.pending_from = datetime.datetime.now()
    
    #check if status is progress
    if data['status'] == status[3]:
        if previous_status == 'Pending':
            feedback_obj.assignee = feedback_obj.previous_assignee
    
    #check if status is closed
    if data['status'] == status[1]:
        feedback_obj.closed_date = datetime.datetime.now()
    feedback_obj.save()

    if assign_status and feedback_obj.assignee:
        feedback_obj.previous_assignee = feedback_obj.assignee
        feedback_obj.assignee_created_date = datetime.datetime.now()
        date = set_due_date(data['Priority'], feedback_obj)
        feedback_obj.due_date = date['due_date']
        feedback_obj.reminder_date = date['reminder_date'] 
        feedback_obj.save()
        context = create_context('INITIATOR_FEEDBACK_MAIL_DETAIL',
                                 feedback_obj)
        if reporter_email_id:
            mail.send_email_to_initiator_after_issue_assigned(context,
                                                         reporter_email_id)
        else:
            logger.info("Reporter emailId not found.")
            dealer_asc_obj = models.ServiceAdvisor.objects.get_dealer_asc_obj(feedback_obj.reporter)
            if dealer_asc_obj.user.user.email:
                context = create_context('INITIATOR_FEEDBACK_MAIL_DETAIL_TO_DEALER',
                                 feedback_obj)
                mail.send_email_to_dealer_after_issue_assigned(context,
                                                         dealer_asc_obj.user.user.email)
            else:
                logger.info("Dealer / Asc emailId not found.")

        send_sms('INITIATOR_FEEDBACK_DETAILS', reporter_phone_number,
                 feedback_obj)

    if data['comments']:
        comment_object = models.Comment(
                                        comment=data['comments'],
                                        user=user, created_date=datetime.datetime.now(),
                                        modified_date=datetime.datetime.now(),
                                        feedback_object=feedback_obj)
        comment_object.save()

#check if status is resolved
    if feedback_obj.status == status[2]:
        servicedesk_obj_all = User.objects.filter(groups__name=Roles.SDMANAGERS)
        feedback_obj.resolved_date = datetime.datetime.now()
        feedback_obj.resolved_date = datetime.datetime.now()
        feedback_obj.root_cause = data['rootcause']
        feedback_obj.resolution = data['resolution']
        feedback_obj.save()
        comments = models.Comment.objects.filter(feedback_object=feedback_obj.id).order_by('-created_date')
        if reporter_email_id:
            context = create_context('INITIATOR_FEEDBACK_RESOLVED_MAIL_DETAIL',
                                  feedback_obj, comments[0])
            mail.send_email_to_initiator_after_issue_resolved(context,
                                                          feedback_obj, host, reporter_email_id)
        else:
            logger.info("Reporter emailId not found.")
            dealer_asc_obj = models.ServiceAdvisor.objects.get_dealer_asc_obj(feedback_obj.reporter)
            if dealer_asc_obj.user.user.email:
                context = create_context('FEEDBACK_RESOLVED_MAIL_TO_DEALER',
                                 feedback_obj)
                mail.send_email_to_dealer_after_issue_assigned(context,
                                                         dealer_asc_obj.user.user.email)
            else:
                logger.info("Dealer / Asc emailId not found.")
                    
        context = create_context('TICKET_RESOLVED_DETAIL_TO_BAJAJ',
                                 feedback_obj)
        mail.send_email_to_bajaj_after_issue_resolved(context)
        context = create_context('TICKET_RESOLVED_DETAIL_TO_MANAGER',
                                 feedback_obj)
        mail.send_email_to_manager_after_issue_resolved(context,
                                                        servicedesk_obj_all[0])
        send_sms('INITIATOR_FEEDBACK_STATUS', reporter_phone_number,
                 feedback_obj)
  
    if pending_status:
        set_wait_time(feedback_obj)
 
    if feedback_obj.assignee:
        if assign_number != feedback_obj.assignee.user_profile.phone_number:
            context = create_context('ASSIGNEE_FEEDBACK_MAIL_DETAIL',
                                      feedback_obj)
            mail.send_email_to_assignee(context, feedback_obj.assignee.user_profile.user.email)
            send_sms('SEND_MSG_TO_ASSIGNEE',
                     feedback_obj.assignee.user_profile.phone_number,
                     feedback_obj, comment_object)
