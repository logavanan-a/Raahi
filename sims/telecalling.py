from django.shortcuts import render,redirect
from . models import *
from master_data . models import *
from master_data . views import *
from . views import *
from django.contrib.auth.decorators import login_required
from master_data . android_api import send_sms 

@login_required(login_url='/login/')
def spectacle_list(request):
    heading = ' Spectacle List'
    search = request.GET.get('search', '')
    page = request.GET.get('page', '1')
    call_group = request.GET.get('call_group', '')

    if request.session.get('role_id') == 4:
        user_vision = UserPartnerLinkage.objects.get(user=request.user)
        partner_details = Partner.objects.filter(id=user_vision.partner.id).values_list('id', flat=True)
        vision_center_details = VisionCenter.objects.filter(partner_id__in=partner_details).values_list('id', flat=True)
        user_vision_details = UserVisionCenterLinkage.objects.filter(vision_center_id__in=vision_center_details).values_list('user__id', flat=True)
            
        # spectacle_list = Patient.objects.filter(status=2,user__user_id__in=user_vision_details).values_list('uuid', flat=True)
        # screening_obj = Screening.objects.filter(status=2, patient_uuid__in=spectacle_list).values_list('uuid', flat=True)
        # glass_pres = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_obj).values_list('uuid', flat=True)
        # spect_type = SpectacleType.objects.filter(status=2, glass_prescription_uuid__in=glass_pres, spectacle_status=3).values_list('glass_prescription_uuid', flat=True)
        # glass_pres_obj = GlassPrescription.objects.filter(status=2, uuid__in=spect_type).values_list('screening_uuid', flat=True)
        # screening_data = Screening.objects.filter(status=2, uuid__in=glass_pres_obj).values_list('patient_uuid', flat=True)
        # patient_list = Patient.objects.filter(status=2, uuid__in=screening_data)
       
        spectacle_patient_list = Patient.objects.filter(status=2,user__user_id__in=user_vision_details).values_list('uuid', flat=True)
        screening_patient_list = Screening.objects.filter(status=2,patient_uuid__in=spectacle_patient_list).values_list('uuid', flat=True)
        glass_pres_patient_list = GlassPrescription.objects.filter(status=2,screening_uuid__in=screening_patient_list).values_list('uuid', flat=True)
        spectacle_type_patient_list = SpectacleType.objects.filter(status=2,spectacle_status=3,glass_prescription_uuid__in=glass_pres_patient_list).values_list('glass_prescription_uuid', flat=True)
        glass_pres_obj_patient_list = GlassPrescription.objects.filter(status=2,uuid__in=spectacle_type_patient_list).values_list('screening_uuid', flat=True)
        screening_data_patient_list = Screening.objects.filter(status=2,uuid__in=glass_pres_obj_patient_list).values_list('patient_uuid', flat=True)
        cataract_details_patient_list = TellicallingQuestionsAndAnswers.objects.filter(status=2,patient__user__user_id__in=user_vision_details).values_list('patient_id', flat=True)
        patient_list = Patient.objects.filter(status=2,id__in=cataract_details_patient_list)

    elif request.session.get('role_id') == 7:
        spectacle_list = Patient.objects.filter(status=2).values_list('uuid', flat=True)
        screening_obj = Screening.objects.filter(status=2, patient_uuid__in=spectacle_list).values_list('uuid', flat=True)
        glass_pres = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_obj).values_list('uuid', flat=True)
        spect_type = SpectacleType.objects.filter(status=2, glass_prescription_uuid__in=glass_pres, spectacle_status=3).values_list('glass_prescription_uuid', flat=True)
        glass_pres_obj = GlassPrescription.objects.filter(status=2, uuid__in=spect_type).values_list('screening_uuid', flat=True)
        screening_data = Screening.objects.filter(status=2, uuid__in=glass_pres_obj).values_list('patient_uuid', flat=True)
        patient_list = Patient.objects.filter(status=2, uuid__in=screening_data)
    else:
        get_spectacles = TellicallingQuestionsAndAnswers.objects.filter(status=2).values_list('patient_id', flat=True)
        patient_list = Patient.objects.filter(status=2, id__in= get_spectacles)
    
    if search:
        if request.session.get('role_id') == 4:
            patient_list = Patient.objects.filter(Q(Q(name__icontains=search)|Q(unique_id__icontains=search)),id__in=cataract_details_patient_list )
        elif request.session.get('role_id') == 7:
            patient_list = Patient.objects.filter(Q(Q(name__icontains=search)|Q(unique_id__icontains=search)),uuid__in=screening_data)
        else:
            patient_list = Patient.objects.filter(Q(Q(name__icontains=search)|Q(unique_id__icontains=search)),id__in= get_spectacles)
    if call_group:
        get_spectacles = TellicallingQuestionsAndAnswers.objects.filter(status=2,call_disposition_group =2 ).values_list('patient_id', flat=True)
        patient_list = Patient.objects.filter(status=2, id__in= get_spectacles)

    data = pagination_function(request, patient_list)
    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)

    return render(request,'telecaller/spectacle/spectacle_list.html', locals())


