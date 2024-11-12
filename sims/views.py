from django.shortcuts import render,redirect
from . models import *
from sims.orders import *
from master_data . models import *
from master_data . views import *
from django.http import JsonResponse
import datetime
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import uuid
import datetime
from datetime import datetime
from django.db import connection
from django.http import HttpResponse
import csv
import qrcode
import os
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import SimpleDocTemplate, Image as ReportLabImage, Table, Paragraph, TableStyle, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import utils, colors
from reportlab.lib.units import inch
from reportlab.lib import utils
import logging
import traceback
from .models import UserPartnerLinkage, QrCodeGeneration, UserProfile
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


# Create your views here.
@login_required(login_url='/login/')
def camp_list(request):
    heading = 'Camp List'
    search = request.GET.get('search', '')
    state= State.objects.filter(status=2).order_by('name')
    state_name = request.GET.get('state_name','')
    district_name = request.GET.get('district_name','')
    state_names= int(state_name) if state_name != '' else ''
    district_names= int(district_name) if district_name != '' else ''
    if request.session.get('role_id') == 4:
        user_vision = UserPartnerLinkage.objects.get(user=request.user)
        partner_user = Partner.objects.filter(id=user_vision.partner.id)
        partner_details = Partner.objects.filter(id=user_vision.partner.id).values_list('id', flat=True)
        vision_center_details = VisionCenter.objects.filter(partner_id__in=partner_details).values_list('id', flat=True)
        user_vision_details = UserVisionCenterLinkage.objects.filter(vision_center_id__in=vision_center_details).values_list('vision_center__id', flat=True)
        objects = Camp.objects.select_related('district','donor','vision_center','partner').filter(Q(vision_center__in=user_vision_details)|Q(partner__in=partner_user)|Q(created_by=request.user)).order_by('-id')    
    elif request.session.get('role_id') == 11:
        user_donor = UserDonorLinkage.objects.get(user=request.user)
        donor_user = Donor.objects.filter(id=user_donor.donor.id)
        objects = Camp.objects.select_related('district','donor','vision_center','partner').filter(donor_id__in = donor_user ).order_by('-id')
        
    else:
        objects = Camp.objects.select_related('district','donor','vision_center','partner').filter().order_by('-id')
    if search :
        if request.session.get('role_id') == 4:
            objects=objects.filter(Q(name__icontains=search)|Q(partner__name__icontains =search)|Q(vision_center__name__icontains =search), created_by=request.user).order_by('-id')
        else:
            objects=objects.filter(Q(name__icontains=search)|Q(partner__name__icontains=search)|Q(vision_center__name__icontains =search)).order_by('-id')
    
    if state_name:
        objects=objects.filter(district__state__id=state_name)
        district_obj= District.objects.filter(status=2, state_id=state_name)
    if district_names:
        objects=objects.filter(district_id=district_names)
            
    if request.GET.get('export') == 'true':
        return export_camp_list(objects)    
   
            
    data = pagination_function(request, objects)
    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)

    return render (request, 'camp/camp_list.html', locals())


def export_camp_list(objects):
    current_date = datetime.now().strftime('%Y-%m-%d')
    filename = f"camp_list_{current_date}.csv"

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    writer.writerow(['ID', 'Name', 'Code', 'Date', 'Start Time', 'End Time', 'State', 'District', 'Location', 'Donor', 'Vision Center', 'Partner', 'Status'])

    # Write data rows
    for camp in objects:
        writer.writerow([
            camp.id,
            camp.name if camp.name else '',
            camp.code if camp.code else '',
            camp.date if camp.date else '',
            camp.start_time if camp.start_time else '',
            camp.end_time if camp.end_time else '',
            camp.district.state.name if camp.district.state.name  else '',
            camp.district if camp.district else '',
            camp.location if camp.location else '',
            camp.donor if camp.donor else '',
            camp.vision_center if camp.vision_center else '',
            camp.partner if camp.partner else '',
            camp.status if camp.status else ''
        ])

    return response

@login_required(login_url='/login/')
def add_camp(request):
    heading = 'Add Camp'
    states = State.objects.filter(status=2).order_by('name')
    districts = District.objects.filter(status=2).order_by('name')
    partner_users = UserPartnerLinkage.objects.get(user_id=request.user.id)
    donor_partner = DonorPartnerLinkage.objects.filter(status=2,partner_id=partner_users.partner.id).values_list('donor_id',flat=True)
    donors = Donor.objects.filter(status=2,id__in=donor_partner)
    vision_centers = VisionCenter.objects.filter(partner_id=partner_users.partner.id, status=2)
    user_vision = UserPartnerLinkage.objects.get(user=request.user)
    partner_details = Partner.objects.filter(id=user_vision.partner.id).values_list('id', flat=True)
    camp_code_list = Camp.objects.filter().values_list('code', flat=True)
    camp_code = sorted([int(i) for i in camp_code_list])[-1] + 1
    
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        date = request.POST.get('date')
        location = request.POST.get('location')
        address = request.POST.get('address')
        village = request.POST.get('village')
        block = request.POST.get('block')
        district_id = request.POST.get('district')
        expected_glass_prescription = request.POST.get('expected_glass_prescription')
        expected_refer_surgeries = request.POST.get('expected_refer_surgeries')
        expected_camp_OPD = request.POST.get('expected_camp_OPD')
        donor_id = request.POST.get('donor')
        visioncenter_id = request.POST.get('visioncenter')
        coordinator_name = request.POST.get('coordinator_name')
        coordinator_mobile_no = request.POST.get('coordinator_mobile_no')
        exclusive_camp = request.POST.get('exclusive_camp')
        district = District.objects.get(id=district_id)
        donor = Donor.objects.get(id=donor_id)
        # visioncenter = VisionCenter.objects.get(id=visioncenter_id)
        try:
            visioncenter = VisionCenter.objects.get(id=visioncenter_id)
        except VisionCenter.DoesNotExist:
            visioncenter = None
        curr_dt = datetime.now().strftime("%Y%m%d%H%M%S%f")
        uuid_id = str(curr_dt) + "-" + str(uuid.uuid4())

        camp_details = Camp.objects.create(
            uuid = uuid_id,
            # name=location[0:3].upper() + code,
            name=name,
            code=camp_code,
            date=date,
            location=location,
            address=address,
            village=village,
            block=block,
            district=district,
            expected_glass_prescription=expected_glass_prescription,
            expected_refer_surgeries=expected_refer_surgeries,
            expected_camp_OPD=expected_camp_OPD,
            donor = donor,
            coordinator_name=coordinator_name,
            coordinator_mobile_no=coordinator_mobile_no,
            exclusive_camp = exclusive_camp,
            partner_id = user_vision.partner.id,
            vision_center = visioncenter or None,
            created_by = request.user,
            modified_by = request.user
        )
        camp_details.save()
        return redirect('/camp_list/')

    return render (request,'camp/add_camp.html', locals())

