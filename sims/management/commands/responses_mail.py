from django.core.management.base import BaseCommand
from sims.response_mail import *
from datetime import datetime
from master_data.models import *
from master_data.views import *
# from OBLH_HM.settings import TEMPLATE_DIRS,BASE_DIR
# from health_management.management.commands.materialized_view_refresh import refresh_materialized_view


class Command(BaseCommand):

    help = 'Runs cron for sending mail on survey reponses'
    def add_arguments(self, parser):
        # Optional argument
        parser.add_argument('-s','--survey_list', type=str, nargs='+')
    # C def add_arguments(self, parser):
    # C    parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **kwargs):
        if kwargs.get('survey_list')[0] == 'mail':
            start_time = datetime.now()
            try:
                survey_responses(str(kwargs.get('survey_list')[0]))
                
                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='responses_mail -s mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'Success'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = '-'
                logdata.save()
                    
            except Exception as e:

                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='responses_mail -s mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'False'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = e.args[0]
                logdata.save()

        if kwargs.get('survey_list')[0] == 'client_mail':
            start_time = datetime.now()
            try:
                survey_responses(str(kwargs.get('survey_list')[0]))
                
                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='responses_mail -s client_mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'Success'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = '-'
                logdata.save()
                    
            except Exception as e:
                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='responses_mail -s client_mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'False'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = e.args[0]
                logdata.save()
        
        if kwargs.get('survey_list')[0] == 'sync_mail':
            start_time = datetime.now()
            try:
                survey_responses(str(kwargs.get('survey_list')[0]))
                
                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='responses_mail -s sync_mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'Success'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = '-'
                logdata.save()
                    
            except Exception as e:
                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='responses_mail -s client_mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'False'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = e.args[0]
                logdata.save()

        if kwargs.get('survey_list')[0] == 'cron_mail':
            start_time = datetime.now()
            try:
                survey_responses(str(kwargs.get('survey_list')[0]))
                
                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='responses_mail -s cron_mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'Success'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = '-'
                logdata.save()
                    
            except Exception as e:
                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='responses_mail -s cron_mail')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'False'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = e.args[0]
                logdata.save()


        # refresh_materialized_view()
        # attachment_email()