@login_required(login_url='/login/')
def spectacle_details(request,uuid):
    heading = 'Spectacle Details'
    spectacle_details = Patient.objects.get(uuid=uuid)
    screening_detail = Screening.objects.filter(patient_uuid=spectacle_details.uuid).order_by('-server_created_on').first() if spectacle_details else None
    visual_acuity = VisualAcuity.objects.filter(screening_uuid=screening_detail.uuid).order_by('-server_created_on').first() if screening_detail else None
    glass_pres = GlassPrescription.objects.filter(screening_uuid=screening_detail.uuid).order_by('-server_created_on').first() if screening_detail else None
    spectacles = SpectacleType.objects.filter(glass_prescription_uuid=glass_pres.uuid).order_by('-server_created_on').first() if glass_pres else None
    disposition_choices = MasterLookup.objects.filter(status=2, parent__id=137)
    try:
        telecalling = TellicallingQuestionsAndAnswers.objects.filter(patient_id=spectacle_details).order_by('-server_created_on').first()
    except TellicallingQuestionsAndAnswers.DoesNotExist:
        pass

    telecalling_call_group = TellicallingQuestionsAndAnswers.objects.filter(status=2, call_disposition_group=2, patient_id=spectacle_details)
    comments_choices = MasterLookup.objects.filter(status=2, parent__id=138)
    patient = Patient.objects.filter(status=2)
    
    if request.method == 'POST':
        page = request.GET.get('page')
        patient_id = request.POST.get('patient')
        have_received_spectacles = request.POST.get('yes_no1')
        reason = request.POST.get('reason')
        how_many_days = request.POST.get('how_many_days')
        is_using_spectacles = request.POST.get('yes_no2')
        is_satisfied_with_quality = request.POST.get('yes_no3')
        is_problem_raised = request.POST.get('yes_no4')
        is_satisfied_with_service = request.POST.get('yes_no5')
        has_charges = request.POST.get('yes_no6')
        rating = request.POST.get('yes_no7')
        impact_on_driving = request.POST.get('yes_no8')

        ad_text = request.POST.get('ad')
        disposition_name_id = request.POST.get('disposition_name')
        disposition_name = int(disposition_name_id)
        call_disposition_group_id = request.POST.get('call_disposition_group')
        comments_id = request.POST.get('comments')
        comments_name = int(comments_id)
        agent_comments = request.POST.get('agent_comments')

        try:
            disposition_name_instance = MasterLookup.objects.get(pk=disposition_name)
            comments_name_instance = MasterLookup.objects.get(id=comments_name)

        except MasterLookup.DoesNotExist:
            disposition_name_instance = None
            comments_name_instance = None

        model_instance = TellicallingQuestionsAndAnswers.objects.update_or_create(
            patient_id=spectacle_details.id,
            receive_your_spectacles=have_received_spectacles,
            receiver_spectacles_reason=reason,
            ahmd_spectacles_received=how_many_days,
            currently_using_spectacles=is_using_spectacles,
            satisfied_with_spectacle=is_satisfied_with_quality,
            any_problems_raised=is_problem_raised,
            satisfied_with_our_service=is_satisfied_with_service,
            any_charges_while_collecting=has_charges,
            rate_our_services=rating,
            impact_on_their_driving_after_wearing=impact_on_driving,
            defaults={
                "ad":ad_text,
                "disposition_name":disposition_name_instance,
                "call_disposition_group":call_disposition_group_id,
                "comments":comments_name_instance,
                "agent_comments":agent_comments
            }
        )
        
        return redirect('/spectacle-list/?page='+str(page))  
        
    # role_slug = request.session.get('role_slug')
    # if role_slug == 7:
    if request.session.get('role_id') == 7:
        return render(request,'telecaller/spectacle/add_questions.html', locals()) 
    else:
        return render(request,'telecaller/spectacle/spectacle_details.html', locals()) 

