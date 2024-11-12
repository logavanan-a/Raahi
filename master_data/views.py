# from Raahi.settings import DATABASE_HOST
from django.shortcuts import render, redirect
from . models import * 
from django.apps import apps
from django.db.models import Q
from . forms import *
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
import json
from django.conf import settings
from datetime import datetime
from datetime import datetime, timedelta
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import  logging
import sys, traceback
from django.db import transaction
logger = logging.getLogger(__name__)



def pagination_function(request, data):
    records_per_page = 10
    if request.GET.get('page_length'):
        records_per_page = request.GET.get('page_length')
    paginator = Paginator(data, records_per_page)
    page = request.GET.get('page', 1)
    try: 
        pagination = paginator.page(page)
    except PageNotAnInteger:
        pagination = paginator.page(1)
    except EmptyPage:
        pagination = paginator.page(paginator.num_pages)
    return pagination


@login_required(login_url='/login/')
def master_add_form(request, model):
    if model == 'userprofile':
        heading='user profile'
    else:
        heading=model
    user_form = eval(model.title()+'Form') 
    forms=user_form()

    if request.method == 'POST':
        fields = user_form(request.POST)
        if fields.is_valid():
            instance = fields.save()
            instance.code = instance.name
            instance.save()
            return redirect('/list/'+str(model))
        else:
            message = [str(fields.errors[error][0]) for error in fields.errors.as_data()]
            error=''.join(message)
    return render(request, 'user/edit_form.html', locals())

@login_required(login_url='/login/')
def master_details_form(request,model,id):
    heading=model
    if model == 'partner':
        donor_val = DonorPartnerLinkage.objects.filter(partner__id=id)
        model_name=Partner.objects.get(id=id).id
        try:
            user_mapping = UserPartnerLinkage.objects.get(partner_id=model_name).user.id
        except:
            user_mapping = ''
    if model == 'vendor':
        model_name=Vendor.objects.get(id=id).id
        try:
            user_mapping = UserVendorLinkage.objects.get(vendor_id=model_name).user.id
        except:
            user_mapping = ''
            user_prop = ''
    if model == 'visioncenter':
        model_name=VisionCenter.objects.get(id=id).id
        try:
            user_mapping = UserVisionCenterLinkage.objects.get(vision_center_id=model_name).user.id
        except:
            user_mapping = ''
    if model == 'donor':
        model_name=Donor.objects.get(id=id).id
        try:
            user_mapping = UserDonorLinkage.objects.get(donor_id=model_name).user.id
        except:
            user_mapping = ''
    try:
        user_prop = UserProfile.objects.get(user_id=user_mapping)
    except:
        user_prop = ''
    listing_model = apps.get_model(app_label= 'master_data', model_name=model)
    obj=listing_model.objects.get(id=id)
    return render(request, 'user/details_list.html', locals())


@login_required(login_url='/login/')
def master_edit_form(request,model,id):
    if model == 'userprofile':
        heading='user profile'
    else:
        heading=model
   
    if model != 'userprofile':
        listing_model = apps.get_model(app_label= 'master_data', model_name=model)
    else:
        listing_model = apps.get_model(app_label= 'master_data', model_name=model)
    obj=listing_model.objects.get(id=id)
    user_form = eval(model.title()+'Form') 
    
    forms=user_form(request.POST or None,instance=obj)
    if request.method == 'POST' and forms.is_valid():
        page = request.GET.get('page')
        forms.save()
        return redirect('/list/'+str(model)+'/?page='+str(page))
    else:
        message = [str(forms.errors[error][0]) for error in forms.errors.as_data()]
        error=''.join(message)
    return render(request, 'user/edit_form.html', locals())


@login_required(login_url='/login/')
def delete_record(request,model,id):
    page = request.GET.get('page')
    role_name = request.GET.get('role_name')
    
    if model != 'userprofile':
        listing_model = apps.get_model(app_label= 'master_data', model_name=model)
    else:
        listing_model = apps.get_model(app_label= 'master_data', model_name=model)
    obj=listing_model.objects.get(id=id)
    if obj.status == 2:
        obj.status=1
    else:
        obj.status=2
    obj.save()
    return redirect('/list/'+str(model)+'/?page='+str(page)+'&role_name=' + str(role_name))


