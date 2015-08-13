import StringIO
import csv
import smtplib
import logging
from django.core.mail.message import EmailMessage
from django.conf import settings
from django.template import Context, Template
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from gladminds.core.managers import audit_manager
from gladminds.core.auth_helper import GmApps, Roles
from gladminds.core.model_fetcher import get_model

logger = logging.getLogger("gladminds")


def get_email_template(key, brand=None):
    template_object = get_model('EmailTemplate').objects.using(brand).filter(template_key=key).values()
    return template_object[0]

def get_mail_receiver(template_name, mail_detail):
    receivers = []
    receivers.append(mail_detail['receiver'])
    return receivers

def send_email_with_file_attachment(sender, receiver, subject, body, filename, content, brand='bajaj'):
    try:
        yesterday = datetime.now().date() - timedelta(days=1)
        message = EmailMessage(subject, body, sender, receiver)
        message.attach(filename + yesterday.strftime("%b %d %Y") +'.csv', content.getvalue(), 'text/csv')
        message.send()
        audit_manager.email_log(brand, subject, " ", sender, receiver);
        return True
    except Exception as ex:
        logger.error('Exception while sending mail {0}'.format(ex))
        return False
    

def send_email(sender, receiver, subject, body, message=None,smtp_server=settings.MAIL_SERVER, title='GCP_Bajaj_FSC_Feeds'
               , brand='bajaj'):
    try:
        msg = MIMEText(body, 'html', _charset='utf-8')
        msg['Subject'] = subject
        if isinstance(receiver, list):
            msg['To'] = ", ".join(receiver)
        else:
            msg['To'] = receiver
        msg['From'] = title + "<%s>"% sender
        mail = smtplib.SMTP(smtp_server)
        mail.sendmail(from_addr=sender, to_addrs=receiver, msg=msg.as_string())
        mail.quit()
        audit_manager.email_log(brand, subject, message, sender, receiver);
        return True
    except Exception as ex:
        logger.error('Exception while sending mail: {0}'.format(ex))
        return False


def send_email_activation(receiver_email, data=None, brand=None):
    file_stream = open(settings.EMAIL_DIR+'/activation_email.html')
    feed_temp = file_stream.read()
    template = Template(feed_temp)
    context = Context(data)
    body = template.render(context)
    mail_detail = settings.EMAIL_ACTIVATION_MAIL
    send_email(sender=mail_detail['sender'],
               receiver=receiver_email,
               subject=mail_detail['subject'], body=body,
               smtp_server=settings.MAIL_SERVER, title='Support',
               brand=brand)
    
def send_reset_link_email(email,data=None,brand=None):
    file_stream = open(settings.EMAIL_DIR+'/reset_link.html')
    feed_temp = file_stream.read()
    template = Template(feed_temp)
    context = Context(data)
    body = template.render(context)
    mail_detail = settings.RESET_LINK
    send_email(sender=mail_detail['sender'],
               receiver=email,
               subject=mail_detail['subject'], body=body,
               smtp_server=settings.MAIL_SERVER, title='Reset_Password',
               brand=brand)


def send_recycle_mail(sender_id, data=None):
    file_stream = open(settings.EMAIL_DIR+'/recycle_email.html')
    feed_temp = file_stream.read()
    template = Template(feed_temp)
    context = Context({'product_info': data})
    body = template.render(context)
    mail_detail = settings.RECYCLE_MAIL
    send_email(sender=mail_detail['sender'],
               receiver=mail_detail['receiver'],
               subject=mail_detail['subject'], body=body,
               smtp_server=settings.MAIL_SERVER, title='Recycle Product',
               brand=GmApps.AFTERBUY)


def feed_report(feed_data=None, brand=None):
    try:
        yesterday = datetime.now().date() - timedelta(days=1)
        file_stream = open(settings.EMAIL_DIR+'/feed_report.html')
        feed_temp = file_stream.read()
        template = Template(feed_temp)
        context = Context({"feed_logs": feed_data, "yesterday": yesterday})
        body = template.render(context)
        mail_detail = settings.MAIL_DETAIL
        send_email(sender=mail_detail['sender'],
                   receiver=mail_detail['receiver'],
                   subject=mail_detail['subject'], body=body,
                   smtp_server=settings.MAIL_SERVER)

    except Exception as ex:
        logger.info("[Exception feed_report]: {0}".format(ex))


