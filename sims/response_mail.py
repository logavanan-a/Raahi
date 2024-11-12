from Raahi.settings import *
from sims.models import *
from dashboard.models import *
from django.template import loader
from django.core.mail import send_mail
from send_mail.models import *
from django.utils.timezone import localtime
from django.db.models import Count
import datetime
import sys, traceback
import logging
import os


logger = logging.getLogger(__name__)

def survey_responses(key):
    try:
        from datetime import timedelta
        yesterday = datetime.datetime.now() - timedelta(1)
        filename = f'{MEDIA_ROOT}/logSync/{yesterday.year}/{yesterday.month:02d}/{yesterday.day:02d}/SyncLog-{yesterday.year}-{yesterday.month:02d}-{yesterday.day:02d}.txt'
        error_file = f'{DATABASE_HOST}/media/logSync/{yesterday.year}/{yesterday.month:02d}/{yesterday.day:02d}/SyncLog-{yesterday.year}-{yesterday.month:02d}-{yesterday.day:02d}.txt'
        #checking the file is exists or not
        # print(yesterday.date())
        # print(yesterday.hour)
        # print(yesterday.minute)
        # print(yesterday.second)
        isExist = os.path.exists(filename)
        if isExist:
            with open(filename, "r") as f:
                content = f.read()

            pnt_blank_push = content.count('"patient": []')
            pnt_total_push = content.count('"patient"')
            pnt_res=pnt_total_push-pnt_blank_push
            pnt_success_data = Patient.objects.filter(server_modified_on__date=yesterday.date()).distinct('server_modified_on__hour', )
            sc_blank_push = content.count('"screening": []')
            sc_total_push = content.count('"screening"')
            sc_res=sc_total_push-sc_blank_push

            va_blank_push = content.count('"visual_acuity": []')
            va_total_push = content.count('"visual_acuity"')
            va_res=va_total_push-va_blank_push

            gp_blank_push = content.count('"glass_prescription": []')
            gp_total_push = content.count('"glass_prescription"')
            gp_res=gp_total_push-gp_blank_push

            sp_blank_push = content.count('"spectacle_type": []')
            sp_total_push = content.count('"spectacle_type"')
            sp_res=sp_total_push-sp_blank_push

            fm_blank_push = content.count('"family_members": []')
            fm_total_push = content.count('"family_members"')
            fm_res=fm_total_push-fm_blank_push
            

            non_error = content.count('message": "Data send successfully"')
            total_error = content.count('message')
            error_count=total_error-non_error

            result=[]
            for word in content.splitlines():
                if 'message' in word and word not in result: 
                    if word.strip() != '"message": "Data send successfully",':
                        result.append(word.strip())
                if '"Message":' in word and word not in result: 
                    if word.strip() != '"Message": "Messages Queued",' and word.strip() != '"Message": "Accepted",' and word.strip() != '"Message": "Messages Queued!!",': 
                        result.append(word.strip())

            push_read_column = [
                {"name":"Patient", "empty_push": pnt_blank_push, "non_empty_push":  pnt_res},
                {"name":"Screening", "empty_push": sc_blank_push, "non_empty_push": sc_res},
                {"name":"Family Member", "empty_push": fm_blank_push, "non_empty_push": fm_res},
                {"name":"Visual Acuity", "empty_push": va_blank_push, "non_empty_push": va_res},
                {"name":"Glass Prescription", "empty_push": gp_blank_push, "non_empty_push": gp_res},
                {"name":"Spectacle Type", "empty_push": sp_blank_push, "non_empty_push":  sp_res},
            ]
            form_sync_column = [
                {"name":"File Path -", "count": error_file, },
                {"name":"Total number of ERROR input :-", "count": error_count, },
                {"name":"Error List :-", "count": result, },
            ]  
        else:
            push_read_column = [
                {"name":"Patient", "empty_push": 0, "non_empty_push":  0},
                {"name":"Screening", "empty_push": 0, "non_empty_push": 0},
                {"name":"Family Member", "empty_push": 0, "non_empty_push": 0},
                {"name":"Visual Acuity", "empty_push": 0, "non_empty_push": 0},
                {"name":"Glass Prescription", "empty_push": 0, "non_empty_push": 0},
                {"name":"Spectacle Type", "empty_push": 0, "non_empty_push":  0},
            ]
            form_sync_column = [
                {"name":"File Path -", "count": 0, },
                {"name":"Total number of ERROR input :-", "count": 0, },
                {"name":"Error List :-", "count": 0, },
            ]  
        today = datetime.date.today()
        prev_day = today-timedelta(days=1)
        current_week = prev_day - datetime.timedelta(days=prev_day.weekday())
        current_month = datetime.date.today().replace(day=1)

        patient = Patient.objects.filter(status=2)
        py_c = patient.filter(server_created_on__date=prev_day)
        py_m = [py.id for py in patient.filter(server_modified_on__date=prev_day) if py.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != py.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]
        pcw_c = patient.filter(server_created_on__date__range=[current_week,prev_day])
        pcw_m = [py.id for py in patient.filter(server_modified_on__date__range=[current_week,prev_day]) if py.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != py.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]
        pcm_c = patient.filter(server_created_on__date__range=[current_month,prev_day])
        pcm_m = [py.id for py in patient.filter(server_modified_on__date__range=[current_month,prev_day]) if py.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != py.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]

        screening = Screening.objects.filter(status=2, patient_uuid__in=patient.values_list('uuid', flat=True))
        sy_c = screening.filter(server_created_on__date=prev_day)
        sy_m = [sy.id for sy in screening.filter(server_modified_on__date=prev_day) if sy.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != sy.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]
        scw_c = screening.filter(server_created_on__date__range=[current_week,prev_day])
        scw_m = [sy.id for sy in screening.filter(server_modified_on__date__range=[current_week,prev_day]) if sy.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != sy.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]
        scm_c = screening.filter(server_created_on__date__range=[current_month,prev_day])
        scm_m = [sy.id for sy in screening.filter(server_modified_on__date__range=[current_month,prev_day]) if sy.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != sy.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]

        family_member = FamilyMember.objects.filter(status=2, screening_uuid__in=screening.values_list('uuid', flat=True))
        fmy_c = family_member.filter(server_created_on__date=prev_day)
        fmy_m = [fm.id for fm in family_member.filter(server_modified_on__date=prev_day) if fm.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != fm.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]
        fmcw_c = family_member.filter(server_created_on__date__range=[current_week,prev_day])
        fmcw_m = [fm.id for fm in family_member.filter(server_modified_on__date__range=[current_week,prev_day]) if fm.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != fm.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]
        fmcm_c = family_member.filter(server_created_on__date__range=[current_month,prev_day])
        fmcm_m = [fm.id for fm in family_member.filter(server_modified_on__date__range=[current_month,prev_day]) if fm.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != fm.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]

        visual_acuity = VisualAcuity.objects.filter(status=2, screening_uuid__in=screening.values_list('uuid', flat=True))
        vay_c = visual_acuity.filter(server_created_on__date=prev_day)
        vay_m = [va.id for va in visual_acuity.filter(server_modified_on__date=prev_day) if va.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != va.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]
        vacw_c = visual_acuity.filter(server_created_on__date__range=[current_week,prev_day])
        vacw_m = [va.id for va in visual_acuity.filter(server_modified_on__date__range=[current_week,prev_day]) if va.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != va.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]
        vacm_c = visual_acuity.filter(server_created_on__date__range=[current_month,prev_day])
        vacm_m = [va.id for va in visual_acuity.filter(server_modified_on__date__range=[current_month,prev_day]) if va.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != va.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]

        glass_prescription = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening.values_list('uuid', flat=True))
        gpy_c = glass_prescription.filter(server_created_on__date=prev_day)
        gpy_m = [gp.id for gp in glass_prescription.filter(server_modified_on__date=prev_day) if gp.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != gp.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]
        gpcw_c = glass_prescription.filter(server_created_on__date__range=[current_week,prev_day])
        gpcw_m = [gp.id for gp in glass_prescription.filter(server_modified_on__date__range=[current_week,prev_day]) if gp.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != gp.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]
        gpcm_c = glass_prescription.filter(server_created_on__date__range=[current_month,prev_day])
        gpcm_m = [gp.id for gp in glass_prescription.filter(server_modified_on__date__range=[current_month,prev_day]) if gp.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != gp.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]

        spectacle_type = SpectacleType.objects.filter(status=2,glass_prescription_uuid__in=glass_prescription.values_list('uuid', flat=True))
        sty_c = spectacle_type.filter(server_created_on__date=prev_day)
        sty_m = [st.id for st in spectacle_type.filter(server_modified_on__date=prev_day) if st.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != st.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]
        stcw_c = spectacle_type.filter(server_created_on__date__range=[current_week,prev_day])
        stcw_m = [st.id for st in spectacle_type.filter(server_modified_on__date__range=[current_week,prev_day]) if st.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != st.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]
        stcm_c = spectacle_type.filter(server_created_on__date__range=[current_month,prev_day])
        stcm_m = [st.id for st in spectacle_type.filter(server_modified_on__date__range=[current_month,prev_day]) if st.server_created_on.strftime("%Y-%m-%d %H:%M:%S") != st.server_modified_on.strftime("%Y-%m-%d %H:%M:%S")]


        form_column = [
        {"name":"Patient", "y_c": py_c.count(), "y_m": len(py_m), "cw_c": pcw_c.count(), "cw_m": len(pcw_m), "cm_c": pcm_c.count(), "cm_m": len(pcm_m), "t": patient.count()},
        {"name":"Screening", "y_c": sy_c.count(), "y_m": len(sy_m), "cw_c": scw_c.count(), "cw_m": len(scw_m), "cm_c": scm_c.count(), "cm_m": len(scm_m), "t": screening.count()},
        {"name":"Family Member", "y_c": fmy_c.count(), "y_m": len(fmy_m), "cw_c": fmcw_c.count(), "cw_m": len(fmcw_m), "cm_c": fmcm_c.count(), "cm_m": len(fmcm_m), "t": family_member.count()},
        {"name":"Visual Acuity", "y_c": vay_c.count(), "y_m": len(vay_m), "cw_c": vacw_c.count(), "cw_m": len(vacw_m), "cm_c": vacm_c.count(), "cm_m": len(vacm_m), "t": visual_acuity.count()},
        {"name":"Glass Prescription", "y_c": gpy_c.count(), "y_m": len(gpy_m), "cw_c": gpcw_c.count(), "cw_m": len(gpcw_m), "cm_c": gpcm_c.count(), "cm_m": len(gpcm_m), "t": glass_prescription.count()},
        {"name":"Spectacle Type", "y_c": sty_c.count(), "y_m": len(sty_m), "cw_c": stcw_c.count(), "cw_m": len(stcw_m), "cm_c": stcm_c.count(), "cm_m": len(stcm_m), "t": spectacle_type.count()},
        ]
            

        template_obj = MailTemplate.objects.get(template_name ="Raahi Activity Mailer")
        syn_template_obj = MailTemplate.objects.get(template_name ="Raahi Sync Status")
        cron_template_obj = MailTemplate.objects.get(template_name ="Raahi - Cron Jobs Status Update for")
        send_to_cc = ''
        send_to_bcc = ''
        client_send_to_cc = ''
        client_send_to_bcc = ''
        syn_send_to_cc = ''
        syn_send_to_bcc = ''
        cron_send_to_cc = ''
        cron_send_to_bcc = ''
        if str(key) == 'cron_mail':
            subject = cron_template_obj.subject +' - '+ today.strftime("%d/%m/%Y")
            content = cron_template_obj.content
        elif str(key) == 'sync_mail':
            subject = syn_template_obj.subject +' - '+ today.strftime("%d/%m/%Y")
            content = syn_template_obj.content
        else:
            subject = template_obj.subject +' - '+ today.strftime("%d/%m/%Y")
            content = template_obj.content

        tbody_content = content
        div_content = content
        error_content = content

        dynamic_content = ""
        for form  in form_column:
            survey_name = form["name"]
            yes_response_created = form["y_c"]
            yes_response_modified = form["y_m"]
            current_week_response_created = form["cw_c"]
            current_week_response_modified = form["cw_m"]
            current_month_response_created = form["cm_c"]
            current_month_response_modified = form["cm_m"]
            total_response   = form["t"]
            dynamic_content = dynamic_content + "<tr>  <td>{0}</td> <td>{1}</td>  <td>{2}</td> <td>{3}</td> <td>{4}</td> <td>{5}</td> <td>{6}</td> <td>{7}</td> <tr>".format(survey_name , yes_response_created,yes_response_modified,current_week_response_created,current_week_response_modified,current_month_response_created,current_month_response_modified,total_response)
        content = tbody_content.replace("@@tbody",dynamic_content)
        
        push_dynamic_content = ""
        for push_sync  in push_read_column:
            survey_name = push_sync["name"]
            empty_push = push_sync["empty_push"]
            non_empty_push = push_sync["non_empty_push"]
            push_dynamic_content =  push_dynamic_content + "<tr>  <td>{0}</td> <td>{1}</td>  <td>{2}</td> <tr>".format(survey_name , empty_push, non_empty_push)
        push_content = div_content.replace("@@tbody",push_dynamic_content)

        error_syn_dynamic_content = ""
        for form_sync  in form_sync_column:
            survey_name = form_sync["name"]
            count = form_sync["count"]
            error_syn_dynamic_content = error_syn_dynamic_content + "<p><span><b>{0}</b></span> <span>{1}</span></p>".format(survey_name , count)
        error_syn_content = error_content.replace("@@tbody",error_syn_dynamic_content)

        cron_list = CronJobSummaryLog.objects.filter()
        cron_list_two = DashboardWidgetSummaryLog.objects.filter()
        cron_dynamic_content = ""
        for cron  in cron_list:
            cron_dynamic_content =  cron_dynamic_content + "<tr>  <td>{0}</td> <td>{1}</td>  <td>{2}</td> <td>{3}</td><td>{4}</td><tr>".format(cron.log_key, 
            localtime(cron.most_recent_update).strftime("%d-%m-%Y %I:%M %p"), localtime(cron.last_successful_update).strftime("%d-%m-%Y %I:%M %p"), cron.most_recent_update_time_taken_millis, cron.most_recent_update_status)
        
        for cron  in cron_list_two:
            cron_dynamic_content =  cron_dynamic_content + "<tr>  <td>{0}</td> <td>{1}</td>  <td>{2}</td> <td>{3}</td><td>{4}</td><tr>".format(cron.log_key, 
            localtime(cron.most_recent_update).strftime("%d-%m-%Y %I:%M %p"), localtime(cron.last_successful_update).strftime("%d-%m-%Y %I:%M %p"), cron.most_recent_update_time_taken_millis, cron.most_recent_update_status)
        
        cron_content = error_content.replace("@@tbody",cron_dynamic_content)
        # # to_ = ["girish.n.s@mahiti.org","pervin.d@mahiti.org","dmresearch@akrspi.org"]
        to_ = ';'.join(ACTIVITY_MAIL_RECIEVER)
        send_to_cc = ';'.join(ACTIVITY_MAIL_CC)
        client_to_ = ';'.join(CLIENT_ACTIVITY_MAIL_RECIEVER)
        client_send_to_cc = ';'.join(CLIENT_ACTIVITY_MAIL_CC)
        syn_to_ = ';'.join(SYNC_ACTIVITY_MAIL_RECIEVER)
        syn_send_to_cc = ';'.join(SYNC_ACTIVITY_MAIL_CC)
        cron_to_ = ';'.join(CRON_ACTIVITY_MAIL_RECIEVER)
        cron_send_to_cc = ';'.join(CRON_ACTIVITY_MAIL_CC)
        if str(key) == 'mail':
            send_data_obj = MailData.objects.create(subject = subject,content = content,syn_content=push_content, error_content=error_syn_content, 
                                                    mail_to = to_,mail_cc =send_to_cc,mail_bcc =send_to_bcc,
                                                    priority = 1,mail_status = 1, 
                                                    template_name = template_obj )
            # send_mail(subject,message,"loga.vanan@thesocialbytes.com",to_,fail_silently=False,html_message=html_message)

            return send_data_obj
        if str(key) == 'client_mail':
            client_send_data_obj = MailData.objects.create(subject = subject,content = content,syn_content=push_content, error_content=error_syn_content, 
                                                    client_mail_to = client_to_,client_mail_cc =client_send_to_cc,client_mail_bcc =client_send_to_bcc,
                                                    priority = 1,mail_status = 1, 
                                                    template_name = template_obj )
            # send_mail(subject,message,"loga.vanan@thesocialbytes.com",to_,fail_silently=False,html_message=html_message)

            return client_send_data_obj
        
        if str(key) == 'sync_mail':
            syn_send_data_obj = MailData.objects.create(subject = subject,content = content,syn_content=push_content, error_content=error_syn_content, 
                                                    syn_mail_to = syn_to_,syn_mail_cc =syn_send_to_cc,syn_mail_bcc =syn_send_to_bcc,
                                                    priority = 1,mail_status = 1, 
                                                    template_name = template_obj )
            
        #     # send_mail(subject,message,"loga.vanan@thesocialbytes.com",to_,fail_silently=False,html_message=html_message)

            return syn_send_data_obj
        
        if str(key) == 'cron_mail':

            cron_send_data_obj = MailData.objects.create(subject = subject,content = content,syn_content=push_content, cron_content=cron_content, error_content=error_syn_content, 
                                                    cron_mail_to = cron_to_,cron_mail_cc=cron_send_to_cc,cron_mail_bcc=cron_send_to_bcc,
                                                    priority = 1,mail_status = 1,
                                                    template_name = template_obj )
            
        #     # send_mail(subject,message,"loga.vanan@thesocialbytes.com",to_,fail_silently=False,html_message=html_message)

            return cron_send_data_obj
        

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        errors = str(error_stack) 
        logger.error(errors)


def attachment_email():
    from datetime import timedelta
    today = datetime.date.today()
    prev_day = today-timedelta(days=1)
    template_obj = MailTemplate.objects.get(template_name ="Raahi Activity Mailer")
    send_to_cc = ''
    send_to_bcc = ''
    subject = template_obj.subject
    content = template_obj.content
    content = content.replace("@@date",str(prev_day))
    # to_ = ["girish.n.s@mahiti.org","pervin.d@mahiti.org","dmresearch@akrspi.org"]
    to_ = ';'.join(ACTIVITY_MAIL_RECIEVER)
    send_to_cc = ';'.join(ACTIVITY_MAIL_CC)
    send_data_obj = MailData.objects.create(subject = subject,content = content,mail_to = to_,
                                        mail_cc =send_to_cc,mail_bcc =send_to_bcc,priority = 1,mail_status = 1, 
                                        template_name = template_obj )
  

    send_data_obj.file_paths.append({"filename":"HouseHoldActivity.csv","file_path":"media/export_data/data_dump_survey_425_2021Sep02235336.xlsx","file_type":"csv"})
    send_data_obj.save()
    # send_mail(subject,message,"mis@akrspi.org",to_,fail_silently=False,html_message=html_message)

    return send_data_obj