@login_required(login_url='/login/')
def master_list_form(request,model):
    heading = 'user profile'    
    page = request.GET.get('page', '1')
    state= State.objects.filter(status=2).order_by('name')
    district= District.objects.filter(status=2).order_by('name')
    user_role = Role.objects.filter(status=2).order_by('name')
    partner = Partner.objects.filter(status=2).order_by('name')
    search = request.GET.get('search', '')
    state_name = request.GET.get('state_name','')
    district_name = request.GET.get('district_name','')
    role_name = request.GET.get('role_name', '')
    partner_name = request.GET.get('partner_name', '')
    state_names= int(state_name) if state_name != '' else ''
    district_names= int(district_name) if district_name != '' else ''
    role_names= int(role_name) if role_name != '' else ''
    partner_names= int(partner_name) if partner_name != '' else ''
    headings={
        "state":"state",
        "district":"district",
        "userprofile":"user profile",
        "visioncenter":"vision center"
    }
    heading=headings.get(model,model)
    orderlist='name' if model != 'userprofile' else 'user__username'
    if model != 'userprofile':
        listing_model = apps.get_model(app_label= 'master_data', model_name=model)
    else:
        listing_model = apps.get_model(app_label= 'master_data', model_name=model)
    objects=listing_model.objects.all().order_by('-id')
    
     
    if search and model == 'userprofile':
        objects=objects.filter(user__username__icontains=search).order_by('-id')
    elif search:
        objects=objects.filter(name__icontains=search).order_by('-id')
   
    if model =='vendor':
        if state_name :
            objects=objects.filter(id=state_name).order_by('-id')
    else:
        if state_name :
            objects=objects.filter(state__id=state_name).order_by('-id')
    # if district_name :
    #     objects=objects.filter(district_id=district_name)
    if role_name:
        objects=objects.filter(role__id=role_name)
    if partner_name:
        objects=objects.filter(partner__id=partner_name)


    if state_name and model == '':
        objects=objects.filter(id=state_name).order_by('-id')
    if model =='visioncenter' or model =='partner' or model =='vendor':
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
    return render(request, 'user/list_form.html', locals())

def otp_list(request):
    return render(request, 'sms/otp.html')



@login_required(login_url='/login/')
def user_add(request):
    mail_web = settings.DATABASE_HOST
    heading = 'user profile'
    userrole = Role.objects.filter(role_slug='1').order_by('name')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        role = request.POST.get('role', '')
        role = int(role) if role != '' else None
        try:
            with transaction.atomic():
                if User.objects.filter(username=username).exists():
                    user_exist = "Username already exists"
                    return render(request, 'user/add_userprofile.html', locals())
                if User.objects.filter(email=email).exists():
                    email_exist = "email already exists"
                    return render(request, 'user/add_userprofile.html', locals())
                user=User.objects.create_user(username=username.lower().strip(),password=password, first_name=first_name, email=email)
                user_profile=UserProfile.objects.create(user=user, role_id=role)
                user_profile.save()
                dear = 'Dear  '
                html_message =  render(request, 'mailer/create_user.html', locals()).content.decode("utf-8")
                register_mailer(user_profile.user.email,html_message)
                return redirect('/list/userprofile/')
        except Exception as e:
            logger.error(e.args[0])
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(error_stack)
            error = f"User is not created. Please try again. Error: {str(e)}"
            # error = "User is not created. Please try again."

    return render(request, 'user/add_userprofile.html', locals())

def register_mailer(email,html_message,isTls=True):
    import smtplib
    import os
    from weasyprint import HTML, CSS
    from email.mime.image import MIMEImage
    from email import encoders
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText

    msg = MIMEMultipart()
    msg['From'] = "misindia@sightsaversindia.org"
    msg['To'] = email
    msg['Subject'] = 'Welcome to Raahi'
       
    part=MIMEText(html_message, 'html')
    html_content = html_message
    html = HTML(string=html_content)
    # part = MIMEBase('application', "octet-stream")
    # encoders.encode_base64(part)
    msg.attach(part)
    smtp = smtplib.SMTP(settings.EMAIL_HOST,settings.EMAIL_PORT)

    if isTls:
        smtp.starttls()
    smtp.login(settings.EMAIL_HOST_USER,settings.EMAIL_HOST_PASSWORD)
   
    msg_send_status = smtp.sendmail(msg['From'], msg['To'] ,msg.as_string())
    smtp.quit()
    return msg_send_status

