# # your_app/management/commands/update_camp_start_end_time.py
   
from django.core.management.base import BaseCommand
from master_data.models import *
from sims.models import *
from datetime import datetime
from django.utils.timezone import localtime
from master_data.views import *

class Command(BaseCommand):
    help = 'Update Start time and End time '

    def handle(self, *args, **options):
        camps = Camp.objects.filter(status=2, date=datetime.now().date())
        start_time = datetime.now()
        try:
            for camp in camps:
                start_date, end_date = camp.get_start_end_date()

                if start_date and end_date:
                    Camp.objects.filter(id=camp.id).update(start_time=localtime(start_date), end_time=localtime(end_date))

            end_time = datetime.now()
            # time_taken_seconds = (end_time - start_time).total_seconds()
            duration = end_time - start_time
            time_output = format_duration(duration)

            logdata, created = CronJobSummaryLog.objects.get_or_create(
                log_key='update_camp_start_end_time')
            logdata.last_successful_update = start_time
            logdata.most_recent_update = end_time
            logdata.most_recent_update_status = 'Success'
            logdata.most_recent_update_time_taken_millis = time_output
            logdata.error = "-"
            logdata.save()
        except Exception as e:
            now = datetime.now()
            end_time = datetime.now()
            # time_taken_seconds = (end_time - start_time).total_seconds()
            duration = end_time - start_time
            time_output = format_duration(duration)

            logdata, created = CronJobSummaryLog.objects.get_or_create(
                log_key='update_camp_start_end_time')
            logdata.last_successful_update = start_time
            logdata.most_recent_update = end_time
            logdata.most_recent_update_status = 'False'
            logdata.most_recent_update_time_taken_millis = time_output
            logdata.error = e.args[0]
            logdata.save()
                 

            
        # camps = Camp.objects.filter(status=2, date=datetime.now().date())
        # patient_obj = Patient.objects.filter(status=2, camp_id__in=camps).order_by('server_created_on')

        # if patient_obj.exists():
        #     start_time = patient_obj.first().server_modified_on
        #     end_time = patient_obj.last().server_modified_on
        #     Camp.objects.filter(status=2,id__in=patient_obj).update(start_time=start_time, end_time=end_time)
        


    