@login_required(login_url='/login/')
def cataract_list(request):
    heading = ' Cataract List'
    search = request.GET.get('search', '')
    call_group = request.GET.get('call_group', '')
    page = request.GET.get('page', '1')

    if request.session.get('role_id') == 4 :
        user_vision = UserPartnerLinkage.objects.get(user=request.user)
        partner_details = Partner.objects.filter(id=user_vision.partner.id).values_list('id', flat=True)
        vision_center_details = VisionCenter.objects.filter(partner_id__in=partner_details).values_list('id', flat=True)
        user_vision_details = UserVisionCenterLinkage.objects.filter(vision_center_id__in=vision_center_details).values_list('user__id', flat=True)
                
        # cataract_details = Patient.objects.filter(status=2,user__user_id__in=user_vision_details).values_list('uuid',flat=True)
        # screening_obj = Screening.objects.filter(patient_uuid__in=cataract_details).values_list('uuid',flat=True)
        # visual_obj = VisualAcuity.objects.filter(screening_uuid__in=screening_obj,refer_for__in = [123,124]).values_list('screening_uuid',flat=True)
        # screening_uuid_obj = Screening.objects.filter(uuid__in=visual_obj).values_list('patient_uuid',flat=True)

        # patient_list = Patient.objects.filter(status=2,uuid__in=screening_uuid_obj)
        cataract_details = CataractQuestions.objects.filter(status=2,patient__user__user_id__in=user_vision_details).values_list('patient_id', flat=True)
        patient_list = Patient.objects.filter(status=2,id__in=cataract_details)

    elif request.session.get('role_id') == 7:
        cataract_details = Patient.objects.filter(status=2).values_list('uuid',flat=True)
        screening_obj = Screening.objects.filter(patient_uuid__in=cataract_details).values_list('uuid',flat=True)
        visual_obj = VisualAcuity.objects.filter(screening_uuid__in=screening_obj,refer_for__in = [123,124]).values_list('screening_uuid',flat=True)
        screening_uuid_obj = Screening.objects.filter(uuid__in=visual_obj).values_list('patient_uuid',flat=True)
        patient_list = Patient.objects.filter(status=2,uuid__in=screening_uuid_obj)

    else:
        get_cataract = CataractQuestions.objects.filter(status=2).values_list('patient_id', flat=True)
        patient_list = Patient.objects.filter(status=2, id__in= get_cataract)
    
    if search:
        if request.session.get('role_id') == 4:
            patient_list = Patient.objects.filter(Q(Q(name__icontains=search)|Q(unique_id__icontains=search)),id__in=cataract_details )
        elif request.session.get('role_id') == 7:
            patient_list = Patient.objects.filter(Q(Q(name__icontains=search)|Q(unique_id__icontains=search)),uuid__in=screening_uuid_obj)
        else:
            patient_list = Patient.objects.filter(Q(Q(name__icontains=search)|Q(unique_id__icontains=search)),id__in= get_cataract)
    if call_group:
        get_cataract = CataractQuestions.objects.filter(status=2, call_disposition_group = 2).values_list('patient_id', flat=True)
        patient_list = Patient.objects.filter(status=2, id__in= get_cataract)
    
    data = pagination_function(request, patient_list)
    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)

    return render(request,'telecaller/cataract/cataract_list.html', locals()) 

