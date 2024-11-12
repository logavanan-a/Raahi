from django.core.management.base import BaseCommand
from master_data.models import *
from sims.models import *
from datetime import datetime
from django.utils.timezone import localtime
from master_data. views import *

class Command(BaseCommand):
    help = 'Make Patient Inactive '
    def add_arguments(self, parser):
        # Optional argument
        parser.add_argument('-s','--survey_list', type=int, nargs='+')
    def handle(self, *args, **kwargs):
        start_time = datetime.now()
        try:
            if kwargs.get('survey_list')[0] == 1:
                patients_obj = Patient.objects.filter()
                data_list = list({app_created_date.app_created_at.date().strftime('%Y-%m') for app_created_date in patients_obj})
                date_base_list = list(set(data_list + [datetime.now().date().strftime('%Y-%m')]))
                for dv in date_base_list:
                    date_object = dv + '-06'
                    syn_sdate = datetime.strptime(date_object, "%Y-%m-%d").date()
                    from dateutil.relativedelta import relativedelta
                    syn_edate = syn_sdate + relativedelta(months=1)
                    start_date = syn_sdate.strftime('%Y-%m-%d')
                    end_date = syn_edate.strftime('%Y-%m-05')
                    for vc in VisionCenter.objects.filter(status=2):
                        obj, created = DataFreeze.objects.update_or_create(
                            hospital_name=vc.partner,
                            camp=None,
                            vision_center=vc,
                            start_date=start_date,
                            end_date=end_date,
                        )
                    for camp in Camp.objects.filter(status=2):
                        obj, created = DataFreeze.objects.update_or_create(
                            camp=camp,
                            start_date=start_date,
                            end_date=end_date,
                            hospital_name=camp.partner,
                            defaults= {
                                "vision_center": camp.vision_center or None,
                            }
                        ) 
                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='patient_make_inactive -s 1')
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
                log_key='patient_make_inactive -s 1')
            logdata.last_successful_update = start_time
            logdata.most_recent_update = end_time
            logdata.most_recent_update_status = 'False'
            logdata.most_recent_update_time_taken_millis = time_output
            logdata.error = e.args[0]
            logdata.save()
                                
        start_time = datetime.now()
        try:    
            if kwargs.get('survey_list')[0] == 2:
                for df in DataFreeze.objects.all():  
                    if df.camp:
                        pnt_obj=Patient.objects.filter(camp=df.camp)
                        pnt_syn=pnt_obj.filter(app_created_at__date__range=(df.start_date, df.end_date))
                        pnt_not_syn=pnt_syn.filter(data_freeze_status=2,server_created_on__date__gt=df.end_date)
                        pnt_list=', '.join((map(str, list(pnt_not_syn.values_list('id',flat=True)))))
                        pnt_syn.filter(server_created_on__date__range=(df.start_date, df.end_date)).update(data_freeze_status=1)
                        pnt_not_syn.update(status=3)   

                        # sg_obj=Screening.objects.filter(patient_uuid__in=pnt_obj.values_list('uuid',flat=True))
                        # sg_syn=sg_obj.filter(data_freeze_status=2,app_created_at__date__range=(df.start_date, df.end_date))
                        # sg_non_syn=sg_syn.filter(server_created_on__date__gt=df.end_date)
                        # sg_list=', '.join((map(str, list(sg_non_syn.values_list('id',flat=True)))))
                        # sg_syn.filter(server_created_on__date__range=(df.start_date, df.end_date)).update(data_freeze_status=1)
                        # sg_non_syn.update(status=3)

                        # fm_syn=FamilyMember.objects.filter(screening_uuid__in=sg_obj.values_list('uuid',flat=True),app_created_at__date__range=(df.start_date, df.end_date))
                        # fm_non_syn=fm_syn.filter(data_freeze_status=2,server_created_on__date__gt=df.end_date)
                        # fm_list=', '.join((map(str, list(fm_non_syn.values_list('id',flat=True)))))
                        # fm_syn.filter(server_created_on__date__range=(df.start_date, df.end_date)).update(data_freeze_status=1)
                        # fm_non_syn.update(status=3)

                        # gp_obj=GlassPrescription.objects.filter(screening_uuid__in=sg_obj.values_list('uuid',flat=True))
                        # gp_syn=gp_obj.filter(data_freeze_status=2,app_created_at__date__range=(df.start_date, df.end_date))
                        # gp_non_syn=gp_syn.filter(server_created_on__date__gt=df.end_date)
                        # gp_list=', '.join((map(str, list(gp_non_syn.values_list('id',flat=True)))))
                        # gp_syn.filter(server_created_on__date__range=(df.start_date, df.end_date)).update(data_freeze_status=1)
                        # gp_non_syn.update(status=3)

                        # va_syn=VisualAcuity.objects.filter(screening_uuid__in=sg_obj.values_list('uuid',flat=True),app_created_at__date__range=(df.start_date, df.end_date))
                        # va_non_syn=va_syn.filter(data_freeze_status=2,server_created_on__date__gt=df.end_date)
                        # va_list=', '.join((map(str, list(va_non_syn.values_list('id',flat=True)))))
                        # va_syn.filter(server_created_on__date__range=(df.start_date, df.end_date)).update(data_freeze_status=1)
                        # va_non_syn.update(status=3)

                        # st_syn=SpectacleType.objects.filter(glass_prescription_uuid__in=gp_obj.values_list('uuid',flat=True),app_created_at__date__range=(df.start_date, df.end_date))
                        # st_non_syn=st_syn.filter(data_freeze_status=2,server_created_on__date__gt=df.end_date)
                        # st_list=', '.join((map(str, list(st_non_syn.values_list('id',flat=True)))))
                        # st_syn.filter(server_created_on__date__range=(df.start_date, df.end_date)).update(data_freeze_status=1)
                        # st_non_syn.update(status=3)

                        data_freeze=DataFreeze.objects.filter(camp=df.camp,start_date=df.start_date,end_date=df.end_date)
                        # data_freeze.update(no_of_patients_syn=pnt_syn.count(),no_of_patients_not_syn=pnt_not_syn.count(),not_syn_patients_ids=pnt_list,
                        # no_of_screening_syn=sg_syn.count(),no_of_screening_not_syn=sg_non_syn.count(),not_syn_screening_ids=sg_list,
                        # no_of_family_member_syn=fm_syn.count(),no_of_family_member_not_syn=fm_non_syn.count(),not_syn_family_member_ids=fm_list,
                        # no_of_glass_prescription_syn=gp_syn.count(),no_of_glass_prescription_not_syn=gp_non_syn.count(),not_syn_glass_prescription_ids=gp_list,
                        # no_of_visual_acuity_syn=va_syn.count(),no_of_visual_acuity_not_syn=va_non_syn.count(),not_syn_visual_acuity_ids=va_list,
                        # no_of_spectacle_type_syn=st_syn.count(),no_of_spectacle_type_not_syn=st_non_syn.count(),not_syn_spectacle_type_ids=st_list,
                        # )
                        
                    else:
                        pnt_obj=Patient.objects.filter(vision_center_id=df.vision_center.id,camp__isnull=True)
                        pnt_syn=pnt_obj.filter(app_created_at__date__range=(df.start_date, df.end_date))
                        pnt_not_syn=pnt_syn.filter(data_freeze_status=2,server_created_on__date__gt=df.end_date)
                        pnt_list=', '.join((map(str, list(pnt_not_syn.values_list('id',flat=True)))))
                        pnt_syn.filter(server_created_on__date__range=(df.start_date, df.end_date)).update(data_freeze_status=1)
                        pnt_not_syn.update(status=3)
                        data_freeze=DataFreeze.objects.filter(vision_center_id=df.vision_center.id,camp__isnull=True,start_date=df.start_date,end_date=df.end_date)
                        
                    sg_all_obj=Screening.objects.filter()
                    sg_obj=sg_all_obj.filter(patient_uuid__in=pnt_obj.values_list('uuid',flat=True))
                    sg_syn=sg_obj.filter(app_created_at__date__range=(df.start_date, df.end_date))
                    sg_non_syn=sg_syn.filter(data_freeze_status=2,server_created_on__date__gt=df.end_date)
                    sg_list=', '.join((map(str, list(sg_non_syn.values_list('id',flat=True)))))
                    sg_syn.filter(server_created_on__date__range=(df.start_date, df.end_date)).update(data_freeze_status=1)
                    sg_non_syn.update(status=3)
                    sg_all_obj.filter(patient_uuid__in=pnt_obj.filter(status=3).values_list('uuid',flat=True)).update(status=3)

                    fm_all_obj=FamilyMember.objects.filter()
                    fm_syn=fm_all_obj.filter(screening_uuid__in=sg_obj.values_list('uuid',flat=True),app_created_at__date__range=(df.start_date, df.end_date))
                    fm_non_syn=fm_syn.filter(data_freeze_status=2,server_created_on__date__gt=df.end_date)
                    fm_list=', '.join((map(str, list(fm_non_syn.values_list('id',flat=True)))))
                    fm_syn.filter(server_created_on__date__range=(df.start_date, df.end_date)).update(data_freeze_status=1)
                    fm_non_syn.update(status=3)
                    fm_all_obj.filter(screening_uuid__in=sg_obj.filter(status=3).values_list('uuid',flat=True)).update(status=3)


                    gp_all_obj=GlassPrescription.objects.filter()
                    gp_obj=gp_all_obj.filter(screening_uuid__in=sg_obj.values_list('uuid',flat=True))
                    gp_syn=gp_obj.filter(app_created_at__date__range=(df.start_date, df.end_date))
                    gp_non_syn=gp_syn.filter(data_freeze_status=2,server_created_on__date__gt=df.end_date)
                    gp_list=', '.join((map(str, list(gp_non_syn.values_list('id',flat=True)))))
                    gp_syn.filter(server_created_on__date__range=(df.start_date, df.end_date)).update(data_freeze_status=1)
                    gp_non_syn.update(status=3)
                    gp_all_obj.filter(screening_uuid__in=sg_obj.filter(status=3).values_list('uuid',flat=True))

                    va_all_obj=VisualAcuity.objects.filter()
                    va_syn=va_all_obj.filter(screening_uuid__in=sg_obj.values_list('uuid',flat=True),app_created_at__date__range=(df.start_date, df.end_date))
                    va_non_syn=va_syn.filter(data_freeze_status=2,server_created_on__date__gt=df.end_date)
                    va_list=', '.join((map(str, list(va_non_syn.values_list('id',flat=True)))))
                    va_syn.filter(server_created_on__date__range=(df.start_date, df.end_date)).update(data_freeze_status=1)
                    va_non_syn.update(status=3)
                    va_all_obj.filter(screening_uuid__in=sg_obj.filter(status=3).values_list('uuid',flat=True))


                    st_all_obj=SpectacleType.objects.filter()
                    st_syn=st_all_obj.filter(glass_prescription_uuid__in=gp_obj.values_list('uuid',flat=True),app_created_at__date__range=(df.start_date, df.end_date))
                    st_non_syn=st_syn.filter(data_freeze_status=2,server_created_on__date__gt=df.end_date)
                    st_list=', '.join((map(str, list(st_non_syn.values_list('id',flat=True)))))
                    st_syn.filter(server_created_on__date__range=(df.start_date, df.end_date)).update(data_freeze_status=1)
                    st_non_syn.update(status=3)
                    st_all_obj.filter(glass_prescription_uuid__in=gp_obj.filter(status=3).values_list('uuid',flat=True))

                    
                    data_freeze.update(no_of_patients_syn=pnt_syn.count(),no_of_patients_not_syn=pnt_not_syn.count(),not_syn_patients_ids=pnt_list,
                    no_of_screening_syn=sg_syn.count(),no_of_screening_not_syn=sg_non_syn.count(),not_syn_screening_ids=sg_list,
                    no_of_family_member_syn=fm_syn.count(),no_of_family_member_not_syn=fm_non_syn.count(),not_syn_family_member_ids=fm_list,
                    no_of_glass_prescription_syn=gp_syn.count(),no_of_glass_prescription_not_syn=gp_non_syn.count(),not_syn_glass_prescription_ids=gp_list,
                    no_of_visual_acuity_syn=va_syn.count(),no_of_visual_acuity_not_syn=va_non_syn.count(),not_syn_visual_acuity_ids=va_list,
                    no_of_spectacle_type_syn=st_syn.count(),no_of_spectacle_type_not_syn=st_non_syn.count(),not_syn_spectacle_type_ids=st_list,
                    )

                end_time = datetime.now()
                duration = end_time - start_time
                time_output = format_duration(duration)
                logdata, created = CronJobSummaryLog.objects.get_or_create(
                    log_key='patient_make_inactive -s 2')
                logdata.last_successful_update = start_time
                logdata.most_recent_update = end_time
                logdata.most_recent_update_status = 'Success'
                logdata.most_recent_update_time_taken_millis = time_output
                logdata.error = '-'
                logdata.save()
        except Exception as e:
            now = datetime.now()
            end_time = datetime.now()
            duration = end_time - start_time
            time_output = format_duration(duration)
            logdata, created = CronJobSummaryLog.objects.get_or_create(
                log_key='patient_make_inactive -s 2')
            logdata.last_successful_update = start_time
            logdata.most_recent_update = end_time
            logdata.most_recent_update_status = 'False'
            logdata.most_recent_update_time_taken_millis = time_output
            logdata.error = e.args[0]
            logdata.save()
                         

        return 'Data Updated Successfully....'

        