@login_required(login_url='/login/')
def edit_camp(request, id):
    heading = 'Edit Camp'
    states = State.objects.filter(status=2).order_by('name')
    donors = Donor.objects.filter(status=2)
    camp = Camp.objects.get(id=id)
    districts = District.objects.filter(status=2, state_id=camp.district.state.id).order_by('name')
    donor_partner = DonorPartnerLinkage.objects.filter(status=2,partner_id=camp.partner.id).values_list('donor_id',flat=True)
    donors = Donor.objects.filter(status=2,id__in=donor_partner)
    vision_centers = VisionCenter.objects.filter(partner_id=camp.partner.id, status=2)

    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        date = request.POST.get('date')
        location = request.POST.get('location')
        address = request.POST.get('address')
        village = request.POST.get('village')
        block = request.POST.get('block')
        district_id = request.POST.get('district')
        expected_glass_prescription = request.POST.get('expected_glass_prescription')
        expected_refer_surgeries = request.POST.get('expected_refer_surgeries')
        expected_camp_OPD = request.POST.get('expected_camp_OPD')
        donor_id = request.POST.get('donor')
        visioncenter_id = request.POST.get('visioncenter')
        coordinator_name = request.POST.get('coordinator_name')
        coordinator_mobile_no = request.POST.get('coordinator_mobile_no')
        exclusive_camp = request.POST.get('exclusive_camp')

        camp.name = name
        camp.code = code
        camp.date = date
        camp.location = location
        camp.address = address
        camp.village = village
        camp.block = block
        camp.district_id = district_id
        camp.expected_glass_prescription = expected_glass_prescription
        camp.expected_refer_surgeries = expected_refer_surgeries
        camp.expected_camp_OPD = expected_camp_OPD
        camp.donor_id = donor_id
        camp.exclusive_camp = exclusive_camp
        camp.coordinator_name = coordinator_name
        camp.coordinator_mobile_no = coordinator_mobile_no
        camp.modified_by = request.user
        camp.partner_id = camp.partner.id
        camp.vision_center_id = visioncenter_id or None  
        camp.save()
        return redirect('/camp_list/')
    return render(request, 'camp/edit_camp.html', locals())


@login_required(login_url='/login/')
def camp_date_update(request, camp_id, date, reason):
    obj=Camp.objects.get(id=camp_id)
    obj.delay_reason = reason
    obj.date = date
    obj.save()
    return redirect('/camp_list/')


@login_required(login_url='/login/')
def delete_camp(request,id):
    
    obj=Camp.objects.get(id=id)
    if obj.status == 2:
        obj.status=1
    else:
        obj.status=2
    obj.save()
    return redirect('/camp_list/')

@login_required(login_url='/login/')
def drop_check(request):
    heading = 'Check box'
    camps = Camp.objects.all()
    partners = Partner.objects.all()
    if request.method == 'POST':
        selection = request.POST.get('selection')
        if selection == 'camps':
            items = Camp.objects.all()
        elif selection == 'partners':
            items = Partner.objects.all()
        else:
            items = []
    else:
        items = []

    return render(request, 'forms/drop_down_checkbox.html', locals())
    


# for dtl in details_obj:
        
# import ipdb;ipdb.set_trace()