@login_required(login_url='/login/')
def cataract_details(request,uuid):
    heading = 'Cataract Details'
    cataract_details = Patient.objects.get(uuid=uuid)
    screening_detail = Screening.objects.filter(patient_uuid=cataract_details.uuid).order_by('-server_created_on').first() if cataract_details else None
    visual_acuity = VisualAcuity.objects.filter(screening_uuid=screening_detail.uuid).order_by('-server_created_on').first() if screening_detail else None
    glass_pres = GlassPrescription.objects.filter(screening_uuid=screening_detail.uuid).order_by('-server_created_on').first() if screening_detail else None
   
    # telecalling = CataractQuestions.objects.get(patient_id=cataract_details)
    disposition_choices = MasterLookup.objects.filter(status=2, parent__id=137)
    comments_choices = MasterLookup.objects.filter(status=2, parent__id=138)

    patient = Patient.objects.filter(status=2)
    try:
        telecalling = CataractQuestions.objects.filter(patient_id=cataract_details).order_by('-server_created_on').first()
        # telecalling = CataractQuestions.objects.get(patient_id=cataract_details).order_by('-server_created_on').first()
    except CataractQuestions.DoesNotExist:
        pass
    catract_call_group = CataractQuestions.objects.filter(status=2, call_disposition_group=2, patient_id=cataract_details)

    if request.method == 'POST':
        page = request.GET.get('page')
        patient_id = request.POST.get('patient')
        have_received_spectacles = request.POST.get('yes_no1')
        reason_cataract = request.POST.get('reason_cataract')
        visited_hospital = request.POST.get('yes_no2')
        reason_visited_hospital = request.POST.get('reason_visited_hospital')
        hospital_recomand_cataract_surgery = request.POST.get('yes_no3')
        reason_cataract_surgery = request.POST.get('reason_cataract_surgery')
        undergo_surgery = request.POST.get('yes_no4')
        reason_undergo_surgery = request.POST.get('reason_undergo_surgery')
        place_cataract_surgery = request.POST.get('place_cataract_surgery')
        date_cataract_surgery = request.POST.get('date_cataract_surgery')
        free_or_paid = request.POST.get('free_or_paid')
        how_it_paid = request.POST.get('how_it_paid')
        improvement_vision = request.POST.get('improvement_vision')
        helpful_for_driving = request.POST.get('helpful_for_driving')
        beneficiary_feed_back = request.POST.get('beneficiary_feed_back')
        ad_text = request.POST.get('ad')
        disposition_name_id = request.POST.get('disposition_name')
        disposition_name = int(disposition_name_id)
        call_disposition_group_id = request.POST.get('call_disposition_group')
        comments_id = request.POST.get('comments')
        comments_name = int(comments_id)
        agent_comments = request.POST.get('agent_comments')

        try:
            disposition_name_instance = MasterLookup.objects.get(id=disposition_name)
            comments_name_instance = MasterLookup.objects.get(id=comments_name)
        except MasterLookup.DoesNotExist:
            disposition_name_instance = None
            comments_name_instance = None

        model_instance = CataractQuestions.objects.update_or_create(
            patient_id=cataract_details.id,
            referred_to_hospital_for_cataract=have_received_spectacles,
            reason_for_cataract_no=reason_cataract,
            visited_hospital=visited_hospital,
            reason_for_visited_hospital_no=reason_visited_hospital,
            hospital_recomand_cataract_surgery=hospital_recomand_cataract_surgery,
            reason_for_hospital_recomand_cataract_surgery_no=reason_cataract_surgery,
            undergo_surgery=undergo_surgery,
            reason_for_undergo_surgery_no=reason_undergo_surgery,
            place_cataract_surgery=place_cataract_surgery,
            date_cataract_surgery=date_cataract_surgery or None,
            treatment_free=free_or_paid or None,
            how_it_paid=how_it_paid or None,
            improvement_vision=improvement_vision,
            helpful_for_driving=helpful_for_driving,
            beneficiary_feed_back=beneficiary_feed_back,

            defaults={
                "ad":ad_text,
                "disposition_name":disposition_name_instance,
                "call_disposition_group":call_disposition_group_id,
                "comments":comments_name_instance,
                "agent_comments":agent_comments
            }
            )

        return redirect('/cataract-list/?page='+str(page))  


    if request.session.get('role_id') == 7:
        return render(request,'telecaller/cataract/add_question.html', locals()) 
    else:
        return render(request,'telecaller/cataract/cataract_details.html', locals()) 