def customer_phone_number_update(customer_details=None, brand=None):
    try:
        yesterday = datetime.now().date() - timedelta(days=1)
        mail_detail = get_email_template('CUSTOMER_PHONE_NUMBER_UPDATE', brand)
        receivers = get_mail_receiver(settings.CUSTOMER_PHONE_NUMBER_UPDATE, mail_detail)
        csvfile = StringIO.StringIO()
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["DEALER/ASC/MANAGER ID", "CUSTOMER ID", "CUSTOMER NAME", "OLD NUMBER", "NEW NUMBER", "MODIFIED DATE"])

        for customer in customer_details:
            csvwriter.writerow([customer['dealer_asc_id'], customer['customer_id'], customer['customer_name'],
                                customer['old_number'], customer['new_number'], customer['modified_date']])
        if settings.ENV in settings.IGNORE_ENV:
            mail_detail['subject'] = mail_detail['subject'] + '- ' + settings.ENV
        send_email_with_file_attachment(mail_detail['sender'], receivers, mail_detail['subject'],
                                          mail_detail['body'].format(date=yesterday.strftime("%b %d %Y")), 'customer_phone_number_update_',
                                          csvfile)
        logger.info("Sending out customer phone number update emails")
    except Exception as ex:
        logger.info("[Exception customer phone number update]: {0}".format(ex))


def discrepant_coupon_update(csv_file, brand=None):
    try:
        yesterday = datetime.now().date() - timedelta(days=1)
        mail_detail = get_email_template('POLICY_DISCREPANCY_MAIL_TO_MANAGER', brand)
        receivers = get_mail_receiver(settings.DISCREPANCY_MAIL_TO_MANAGER, mail_detail)
        send_email_with_file_attachment(mail_detail['sender'], receivers, mail_detail['subject'],
                                          mail_detail['body'].format(date=yesterday.strftime("%b %d %Y")), 
                                          'discrepant_coupon_update_', csv_file)

        logger.info("Sending out Policy Discrepency coupon update emails")
    except Exception as ex:
        logger.info("[Exception Policy Discrepency  while sending mail]: {0}".format(ex))

def send_vin_sync_feed_report(feed_data=None, brand=None):
    try:
        yesterday = datetime.now().date() - timedelta(days=1)
        mail_detail = get_email_template('VIN_SYNC_FEED', brand)
        receivers = get_mail_receiver(settings.VIN_SYNC_FEED, mail_detail)
        csvfile = StringIO.StringIO()
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["CHASSIS", "DEALER/ASC ID", "STATUS CODE", "UCN COUNT"])
        for feed in feed_data:
            csvwriter.writerow([feed['vin'], feed['dealer_asc_id'], feed['status_code'], feed['ucn_count']])

        send_email_with_file_attachment(mail_detail['sender'], receivers, mail_detail['subject'],
                                          mail_detail['body'] + yesterday.strftime("%b %d %Y"), 'vin_sync_feed_', csvfile)
        logger.info("Sending out vin sync feed emails")
    except Exception as ex:
        logger.info("[Exception feed_fail_report]: {0}".format(ex))


def feed_failure(feed_data=None, brand=None):
    try:
        mail_detail = get_email_template('FEED_FAILURE', brand)
        receivers = get_mail_receiver(settings.FEED_FAILURE, mail_detail)
        csvfile = StringIO.StringIO()
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Timestamp", "FeedType", "Reason"])
        feed_type = ''
        feed_log_time = ''
        for feed in feed_data:
            csvwriter.writerow([feed['created_date'], feed['feed_type'], feed['reason']])
            feed_type = feed['feed_type']
        try:
            feed_log_time = get_model('EmailLog').objects.filter(subject='Gladminds Failure Report - '+feed_type).order_by('-id')[0]
            feed_log_time = feed_log_time.created_date.strftime("%b %d %Y") 
        except:
            feed_log_time = datetime.now().strftime("%b %d %Y")

        send_email_with_file_attachment(mail_detail['sender'], receivers, mail_detail['subject'].format(feed_type=feed_type) ,
                                          mail_detail['body'].format(feed_type=feed_type, date=feed_log_time), 'feed_failure_', csvfile)
        logger.info("Sending feed failure mails")
    except Exception as ex:
        logger.info("[Exception feed_fail_report]: {0}".format(ex))