@login_required(login_url='/login/')
def patient_list(request):
    heading = 'Patient List'
    search = request.GET.get('search', '')
    state_name = request.GET.get('state_name','')
    district_name = request.GET.get('district_name','')
    donor_name = request.GET.get('donor_name', '')
    partner_name = request.GET.get('partner_name', '')
    spoke = request.GET.get('spoke', '')
    camp = request.GET.get('camp', '')
    static_center = request.GET.get('static_center', '')
    both = request.GET.get('both', '')
    state_names= int(state_name) if state_name != '' else ''
    district_names= int(district_name) if district_name != '' else ''
    donor_names = int(donor_name) if donor_name != '' else ''
    partner_names = int(partner_name) if partner_name != '' else ''
    spokes = int(spoke) if spoke != '' else ''
    camps = int(camp) if camp != '' else ''
    static_centers = int(static_center) if static_center != '' else ''
    boths = int(both) if both != '' else ''
    district=District.objects.filter(status=2).order_by('name')
    start_filter = request.GET.get('start_filter', '')
    end_filter = request.GET.get('end_filter', '')

    from itertools import chain

    if request.session.get('role_id') == 4:
        partner_users = UserPartnerLinkage.objects.get(user_id=request.user.id)
        donor_partner = DonorPartnerLinkage.objects.filter(status=2,partner_id=partner_users.partner.id).values_list('donor_id',flat=True)
        donors = Donor.objects.filter(status=2,id__in=donor_partner).order_by('name')
        vision_centers = VisionCenter.objects.filter(partner_id=partner_users.partner.id).order_by('name')
        camp_obj = Camp.objects.filter(Q(vision_center__in=vision_centers) | Q(partner_id=partner_users.partner.id),status=2).order_by('name')
        both_obj = list(chain(vision_centers, camp_obj))
        partners = Partner.objects.filter(id__in=[partner_users.partner_id]).order_by('name')
        partner_state_ids = partners.values_list('state_id', flat=True)  
        state = State.objects.filter(id__in=partner_state_ids)  
    else:
        state=State.objects.filter(status=2).order_by('name')
        vision_centers = VisionCenter.objects.filter().order_by('name')
        camp_obj = Camp.objects.filter().order_by('name')
        both_obj = list(chain(vision_centers, camp_obj))
        partners = Partner.objects.filter(state_id=state_names if state_names else None).order_by('name')
        donor_partner = DonorPartnerLinkage.objects.filter(status=2,partner_id__in=partners).values_list('donor_id',flat=True)
        donors = Donor.objects.filter(status=2,id__in=donor_partner).order_by('name')
    search_id = ""
    if search:
        search_id = "AND (pt.name LIKE '%{}%' OR pt.patient_unique_id LIKE '%{}%' OR pt.contact_1 LIKE '%{}%')".format(search, search, search)

    state_id = ""
    if state_name:
        district_obj= District.objects.filter(status=2, state_id=state_name)
        state_id = "AND pt.part_state_id = '{}'".format(state_name)

    # district_id = ""
    # if district_name:
    #     district_id = "AND pt.district_id = '{}'".format(district_name)
    
    donor_id=""
    if donor_name:
        donor_id = "AND pt.donor_id = '{}'".format(donor_name)
    
    partner_id=""
    if partner_name:
        partner_id = "AND pt.partner_id = '{}'".format(partner_name)

    spoke_id = ""
    if spoke == '1':
        spoke_id = "AND pt.model_type IN ('{}', '{}')".format(2, 3)
    elif spoke == '2':
        spoke_id = "AND pt.model_type = '{}'".format(spoke)
    elif spoke == '3':
        spoke_id = "AND pt.model_type = '{}'".format(spoke)

    # import ipdb; ipdb.set_trace()
    
    camp_id=""
    static_center_id = ""
    both_id = ""
    if camp:
        camp_id = "AND pt.camp_id = '{}'".format(camp)
    elif static_center:    
        static_center_id = "AND pt.vision_center_id = '{}'".format(static_center)     
    elif both:
        camp_vc_data = int(both)
        
        camp_name = None
        vc_name = None

        try:
            camp_opt = Camp.objects.get(id=camp_vc_data)
            camp_name = camp_opt.name
        except Camp.DoesNotExist:
            pass  

        if camp_name is None:
            try:
                vc_obj = VisionCenter.objects.get(id=camp_vc_data)
                vc_name = vc_obj.name
            except VisionCenter.DoesNotExist:
                pass  
        
        if camp_name:
            condition = "pt.camp_name = '{}'".format(camp_name)
        elif vc_name:
            condition = "pt.vision_center_name = '{}'".format(vc_name)
        else:
            raise ValueError("No matching Camp or VisionCenter found for the provided ID")

        both_id = "AND ({})".format(condition)
    
    start_date = ""
    if start_filter != '' and end_filter != '':
        start_date = "AND pt.registered_date >= '{}' AND pt.registered_date <= '{}'".format(start_filter, end_filter)
        # order = order.filter(server_created_on__gte=start_filter, server_created_on__lte=end_filter).order_by('-server_created_on')


    partner_details = ""
    if request.session.get('role_id') == 4:
        user_partner = UserPartnerLinkage.objects.filter(user=request.user).values_list('user', flat=True)
        user_vision = UserPartnerLinkage.objects.get(user=request.user)
        partner_details_queryset = Partner.objects.filter(id=user_vision.partner.id)
        vision_center_details = VisionCenter.objects.filter(partner_id__in=partner_details_queryset).values_list('id', flat=True)
        user_vision_details = UserVisionCenterLinkage.objects.filter(vision_center_id__in=vision_center_details).values_list('user__id', flat=True)
        user_partner_id = user_partner[0] if user_partner else None
        partner_details = partner_details_queryset.first().id if partner_details_queryset.exists() else None
        objects = f'''SELECT
                pt.patient_uuid,
                pt.patient_unique_id,
                pt.name,
                pt.age,
                CASE
                    WHEN pt.gender_id = 1 THEN 'Male'
                    WHEN pt.gender_id = 2 THEN 'Female'
                    WHEN pt.gender_id = 3 THEN 'Third gender'
                    ELSE '-'
                END AS gender,
                pt.state_name,
                CASE
                    WHEN pt.camp_name IS NOT NULL THEN pt.camp_name
                    ELSE pt.vision_center_name
                END AS hub_spoke,
                pt.partner_name,
                pt.donar_name,
                pt.contact_1,
                pt.registered_date AS formatted_registered_date,
                pt.languages,
                pt.address
            FROM
                patient_basic_info_view pt  
            WHERE
                1=1
                AND pt.partner_id = {partner_details} ''' +search_id +state_id+donor_id+partner_id+spoke_id+camp_id+static_center_id+both_id+start_date+'''
            ORDER BY
                formatted_registered_date DESC;
        '''
    elif request.session.get('role_id') == 11:
        user_donor = UserDonorLinkage.objects.get(user=request.user)
        user_donor_linked = Donor.objects.filter(id=user_donor.donor.id)
        donor_linkage = user_donor_linked.first().id if user_donor_linked.exists() else None
        
        objects = f'''SELECT
                pt.patient_uuid,
                pt.patient_unique_id,
                pt.name,
                pt.age,
                CASE
                    WHEN pt.gender_id = 1 THEN 'Male'
                    WHEN pt.gender_id = 2 THEN 'Female'
                    WHEN pt.gender_id = 3 THEN 'Third gender'
                    ELSE '-'
                END AS gender,
                pt.state_name,
                CASE
                    WHEN pt.camp_name IS NOT NULL THEN pt.camp_name
                    ELSE pt.vision_center_name
                END AS hub_spoke,
                pt.partner_name,
                pt.donar_name,
                pt.contact_1,
                pt.registered_date AS formatted_registered_date,
                pt.languages,
                pt.address
            FROM
                patient_basic_info_view pt  
            WHERE
                1=1
                AND pt.donor_id = {donor_linkage} ''' +search_id +state_id+donor_id+partner_id+spoke_id+camp_id+static_center_id+both_id+start_date+'''
            ORDER BY
                formatted_registered_date DESC;
        '''
    else:
        objects = '''  
            SELECT
                pt.patient_uuid,
                pt.patient_unique_id,
                pt.name,
                pt.age,
                CASE
                    WHEN pt.gender_id = 1 THEN 'Male'
                    WHEN pt.gender_id = 2 THEN 'Female'
                    WHEN pt.gender_id = 3 THEN 'Third gender'
                    ELSE '-'
                END AS gender,
                pt.state_name,
                CASE
                    WHEN pt.camp_name IS NOT NULL THEN pt.camp_name
                    ELSE pt.vision_center_name
                END AS hub_spoke,
                pt.partner_name,
                pt.donar_name,
                pt.contact_1,
                pt.registered_date AS formatted_registered_date,
                pt.languages,
                pt.address
            FROM
                patient_basic_info_view pt  
            where 1=1 '''+search_id +state_id+donor_id+partner_id+spoke_id+camp_id+static_center_id+both_id+start_date+''' order by formatted_registered_date DESC    
        '''
    page_length = request.GET.get('page_length',10)
    patient_obj = SqlHeader(objects)
    data = pagination_function(request, patient_obj)

    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)

    return render(request,'patients/patient_list.html', locals())    