@login_required(login_url='/login/')
def application_user_state_linkage_list(request, user_id):
    heading = 'User State Linkage'
    user_state_linkage = ApplicationUserStateLinkage.objects.filter(user_id=user_id)
    if user_state_linkage:
        linkage_id = user_state_linkage.first().id
    data = pagination_function(request, user_state_linkage)
    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)
    return render(request, 'linkages/application_user_state_list.html', locals())

@login_required(login_url='/login/')
def add_application_user_state_linkage(request, user_id):
    heading = 'Add User State Linkage'
    
    zone_obj = Zone.objects.filter(status=2)
    if request.method == 'POST':
        state = request.POST.getlist('state', '')
        user_state_obj = ApplicationUserStateLinkage.objects.create(user_id=user_id)
        user_state_obj.state.add(*state)
        user_state_obj.save()
        return redirect('/application-user-state-linkage/list/'+str(user_id)+'/')
    return render(request, 'linkages/add_application_user_state_linkage.html', locals())

@login_required(login_url='/login/')
def edit_application_user_state_linkage(request, user_id, id):
    heading = 'Edit application User State Linkage'
    zone_obj = Zone.objects.filter(status=2)
    user_state_obj = ApplicationUserStateLinkage.objects.get(user_id=user_id, id=id)
    user_state = ApplicationUserStateLinkage.objects.filter(user_id=user_id, id=id)
    state_vlu = user_state.values_list('state__id', flat=True)
    zone_vlu = Zone.objects.filter(id__in=user_state.values_list('state__zone__id', flat=True)).first().id
    state_obj = State.objects.filter(status=2, zone__id__in=user_state.values_list('state__zone__id', flat=True))
    if request.method == 'POST':
        state = request.POST.getlist('state', '')
        user_state_obj.user_id = user_id
        user_state_obj.state.clear()
        user_state_obj.state.add(*state)
        user_state_obj.save()
        return redirect('/application-user-state-linkage/list/'+str(user_id)+'/')
    return render(request, 'linkages/add_application_user_state_linkage.html', locals())


