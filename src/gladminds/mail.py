from django.conf import settings
from django.template import Context, Template

import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import logging

logger = logging.getLogger("gladminds")

def send_email(sender, receiver, subject, body, smtp_server=settings.MAIL_SERVER):
    msg = MIMEText(body, 'html', _charset='utf-8')
    msg['Subject'] = subject
    msg['To'] = receiver
    msg['From'] = "Gladminds<%s>" % sender
    mail = smtplib.SMTP(smtp_server)
    mail.sendmail(sender, receiver, msg.as_string())
    mail.quit()

def feed_report(feed_data = None):
    from gladminds import mail
    try:
        file_stream = open(settings.TEMPLATE_DIR+'/feed_report.html')
        feed_temp = file_stream.read()
        template = Template(feed_temp)
        context = Context({"feed_logs": feed_data})
        body = template.render(context)
        mail_detail = settings.MAIL_DETAIL
        mail.send_email(sender = mail_detail['sender'], receiver = mail_detail['reciever'], 
                   subject = mail_detail['subject'], body = body, 
                   smtp_server = settings.MAIL_SERVER)
    except Exception as ex:
        logger.info("[Exception feed_report]: {0}".format(ex))
        
def item_purchase_interest(data = None, receiver = None, subject = None):
    from gladminds import mail
    try:
        file_stream = open(settings.TEMPLATE_DIR+'/purchase_interest_mail.html')
        item = file_stream.read()
        template = Template(item)
        context = Context({"user": data})
        body = template.render(context)
        mail.send_email(sender = data['email_id'],receiver = receiver, 
                   subject = subject, body = body, 
                   smtp_server = settings.MAIL_SERVER)
    except Exception as ex:
        logger.info("[Exception item purchase report]: {0}".format(ex))

def warrenty_extend(data = None, receiver = None, subject = None):
    from gladminds import mail
    try:
        file_stream = open(settings.TEMPLATE_DIR+'/warrenty_extend_mail.html')
        item = file_stream.read()
        template = Template(item)
        context = Context({"user": data})
        body = template.render(context)
        mail.send_email(sender = data['email_id'],receiver = receiver, 
                   subject = subject, body = body, 
                   smtp_server = settings.MAIL_SERVER)
    except Exception as ex:
        logger.info("[Exception item warrenty extend]: {0}".format(ex))

def insurance_extend(data = None, receiver = None, subject = None):
    from gladminds import mail
    try:
        file_stream = open(settings.TEMPLATE_DIR+'/insurance_extend_mail.html')
        item = file_stream.read()
        template = Template(item)
        context = Context({"user": data})
        body = template.render(context)
        mail.send_email(sender = data['email_id'],receiver = receiver, 
                   subject = subject, body = body, 
                   smtp_server = settings.MAIL_SERVER)
    except Exception as ex:
        logger.info("[Exception item insurance extend]: {0}".format(ex))
        

    