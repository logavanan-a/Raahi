# # your_app/management/commands/remainder_sms.py

from django.core.management.base import BaseCommand
from sims.views import *
from master_data.models import *
from master_data.views import *

class Command(BaseCommand):
    help = 'Send Remainder mail after 7 days'

    def handle(self, *args, **options):
        start_time = datetime.now()
        try:
            mock_request = self.create_request() 
            remainder_sms(mock_request)

            end_time = datetime.now()
            duration = end_time - start_time
            time_output = format_duration(duration)

            logdata, created = CronJobSummaryLog.objects.get_or_create(
                log_key='remainder_sms')
            logdata.last_successful_update = start_time
            logdata.most_recent_update = end_time
            logdata.most_recent_update_status = 'Success'
            logdata.most_recent_update_time_taken_millis = time_output
            logdata.error = "-"
            logdata.save()

        except Exception as e:
            now = datetime.now()
            end_time = datetime.now()
            duration = end_time - start_time
            time_output = format_duration(duration)

            logdata, created = CronJobSummaryLog.objects.get_or_create(
                log_key='remainder_sms')
            logdata.last_successful_update = start_time
            logdata.most_recent_update = end_time
            logdata.most_recent_update_status = 'False'
            logdata.most_recent_update_time_taken_millis = time_output
            logdata.error = e.args[0]
            logdata.save()

            
    def create_request(self):
        from django.http import HttpRequest
        return HttpRequest()