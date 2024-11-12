from __future__ import unicode_literals
from django.shortcuts import render
from .models import *
# Create your views here.
from django.template.loader import render_to_string
from django.core.mail import send_mail
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import To, Mail,ReplyTo,Email,Cc,Bcc,Attachment, FileContent, FileName, FileType, Disposition, to_email
from string import Template
import logging
from django.conf import settings
import os
from datetime import datetime
import sys, traceback
import base64
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def convert_safe_text(html_string):
	try:
		if type(html_string) != str:
			html_string = str(html_string)
	except:
		html_string = str(html_string.encode("utf8"))
	return html_string


def send_mail(mail_to, mail_subject, mail_content, mail_syn_content, mail_error_content, html_template = None,reply_to=None,cc=[],bcc =[],filepaths=None):
    config_status=Config.objects.get(code='send_email -s mail').value
    if int(config_status) != 0:
        if not html_template:
            html_message = mail_content
        else:
            template_name = html_template
            html_string = render_to_string(template_name,{'content':mail_content, 'push_content': mail_syn_content, "error_syn_content": mail_error_content, 'cron_content': '', 'date':datetime.now().strftime("%d %B %Y")})
            html_message = convert_safe_text(html_string)
        msg = MIMEMultipart()
        msg['From'] = settings.DEFAULT_FROM_EMAIL
        msg['To'] = ", ".join(mail_to)
        msg['Subject'] = str(mail_subject)
        isTls = True
        part = MIMEText(html_message, 'html')
        msg.attach(part)
        logger = logging.getLogger('user_obj')
        try:
            smtp = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            if isTls:
                smtp.starttls()
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            msg_send_status = smtp.sendmail(msg['From'], mail_to, msg.as_string())
            smtp.quit()
            response = {'status':200,'message':'success'}
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            message = str(error_stack)
            logger.error(message)
            #e.body will display details of the error from sendgrid
            logger.error(e.body)
            response = {'status':500,'message':'failed-'+message}
        return response
    

def client_send_mail(client_mail_to, mail_subject, mail_content, html_template = None,reply_to=None,client_cc=[],client_bcc =[],filepaths=None):
    config_status=Config.objects.get(code='send_email -s client_mail').value
    if int(config_status) != 0:
        if not html_template:
            client_html_message = mail_content
        else:
            template_name = html_template
            client_html_string = render_to_string(template_name,{'content':mail_content, 'push_content': '', "error_syn_content": '', 'cron_content': '', 'date':datetime.now().strftime("%d %B %Y")})
            client_html_message = convert_safe_text(client_html_string)
        msg = MIMEMultipart()
        msg['From'] = settings.DEFAULT_FROM_EMAIL
        msg['To'] = ", ".join(client_mail_to)
        msg['Subject'] = str(mail_subject)
        isTls = True
        part = MIMEText(client_html_message, 'html')
        msg.attach(part)
        logger = logging.getLogger('user_obj')
        try:
            smtp = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            if isTls:
                smtp.starttls()
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            msg_send_status = smtp.sendmail(msg['From'], client_mail_to, msg.as_string())
            smtp.quit()
            response = {'status':200,'message':'success'}
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            message = str(error_stack)
            logger.error(message)
            #e.body will display details of the error from sendgrid
            logger.error(e.body)
            response = {'status':500,'message':'failed-'+message}
        return response

def syn_send_mail(syn_mail_to, mail_subject, mail_content, mail_syn_content, mail_error_content, html_template = None,reply_to=None,syn_cc=[],syn_bcc =[],filepaths=None):
    config_status=Config.objects.get(code='send_email -s sync_mail').value
    if int(config_status) != 0:
        if not html_template:
            syn_html_message = mail_content
        else:
            template_name = html_template
            syn_html_string = render_to_string(template_name,{'content':'', 'push_content': mail_syn_content, "error_syn_content": mail_error_content, 'cron_content': '',  'date':datetime.now().strftime("%d %B %Y")})
            syn_html_message = convert_safe_text(syn_html_string)
        msg = MIMEMultipart()
        msg['From'] = settings.DEFAULT_FROM_EMAIL
        msg['To'] = ", ".join(syn_mail_to)
        msg['Subject'] = str(mail_subject)
        isTls = True
        part = MIMEText(syn_html_message, 'html')
        msg.attach(part)
        logger = logging.getLogger('user_obj')
        try:
            smtp = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            if isTls:
                smtp.starttls()
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            msg_send_status = smtp.sendmail(msg['From'], syn_mail_to, msg.as_string())
            smtp.quit()
            response = {'status':200,'message':'success'}
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            message = str(error_stack)
            logger.error(message)
            #e.body will display details of the error from sendgrid
            logger.error(e.body)
            response = {'status':500,'message':'failed-'+message}
        return response


def cron_send_mail(cron_mail_to, mail_subject, mail_content, mail_syn_content, mail_error_content,mail_cron_content, html_template = None,reply_to=None,cron_cc=[],cron_bcc =[],filepaths=None):
    config_status=Config.objects.get(code='send_email -s cron_mail').value
    if int(config_status) != 0:
        if not html_template:
            cron_html_message = mail_content
        else:
            template_name = html_template
            cron_html_string = render_to_string(template_name,{'content':'', 'push_content': '', "error_syn_content": '', 'cron_content': mail_cron_content, 'date':datetime.now().strftime("%d %B %Y")})
            cron_html_message = convert_safe_text(cron_html_string)
        msg = MIMEMultipart()
        msg['From'] = settings.DEFAULT_FROM_EMAIL
        msg['To'] = ", ".join(cron_mail_to)
        msg['Subject'] = str(mail_subject)
        isTls = True
        part = MIMEText(cron_html_message, 'html')
        msg.attach(part)
        logger = logging.getLogger('user_obj')
        try:
            smtp = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            if isTls:
                smtp.starttls()
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            msg_send_status = smtp.sendmail(msg['From'], cron_mail_to, msg.as_string())
            smtp.quit()
            response = {'status':200,'message':'success'}
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            message = str(error_stack)
            logger.error(message)
            #e.body will display details of the error from sendgrid
            logger.error(e.body)
            response = {'status':500,'message':'failed-'+message}
        return response
    