def send_registration_failure(feed_data=None,
                              feed_type=None, brand=None):
    try:
        file_stream = open(settings.TEMPLATE_DIR +
                            '/portal/registration_failure_report.html')
        feed_temp = file_stream.read()
        template = Template(feed_temp)
        context = Context({"feed_type": feed_type,
                           "feed_logs": feed_data})
        body = template.render(context)

        mail_detail = settings.REGISTRATION_CONFIG[brand][feed_type][
                                                         'fail_mail_detail']
        logger.info(mail_detail)
        logger.info(settings.MAIL_SERVER)
        send_email(sender=mail_detail['sender'], receiver=mail_detail[
              'receiver'], subject=mail_detail['subject'], body=body,
                   smtp_server=settings.MAIL_SERVER)

    except Exception as ex:
        logger.info("[Exception feed_report]: {0}".format(ex))


def item_purchase_interest(data=None, receiver=None, subject=None):
    try:
        file_stream = open(
            settings.EMAIL_DIR + '/purchase_interest_mail.html')
        item = file_stream.read()
        template = Template(item)
        context = Context({"user": data})
        body = template.render(context)
        send_email(sender=data['email_id'], receiver=receiver,
                        subject=subject, body=body,
                        smtp_server=settings.MAIL_SERVER)
    except Exception as ex:
        logger.info("[Exception item purchase report]: {0}".format(ex))


def warrenty_extend(data=None, receiver=None, subject=None):
    try:
        file_stream = open(
            settings.EMAIL_DIR + '/warrenty_extend_mail.html')
        item = file_stream.read()
        template = Template(item)
        context = Context({"user": data})
        body = template.render(context)
        send_email(sender=data['email_id'], receiver=receiver,
                        subject=subject, body=body,
                        smtp_server=settings.MAIL_SERVER)
    except Exception as ex:
        logger.info("[Exception item warrenty extend]: {0}".format(ex))


def insurance_extend(data=None, receiver=None, subject=None):
    try:
        file_stream = open(
            settings.EMAIL_DIR + '/insurance_extend_mail.html')
        item = file_stream.read()
        template = Template(item)
        context = Context({"user": data})
        body = template.render(context)
        send_email(sender=data['email_id'], receiver=receiver,
                        subject=subject, body=body,
                        smtp_server=settings.MAIL_SERVER)
    except Exception as ex:
        logger.info("[Exception item insurance extend]: {0}".format(ex))


def sent_password_reset_link(receiver=None, data=None, brand=None):
    try:
        file_stream = open(settings.EMAIL_DIR+'/password_reset_email.html')
        feed_temp = file_stream.read()
        template = Template(feed_temp)
        context = Context(data)
        body = template.render(context)
        mail_detail = settings.PASSWORD_RESET_MAIL
        send_email(sender = mail_detail['sender'], receiver = receiver, 
                   subject = mail_detail['subject'], body = body,
                   smtp_server = settings.MAIL_SERVER, title='Support',
                   brand = brand)
    except Exception as ex:
        logger.info("[Exception otp email]: {0}".format(ex))


def sent_otp_email(data=None, receiver=None, subject=None):
    try:
        date = datetime.now().date()
        file_stream = open(settings.EMAIL_DIR+'/otp_email.html')
        feed_temp = file_stream.read()
        template = Template(feed_temp)
        context = Context({"otp": data})
        body = template.render(context)
        mail_detail = settings.OTP_MAIL
        send_email(sender = mail_detail['sender'], receiver = receiver, 
                   subject = mail_detail['subject'], body = body, 
                   smtp_server = settings.MAIL_SERVER)
    except Exception as ex:
        logger.info("[Exception otp email]: {0}".format(ex))
    