@login_required(login_url='/login/')
def patient_details(request,uuid):
    heading = 'Patient Details'
    states = State.objects.filter(status=2)
    districts = District.objects.filter(status=2)
    details = Patient.objects.get(uuid=uuid)
    # screening = Screening.objects.get(patient_uuid=details.uuid)
    # import ipdb; ipdb.set_trace()
    screening = Screening.objects.filter(patient_uuid=details.uuid).order_by('-server_created_on').first() if details else None
    famil_details = FamilyMember.objects.filter(screening_uuid=screening.uuid).order_by('-server_created_on') if screening else None
    cataract_questions = CataractQuestions.objects.filter(patient_id=details.id).order_by('-server_created_on').first() if details else None
    visual_acuity = VisualAcuity.objects.filter(screening_uuid=screening.uuid).order_by('-server_created_on').first() if screening else None
    glass_prescription = GlassPrescription.objects.filter(screening_uuid=screening.uuid).order_by('-server_created_on').first() if screening else ''
    if glass_prescription:
        spectacles_type = SpectacleType.objects.filter(glass_prescription_uuid=glass_prescription.uuid)
        spectacles_ty = SpectacleType.objects.filter(glass_prescription_uuid=glass_prescription.uuid).first()
        spectacle_r2c = SpectacleType.objects.filter(glass_prescription_uuid=glass_prescription.uuid,spectacle_type_id__in=[100,227]).first()
    else:
        spectacles_type = ['']
        spectacles_ty = ''
        spectacle_r2c = ''
    return render(request,'patients/patient_details.html', locals())  

@login_required(login_url='/login/')
def screening_list(request):
    heading = 'Screening Details'
    search = request.GET.get('search', '')
    state_name = request.GET.get('state_name','')
    district_name = request.GET.get('district_name','')
    state_names= int(state_name) if state_name != '' else ''
    district_names= int(district_name) if district_name != '' else ''
    state=State.objects.filter(status=2).order_by('name')
    district=District.objects.filter(status=2).order_by('name')
    if request.session.get('role_id') == 4:
        objects = Screening.objects.filter(status=2,created_by=request.user).order_by('-id')
    else:
        objects = Screening.objects.filter(status=2).order_by('-id')
    # objects = Screening.objects.filter(status=2).order_by('-id')

    if search:
        objects=objects.filter(name__icontains=search).order_by('-id')
   
    if state_name:
        objects=objects.filter(district__state__id=state_name).order_by('-id')
        district_obj= District.objects.filter(status=2, state_id=state_name)
    if district_names:
        objects=objects.filter(district_id=district_names).order_by('-id')
            
    data = pagination_function(request, objects)
    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)

    return render(request,'screening/screening_list.html', locals()) 


# def int_to_letters(n):
#     if n == 0:
#         return 'a'

#     result = ''
#     while n > 0:
#         n, remainder = divmod(n - 1, 26)
#         result = chr(remainder + ord('a')) + result

#     return result


# @login_required(login_url='/login/')
# def qr_code_generation(request):
#     from reportlab.lib.styles import getSampleStyleSheet
#     import qrcode
#     import os
#     from PIL import Image, ImageDraw, ImageFont

#     # from PIL import Image, ImageDraw, ImageFont
#     heading = 'QR Code Generation'
#     user_vlu = UserPartnerLinkage.objects.get(user_id=request.user.id)
#     state = user_vlu.partner.state.code if user_vlu.partner else ''
#     partner_id = user_vlu.partner.id
#     letters_representation = int_to_letters(partner_id).upper()

#     code = state.split('-')[0] if state else ''
#     rg_no = state.split('-')[-1] if state else ''
#     state = user_vlu.partner.state if user_vlu.partner else ''
#     qr_last_range_to = QrCodeGeneration.objects.filter(
#             status=2, user__user_id=request.user.id
#         ).order_by('-range_to').first()
#     user_id = UserProfile.objects.get(user_id=request.user.id).id
#     range_to_last_value = int(qr_last_range_to.range_to) if qr_last_range_to else 0
#     range_to_value = range_to_last_value + 1
#     last_qr_code_value =  qr_last_range_to.unique_id