@login_required(login_url='/login/')
def add_questions(request):
    heading = 'Tele Calling Questions'
    tele_questions = TellicallingQuestionsAndAnswers.objects.filter(status=2)
    disposition_choices = MasterLookup.objects.filter(status=2, parent__id=137)
    call_disposition_choices = TellicallingQuestionsAndAnswers.objects.filter(call_disposition_group__id=139)  #no use
    comments_choices = MasterLookup.objects.filter(status=2, parent__id=138)
    patient = Patient.objects.filter(status=2)
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')  
        receive_your_spectacles = request.POST.get('yes_no1')
        ahmd_spectacles_received = request.POST.get('how_many_days')
        currently_using_spectacles = request.POST.get('yes_no2')
        satisfied_with_spectacle =  request.POST.get('yes_no3')
        any_problems_raised =  request.POST.get('yes_no4')
        satisfied_with_our_service =  request.POST.get('yes_no5')
        any_charges_while_collecting =  request.POST.get('yes_no6')
        rate_our_services =  request.POST.get('yes_no7')
        try:
            patient = Patient.objects.get(id=patient_id)
            obj = TellicallingQuestionsAndAnswers(
                patient=patient,
                receive_your_spectacles=receive_your_spectacles,
                ahmd_spectacles_received=ahmd_spectacles_received,
                currently_using_spectacles=currently_using_spectacles,
                satisfied_with_spectacle=satisfied_with_spectacle,
                any_problems_raised=any_problems_raised,
                satisfied_with_our_service=satisfied_with_our_service,
                any_charges_while_collecting=any_charges_while_collecting,
                rate_our_services=rate_our_services,
            )
            obj.save()
            return redirect('/spectacle-list/')  
        except Patient.DoesNotExist:
            return HttpResponse('error_page')  

    return render(request,'telecaller/spectacle/add_questions.html', locals()) 

@login_required(login_url='/login/')
def cataract_patient_details(request,uuid):
    heading = 'Cataract Details'
    states = State.objects.filter(status=2)
    districts = District.objects.filter(status=2)
    details = Patient.objects.get(uuid=uuid)
    screening = Screening.objects.filter(patient_uuid=details.uuid).order_by('-server_created_on').first() if details else None
    visual_acuity = VisualAcuity.objects.filter(screening_uuid=screening.uuid).order_by('-server_created_on').first() if screening else None
    glass_prescription = GlassPrescription.objects.filter(screening_uuid=screening.uuid).order_by('-server_created_on').first() if screening else None
    cataract_questions = CataractQuestions.objects.filter(patient_id=details.id).order_by('-server_created_on').first() if details else None
    if glass_prescription:
        spectacles_type = SpectacleType.objects.filter(glass_prescription_uuid=glass_prescription.uuid)
        spectacles_ty = SpectacleType.objects.filter(glass_prescription_uuid=glass_prescription.uuid).first()
    else:
        spectacles_type = ['']
        spectacles_ty = ''

    return render(request,'telecaller/cataract/screening_info.html', locals()) 

@login_required(login_url='/login/')
def spectacle_patient_details(request,uuid):
    heading = 'Patient Details'
    states = State.objects.filter(status=2)
    districts = District.objects.filter(status=2)
    details = Patient.objects.get(uuid=uuid)
    screening = Screening.objects.filter(patient_uuid=details.uuid).order_by('-server_created_on').first() if details else None
    visual_acuity = VisualAcuity.objects.filter(screening_uuid=screening.uuid).order_by('-server_created_on').first() if screening else None
    glass_prescription = GlassPrescription.objects.filter(screening_uuid=screening.uuid).order_by('-server_created_on').first() if screening else None
    cataract_questions = CataractQuestions.objects.filter(patient_id=details.id).order_by('-server_created_on').first() if details else None
    if glass_prescription:
        spectacles_type = SpectacleType.objects.filter(glass_prescription_uuid=glass_prescription.uuid)
        spectacles_ty = SpectacleType.objects.filter(glass_prescription_uuid=glass_prescription.uuid).first()
    else:
        spectacles_type = ['']
        spectacles_ty = ''
    return render(request,'telecaller/spectacle/screening_info.html', locals()) 
    

