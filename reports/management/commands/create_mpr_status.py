from django.core.management.base import BaseCommand
from master_data.models import *
from sims.models import *
from reports.models import *
from datetime import datetime
from django.utils.timezone import localtime
from django.db import connection
from datetime import datetime
from master_data.views import *

class Command(BaseCommand):
    help = 'Update Start time and End time '
    def handle(self, *args, **options):
        from dateutil.relativedelta import relativedelta
        start_time = datetime.now()
        try:
            new_time = start_time - relativedelta(months=1)
            current_month_year= str(datetime.now().month)+'-'+str(datetime.now().year)
            user_vlu = UserProfile.objects.filter(role_id=9, status=2).values_list('user_id',flat=True)
            apl_vlu= ApplicationUserStateLinkage.objects.filter(user_id__in=user_vlu, status=2).values_list('state', flat=True)
            pnr_vlu = Partner.objects.filter(status=2, state_id__in=apl_vlu).values_list('id', flat=True)
            month = str(new_time.month).zfill(2)
            year = str(new_time.year)
            for upl in UserPartnerLinkage.objects.filter(status=2, partner_id__in=pnr_vlu):
                if not MprStatusUpdate.objects.filter(created_by=upl.user,mpr_report_code = int(year+month)).exists():
                    mpr_obj =  MprStatusUpdate.objects.create(month=int(month),year=int(year), mpr_report_code = int(year+month),
                                                        created_by=upl.user,partner=upl.partner)
                    mpr_obj.save()
            
            end_time = datetime.now()
            duration = end_time - start_time
            time_output = format_duration(duration)
            logdata, created = CronJobSummaryLog.objects.get_or_create(
                log_key='create_mpr_status')
            logdata.last_successful_update = start_time
            logdata.most_recent_update = end_time
            logdata.most_recent_update_status = 'Success'
            logdata.most_recent_update_time_taken_millis = time_output
            logdata.error = "-"
            logdata.save()
        
            print('Created the MPR Status')

        except Exception as e:

            end_time = datetime.now()
            duration = end_time - start_time
            time_output = format_duration(duration)
            logdata, created = CronJobSummaryLog.objects.get_or_create(
                log_key='create_mpr_status')
            logdata.last_successful_update = start_time
            logdata.most_recent_update = end_time
            logdata.most_recent_update_status = 'False'
            logdata.most_recent_update_time_taken_millis = time_output
            logdata.error = e.args[0]
            logdata.save()