def send_ucn_request_alert(data=None):
    try:
        file_stream = open(settings.EMAIL_DIR+'/ucn_request_email.html')
        feed_temp = file_stream.read()
        template = Template(feed_temp)
        context = Context({"content": data})
        body = template.render(context)
        mail_detail = settings.UCN_RECOVERY_MAIL_DETAIL
        
        send_email(sender = mail_detail['sender'], receiver = mail_detail['receiver'], 
                   subject = mail_detail['subject'], body = body, 
                   smtp_server = settings.MAIL_SERVER)
    except Exception as ex:
        logger.info("[Exception ucn request email]: {0}".format(ex))
    
def send_feedback_received(data, receiver_email):
    try:
        file_stream = open(settings.EMAIL_DIR+'/base_email_template.html')
        feed_temp = file_stream.read()
        template = Template(feed_temp)
        context = Context({"content": data['content']})
        body = template.render(context)
        send_email(sender = data['sender'], receiver = receiver_email, 
                   subject = data['newsubject'], body = body, message=data['content'],
                   smtp_server = settings.MAIL_SERVER, title='gm_support')
    except Exception as ex:
        logger.info("[Exception feedback received email]: {0}".format(ex))

def send_due_date_exceeded(data, receiver_email):
    try:
        file_stream = open(settings.EMAIL_DIR+'/base_email_template.html')
        feed_temp = file_stream.read()
        template = Template(feed_temp)
        context = Context({"content": data['content']})
        body = template.render(context)
        send_email(sender = data['sender'], receiver = receiver_email, 
                   subject = data['subject'], body = body, message=data['content'],
                   smtp_server = settings.MAIL_SERVER, title='gm_support')
    except Exception as ex:
        logger.info("[Exception due date exceeded email]: {0}".format(ex))


def send_due_date_reminder(data, receiver_email):
    try:
        file_stream = open(settings.EMAIL_DIR+'/base_email_template.html')
        feed_temp = file_stream.read()
        template = Template(feed_temp)
        context = Context({"content": data['content']})
        body = template.render(context)
        send_email(sender = data['sender'], receiver = receiver_email, 
                   subject = data['subject'], body = body, message=data['content'],
                   smtp_server = settings.MAIL_SERVER, title='gm_support')
    except Exception as ex:
        logger.info("[Exception due date reminder email]: {0}".format(ex))
        
def send_servicedesk_feedback(data, reporter_email_id):
    try:
        context = Context({"content": data['content']})
        send_template_email("base_email_template.html", context,
                            data, receiver= reporter_email_id,
                            message=data['content'], title='gm_support')
    except Exception as ex:
        logger.info("[Exception feedback initiator email]  {0}".format(ex))

def send_dealer_feedback(data, dealer_email):
    try:
        file_stream = open(settings.EMAIL_DIR+'/base_email_template.html')
        feed_temp = file_stream.read()
        template = Template(feed_temp)
        context = Context({"content": data['content']})
        body = template.render(context)
        send_email(sender = data['sender'], receiver = dealer_email, 
                   subject = data['subject'], body = body, message=data['content'],
                   smtp_server = settings.MAIL_SERVER, title='gm_support')
    except Exception as ex:
        logger.info("[Exception dealer feedback email]: {0}".format(ex))
        

def send_email_to_assignee(data, assignee_email):
    try:
        context = Context({"content": data['content']})
        send_template_email("base_email_template.html", context,
                             data, receiver = assignee_email,
                             message=data['content'], title='gm_support')
    except Exception as ex:
        logger.info("[Exception feedback receiver email]  {0}".format(ex)) 
        
def send_email_to_initiator_after_issue_assigned(data, reporter_email):
    try:
        context = Context({"content": data['content']})
        send_template_email("base_email_template.html", context,
                            data, receiver=reporter_email,
                            message=data['content'], title='gm_support')
    except Exception as ex:
        logger.info("[Exception feedback initiator after issue assigned email]  {0}".format(ex)) 

def send_email_to_dealer_after_issue_assigned(data, dealer_email):
    try:
        context = Context({"content": data['content']})
        send_template_email("base_email_template.html", context,
                            data, receiver=dealer_email,
                            message=data['content'], title='gm_support')
    except Exception as ex:
        logger.info("[Exception feedback initiator after issue assigned email]  {0}".format(ex)) 