@login_required(login_url='/login/')
def glass_list_pending(request):
    heading = 'glass Pending List'
    search = request.GET.get('search', '')
    if request.session.get('role_id') == 4:
        user_vision = UserPartnerLinkage.objects.get(user=request.user)
        partner_details = Partner.objects.filter(id=user_vision.partner.id).values_list('id', flat=True)
        vision_center_details = VisionCenter.objects.filter(partner_id__in=partner_details).values_list('id', flat=True)
        user_vision_details = UserVisionCenterLinkage.objects.filter(vision_center_id__in=vision_center_details).values_list('user__id', flat=True)
        patient = Patient.objects.filter(status=2, user__user_id__in=user_vision_details).values_list('uuid', flat=True)
        screening_obj = Screening.objects.filter(status=2, patient_uuid__in=patient).values_list('uuid', flat=True)
        glass_pres = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_obj).values_list('uuid', flat=True)
        spectacle_details = SpectacleType.objects.filter(status=2, glass_prescription_uuid__in=glass_pres, spectacle_status=1).order_by('-server_created_on')

        # spectacle_details = SpectacleType.objects.filter(status=2,spectacle_status=1).order_by('-server_created_on')
    elif request.session.get('role_id') == 11:
        user_donor = UserDonorLinkage.objects.get(user=request.user)
        donor_user = Donor.objects.filter(id=user_donor.donor.id)
        patient = Patient.objects.filter(status=2, donor_id__in=donor_user).values_list('uuid', flat=True)
        screening_obj = Screening.objects.filter(status=2, patient_uuid__in=patient).values_list('uuid', flat=True)
        glass_pres = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_obj).values_list('uuid', flat=True)
        spectacle_details = SpectacleType.objects.filter(status=2, glass_prescription_uuid__in=glass_pres, spectacle_status=1).order_by('-server_created_on')
    else:
        spectacle_details = SpectacleType.objects.filter(status=2,spectacle_status=1).order_by('-server_created_on')

    if search:
        if request.session.get('role_id') == 4:
            patient = Patient.objects.filter(Q(Q(name__icontains=search)|Q(unique_id__icontains=search)|Q(contact_no_1__icontains=search)),user__user_id__in=user_vision_details ).values_list('uuid', flat=True)
            screening_obj = Screening.objects.filter(status=2, patient_uuid__in=patient).values_list('uuid', flat=True)
            glass_pres = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_obj).values_list('uuid', flat=True)
            spectacle_details = spectacle_details.filter(status=2,  glass_prescription_uuid__in=glass_pres, spectacle_status=1).order_by('-id')
        else:
            patient = Patient.objects.filter(Q(Q(name__icontains=search)|Q(unique_id__icontains=search)|Q(contact_no_1__icontains=search))).values_list('uuid', flat=True)
            screening_obj = Screening.objects.filter(status=2, patient_uuid__in=patient).values_list('uuid', flat=True)
            glass_pres = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_obj).values_list('uuid', flat=True)
            spectacle_details = spectacle_details.filter(status=2, glass_prescription_uuid__in=glass_pres, spectacle_status=1).order_by('-id')

    data = pagination_function(request, spectacle_details)
    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)

    return render(request,'glass/glass_pending_list.html', locals())

