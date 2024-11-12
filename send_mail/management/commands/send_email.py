from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from send_mail.views import *
from master_data . models import *
import datetime 
from send_mail.models import MailData
from django.conf import settings
import sys, traceback
import  logging
from Raahi.settings import DATABASE_HOST
logger = logging.getLogger(__name__)
from datetime import datetime
from master_data.views import *

def sendmail(key):
    batch_size = settings.APP_EMAIL_SETTINGS['BATCH_SIZE']
    #mail status: choices  1-new, 2-makedToSend, 3-Sent, 4-Failed ,5 -Ignored
    mail_obj = MailData.objects.filter(mail_status = 1).order_by('priority','-send_attempt')[:batch_size]
    max_attempts = settings.APP_EMAIL_SETTINGS['MAX_ATTEMPTS']
    if str(key) == 'mail':
        for x in mail_obj:
            try:
                mail_to = x.mail_to.split(";")
                cc      = x.mail_cc.split(";")
                bcc     = x.mail_bcc.split(";")

                x.mail_status = 2
                if settings.APP_EMAIL_SETTINGS['MODE'] == 'TEST':
                    test_mail_list = set(settings.APP_EMAIL_SETTINGS['TEST_MAIL_LIST'])
                    mail_to = [item for item in mail_to if item in test_mail_list]
                    cc = [item for item in cc if item in test_mail_list]
                    bcc = [item for item in bcc if item in test_mail_list]
                    if len(mail_to) == 0 and len(cc)== 0 and len(bcc) == 0:
                        x.mail_status = 5
                        x.error_details = 'Ignored because MODE is TEST and email ID not in TEST_MAIL_LIST'  
                if x.mail_status == 2:
                    mail_subject = x.subject + ' ('+DATABASE_HOST.split('//')[1]+')'
                    mail_content = x.content
                    mail_syn_content = x.syn_content
                    mail_error_content = x.error_content
                    mail_template = x.template_name.html_template
                    response = send_mail(mail_to,mail_subject,mail_content, mail_syn_content, mail_error_content, mail_template,cc=cc,filepaths=x.file_paths,)
                    x.send_attempt = int(x.send_attempt)+1
                    x.time_last_attempt = datetime.datetime.now()
                    x.mode = settings.APP_EMAIL_SETTINGS['MODE']
                    if response['status'] == 200:
                        x.mail_status = 3
                    elif x.send_attempt >= max_attempts:
                        x.error_details = str(response)
                        x.mail_status = 4
                    else:
                        x.error_details = str(response)
                        x.mail_status = 1
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                x.error_details = str(error_stack)
            x.save()
            
            
                
            


    if str(key) == 'client_mail':
        for cx in mail_obj:
            try:
                client_mail_to = cx.client_mail_to.split(";")
                client_cc      = cx.client_mail_cc.split(";")
                client_bcc     = cx.client_mail_bcc.split(";")
            #If test mode, check if mail_to id in TEST_MAIL_LIST
            # if mail_to in list, send the email otherwise don't send email and set status to ignored
                cx.mail_status = 2
                if settings.APP_EMAIL_SETTINGS['MODE'] == 'TEST':
                    
                    client_mail_list = set(settings.APP_EMAIL_SETTINGS['CLIENT_MAIL_LIST'])
                    client_mail_to = [item for item in client_mail_to if item in client_mail_list]
                    client_cc = [item for item in client_cc if item in client_mail_list]
                    client_bcc = [item for item in client_bcc if item in client_mail_list]
                    if len(client_mail_to) == 0 and len(client_cc)== 0 and len(client_bcc) == 0:
                        cx.mail_status = 5
                        cx.error_details = 'Ignored because MODE is TEST and email ID not in CLIENT_MAIL_LIST'
            #if not test mode and 
                if cx.mail_status == 2:
                    mail_subject = cx.subject + ' ('+DATABASE_HOST.split('//')[1]+')'
                    mail_content = cx.content
                    mail_syn_content = cx.syn_content
                    mail_error_content = cx.error_content
                    mail_template = cx.template_name.html_template
                    response = client_send_mail(client_mail_to,mail_subject,mail_content, mail_template,client_cc=client_cc,filepaths=cx.file_paths,)
                    cx.send_attempt = int(cx.send_attempt)+1
                    cx.time_last_attempt = datetime.datetime.now()
                    cx.mode = settings.APP_EMAIL_SETTINGS['MODE']
                    if response['status'] == 200:
                        cx.mail_status = 3
                    elif cx.send_attempt >= max_attempts:
                        cx.error_details = str(response)
                        cx.mail_status = 4
                    else:
                        cx.error_details = str(response)
                        cx.mail_status = 1
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                cx.error_details = str(error_stack)
            cx.save()
            
           
                
             

    if str(key) == 'sync_mail':
        for sx in mail_obj:
            try:
                # import ipdb; ipdb.set_trace();
                syn_mail_to = sx.syn_mail_to.split(";")
                syn_cc      = sx.syn_mail_cc.split(";")
                syn_bcc     = sx.syn_mail_bcc.split(";")
            #If test mode, check if mail_to id in TEST_MAIL_LIST
            # if mail_to in list, send the email otherwise don't send email and set status to ignored
                sx.mail_status = 2
                if settings.APP_EMAIL_SETTINGS['MODE'] == 'TEST':
                    syn_mail_list = set(settings.APP_EMAIL_SETTINGS['SYNC_MAIL_LIST'])
                    syn_mail_to = [item for item in syn_mail_to if item in syn_mail_list]
                    syn_cc = [item for item in syn_cc if item in syn_mail_list]
                    syn_bcc = [item for item in syn_bcc if item in syn_mail_list]
                    if len(syn_mail_to) == 0 and len(syn_cc)== 0 and len(syn_bcc) == 0:
                        sx.mail_status = 5
                        sx.error_details = 'Ignored because MODE is TEST and email ID not in SYNC_MAIL_LIST'
            #if not test mode and 
                if sx.mail_status == 2:
                    mail_subject = sx.subject + ' ('+DATABASE_HOST.split('//')[1]+')'
                    mail_content = sx.content
                    mail_syn_content = sx.syn_content
                    mail_error_content = sx.error_content
                    mail_template = sx.template_name.html_template
                    response = syn_send_mail(syn_mail_to,mail_subject,mail_content, mail_syn_content, mail_error_content, mail_template,syn_cc=syn_cc,filepaths=sx.file_paths,)
                    sx.send_attempt = int(sx.send_attempt)+1
                    sx.time_last_attempt = datetime.datetime.now()
                    sx.mode = settings.APP_EMAIL_SETTINGS['MODE']
                    if response['status'] == 200:
                        sx.mail_status = 3
                    elif sx.send_attempt >= max_attempts:
                        sx.error_details = str(response)
                        sx.mail_status = 4
                    else:
                        sx.error_details = str(response)
                        sx.mail_status = 1
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                sx.error_details = str(error_stack)
            sx.save()
            
            
    if str(key) == 'cron_mail':
        for crx in mail_obj:
            try:
                cron_mail_to = crx.cron_mail_to.split(";")
                cron_cc      = crx.cron_mail_cc.split(";")
                cron_bcc     = crx.cron_mail_bcc.split(";")
            #If test mode, check if mail_to id in TEST_MAIL_LIST
            # if mail_to in list, send the email otherwise don't send email and set status to ignored
                crx.mail_status = 2
                if settings.APP_EMAIL_SETTINGS['MODE'] == 'TEST':
                    
                    cron_mail_list = set(settings.APP_EMAIL_SETTINGS['CRON_MAIL_LIST'])
                    cron_mail_to = [item for item in cron_mail_to if item in cron_mail_list]
                    cron_cc = [item for item in cron_cc if item in cron_mail_list]
                    cron_bcc = [item for item in cron_bcc if item in cron_mail_list]
                    if len(cron_mail_to) == 0 and len(cron_cc)== 0 and len(cron_bcc) == 0:
                        crx.mail_status = 5
                        crx.error_details = 'Ignored because MODE is TEST and email ID not in CRON_MAIL_LIST'
            #if not test mode and 
                if crx.mail_status == 2:
                    mail_subject = crx.subject + ' ('+DATABASE_HOST.split('//')[1]+')'
                    mail_content = crx.content
                    mail_syn_content = crx.syn_content
                    mail_error_content = crx.error_content
                    mail_cron_content = crx.cron_content
                    mail_template = crx.template_name.html_template
                    response = cron_send_mail(cron_mail_to,mail_subject,mail_content,mail_syn_content, mail_error_content, mail_cron_content, mail_template,cron_cc=cron_cc,filepaths=crx.file_paths,)
                    crx.send_attempt = int(crx.send_attempt)+1
                    crx.time_last_attempt = datetime.datetime.now()
                    crx.mode = settings.APP_EMAIL_SETTINGS['MODE']
                    if response['status'] == 200:
                        crx.mail_status = 3
                    elif crx.send_attempt >= max_attempts:
                        crx.error_details = str(response)
                        crx.mail_status = 4
                    else:
                        crx.error_details = str(response)
                        crx.mail_status = 1
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                crx.error_details = str(error_stack)
            crx.save()
        
        
                

    