#     if request.method == "POST":
#         prefix = request.POST.get('prefix')
#         range_from = request.POST.get('range_from')
#         range_to = request.POST.get('range_to')
#         if not QrCodeGeneration.objects.filter(user__user_id=request.user.id,range_to=range_to).exists():
#             data_value = []
#             image_paths = []
#             pdf_values = []
#             for idx, i in enumerate(range(int(range_from), int(range_to) + 1)):
#                 qr_obj = QrCodeGeneration.objects.create(user_id=user_id, prefix=prefix, 
#                 range_from=range_from, range_to=i)
#                 qr_obj.save()
#                 data = qr_obj.prefix +'-'+ rg_no+letters_representation + '-' + str(qr_obj.range_to)
#                 QrCodeGeneration.objects.filter(id=qr_obj.id).update(unique_id=data)
#                 data_value.append(data)
#                 qr = qrcode.QRCode(
#                     version=1,       # QR code version (1 to 40)
#                     error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
#                     box_size=10,      # Size of each box/pixel in the QR code
#                     border=1          # Border size
#                 )
#                 # Add the data to the QR code instance
#                 qr.add_data(data)
#                 qr.make(fit=True)
#                 # Create a PIL (Python Imaging Library) image from the QR code instance
#                 qr_img = qr.make_image(fill_color="black", back_color="white")
#                 image_path = settings.MEDIA_ROOT + '/' + data+'.png'
#                 text = data
#                 image_width = max(qr_img.size[0], len(text) * 30)  # Adjust width as needed
#                 image_height = qr_img.size[1] + 50  # Adjust height as needed
#                 # image_width = 230
#                 # image_height = 280
#                 image = Image.new("RGB", (image_width, image_height), "white")
#                 draw = ImageDraw.Draw(image)
#                 # Paste QR code at the top-center of the image
#                 qr_position = ((image_width - qr_img.size[0]) // 2, 0)
#                 image.paste(qr_img, qr_position)
#                 ttf_path = os.path.join(settings.BASE_DIR, 'static/fonts/Arial.ttf')

#                 # Draw text at the center of the image
#                 font = ImageFont.truetype(ttf_path, 25)  # You might need to adjust the font path
#                 text_position = ((image_width - len(text) * 15) // 2, qr_img.size[1] + 10)
#                 draw.text(text_position, text, fill="black", font=font)
#                 # Save or display the final image
#                 image.save(image_path)
#                 image_paths.append(image_path)
#             pdf_value_range = str(data_value[0]) + '_to_' + str(data_value[-1])
#             # from PIL import Image, ImageDraw
#             # Create the PDF object, using the buffer as its "file."
#             pdf_path = settings.MEDIA_ROOT + '/pdf_file/' + pdf_value_range+".pdf"

#             from reportlab.platypus import SimpleDocTemplate, Image, Spacer
#             from reportlab.lib.pagesizes import letter
#             from reportlab.lib import utils
#             from reportlab.lib.units import inch
#             doc = SimpleDocTemplate(pdf_path, pagesize=letter)
#             story = []
#             styles = getSampleStyleSheet()
#             # Add Image
#             images = []
#             for value in reversed(image_paths):
#                 img = utils.ImageReader(value)
#                 width, height = img.getSize()
#                 aspect_ratio = height / float(width)
#                 images.insert(0,Image(value, width=80, height=80 * aspect_ratio))
#                 images.insert(1,Image(value, width=80, height=80 * aspect_ratio))
#             main_vlu = []
#             step = 6
#             for i in range(0, len(images), step):
#                 x = i
#                 main_vlu.append(images[x:x+step])
#             from reportlab.platypus import Table
#             table = Table(main_vlu)
#             story.append(table)
#             # Build and Save PDF
#             doc.build(story)
#             for value in image_paths:
#                 os.remove(value)
#             path_open = '/media/pdf_file/' + pdf_value_range+".pdf"
#             return redirect(path_open)
#     return render(request,'user/qr_code.html', locals())


@login_required(login_url='/login/')
def qr_code_generation(request):
    heading = 'QR Code Generation'
    image_paths=None
    try:
        user_vlu = UserPartnerLinkage.objects.get(user_id=request.user.id)
        state = user_vlu.partner.state.code if user_vlu.partner else ''
        code = state.split('-')[0] if state else ''
        rg_no = state.split('-')[-1] if state else ''
        partner_id = user_vlu.partner.id
        letters_representation = int_to_letters(partner_id).upper()
        qr_last_range_to = QrCodeGeneration.objects.filter(
            status=2, user__user_id=request.user.id
        ).order_by('-range_to').first()
        user_id = UserProfile.objects.get(user_id=request.user.id).id
        range_to_last_value = int(qr_last_range_to.range_to) if qr_last_range_to else 0
        range_to_value = range_to_last_value + 1
        last_qr_code_value =  str(state if state!=None else '')+letters_representation+ '-' + str(range_to_last_value)
        if request.method == "POST":
            prefix = request.POST.get('prefix')
            range_from = int(request.POST.get('range_from'))
            range_to = int(request.POST.get('range_to'))+1
            if not QrCodeGeneration.objects.filter(
                user__user_id=request.user.id, range_to=range_to
            ).exists():
                logger.info('718 data_saving-----------')
                
                image_paths, pdf_values = generate_qr_codes(
                    user_id, prefix, range_from, range_to, rg_no, letters_representation
                )

                pdf_path = create_pdf(image_paths, pdf_values)
                return redirect(f'/media/pdf_file/{pdf_path}')
        return render(request, 'user/qr_code.html', locals())
    except ObjectDoesNotExist:
        logger.error('User data not found.')
        exc_type, exc_value, exc_traceback = traceback.format_exc()
        logger.error(exc_traceback)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        exc_type, exc_value, exc_traceback = traceback.format_exc()
        logger.error(exc_traceback)
    finally:
        if image_paths:
            clean_up_images(image_paths)



def generate_qr_codes(user_id, prefix, range_from, range_to, rg_no, letters_representation):
    data_value = []
    image_paths = []
    logger.info('739 data_saving-----------')
    logger.info('745: range_from-range_to: ' + str(range_from) + ":" + str(range_to))
    for i in range(range_from, range_to):
        data = f"{prefix}-{rg_no}{letters_representation}-{i}"
        qr_obj = QrCodeGeneration.objects.create(
            user_id=user_id, prefix=prefix, range_from=range_from, range_to=i,unique_id=data
        )
        qr_obj.save()
        data_value.append(data)
        image_path = create_qr_image(data)
        image_paths.append(image_path)
        # image_paths.insert(1,image_path)
    logger.info('756 data_saving:' + str(data_value[0]) + "---" +str(data_value[-1]))
    return image_paths, data_value

