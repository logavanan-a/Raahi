from django.core.management.base import BaseCommand
from django.conf import settings
from sims.models import *
from master_data.android_api import *
import requests
from Raahi.settings import DATABASE_HOST, API_URL, API_KEY, send_sms_num_attempts, SENDER_ID
from django.http import JsonResponse

class Command(BaseCommand):
    help = 'Received SMS every 5 minutes'

    def handle(self, *args, **options):
        # sms_status 1-new, 2-success 3-failed
        send_sms_obj = ReceivedSMS.objects.filter(sms_status=1).order_by('-server_created_on')[:50]
        sms_status= 3 
        for sms in send_sms_obj:
            send_status = 3
            error_info = ''
            try: 
                response_vlu=send_sms_main(sms.content, sms.mobile_no)
                if response_vlu['status'] == "success":
                    send_status = 2
                else: 
                    send_status = 1
                    error_info = response_vlu['message']
            except Exception as e:
                send_status = 1
                logger.error(e.args[0])
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.error(error_stack)
                error_info = error_stack
            sms.no_of_times_attempt = sms.no_of_times_attempt+1
            sms.last_attempt_on = datetime.now()
            if send_status == 2:
                error_info = ''
            elif sms.no_of_times_attempt >= send_sms_num_attempts:
                send_status = 3
            sms.sms_status = send_status
            sms.error_info = error_info
            sms.save()

def send_sms_main(text, mobile_no):
    data = {
                "Text" : text,
                "Number" : "91"+str(mobile_no),
                "SenderId" : SENDER_ID,
                "DRNotifyUrl" : DATABASE_HOST,
                "DRNotifyHttpMethod" : "POST",
                "Message"  : "Accepted",
                "Tool":"API"
            } 

    try:
        response = requests.post(API_URL, json=data, headers={'Authorization': f'Basic {API_KEY}'})
        response.raise_for_status()  
        
        response_data = response.json()
        if response_data.get('Success') == 'True':
            response_vlu = {"status": "success", "message": response_data.get("Message")}
        else:
            response_vlu = {"status": "error", "message": response_data.get("Message")}
    except requests.RequestException as e:
        response_vlu = {"status": "error", "message": str(e)}
    except ValueError as e:
        response_vlu = {"status": "error", "message": "Invalid JSON response"}

    return response_vlu