# your_app/management/commands/update_custom_made_status.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from master_data . models import *
from sims . models import *
from datetime import  timedelta
from django.core.management import call_command
from sims . orders import *
from sims . views import *
from django.core.management import call_command
from django.template.loader import render_to_string
from master_data.views import *

class Command(BaseCommand):
    help = 'Update order status at 12 AM'
    def handle(self, *args, **options):
        from datetime import datetime
        current_date = datetime.now().date()
        custom_date = current_date - timedelta(days=1)
        spectacletype_obj = SpectacleType.objects.filter(status=2, spectacle_name='Custom made', order_id=0, server_created_on__date__lte = custom_date).order_by('-server_created_on')
        # spectacletype_obj = SpectacleType.objects.filter(status=2, spectacle_name='Custom made', order_id=0).order_by('-server_created_on')
        start_time = datetime.now()          
        try:
            for spo in spectacletype_obj:
                
                modify_date = SpectacleType.objects.get(id=spo.id)
                # modify_date.server_created_on = datetime.now()
                # modify_date.save()
                
                try:
                    camp_vlu = Camp.objects.get(id=spo.get_pnt_details()[0].camp_id)
                except:
                    camp_vlu = None
                if camp_vlu is None:
                    order_request_id = 1
                    vision_vlu = VisionCenter.objects.get(id=spo.get_pnt_details()[0].vision_center_id)
                else:
                    order_request_id = 2
                    vision_vlu = None
                try:
                    ship_is = spo.get_partner_shippment_address()[0].id
                except:
                    ship_is = None
                if ship_is:
                    partner_id  = UserVisionCenterLinkage.objects.get(vision_center_id=spo.get_partner_shippment_address()[0].id).vision_center.partner.id
                    pvid  = UserPartnerLinkage.objects.get(partner_id=partner_id).user.id
                    user_name = 'vision'
                else:
                    pvid = spo.get_partner_shippment_address()[1].user.id
                    user_name = 'partner'
                
                order_id = OrderRequest.objects.filter(vision_center_id=vision_vlu,camp_id=camp_vlu,order_status=3,order_for=int(order_request_id),server_created_on__date=modify_date.server_created_on.date()).first()
                if order_id:
                    SpectacleType.objects.filter(id=spo.id).update(order_id=order_id.id)
                if not OrderRequest.objects.filter(vision_center=vision_vlu,camp=camp_vlu,order_status=3,order_for=int(order_request_id),server_created_on__date=modify_date.server_created_on.date()).exists(): 
                    obj, created = OrderRequest.objects.update_or_create(
                        camp=camp_vlu,
                        vision_center=vision_vlu, 
                        approved_on=modify_date.server_created_on.date(),
                        order_status=3,
                        donor_id=spo.get_pnt_details()[0].donor.id, 
                        order_for=int(order_request_id),
                        approved_by_id=95,
                        created_by_id=pvid, 
                        shippment_address=4,
                        defaults={
                            "modified_by_id":pvid,
                        }
                        )
                    print(camp_vlu,modify_date.server_created_on.date(),'camp_vlucamp_vlu')
                    print(vision_vlu,modify_date.server_created_on.date(),'vision_vluvision_vlu')
                    obj.server_created_on = modify_date.server_created_on.date()
                    obj.save()
                    order_dtl_obj = OrderRequestDetails.objects.create(order_request_id=obj.id, product_id=5)
                    order_dtl_obj.save()
                    SpectacleType.objects.filter(id=spo.id).update(order_id=obj.id)
                    dummy_request = self.create_dummy_request()
                    approve_remark(dummy_request, obj.id,3)

            # print
            # if order_id:

            end_time = datetime.now()        
            now = datetime.now()
            # time_taken_seconds = (end_time - start_time).total_seconds()
            duration = end_time - start_time
            time_output = format_duration(duration)

            logdata, created = CronJobSummaryLog.objects.get_or_create(
                log_key='update_custom_made_status')
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
                log_key='update_custom_made_status')
            logdata.last_successful_update = start_time
            logdata.most_recent_update = end_time
            logdata.most_recent_update_status = 'False'
            logdata.most_recent_update_time_taken_millis = time_output
            logdata.error = e.args[0]
            logdata.save()
                 
                    
    def create_dummy_request(self):
        """
        Create a dummy request object for use in management commands.
        """
        from django.http import HttpRequest
        from django.contrib.auth.models import User

        # user = User.objects.first()
        user = User.objects.get(id=2)  

        request = HttpRequest()
        request.user = user

        return request
    