@login_required(login_url='/login/')
def glass_list_ready(request):
    heading = 'glass Ready List'
    search = request.GET.get('search', '')
    if request.session.get('role_id') == 4:
        user_vision = UserPartnerLinkage.objects.get(user=request.user)
        partner_details = Partner.objects.filter(id=user_vision.partner.id).values_list('id', flat=True)
        vision_center_details = VisionCenter.objects.filter(partner_id__in=partner_details).values_list('id', flat=True)
        user_vision_details = UserVisionCenterLinkage.objects.filter(vision_center_id__in=vision_center_details).values_list('user__id', flat=True)
        patient = Patient.objects.filter(status=2, user__user_id__in=user_vision_details).values_list('uuid', flat=True)
        screening_obj = Screening.objects.filter(status=2, patient_uuid__in=patient).values_list('uuid', flat=True)
        glass_pres = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_obj).values_list('uuid', flat=True)
        spectacle_details = SpectacleType.objects.filter(status=2, glass_prescription_uuid__in=glass_pres, spectacle_status=2).order_by('-server_created_on')
    elif request.session.get('role_id') == 11:
        user_donor = UserDonorLinkage.objects.get(user=request.user)
        donor_user = Donor.objects.filter(id=user_donor.donor.id)
        patient = Patient.objects.filter(status=2, donor_id__in=donor_user).values_list('uuid', flat=True)
        screening_obj = Screening.objects.filter(status=2, patient_uuid__in=patient).values_list('uuid', flat=True)
        glass_pres = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_obj).values_list('uuid', flat=True)
        spectacle_details = SpectacleType.objects.filter(status=2, glass_prescription_uuid__in=glass_pres, spectacle_status=2).order_by('-server_created_on')
    
    else:
        spectacle_details = SpectacleType.objects.filter(status=2,spectacle_status=2).order_by('-server_created_on')

    if search:
        if request.session.get('role_id') == 4:
            patient = Patient.objects.filter(Q(Q(name__icontains=search)|Q(unique_id__icontains=search)|Q(contact_no_1__icontains=search)),user__user_id__in=user_vision_details ).values_list('uuid', flat=True)
            screening_obj = Screening.objects.filter(status=2, patient_uuid__in=patient).values_list('uuid', flat=True)
            glass_pres = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_obj).values_list('uuid', flat=True)
            spectacle_details = spectacle_details.filter(status=2,  glass_prescription_uuid__in=glass_pres, spectacle_status=2).order_by('-id')
        else:
            patient = Patient.objects.filter(Q(Q(name__icontains=search)|Q(unique_id__icontains=search)|Q(contact_no_1__icontains=search))).values_list('uuid', flat=True)
            screening_obj = Screening.objects.filter(status=2, patient_uuid__in=patient).values_list('uuid', flat=True)
            glass_pres = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_obj).values_list('uuid', flat=True)
            spectacle_details = spectacle_details.filter(status=2, glass_prescription_uuid__in=glass_pres, spectacle_status=2).order_by('-id')

    data = pagination_function(request, spectacle_details)
    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)

    return render(request,'glass/glass_ready_list.html', locals())