def send_email_to_initiator_after_issue_resolved(data, feedback_obj, host, reporter_email):
    try:
        context = Context({"content": data['content'],
                            "id":feedback_obj.id,
                            "url":host,
                            })
        send_template_email("initiator_feedback_resolved.html", context,
                            data, receiver=reporter_email,
                            message=data['content'], title='gm_support')
    except Exception as ex:
        logger.info("[Exception feedback initiator after issue resloved email]  {0}".format(ex))

def send_email_to_initiator_when_due_date_is_changed(data, reporter_email):
    try:
        context = Context({"content": data['content']})
        send_template_email("base_email_template.html", context,
                            data, receiver=reporter_email,
                            message=data['content'], title='gm_support')
    except Exception as ex:
        logger.info("[Exception feedback initiator on change of due date]  {0}".format(ex)) 

        
def send_email_to_brand_after_issue_resolved(data):
    try:
        context = Context({"content": data['content']})
        send_template_email("base_email_template.html", context, data,
                            message=data['content'], title='gm_support')
    except Exception as ex:
        logger.info("[Exception fail to send mail to bajaj]  {0}".format(ex)) 

def send_email_to_manager_after_issue_resolved(data, manager_obj):
    try:
        context = Context({"content": data['content']})
        send_template_email("base_email_template.html", context,
                             data, receiver = manager_obj.email_id,
                             message=data['content'], title='gm_support')
    except Exception as ex:
        logger.info("[Exception fail to send mail to manager]  {0}".format(ex))
        
def send_email_to_redemption_request_partner(data, partner_email):
    try:
        context = Context({"content": data['content']})
        send_template_email("base_email_template.html", context,
                             data, receiver = partner_email, message=data['content'])
    except Exception as ex:
        logger.info("[Exception fail to send mail to partner of redemption]  {0}".format(ex))        

def send_email_to_redeem_escaltion_group(data, redeem_escaltion_email):
    try:
        context = Context({"content": data['content']})
        send_template_email("base_email_template.html", context,
                             data, receiver = redeem_escaltion_email, message=data['content'])
    except Exception as ex:
        logger.info("[Exception fail to send mail to redemption escalation group]  {0}".format(ex))        

def send_email_to_asc_customer_support(data, asc_email_id):
    try:
        file_stream = open(settings.EMAIL_DIR+'/customer_support.html')
        feed_temp = file_stream.read()
        template = Template(feed_temp)
        context = Context({"content": data['content']})
        body = template.render(context)
        send_email(sender = data['sender'], receiver = asc_email_id, 
                   subject = data['subject'], body = body, message=data['content'],
                   smtp_server = settings.MAIL_SERVER)
    except Exception as ex:
        logger.info("[Exception fail to send mail to ASCs on Customer Support]  {0}".format(ex))
    
def send_email_to_welcomekit_escaltion_group(data, welcomekit_escaltion_email):
    try:
        context = Context({"content": data['content']})
        send_template_email("base_email_template.html", context,
                             data, receiver = welcomekit_escaltion_email, message=data['content'])
    except Exception as ex:
        logger.info("[Exception fail to send mail to welcome kit escalation group ]  {0}".format(ex))        

def send_template_email(template_name, context, mail_detail,receiver=None, message=None, title='GCP_Bajaj_FSC_Feeds'): 
    '''generic function use for send mail for any html template'''
    
    file_stream = open(settings.EMAIL_DIR+'/'+ template_name)
    feed_temp = file_stream.read()
    template = Template(feed_temp)
    body = template.render(context)
    if receiver is None:
        receiver =  mail_detail['receiver']
    send_email(sender =  mail_detail['sender'], receiver = receiver, 
               subject = mail_detail['newsubject'], body = body, message=message,
               smtp_server = settings.MAIL_SERVER, title=title)
    logger.info("Mail sent successfully")
    #TODO We have to remove hard code receiver

def send_mail_when_vin_does_not_exist(data=None):
    try:
        file_stream = open(settings.TEMPLATE_DIR+'/portal/vin_does_not_exist.html')
        feed_temp = file_stream.read()
        template = Template(feed_temp)
        context = Context({"content": data})
        body = template.render(context)
        mail_detail = settings.VIN_DOES_NOT_EXIST_DETAIL
        send_email(sender=mail_detail['sender'], receiver=mail_detail['receiver'],
                   subject=mail_detail['subject'], body=body,
                   smtp_server=settings.MAIL_SERVER)
    except Exception as ex:
        logger.info("[Exception VIN not found email]: {0}".format(ex))