@login_required(login_url='/login/')
def vendor_partner_user_mapping(request,vendor_partner_id,model):
    heading = 'user profile'
    mail_web = settings.DATABASE_HOST
    if model == 'partner':
        partner_name=Partner.objects.get(id=vendor_partner_id).name
        heading_vpl = 'Partner -' + str(partner_name)
        role_id=4
        try:
            user_mapping = UserPartnerLinkage.objects.get(partner_id=vendor_partner_id).user.id
            user_profile = UserProfile.objects.get(user_id=user_mapping)
            user_obj = User.objects.get(id=user_profile.user.id)
        except:
            user_mapping = None
            user_profile = None
            user_obj = None
    if model == 'vendor':
        vendor_name=Vendor.objects.get(id=vendor_partner_id).name
        heading_vpl = 'Vendor -' + str(vendor_name)
        role_id=6
        try:
            user_mapping = UserVendorLinkage.objects.get(vendor_id=vendor_partner_id).user.id
            user_profile = UserProfile.objects.get(user_id=user_mapping)
            user_obj = User.objects.get(id=user_profile.user.id)
        except:
            user_mapping = None
            user_profile = None
            user_obj = None
    if model == 'visioncenter':
        vision_name=VisionCenter.objects.get(id=vendor_partner_id).name
        heading_vpl = 'Vision Center -' + str(vision_name)
        role_id=5
        try:
            user_mapping = UserVisionCenterLinkage.objects.get(vision_center_id=vendor_partner_id).user.id
            user_profile = UserProfile.objects.get(user_id=user_mapping)
            user_obj = User.objects.get(id=user_profile.user.id)
        except:
            user_mapping = None
            user_profile = None
            user_obj = None
    if model == 'donor':
        donor_name=Donor.objects.get(id=vendor_partner_id).name
        heading_vpl = 'Donor -' + str(donor_name)
        role_id=11
        try:
            user_mapping = UserDonorLinkage.objects.get(donor_id=vendor_partner_id).user.id
            user_profile = UserProfile.objects.get(user_id=user_mapping)
            user_obj = User.objects.get(id=user_profile.user.id)
        except:
            user_mapping = None
            user_profile = None
            user_obj = None
    userrole = Role.objects.filter(status=2).order_by('name')

        
            
    if request.method == 'POST':
        try:
            with transaction.atomic():
                username = request.POST.get('username')
                email = request.POST.get('email')
                password = request.POST.get('password')
                first_name = request.POST.get('first_name')
                if User.objects.filter(email=email).exclude(id=user_mapping).exists():
                    email_exist = "Email already exists"
                    return render(request, 'user/add_user_link_to_role.html', locals())
                if User.objects.filter(username=username).exclude(id=user_mapping).exists():
                    user_exist = "Username already exists"
                    return render(request, 'user/add_user_link_to_role.html', locals())
                if user_mapping:
                    user_obj.email = email
                    user_obj.username = username.lower()
                    user_obj.first_name=first_name

                    user_obj.save()

                    user_profile.role_id =role_id
                    user_profile.user.set_password(password)
                    user_profile.save()
                else:
                    if User.objects.filter(email=email).exclude(id=user_mapping).exists():   
                        email_exist = "email already exists"
                        return render(request, 'user/add_user_link_to_role.html', locals())
                    user=User.objects.create_user(username=username.lower(),password=password, first_name=first_name, email=email)
                    user_profile=UserProfile.objects.create(user=user, role_id=role_id)
                    user_profile.save()
                    if model == 'partner':
                        partner_obj=UserPartnerLinkage.objects.create(
                            partner_id = vendor_partner_id,
                            user_id = user.id
                        )
                        partner_obj.save()
                    if model == 'vendor':
                        vendor_obj=UserVendorLinkage.objects.create(
                            vendor_id = vendor_partner_id,
                            user_id = user.id
                        )
                        vendor_obj.save()
                    if model == 'visioncenter':
                        visioncenter_obj=UserVisionCenterLinkage.objects.create(
                            vision_center_id = vendor_partner_id,
                            user_id = user.id
                        )
                        visioncenter_obj.save()
                    if model == 'donor':
                        donor_obj=UserDonorLinkage.objects.create(
                            donor_id = vendor_partner_id,
                            user_id = user.id
                        )
                        donor_obj.save()
                dear = 'Dear  '
                html_message =  render(request, 'mailer/create_user.html', locals()).content.decode("utf-8")
                register_mailer(user_profile.user.email,html_message)
            return redirect('/list/userprofile/')
        except Exception as e:
            error = f"User is not created. Please try again. Error: {str(e)}"
    return render(request, 'user/add_user_link_to_role.html', locals())


@login_required(login_url='/login/')
def donor_partner_location_listing(request, partner_id):
    heading = 'Partner Donor location listing'
    donor_parner_obj = DonorPartnerLinkage.objects.filter(partner__id=partner_id)
    data = pagination_function(request, donor_parner_obj)
    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)
    return render(request, 'linkages/donor_location_list.html', locals())



@login_required(login_url='/login/')
def donor_partner_location_mapping(request, partner_id):
    heading = 'Partner Donor location mapping'
    ptr = Partner.objects.get(id=partner_id)
    district_obj = District.objects.filter(state__id=ptr.state.id)
    donor_obj = Donor.objects.filter(status=2)
    heading_vpl = 'Partner - ' + ptr.name
    donor_parner_obj = DonorPartnerLinkage.objects.filter(partner__id=partner_id)
    if request.method == "POST":
        data = request.POST
        for index in range(int(data.get('donor_index','0'))):
            donor_list = data.get('group-a['+str(index)+'][donor]')
            district = data.get('group-a['+str(index)+'][district]')
            obj, created = DonorPartnerLinkage.objects.update_or_create(
                partner_id=partner_id,
                district_id=district,
                donor_id=donor_list,
            )
            obj.save()
        return redirect('/donor-location-listing/'+str(partner_id)+'/')      
    return render(request, 'linkages/add_donor_location.html', locals())