class Command(BaseCommand):
    def add_arguments(self, parser):
        # Optional argument
        parser.add_argument('-s','--survey_list', type=str, nargs='+')
    def handle(self, *args, **kwargs):
        if kwargs.get('survey_list')[0] == 'mail':
            start_time = datetime.now()
            try:
                sendmail(str(kwargs.get('survey_list')[0]))

                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='send_email -s mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'Success'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = "-"
                logdata.save()
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logging.error(str(error_stack))
                
                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='send_email -s mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'False'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = e.args[0]
                logdata.save()
        if kwargs.get('survey_list')[0] == 'client_mail':
            start_time = datetime.now()
            try:
                sendmail(str(kwargs.get('survey_list')[0]))
                
                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='send_email -s client_mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'Success'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = "-"
                logdata.save()
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logging.error(str(error_stack))
                
                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='send_email -s client_mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'False'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = e.args[0]
                logdata.save()
        if kwargs.get('survey_list')[0] == 'sync_mail':
            start_time = datetime.now()
            try:
                sendmail(str(kwargs.get('survey_list')[0]))
                
                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='send_email -s sync_mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'Success'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = "-"
                logdata.save()
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logging.error(str(error_stack))
                
                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='send_email -s sync_mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'False'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = e.args[0]
                logdata.save()
        if kwargs.get('survey_list')[0] == 'cron_mail':
            start_time = datetime.now()
            try:
                sendmail(str(kwargs.get('survey_list')[0]))

                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='send_email -s cron_mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'Success'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = "-"
                logdata.save()
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logging.error(str(error_stack))

                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='send_email -s cron_mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'False'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = e.args[0]
                logdata.save()