def create_qr_image(data):
    # logger.info('763 data_saving-----------')
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1
    )
    # logger.info('770 data_saving-----------')

    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    image_path = os.path.join(settings.MEDIA_ROOT, f'{data}.png')
    text = data
    image_width = max(qr_img.size[0], len(text) * 30)
    image_height = qr_img.size[1] + 50
    image = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(image)
    qr_position = ((image_width - qr_img.size[0]) // 2, 0)
    image.paste(qr_img, qr_position)

    ttf_path = os.path.join(settings.BASE_DIR, 'static/fonts/Arial.ttf')
    font = ImageFont.truetype(ttf_path, 25)
    text_position = ((image_width - len(text) * 15) // 2, qr_img.size[1] + 10)
    draw.text(text_position, text, fill="black", font=font)
    image.save(image_path)
    
    return image_path


def create_pdf(image_paths, data_value):
    """
    Create a PDF with images arranged in a table format.

    Args:
        image_paths (list): List of file paths for the images to be included in the PDF.
        data_value (list): List of data values used for naming the PDF.

    Returns:
        str: The name of the generated PDF file.
    """
    # Define constants for the PDF
    PDF_MARGIN = 20 / 72.0 * inch  # 20px margin in inches
    IMAGE_WIDTH = 120
    IMAGE_HEIGHT = 120
    IMAGES_PER_ROW = 6
    PADDING = 10
    COL_WIDTH = 1.5 * inch

    # Generate the PDF file name
    pdf_value_range = f"{data_value[0]}_to_{data_value[-1]}"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'pdf_file', f"{pdf_value_range}.pdf")

    # Set up document with margins for padding
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,title=f"{pdf_value_range}.pdf",
                            leftMargin=PDF_MARGIN, rightMargin=PDF_MARGIN,
                            topMargin=PDF_MARGIN, bottomMargin=PDF_MARGIN)
    
    story = []
    styles = getSampleStyleSheet()

    try:
        # Prepare the images with fixed width and height
        images = [
            ReportLabImage(value, width=IMAGE_WIDTH, height=IMAGE_HEIGHT * (utils.ImageReader(value).getSize()[1] / float(utils.ImageReader(value).getSize()[0])))
            for value in image_paths for _ in range(2)
        ]

        # Ensure each row contains exactly 6 images
        rows = [images[i:i + IMAGES_PER_ROW] for i in range(0, len(images), IMAGES_PER_ROW)]
        for row in rows:
            if len(row) < IMAGES_PER_ROW:
                row.extend([''] * (IMAGES_PER_ROW - len(row)))

        # Create the table with centered images and padding
        table = Table(rows, colWidths=[COL_WIDTH] * IMAGES_PER_ROW, hAlign='CENTER')
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), PADDING),
            ('RIGHTPADDING', (0, 0), (-1, -1), PADDING),
            ('TOPPADDING', (0, 0), (-1, -1), PADDING),
            ('BOTTOMPADDING', (0, 0), (-1, -1), PADDING),
        ]))

        # Add some space before the table
        story.append(Spacer(1, 12))
        story.append(table)
        doc.build(story)
    except Exception as e:
        logger.error(f"An error occurred while creating the PDF: {e}")
        exc_type, exc_value, exc_traceback = traceback.format_exc()
        logger.error(exc_traceback)

    return pdf_value_range + ".pdf"

def clean_up_images(image_paths):
    try:
        for path in image_paths:
            os.remove(path)
    except Exception as e:
        logger.error(f"Clean Up PDF: {e}")
        exc_type, exc_value, exc_traceback = traceback.format_exc()
        logger.error(exc_traceback)

# Utility function to convert integer to letters (Example: 1 -> A, 2 -> B, ..., 27 -> AA, ...)
def int_to_letters(num):
    result = ''
    while num:
        num -= 1
        result = chr(num % 26 + 65) + result
        num //= 26
    return result