def send_asc_registration_mail(data=None):
    try:
        file_stream = open(settings.TEMPLATE_DIR+'/asc_username_password_email.html')
        feed_temp = file_stream.read()
        template = Template(feed_temp)
        context = Context({"content": data})
        body = template.render(context)
        mail_detail = settings.REGISTER_ASC_MAIL_DETAIL

        send_email(sender = mail_detail['sender'], receiver = data['receiver'], 
                   subject = mail_detail['subject'], body = body, 
                   smtp_server = settings.MAIL_SERVER)
    except Exception as ex:
        logger.info("[Exception asc registration email]: {0}".format(ex))

def send_recovery_email_to_admin(file_obj, coupon_data, brand=None):
    file_location = file_obj.file_location
    reason = file_obj.reason
    customer_id = file_obj.customer_id
    requester = str(file_obj.user.user.username)
    data = get_email_template('UCN_REQUEST_ALERT', brand)['body'].format(requester,coupon_data.service_type,
                customer_id, coupon_data.actual_kms, reason, file_location)
    send_ucn_request_alert(data=data)

def send_phone_number_update_count_exceeded(update_details=None, brand=None):
    try:
        yesterday = datetime.now().date() - timedelta(days=1)
        mail_detail = get_email_template('PHONE_NUMBER_UPDATE_COUNT_EXCEEDED', brand)
        receivers = get_mail_receiver(settings.PHONE_NUMBER_UPDATE_COUNT_EXCEEDED_MAIL_TO_ASM, mail_detail)
        csvfile = StringIO.StringIO()
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["UPDATED BY", "CUSTOMER ID", "CUSTOMER NAME", "OLD NUMBER", "NEW NUMBER", "MODIFIED DATE","PRODUCT ID"])

        for update in update_details:
            csvwriter.writerow([update['updated_by'], update['customer_id'], update['customer_name'],
                                update['old_number'], update['new_number'], update['modified_date'], update['product_id']])
        if settings.ENV in settings.IGNORE_ENV:
            mail_detail['subject'] = mail_detail['subject'] + '- ' + settings.ENV
        send_email_with_file_attachment(mail_detail['sender'], receivers, mail_detail['subject'],
                                          mail_detail['body'].format(date=yesterday.strftime("%b %d %Y")), 'customer_phone_number_update_exceed_',
                                          csvfile)
        logger.info("Sending out customer phone number update exceeds emails")
    except Exception as ex:
        logger.info("[Exception customer phone number update]: {0}".format(ex))


def send_epc_feed_received_mail(brand, template_name):
    try:
        data = get_email_template(template_name, brand)
        file_stream = open(settings.EMAIL_DIR+'/base_email_template.html')
        feed_temp = file_stream.read()
        template = Template(feed_temp)
        context = Context({"content": data['body']})
        body = template.render(context)
        epc_users = get_model('UserProfile').objects.filter(user__groups__name=Roles.VISUALIZATIONUSER)
        receiver_email = []
        for user in epc_users:
            receiver_email.append(user.user.email)

        send_email(sender = data['sender'], receiver = receiver_email, 
                   subject = data['subject'], body = body, message=data['body'],
                   smtp_server = settings.MAIL_SERVER)
    except Exception as ex:
        logger.info("[Exception while sending {0} email]: {1} ".format(template_name, ex))
        
def discrepant_manufacture_data(csv_file, brand=None):
    try:
        yesterday = datetime.now().date() - timedelta(days=1)
        mail_detail = get_email_template('MANUFACTURE_DISCREPANCY_MAIL_TO_MANAGER', brand)
        receivers = get_mail_receiver(settings.DISCREPANCY_MAIL_TO_MANAGER, mail_detail)
        send_email_with_file_attachment(mail_detail['sender'], receivers, mail_detail['subject'],
                                          mail_detail['body'].format(date=yesterday.strftime("%b %d %Y")), 
                                          'discrepant_manufacture_data_', csv_file)

        logger.info("Sending out discrepant manufacture data emails")
    except Exception as ex:
        logger.info("[Exception discrepant manufacture data while sending mail]: {0}".format(ex))