@login_required(login_url='/login/')
def partner_donor_status_update(request, dpl_id):
    dpl_data=DonorPartnerLinkage.objects.get(id=dpl_id)
    if dpl_data.status == 2:
        dpl_data.status = 1
    else:
        dpl_data.status = 2
    dpl_data.save()
    return redirect('/donor-location-listing/'+str(dpl_data.partner.id)+'/')      

@login_required(login_url='/login/')
def user_status_status_update(request, usl_id):
    ausl_data=ApplicationUserStateLinkage.objects.get(id=usl_id)
    if ausl_data.status == 2:
        ausl_data.status = 1
    else:
        ausl_data.status = 2
    ausl_data.save()
    return redirect('/application-user-state-linkage/list/'+str(ausl_data.user_id)+'/')




@login_required(login_url='/login/')    
def user_edit(request, id):
    heading = 'user profile'
    userrole = Role.objects.filter(role_type=0).order_by('name')
    user_profile = UserProfile.objects.get(id=id)
    user_obj = User.objects.get(id=user_profile.user.id)
    # try:
    #     user_partner = UserPartnerLinkage.objects.get(user_id=user_obj.id)
    #     partner_name=Partner.objects.get(id=user_partner.partner.id).name
    #     if partner_name:
    #         heading_vpl = 'Partner -' + str(partner_name)
    # except:
    #     heading_vpl = ''
    
    try:
        user_partner = UserPartnerLinkage.objects.get(user_id=user_obj.id).partner.name
    except:
        user_partner = ''
    try:
        user_vendor = UserVendorLinkage.objects.get(user_id=user_obj.id).vendor.name
    except:
        user_vendor = ''
    try:
        user_visioncenter = UserVisionCenterLinkage.objects.get(user_id=user_obj.id).vision_center.name
    except:
        user_visioncenter = ''


    if user_vendor:
        heading_vpl = 'Vendor -' + str(user_vendor)
    elif user_partner:
        heading_vpl = 'Partner -' + str(user_partner)
    elif user_visioncenter:
        heading_vpl = 'Visioncenter -' + str(user_visioncenter)
    else:
        heading_vpl=''
        
    if request.method == 'POST':
        page = request.GET.get('page')
        role_name = request.GET.get('role_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        role = request.POST.get('role', '')
        if User.objects.filter(email=email).exclude(id=user_obj.id).exists():
            email_exist = "Email already exists"
            return render(request, 'user/add_user_link_to_role.html', locals())
        if User.objects.filter(username=username).exclude(id=user_obj.id).exists():
            user_exist = "Username already exists"
            return render(request, 'user/add_user_link_to_role.html', locals())
                
        user_obj.email = email
        user_obj.username = username.lower().strip()
        user_obj.first_name=first_name
        user_obj.save()

        if role:
            user_profile.role_id = role 
        user_profile.user.set_password(password)
        user_profile.save()
        return redirect('/list/userprofile/?page='+str(page)+'&role_name=' + str(role_name))
    
    return render(request, 'user/add_user_link_to_role.html', locals())


@login_required(login_url='/login/')
def edit_password(request, id):
    heading = 'userprofile'
    user_obj = User.objects.get(id=id)

    if request.method == 'POST':
        page = request.GET.get('page')
        role_name = request.GET.get('role_name')
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj.set_password(password)
        user_obj.save()

        return redirect('/list/userprofile/?page='+str(page)+'&role_name=' + str(role_name))

    return render(request, 'user/edit_password.html', locals())


@login_required(login_url='/login/')
def get_district(request, state_id):
    if request.method == 'GET':
        result_set = []
        district_obj = District.objects.filter(status=2, state_id=state_id).order_by('name')
        for district in district_obj:
            result_set.append(
                {'id': district.id, 'name': district.name,})
        return HttpResponse(json.dumps(result_set))
    
@login_required(login_url='/login/')
def get_state(request, zone_id):
    if request.method == 'GET':
        result_set = []
        if request.session.get('role_id') in (8,9,10):
            get_state_partner_linkage = ApplicationUserStateLinkage.objects.filter(status=2,user_id=request.user.id).values_list('state',flat=True)
            state_obj = State.objects.filter(status=2,id__in=get_state_partner_linkage,zone=zone_id).order_by('name')
        elif request.session.get('role_id') == 4:
            partner_users = UserPartnerLinkage.objects.get(user_id=request.user.id)
            partner_filter=Partner.objects.filter(status=2,id=partner_users.partner_id).order_by('name')
            state_id = Partner.objects.filter(status=2,id=partner_users.partner_id).values_list('state_id',flat=True)
            state_obj = State.objects.filter(status=2,id__in=state_id,zone=zone_id).order_by('name')  
        else:    
            state_obj = State.objects.filter(status=2, zone=zone_id).order_by('name')
        for state in state_obj:
            result_set.append(
                {'id': state.id, 'name': state.name,})
        return HttpResponse(json.dumps(result_set))

@login_required(login_url='/login/')
def get_donor(request, partner_id):
    if request.method == 'GET':
        result_set = []
        dpl = DonorPartnerLinkage.objects.filter(status=2, partner_id=partner_id).values_list('donor_id', flat=True)
        partner_obj = Donor.objects.filter( id__in=dpl)
        for partner in partner_obj:
            result_set.append(
                {'id': partner.id, 'name': partner.name,})
        return HttpResponse(json.dumps(result_set))


def get_partner_state(request, state_id):
    if request.method == 'GET':
        result_set = []
        partner_obj = Partner.objects.filter(status=2, state_id=state_id).values_list('id', 'name')
        for partner_id, partner_name in partner_obj:
            result_set.append({'id': partner_id, 'name': partner_name})

        return HttpResponse(json.dumps(result_set))


def get_donor_district(request, donor_id):
    if request.method == 'GET':
        result_set = []
        partner_users = UserPartnerLinkage.objects.get(user_id=request.user.id)
        partner = Partner.objects.get(status=2, id=partner_users.partner_id)
        donor_obj = DonorPartnerLinkage.objects.filter(status=2, partner_id=partner.id, donor_id=donor_id).values_list('district_id', flat=True)
        district_donor = District.objects.filter(id__in=donor_obj)
        for dist in district_donor:
            result_set.append({'id': dist.id, 'name': dist.name})
        return HttpResponse(json.dumps(result_set), content_type='application/json')


def get_district_donor(request, district_id,partner_id):
    if request.method == 'GET':
        result_set = []
        donor_partner = DonorPartnerLinkage.objects.filter(district_id=district_id, partner_id=partner_id).values_list('donor_id', flat=True)
        donor_obj = Donor.objects.filter(status=2).exclude(id__in = donor_partner)
        for donor in donor_obj:
                result_set.append({'id': donor.id, 'name': donor.name})
        return HttpResponse(json.dumps(result_set), content_type='application/json')


# def get_user_state(request, zone_id):
#     if request.method == 'GET':
#         result_set = []
#         state_obj = State.objects.filter(status=2, zone_id=zone_id).order_by('name')
#         for state in state_obj:
#             result_set.append(
#                 {'id': state.id, 'name': state.name,})
#         return HttpResponse(json.dumps(result_set))


@login_required(login_url='/login/')
def change_user_password(request):
    heading = 'userprofile'
    user_obj = User.objects.get(id=request.user.id)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        old_password = request.POST.get('old_password')

        if not user_obj.check_password(old_password):
            error = "Old Password is not correct. Please try again."
            return render(request, 'user/change_user_password.html', locals())

        if password != request.POST.get('password2'):
            error = "Passwords do not match. Please try again."
            return render(request, 'user/change_user_password.html', locals())

        user_obj.set_password(password)
        user_obj.save()

        return redirect('/list/userprofile/')

    return render(request, 'user/change_user_password.html', locals())


def format_duration(duration):
    total_seconds = duration.total_seconds()
    total_minutes = total_seconds // 60
    if total_seconds < 60:
        return f"{total_seconds:.2f} Sec"
    else:
        return f"{total_minutes:.2f} Min"
   