@login_required(login_url='/login/')
def data_freeze(request):
    
    heading = 'Data Freeze'
    from dateutil.relativedelta import relativedelta
    current_date = datetime.now().date()
    syn_date = current_date + relativedelta(months=1)
    start_date = current_date.strftime('%B %Y')
    end_date = syn_date.strftime('%B %Y')
    state=State.objects.filter(status=2).order_by('name')
    donor_obj = Donor.objects.filter(status=2).order_by('name')
    partner_obj = Partner.objects.filter(status=2).order_by('name')
    camp_obj = Camp.objects.filter(status=2).order_by('name')
    state_name = request.GET.get('state_name','')
    district_name = request.GET.get('district_name','')
    spoke = request.GET.get('spoke', '')
    donor_name = request.GET.get('donor_name', '')
    hospital_name = request.GET.get('hospital_name', '')
    vision_cent = request.GET.get('vision_cent', '')
    camp_name = request.GET.get('camp_name', '')
    from_date_str = request.GET.get('from_date', '')
    to_date_str = request.GET.get('to_date', '')
    camp = request.GET.get('camp', '')
    static_center = request.GET.get('static_center', '')
    both = request.GET.get('both', '')

    camps = int(camp) if camp != '' else ''
    static_centers = int(static_center) if static_center != '' else ''
    boths = int(both) if both != '' else ''
    state_names= int(state_name) if state_name != '' else ''
    district_names= int(district_name) if district_name != '' else ''
    spokes = int(spoke) if spoke != '' else ''
    donor_names = int(donor_name) if donor_name != '' else ''
    hospital_names = int(hospital_name) if hospital_name != '' else ''
    vision_names = int(vision_cent) if vision_cent != '' else ''
    camp_names = int(camp_name) if camp_name != '' else ''

    partner_objs = Partner.objects.filter(status=2).order_by('name')
    
    user = UserProfile.objects.get(user=request.user) 
    app_obj = ApplicationUserStateLinkage.objects.filter(user_id=user.user.id).values_list('state__id', flat=True)
    partner_obj = Partner.objects.filter(state_id__in=app_obj)
    vc_obj = VisionCenter.objects.filter(partner_id__in=partner_obj.values_list('id', flat=True))
    camp_objects = Camp.objects.filter(status=2,partner_id__in=partner_obj.values_list('id', flat=True))
    from itertools import chain

    # Model type
    vision_centers = VisionCenter.objects.filter(status=2).order_by('name')
    camp_obj = Camp.objects.filter(status=2).order_by('name')
    both_obj = list(chain(vision_centers, camp_obj))

    camp_patients = Patient.objects.filter(status=3, camp__in=camp_objects.values_list('id', flat=True)).values_list('uuid',flat=True) 
    vc_patients = Patient.objects.filter(status=3, vision_center_id__in= vc_obj.values_list('id'), camp__isnull=True).values_list('uuid',flat=True)
    merged_list = list(camp_patients) + list(vc_patients)
    list(camp_patients).extend(list(vc_patients))
    merged_list_extend = list(camp_patients)
    patients = Patient.objects.filter(uuid__in=merged_list,status=3)

    data_freeze_obj=DataFreeze.objects.filter().exclude(no_of_patients_not_syn=0,
    no_of_screening_not_syn=0,
    no_of_family_member_not_syn=0,
    no_of_visual_acuity_not_syn=0,
    no_of_glass_prescription_not_syn=0,
    no_of_spectacle_type_not_syn=0).order_by('-no_of_patients_not_syn','-no_of_screening_not_syn','-no_of_family_member_not_syn','-no_of_visual_acuity_not_syn','-no_of_glass_prescription_not_syn','-no_of_spectacle_type_not_syn')

    if state_name:
        data_freeze_obj=data_freeze_obj.filter(Q(camp__district__state_id=state_name)|Q(vision_center__partner__state_id=state_name)).order_by('-id')
        district_obj= District.objects.filter(status=2, state_id=state_name)
    if district_names:
        data_freeze_obj=data_freeze_obj.filter(Q(camp__district_id=district_names)|Q(vision_center__partner__state=district_names)).order_by('-id')
    if spoke == '1':
        data_freeze_obj = camp_objects.filter(id__isnull=False) | camp_objects.filter(id__isnull=True)
    elif spoke == '2':
        data_freeze_obj = camp_objects.filter(id__isnull=False)
    elif spoke == '3':
        data_freeze_obj = camp_objects.filter(id__isnull=True)
    if donor_name:
        data_freeze_obj = data_freeze_obj.filter(Q(camp__donor_id=donor_names)|Q(vision_center__donor_id=donor_names)).order_by('-id')
    if hospital_names:
        data_freeze_obj = data_freeze_obj.filter(Q(camp__partner_id=hospital_names)|Q(vision_center__partner_id=hospital_names)).order_by('-id')
    if vision_names:
        data_freeze_obj = data_freeze_obj.filter(vision_center_id=vision_names).order_by('-id')
    if camp_names:
        data_freeze_obj = data_freeze_obj.filter(camp_id=camp_names).order_by('-id')
    if from_date_str and to_date_str:
        from dateutil import parser

        from_date = parser.parse(from_date_str)
        to_date = parser.parse(to_date_str)

        from_date = from_date.replace(day=5)
        to_date = to_date.replace(day=6)

        if to_date.day < 6:
            to_date = to_date.replace(month=to_date.month, year=to_date.year)  # Ensure the year is not changed
            from_date = (to_date.replace(day=5) - timedelta(days=1)).replace(day=5)
    
        data_freeze_obj = data_freeze_obj.filter(start_date=from_date, end_date=to_date)

    data = pagination_function(request, data_freeze_obj)
    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)

    return render(request,'data_freeze/data_list.html', locals()) 




def data_freezed_patients(request, data_freeze_id):
    heading = 'Data Freeze'
    data_freeze_obj=DataFreeze.objects.get(id=data_freeze_id)

    patient_list=data_freeze_obj.not_syn_patients_ids if data_freeze_obj.not_syn_patients_ids != "" else []
    if patient_list:
        patient_list = [int(num) for num in patient_list.split(',')]
    patients = Patient.objects.filter(id__in=patient_list)

    screening_list=data_freeze_obj.not_syn_screening_ids if data_freeze_obj.not_syn_screening_ids != "" else []
    if screening_list:
        screening_list = [int(num) for num in screening_list.split(',')]
    screening = Screening.objects.filter(id__in=screening_list)

    family_member_list=data_freeze_obj.not_syn_family_member_ids if data_freeze_obj.not_syn_family_member_ids != "" else []
    if family_member_list:
        family_member_list = [int(num) for num in family_member_list.split(',')]
    family_member = FamilyMember.objects.filter(id__in=family_member_list)

    visual_acuity_list=data_freeze_obj.not_syn_visual_acuity_ids if data_freeze_obj.not_syn_visual_acuity_ids != "" else []
    if visual_acuity_list:
        visual_acuity_list = [int(num) for num in visual_acuity_list.split(',')]
    visual_acuity = VisualAcuity.objects.filter(id__in=visual_acuity_list)

    glass_prescription_list=data_freeze_obj.not_syn_glass_prescription_ids if data_freeze_obj.not_syn_glass_prescription_ids != "" else []
    if glass_prescription_list:
        glass_prescription_list = [int(num) for num in glass_prescription_list.split(',')]
    glass_prescription = GlassPrescription.objects.filter(id__in=glass_prescription_list)

    spectacle_type_list=data_freeze_obj.not_syn_spectacle_type_ids if data_freeze_obj.not_syn_spectacle_type_ids != "" else []
    if spectacle_type_list:
        spectacle_type_list = [int(num) for num in spectacle_type_list.split(',')]
    spectacle_type = SpectacleType.objects.filter(id__in=spectacle_type_list)
    # print(screening)
    # visual_acuity = VisualAcuity.objects.filter(screening_uuid__in=screening.values_list('uuid', flat=True))
    # glass_prescription = GlassPrescription.objects.filter(screening_uuid__in=screening.values_list('uuid', flat=True))
    # spectacle_type = SpectacleType.objects.filter(glass_prescription_uuid__in=glass_prescription.values_list('uuid', flat=True))
    return render(request,'data_freeze/data_freezed_patient_list.html', locals()) 