@login_required(login_url='/login/')
def glass_list_delivered(request):
    heading = 'glass Delivered List'
    search = request.GET.get('search', '')
    if request.session.get('role_id') == 4:
        user_vision = UserPartnerLinkage.objects.get(user=request.user)
        partner_details = Partner.objects.filter(id=user_vision.partner.id).values_list('id', flat=True)
        vision_center_details = VisionCenter.objects.filter(partner_id__in=partner_details).values_list('id', flat=True)
        user_vision_details = UserVisionCenterLinkage.objects.filter(vision_center_id__in=vision_center_details).values_list('user__id', flat=True)
        patient = Patient.objects.filter(status=2, user__user_id__in=user_vision_details).values_list('uuid', flat=True)
        screening_obj = Screening.objects.filter(status=2, patient_uuid__in=patient).values_list('uuid', flat=True)
        glass_pres = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_obj).values_list('uuid', flat=True)
        spectacle_details = SpectacleType.objects.filter(status=2, glass_prescription_uuid__in=glass_pres, spectacle_status=3).order_by('-server_created_on')

        # spectacle_details = SpectacleType.objects.filter(status=2,spectacle_status=3).order_by('-server_created_on')
    elif request.session.get('role_id') == 11:
        user_donor = UserDonorLinkage.objects.get(user=request.user)
        donor_user = Donor.objects.filter(id=user_donor.donor.id)
        patient = Patient.objects.filter(status=2, donor_id__in=donor_user).values_list('uuid', flat=True)
        screening_obj = Screening.objects.filter(status=2, patient_uuid__in=patient).values_list('uuid', flat=True)
        glass_pres = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_obj).values_list('uuid', flat=True)
        spectacle_details = SpectacleType.objects.filter(status=2, glass_prescription_uuid__in=glass_pres, spectacle_status=3).order_by('-server_created_on')

    else:
        spectacle_details = SpectacleType.objects.filter(status=2,spectacle_status=3).order_by('-server_created_on')

    if search:
        if request.session.get('role_id') == 4:
            patient = Patient.objects.filter(Q(Q(name__icontains=search)|Q(unique_id__icontains=search)|Q(contact_no_1__icontains=search)),user__user_id__in=user_vision_details ).values_list('uuid', flat=True)
            screening_obj = Screening.objects.filter(status=2, patient_uuid__in=patient).values_list('uuid', flat=True)
            glass_pres = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_obj).values_list('uuid', flat=True)
            spectacle_details = spectacle_details.filter(status=2,  glass_prescription_uuid__in=glass_pres, spectacle_status=3).order_by('-id')
        else:
            patient = Patient.objects.filter(Q(Q(name__icontains=search)|Q(unique_id__icontains=search)|Q(contact_no_1__icontains=search))).values_list('uuid', flat=True)
            screening_obj = Screening.objects.filter(status=2, patient_uuid__in=patient).values_list('uuid', flat=True)
            glass_pres = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_obj).values_list('uuid', flat=True)
            spectacle_details = spectacle_details.filter(status=2, glass_prescription_uuid__in=glass_pres, spectacle_status=3).order_by('-id')

    data = pagination_function(request, spectacle_details)
    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)

    return render(request,'glass/glass_delivered_list.html', locals())


# @login_required(login_url='/login/')
# def update_glass_followup_status(request,patient_id,followup_status_id):
#     demo = [int(i) for i in patient_id.split(',') if i]
#     SpectacleType.objects.filter(id__in=demo).update(spectacle_status = followup_status_id)
#     if int(followup_status_id) == 2:
#         return redirect('/glass-list-ready/')
#     else:
#         return redirect('/glass-list-delivered/')
        

def update_glass_followup_status(request, patient_id, followup_status_id):
    patient_ids = [int(i) for i in patient_id.split(',') if i]
    
    SpectacleType.objects.filter(id__in=patient_ids).update(spectacle_status=followup_status_id)
    objs = SpectacleType.objects.filter(status=2,id__in=patient_ids, spectacle_status=followup_status_id)

    for obj in objs:
        
        otp_vc_camp = None
        otp_vc_camp_location = None
        location_state = obj.glass_collecting_location if obj.glass_collecting_location else None

        pnt_details = obj.get_pnt_details()[0] if obj.get_pnt_details() else None

        if pnt_details and pnt_details.camp is not None:
            otp_vc_camp = pnt_details.camp.name
            otp_vc_camp_location = pnt_details.camp.location
        else:
            vc_camp_obj = None
            if pnt_details and pnt_details.vision_center_id:
                vc_camp_obj = VisionCenter.objects.filter(id=pnt_details.vision_center_id).first()

            otp_vc_camp = vc_camp_obj.name if vc_camp_obj else None
            otp_vc_camp_location = vc_camp_obj.address if vc_camp_obj else None
        if int(followup_status_id) == 2:
            send_sms(request, None, pnt_details.contact_no_1,
                     pnt_details.unique_id, otp_vc_camp, otp_vc_camp_location,
                     location_state, 3, pnt_details.language.id, 2)
            return redirect('/glass-list-ready/')
        elif int(followup_status_id) == 3:
            send_sms(request, None, pnt_details.contact_no_1,
                     pnt_details.unique_id, otp_vc_camp, otp_vc_camp_location,
                     None, 6, pnt_details.language.id, 3)
            return redirect('/glass-list-delivered/')