def approve_patient(request, data_freeze_id):
    heading = 'Data Freeze Patients' 
    date = datetime.now().date()
    data_freeze_obj=DataFreeze.objects.get(id=data_freeze_id)
    if request.method == 'POST':
        approved_by = request.POST.get('approved_by', '')
        print(approved_by)
        remarks = request.POST.get('remarks', '')

        patient_list=data_freeze_obj.not_syn_patients_ids if data_freeze_obj.not_syn_patients_ids != "" else []
        if patient_list:
            patient_list = [int(num) for num in patient_list.split(',')]
            Patient.objects.filter(id__in=patient_list).update(status=2, data_freeze_status=1, remarks=remarks, approved_by=request.user, approved_on=date)

        screening_list=data_freeze_obj.not_syn_screening_ids if data_freeze_obj.not_syn_screening_ids != "" else []
        if screening_list:
            screening_list = [int(num) for num in screening_list.split(',')]
            Screening.objects.filter(id__in=screening_list).update(status=2, data_freeze_status=1)

        family_member_list=data_freeze_obj.not_syn_family_member_ids if data_freeze_obj.not_syn_family_member_ids != "" else []
        if family_member_list:
            family_member_list = [int(num) for num in family_member_list.split(',')]
            FamilyMember.objects.filter(id__in=family_member_list).update(status=2, data_freeze_status=1)

        visual_acuity_list=data_freeze_obj.not_syn_visual_acuity_ids if data_freeze_obj.not_syn_visual_acuity_ids != "" else []
        if visual_acuity_list:
            visual_acuity_list = [int(num) for num in visual_acuity_list.split(',')]
            VisualAcuity.objects.filter(id__in=visual_acuity_list).update(status=2, data_freeze_status=1)

        glass_prescription_list=data_freeze_obj.not_syn_glass_prescription_ids if data_freeze_obj.not_syn_glass_prescription_ids != "" else []
        if glass_prescription_list:
            glass_prescription_list = [int(num) for num in glass_prescription_list.split(',')]
            GlassPrescription.objects.filter(id__in=glass_prescription_list).update(status=2, data_freeze_status=1)

        spectacle_type_list=data_freeze_obj.not_syn_spectacle_type_ids if data_freeze_obj.not_syn_spectacle_type_ids != "" else []
        if spectacle_type_list:
            spectacle_type_list = [int(num) for num in spectacle_type_list.split(',')]
            SpectacleType.objects.filter(id__in=spectacle_type_list).update(status=2, data_freeze_status=1)
        data_freeze_obj.approved_by = request.user
        data_freeze_obj.remarks = remarks
        data_freeze_obj.approved_on = date
        data_freeze_obj.not_syn_patients_ids = None
        data_freeze_obj.not_syn_screening_ids = None
        data_freeze_obj.not_syn_family_member_ids = None
        data_freeze_obj.not_syn_visual_acuity_ids = None
        data_freeze_obj.not_syn_glass_prescription_ids = None
        data_freeze_obj.not_syn_spectacle_type_ids = None
        data_freeze_obj.no_of_patients_not_syn = 0
        data_freeze_obj.no_of_screening_not_syn = 0
        data_freeze_obj.no_of_family_member_not_syn = 0
        data_freeze_obj.no_of_visual_acuity_not_syn = 0
        data_freeze_obj.no_of_glass_prescription_not_syn = 0
        data_freeze_obj.no_of_spectacle_type_not_syn = 0
        data_freeze_obj.save()
        return redirect('/data-freeze/')
    return render(request,'data_freeze/approve_freeze_data.html', locals()) 



from django.http import HttpResponse
from django.shortcuts import render
from django.core.management.base import BaseCommand
from master_data.models import *
from sims.models import *
from master_data.android_api import send_sms
from datetime import datetime, timedelta
from django.utils.timezone import localtime

def remainder_sms(request):
    
    current_date = datetime.now().date()
    start_date = current_date - timedelta(days=7)
    spect_type = SpectacleType.objects.filter(status=2,spectacle_status=2, server_created_on__date=start_date)
    # spect_type = SpectacleType.objects.filter(status=2, id=185)
    
    for obj in spect_type:
        glass_collect = obj.glass_collecting_location if obj.glass_collecting_location else None
        otp_vc_camp = None
        otp_vc_camp_location = None
        location_state = glass_collect

        pnt_details = obj.get_pnt_details()[0] if obj.get_pnt_details() else None

        if obj.get_pnt_details()[0] and obj.get_pnt_details()[0].camp:
            otp_vc_camp = obj.get_pnt_details()[0].camp
            otp_vc_camp_location = obj.get_pnt_details()[0].camp.location
        else:
            vc_camp_obj = VisionCenter.objects.filter(id=obj.get_pnt_details()[0].vision_center_id).first() if obj.get_pnt_details()[0] else None
            otp_vc_camp = vc_camp_obj.name if vc_camp_obj else None
            otp_vc_camp_location = vc_camp_obj.address if vc_camp_obj else None
        send_sms(request, None, obj.get_pnt_details()[0].contact_no_1,
                 obj.get_pnt_details()[0].unique_id, otp_vc_camp, otp_vc_camp_location,
                 None, 5, obj.get_pnt_details()[0].language.id,obj.spectacle_status)
    return HttpResponse("SMS sent successfully")


def SqlHeader(query):
    cursor = connection.cursor()
    cursor.execute(query)
    descr = cursor.description
    rows = cursor.fetchall()
    data = [dict(zip([column[0] for column in descr], row)) for row in rows]
    return data