from django.shortcuts import render,redirect
from . models import *
from master_data . models import *
from master_data . views import *
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from . views import *
from django.http import JsonResponse
import datetime
from django.contrib.auth.decorators import login_required
import  logging
import sys, traceback
logger = logging.getLogger(__name__)



@login_required(login_url='/login/')
def custom_order_request(request):
    heading = 'Custom Order Request'
    partner_id=UserPartnerLinkage.objects.get(user_id=request.user.id).partner.id
    vision_ids = VisionCenter.objects.filter(status=2, partner_id=partner_id).values_list('id', flat=True)
    user_list=UserVisionCenterLinkage.objects.filter(status=2,vision_center__id__in=vision_ids).values_list('user_id', flat=True)
    patient_list = Patient.objects.filter(status=2,user__user_id__in=user_list).values_list('uuid', flat=True)
    screening_list = Screening.objects.filter(status=2, patient_uuid__in=patient_list).values_list('uuid', flat=True)
    glassprescription_list = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_list).values_list('uuid', flat=True)
    spectacletype_obj = SpectacleType.objects.filter(status=2, glass_prescription_uuid__in=glassprescription_list, spectacle_name='Custom made', order_id=0).order_by('-server_created_on')
    data = pagination_function(request, spectacletype_obj)
    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)
    return render(request, 'inventory/custom_mode/order_list.html', locals())

@login_required(login_url='/login/')
def generate_order_details(request, order_id=None, mail=None):
    heading = 'Custom Order Request details'
    from django.utils.timezone import localtime

    if order_id:
        order = OrderRequest.objects.get(id=order_id)
        partner_id=UserPartnerLinkage.objects.get(user_id=order.created_by.id).partner.id
        partner_contact=UserPartnerLinkage.objects.get(user_id=order.created_by.id).partner
    
        date = localtime(order.server_created_on).strftime("%d-%m-%Y")
        heading_vpl = f'Order #: {order_id}, date : {date}'
        spectacletype_obj = SpectacleType.objects.filter(status=2, spectacle_name='Custom made', order_id=order_id).order_by('-server_created_on')
        if spectacletype_obj:
            try:
                detail_view = spectacletype_obj.first()
                districts=DonorPartnerLinkage.objects.filter(partner_id=detail_view.get_partner_shippment_address()[0].partner.id,donor__id = order.donor.id).values_list('district__name', flat=True)
                donor_linakage_list = ', '.join(list(districts))
            except:
                detail_view = spectacletype_obj.first()
                districts=DonorPartnerLinkage.objects.filter(partner_id=detail_view.get_partner_shippment_address()[1].partner.id,donor__id = order.donor.id).values_list('district__name', flat=True)
                donor_linakage_list = ', '.join(list(districts))

    else:
        partner_id=UserPartnerLinkage.objects.get(user_id=request.user.id).partner.id
        vision_ids = VisionCenter.objects.filter(status=2, partner_id=partner_id).values_list('id', flat=True)
        user_list=UserVisionCenterLinkage.objects.filter(status=2,vision_center__id__in=vision_ids).values_list('user_id', flat=True)
        patient_list = Patient.objects.filter(status=2,user__user_id__in=user_list).values_list('uuid', flat=True)
        screening_list = Screening.objects.filter(status=2, patient_uuid__in=patient_list).values_list('uuid', flat=True)
        glassprescription_list = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening_list).values_list('uuid', flat=True)
        spectacletype_obj = SpectacleType.objects.filter(status=2, glass_prescription_uuid__in=glassprescription_list, spectacle_name='Custom made', order_id=0).order_by('-server_created_on')
        detail_view = spectacletype_obj.first()
        districts=DonorPartnerLinkage.objects.filter(partner_id=detail_view.get_partner_shippment_address()[0].partner.id).values_list('district__name', flat=True)
        donor_linakage_list = ', '.join(list(districts))
        if request.method == 'POST':
            order_request_id = request.POST.get('order_for')
            if int(order_request_id) == 2:
                camp_vlu = detail_view.get_pnt_details()[0].camp.id
                vision_vlu = None
            else:
                vision_vlu = detail_view.get_partner_shippment_address()[0].id
                camp_vlu = None
            order_obj = OrderRequest.objects.create(vision_center_id=vision_vlu, order_status=2,
            camp_id=camp_vlu,donor_id=detail_view.get_pnt_details()[0].donor.id, order_for=int(order_request_id),
            created_by_id=request.user.id, modified_by_id=request.user.id, shippment_address=1)
            order_obj.save()
            order_dtl_obj = OrderRequestDetails.objects.create(order_request_id=order_obj.id, product_id=5)
            order_dtl_obj.save()
            dear = 'Dear Sir/Madam, '
            body = 'Please find the attached custome spectacle order of VC/VC Camp/Exclusive camp for ('+order_obj.donor.name+'). Kindly do the needful. '
            html_message =  render(request, 'mailer/custom_mailer.html', locals()).content.decode("utf-8")
            custom_mailer(order_obj.id,2,html_message)
            spectacletype_obj.update(order_id=order_obj.id)
            return redirect('/custom-order-request/')
    # date = order.server_created_on.strftime("%d-%m-%Y")
    # heading_vpl = f'order # : {order_id} , date : {date}'
    
    details_received = OrderDeliveryDetails.objects.filter(order_request_id=order_id)
    for customs in details_received:
        received = customs.received_quantity
        damage = customs.damaged_quantity
    
    if mail == True and order_id:
        order = OrderRequest.objects.get(id=order_id)
        if order.order_status == 2:
            dear = 'Dear Sir/Madam'
            body = 'We require Readers/R2C spectacles for '+str(order.donor)+'. Kindly do the needful'
        elif order.order_status == 4:
            dear = 'Dear Partner'
            body = 'Your order is rejected due to '+str(order.remark)
        elif order.order_status == 5:
            dear = 'Dear Both,'
            body = 'The above mentioned order is dispatched. Kindly update the status once received.'
        return render(request, 'mailer/custom_mailer.html', locals())
    else:    
        return render(request, 'inventory/custom_mode/order_details.html', locals())


def update_custom_received(request,order_id,invoice_nos = None,):
    details_received = OrderDeliveryDetails.objects.filter(order_request_id=order_id)
    details = OrderRequestDetails.objects.filter(order_request_id=order_id)
    prod_id = details.first().product.id
    order = OrderRequest.objects.get(id=order_id)
    spect = SpectacleType.objects.filter(order_id=order.id)
    invoice_nos = int(invoice_nos.strip()) if invoice_nos else None
    damage_qty = max(spect.count() - invoice_nos, 0)

    obj = OrderDeliveryDetails.objects.create(
        order_request_id = order.id,
        product_id = prod_id,
        received_quantity = invoice_nos,
        damaged_quantity = damage_qty
        )
    obj.save() 
    order.order_status = 6
    order.save()
    
    return redirect(f'/edit_orders_custom/{order_id}')


def custom_mailer(order_id,order_status_id,html_message,isTls=True):
    import smtplib
    import os
    from weasyprint import HTML, CSS
    from email.mime.image import MIMEImage
    try:
        msg = MIMEMultipart()
        msg2 = MIMEMultipart()
        order = OrderRequest.objects.get(id=order_id)
        order_del = OrderRequestDetails.objects.filter(order_request_id=order.id)
        order_dvdel = OrderDeliveryDetails.objects.filter(order_request_id=order.id)
        admin_id = UserProfile.objects.get(role_id=3, status=2).user.id
        admin_eid = User.objects.get(id=admin_id).email
        vendor_id = UserProfile.objects.get(role_id=6, status=2).user.id
        vendor_eid = User.objects.get(id=vendor_id).email
        product_name = 'Custom made'
        try:
            user_id = UserPartnerLinkage.objects.get(user_id=order.created_by.id)
        except:
            user_id = ''
        

        msg['From'] = "misindia@sightsaversindia.org"
        msg['To'] = admin_eid
        msg['Subject'] = 'Order request for custom specs from ' + user_id.partner.name + '.Order #: ' +str(order_id)
        
        part1=MIMEText(html_message, 'html')
        html_content = html_message
        html = HTML(string=html_content)
        pdf_options = {
        'page-size': 'A3',
        'margin-top': '0mm',
        'margin-right': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'orientation': 'Landscape'
        }
        css = CSS(string='''
        .a6T {
            width: 80px;
            height: 45px;
        }
        h1, p, td, th {
            font-size: 10pt;
        }
        table {
            border-collapse: collapse;
            width: 100%;
        }

        th, td {
            border: 1px solid black;
            padding: 8px;
        }
        .text-center {
            text-align: center!important;
        }
        ''')


        # Export the HTML object to a PDF file
        
        pdf_file = settings.MEDIA_ROOT + '/' + user_id.partner.name + '-' + str(order_id) +'.pdf'
        # pdf_file.rotateClockwise(90)
        html.write_pdf(pdf_file, stylesheets=[css], **pdf_options)
        # img_dir = settings.MEDIA_ROOT + '/send_logo'
        # image = 'maillogo.png'
        # file_path = os.path.join(img_dir, image)
        # fp = open(file_path, 'rb')
        # msgImage = MIMEImage(fp.read())
        # fp.close()
        # msgImage.add_header('Content-ID', '<image1>')
        
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(pdf_file, "rb").read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "inline" ,filename= user_id.partner.name + '-' + str(order_id) +'.pdf')
        msg.attach(part)
        msg.attach(part1)
        msg2.attach(part)
        msg2.attach(part1)
        smtp = smtplib.SMTP(settings.EMAIL_HOST,settings.EMAIL_PORT)

        if isTls:
            smtp.starttls()
        smtp.login(settings.EMAIL_HOST_USER,settings.EMAIL_HOST_PASSWORD)
    
        msg_send_status = smtp.sendmail(msg['From'], msg['To'] ,msg.as_string())
        
        smtp.quit()

        os.remove(pdf_file)

        return msg_send_status
    except Exception as e:
        # logger.error(e.args[0])
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        errors = 'product id: ' +str(order_id) +str(error_stack) 
        logger.error(errors)

@login_required(login_url='/login/')
def orderrequest_list(request):
    heading = 'Order Request Details'
    search = request.GET.get('search', '')
    if search:
        order = OrderRequestDetails.objects.filter(created_by__username__icontains=search)
    else:
        order = OrderRequestDetails.objects.filter(status=2)
    data = pagination_function(request, order)
    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)
    return render(request,'inventory/orderdetails_list.html',locals())


@login_required(login_url='/login/')
def add_orderdetails(request):
    heading = 'Order Request Details'
    order_requests = OrderRequest.objects.filter(status=2)
    user = User.objects.all()
    products = Product.objects.all()

    if request.method == 'POST':
        order_request_id = request.POST.get('order_request')
        product_id = request.POST.get('product')
        created_by_id = request.POST.get('created_by')
        modified_by_id = request.POST.get('modified_by')
        quantity = request.POST.get('quantity')
        received_quantity = request.POST.get('received_quantity')
        damaged_quantity = request.POST.get('damaged_quantity')

        order_request = OrderRequest.objects.get(id=order_request_id)
        product = Product.objects.get(id=product_id)
        created_by = User.objects.get(id=created_by_id)
        modified_by = User.objects.get(id=modified_by_id)

        request_details = OrderRequestDetails.objects.create(
            order_request=order_request,
            product=product,
            created_by=created_by,
            modified_by=modified_by,
            quantity=quantity,
            received_quantity=received_quantity,
            damaged_quantity=damaged_quantity
        )

        return redirect('/orderrequest_list/')

    return render(request, 'inventory/add_orderdetails.html', locals())

@login_required(login_url='/login/')
def change_order_status(request, model, id, action):
    if request.method == 'POST':
        id = request.POST.get('id')
        model = request.POST.get('model')
        action = request.POST.get('action')

        if model == 'OrderRequest':
            instance = OrderRequest.objects.get(id=id)

        if action == 'Submit for approval':
            instance.order_request.order_status = 2
            print(instance.order_request.order_status, 'ooooo')
        elif action == 'Approved':
            instance.order_request.order_status = 3
        elif action == 'Cancel':
            instance.order_request.order_status = 1
        
        instance.order_request.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})


@login_required(login_url='/login/')
def orderdelivery_list(request):
    heading = 'Order Delivery List'
    search = request.GET.get('search', '')
    products = Product.objects.filter(status=2).order_by('name')
    orders = OrderRequest.objects.filter(status=2)

    product_names = request.GET.get('product_name', '')
    order_names = request.GET.get('order', '')
    
    state= State.objects.filter(status=2).order_by('name')
    state_name = request.GET.get('state_name','')
    state_names= int(state_name) if state_name != '' else ''
    start_filter = request.GET.get('start_filter', '')
    end_filter = request.GET.get('end_filter', '')

    if request.session.get('role_id') == 4:
        order = OrderRequest.objects.filter(status=2,created_by=request.user, order_status__gte=5).order_by('-server_created_on')
    elif request.session.get('role_id') in [8,9,10]:
        apl_obj = ApplicationUserStateLinkage.objects.filter(user=request.user).values_list('state',flat=True)
        partner_user = Partner.objects.filter(state_id__in=apl_obj).values_list('id', flat=True)
        vision_center_details = VisionCenter.objects.filter(partner_id__in=partner_user).values_list('id', flat=True)
        user_vision_details = UserVisionCenterLinkage.objects.filter(vision_center_id__in=vision_center_details).values_list('vision_center__id', flat=True)
        user_partner_details = UserPartnerLinkage.objects.filter(partner_id__in=partner_user).values_list('user_id', flat=True)
        camp_partner = Camp.objects.filter(partner_id__in=partner_user).values_list('id', flat=True)
        order = OrderRequest.objects.filter(Q(vision_center__in=user_vision_details)|Q(camp__in=camp_partner)|Q(created_by__in=user_partner_details),order_status__gte=5, status=2).order_by('-server_created_on')
    else:
        order = OrderRequest.objects.filter(status=2, order_status__gte=5).order_by('-server_created_on')

    # if search:
    #     order = objects.filter(Q(created_by__username__icontains=search,order_status__in = [5,6])|Q(id=search)).order_by('-server_created_on')
    if search.isdigit():
        order = order.filter(Q(created_by__username__icontains=search) | Q(id=int(search))).order_by('-server_created_on')
    else:
        order = order.filter(created_by__username__icontains=search).order_by('-server_created_on')
    
    if product_names:
        if request.session.get('role_id') == 4:
            order_details = OrderRequestDetails.objects.filter(order_request__status=2,product_id__in=product_names)
            order_ids = order_details.values_list('order_request__id', flat=True).distinct()
            order = OrderRequest.objects.filter(id__in=order_ids,created_by=request.user, order_status__in = [5,6]).order_by('-server_created_on')
        elif request.session.get('role_id') in [8, 9, 10]:
            apl_obj = ApplicationUserStateLinkage.objects.filter(user=request.user).values_list('state',flat=True)
            partner_user = Partner.objects.filter(state_id__in=apl_obj).values_list('id', flat=True)
            vision_center_details = VisionCenter.objects.filter(partner_id__in=partner_user).values_list('id', flat=True)
            user_vision_details = UserVisionCenterLinkage.objects.filter(vision_center_id__in=vision_center_details).values_list('vision_center__id', flat=True)
            user_partner_details = UserPartnerLinkage.objects.filter(partner_id__in=partner_user).values_list('user_id', flat=True)
            camp_partner = Camp.objects.filter(partner_id__in=partner_user).values_list('id', flat=True)
            order_req = OrderRequest.objects.filter(Q(vision_center__in=user_vision_details)|Q(camp__in=camp_partner)|Q(created_by__in=user_partner_details),order_status__gte=5, status=2).order_by('-server_created_on')
            order_details = OrderRequestDetails.objects.filter(order_request__in=order_req,order_request__status=2,product_id__in=product_names)
            order_ids = order_details.values_list('order_request__id', flat=True).distinct()
            order = OrderRequest.objects.filter(id__in=order_ids,order_status__range=[5, 6]).order_by('-server_created_on')
        else:
            order_details = OrderRequestDetails.objects.filter(order_request__status=2,product_id__in=product_names)
            order_ids = order_details.values_list('order_request__id', flat=True).distinct()
            order = OrderRequest.objects.filter(id__in=order_ids,order_status__in = [5,6]).order_by('-server_created_on')

    if order_names:
        order = order.filter(order_status=order_names).order_by('-server_created_on')

    if state_name:
        order=order.filter(id=state_name)

    if start_filter != '' and end_filter != '':
        order = order.filter(server_created_on__gte=start_filter, server_created_on__lte=end_filter).order_by('-server_created_on')

    data = pagination_function(request, order)
    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)
    return render(request,'inventory/order_receipt/orderdelivery_list.html',locals())

@login_required(login_url='/login/')
def add_deliverydetails(request):
    heading = 'Order Delivery Details'
    order_requests = OrderRequest.objects.filter(status=2)
    user = User.objects.all()
    products = Product.objects.filter(status=2)

    if request.method == 'POST':
        order_request_id = request.POST.get('order_request')
        product_id = request.POST.get('product')
        created_by_id = request.POST.get('created_by')
        modified_by_id = request.POST.get('modified_by')
        received_quantity = request.POST.get('received_quantity')
        damaged_quantity = request.POST.get('damaged_quantity')

        order_request = OrderRequest.objects.get(id=order_request_id)
        product = Product.objects.get(id=product_id)
        created_by = User.objects.get(id=created_by_id)
        modified_by = User.objects.get(id=modified_by_id)

        request_details = OrderDeliveryDetails.objects.create(
            order_request=order_request,
            product=product,
            created_by=created_by,
            modified_by=modified_by,
            received_quantity=received_quantity,
            damaged_quantity=damaged_quantity
        )

        return redirect('/orderdelivery_list/')

    return render(request, 'inventory/delivery/add_deliverydetails.html', locals())

@login_required(login_url='/login/')
def edit_deliverydetails(request,id):
    heading = 'Order Delivery Details'
    # heading_vpl = id 
    order = OrderRequest.objects.get(id=id)
    products = OrderRequestDetails.objects.filter(order_request_id=order.id)

    details_received = OrderDeliveryDetails.objects.filter(order_request_id=order.id)
    print(details_received,'jjhghjghj')
    details = OrderRequestDetails.objects.filter(order_request_id=order.id)
    prod_id = details.first().product.id
    date = order.server_created_on.strftime("%d-%m-%Y")
    heading_vpl = f'order # : {id} , date : {date}'
    
    for value in details:
        quant = value.quantity
        rrv = value.rrv
        frame_type = value.frame_type
        if rrv == 1:
            quant_1 = value.quantity
        if rrv == 2:
            quant_2 = value.quantity
        if rrv == 3:
            quant_3 = value.quantity
        if rrv == 4:
            quant_4 = value.quantity
        if rrv == 5:
            quant_5 = value.quantity
        if rrv == 6:
            quant_6 = value.quantity
        if rrv == 7:
            quant_7 = value.quantity
        if rrv == 8:
            quant_8 = value.quantity
        if rrv == 9:
            quant_9 = value.quantity
        if rrv == 11:
            quant_11 = value.quantity
        if rrv == 12:
            quant_12 = value.quantity
        if rrv == 13:
            quant_13 = value.quantity
        if rrv == 14:
            quant_14 = value.quantity
        if rrv == 15:
            quant_15 = value.quantity
        if rrv == 16:
            quant_16 = value.quantity
        if rrv == 17:
            quant_17 = value.quantity
        if rrv == 18:
            quant_18 = value.quantity
        # if rrv == 19:
        #     quant_19 = value.quantity
        # if rrv == 20:
        #     quant_20 = value.quantity
        if frame_type == 1:
            frame_1 = value.quantity
        if frame_type == 2:
            frame_2 = value.quantity

    for value in details_received:
        rec_quant = value.received_quantity
        rrv = value.rrv
        frame_type = value.frame_type
        if rrv == 1:
            rec_quant_1 = value.received_quantity
            dem_quant_1 = value.damaged_quantity
        if rrv == 2:
            rec_quant_2 = value.received_quantity
            dem_quant_2 = value.damaged_quantity
        if rrv == 3:
            rec_quant_3 = value.received_quantity
            dem_quant_3 = value.damaged_quantity
        if rrv == 4:
            rec_quant_4 = value.received_quantity
            dem_quant_4 = value.damaged_quantity
        if rrv == 5:
            rec_quant_5 = value.received_quantity
            dem_quant_5 = value.damaged_quantity
        if rrv == 6:
            rec_quant_6 = value.received_quantity
            dem_quant_6 = value.damaged_quantity
        if rrv == 7:
            rec_quant_7 = value.received_quantity
            dem_quant_7 = value.damaged_quantity
        if rrv == 8:
            rec_quant_8 = value.received_quantity
            dem_quant_8 = value.damaged_quantity
        if rrv == 9:
            rec_quant_9 = value.received_quantity
            dem_quant_9 = value.damaged_quantity
        if rrv == 11:
            rec_quant_11 = value.received_quantity
            dem_quant_11 = value.damaged_quantity
        if rrv == 12:
            rec_quant_12 = value.received_quantity
            dem_quant_12 = value.damaged_quantity
        if rrv == 13:
            rec_quant_13 = value.received_quantity
            dem_quant_13 = value.damaged_quantity
        if rrv == 14:
            rec_quant_14 = value.received_quantity
            dem_quant_14 = value.damaged_quantity
        if rrv == 15:
            rec_quant_15 = value.received_quantity
            dem_quant_15 = value.damaged_quantity
        if rrv == 16:
            rec_quant_16 = value.received_quantity
            dem_quant_16 = value.damaged_quantity
        if rrv == 17:
            rec_quant_17 = value.received_quantity
            dem_quant_17 = value.damaged_quantity
        if rrv == 18:
            rec_quant_18 = value.received_quantity
            dem_quant_18 = value.damaged_quantity
        # if rrv == 19:
        #     rec_quant_19 = value.received_quantity
        #     dem_quant_19 = value.damaged_quantity
        # if rrv == 20:
        #     rec_quant_20 = value.received_quantity
        #     dem_quant_20 = value.damaged_quantity
        if frame_type == 1:
            rec_frame_1 = value.received_quantity
            dem_frame_1 = value.damaged_quantity
        if frame_type == 2:
            rec_frame_2 = value.received_quantity
            dem_frame_2 = value.damaged_quantity
        
    order_requests = OrderRequest.objects.filter(status=2)
    vision_centers = VisionCenter.objects.filter(status=2)
    camps = Camp.objects.filter(status=2)
    donors = Donor.objects.filter(status=2)
    user = User.objects.all()
    time = datetime.datetime.now()

    if request.method == 'POST':
        value = []
        shippment_address = request.POST.get('shippment_address')
        table_choose = request.POST.get('table_choose')
        vision_center = request.POST.get('vision_center')
        address = request.POST.get('address')
        product_id = request.POST.get('table_selection')
        donor = request.POST.get('donor')
        other_address= request.POST.get('other_address')
        order.vision_center_id = vision_center or None
        order.order_for = table_choose
        order.order_status = 2
        order.shippment_address = shippment_address
        order.modified_by = request.user
        order.modified_on = time
        order.save()

        for val in value:
            for key, value in val.items():
                order_detail = OrderRequestDetails.objects.create(
                    order_request=order,
                    product_id=product_id,
                    quantity=value,
                    rrv=key
                )
                order_detail.save()

        return redirect('/orderdelivery_list/')

    return render(request, 'inventory/delivery/edit_delivery.html', locals())

@login_required(login_url='/login/')
def calculate_damagedetails(request,order_id, mail=None):
    heading = 'Order Delivery Details'
    # heading_vpl = f'order # : {order_id}'

    order = OrderRequest.objects.get(id=order_id)
    products = OrderRequestDetails.objects.filter(order_request_id=order.id)
    partner_id=UserPartnerLinkage.objects.get(user_id=order.created_by.id).partner.id
    partner_contact=UserPartnerLinkage.objects.get(user_id=order.created_by.id).partner
    date = order.server_created_on.strftime("%d-%m-%Y")
    heading_vpl = f'order # : {order_id} , date : {date}'
    

    try:
        admin_id = UserProfile.objects.get(role_id=3, status=2).user.id
        admin_eid = User.objects.get(id=admin_id).email
    except:
        admin_eid = ''
    try:
        ptr_vlu = Partner.objects.get(status=2, id=partner_id)
    except:
        ptr_vlu = ''
        
    donor_linked = DonorPartnerLinkage.objects.filter(donor__id = order.donor.id,partner_id=ptr_vlu.id).values_list('district__name',flat=True)
    donor_dist = ', '.join(list(donor_linked))

    details_received = OrderDeliveryDetails.objects.filter(order_request_id=order.id)
    details = OrderRequestDetails.objects.filter(order_request_id=order.id)
    prod_id = details.first().product.id
    
    for value in details:
        quant = value.quantity
        rrv = value.rrv
        frame_type = value.frame_type
        if rrv == 1:
            quant_1 = value.quantity
        if rrv == 2:
            quant_2 = value.quantity
        if rrv == 3:
            quant_3 = value.quantity
        if rrv == 4:
            quant_4 = value.quantity
        if rrv == 5:
            quant_5 = value.quantity
        if rrv == 6:
            quant_6 = value.quantity
        if rrv == 7:
            quant_7 = value.quantity
        if rrv == 8:
            quant_8 = value.quantity
        if rrv == 9:
            quant_9 = value.quantity
        if rrv == 11:
            quant_11 = value.quantity
        if rrv == 12:
            quant_12 = value.quantity
        if rrv == 13:
            quant_13 = value.quantity
        if rrv == 14:
            quant_14 = value.quantity
        if rrv == 15:
            quant_15 = value.quantity
        if rrv == 16:
            quant_16 = value.quantity
        if rrv == 17:
            quant_17 = value.quantity
        if rrv == 18:
            quant_18 = value.quantity
        # if rrv == 19:
        #     quant_19 = value.quantity
        # if rrv == 20:
        #     quant_20 = value.quantity
        if frame_type == 1:
            frame_1 = value.quantity
        if frame_type == 2:
            frame_2 = value.quantity

    for value in details_received:
        rec_quant = value.received_quantity
        rrv = value.rrv
        frame_type = value.frame_type
        if rrv == 1:
            rec_quant_1 = value.received_quantity
            dem_quant_1 = value.damaged_quantity
        if rrv == 2:
            rec_quant_2 = value.received_quantity
            dem_quant_2 = value.damaged_quantity
        if rrv == 3:
            rec_quant_3 = value.received_quantity
            dem_quant_3 = value.damaged_quantity
        if rrv == 4:
            rec_quant_4 = value.received_quantity
            dem_quant_4 = value.damaged_quantity
        if rrv == 5:
            rec_quant_5 = value.received_quantity
            dem_quant_5 = value.damaged_quantity
        if rrv == 6:
            rec_quant_6 = value.received_quantity
            dem_quant_6 = value.damaged_quantity
        if rrv == 7:
            rec_quant_7 = value.received_quantity
            dem_quant_7 = value.damaged_quantity
        if rrv == 8:
            rec_quant_8 = value.received_quantity
            dem_quant_8 = value.damaged_quantity
        if rrv == 9:
            rec_quant_9 = value.received_quantity
            dem_quant_9 = value.damaged_quantity

        if rrv == 11:
            rec_quant_11 = value.received_quantity
            dem_quant_11 = value.damaged_quantity
        if rrv == 12:
            rec_quant_12 = value.received_quantity
            dem_quant_12 = value.damaged_quantity
        if rrv == 13:
            rec_quant_13 = value.received_quantity
            dem_quant_13 = value.damaged_quantity
        if rrv == 14:
            rec_quant_14 = value.received_quantity
            dem_quant_14 = value.damaged_quantity
        if rrv == 15:
            rec_quant_15 = value.received_quantity
            dem_quant_15 = value.damaged_quantity
        if rrv == 16:
            rec_quant_16 = value.received_quantity
            dem_quant_16 = value.damaged_quantity
        if rrv == 17:
            rec_quant_17 = value.received_quantity
            dem_quant_17 = value.damaged_quantity
        if rrv == 18:
            rec_quant_18 = value.received_quantity
            dem_quant_18 = value.damaged_quantity
        # if rrv == 19:
        #     rec_quant_19 = value.received_quantity
        #     dem_quant_19 = value.damaged_quantity
        # if rrv == 20:
        #     rec_quant_20 = value.received_quantity
        #     dem_quant_20 = value.damaged_quantity

        if frame_type == 1:
            rec_frame_1 = value.received_quantity
            dem_frame_1 = value.damaged_quantity
        if frame_type == 2:
            rec_frame_2 = value.received_quantity
            dem_frame_2 = value.damaged_quantity
    
    if request.method == 'POST':
        value = [] 
        if request.POST.get('near1'):
            dict_val = {1:[request.POST.get('near1'),quant_1 - int(request.POST.get('near1'))]}
            value.append(dict_val)
        if request.POST.get('near2'):
            dict_val = {2:[request.POST.get('near2'),quant_2 - int(request.POST.get('near2'))]}
            value.append(dict_val)
        if request.POST.get('near3'):
            dict_val = {3:[request.POST.get('near3'),quant_3 - int(request.POST.get('near3'))]}
            value.append(dict_val)
        if request.POST.get('near4'):
            dict_val = {4:[request.POST.get('near4'),quant_4 - int(request.POST.get('near4'))]}
            value.append(dict_val)
        if request.POST.get('near5'):
            dict_val = {5:[request.POST.get('near5'),quant_5 - int(request.POST.get('near5'))]}
            value.append(dict_val)
        if request.POST.get('near6'):
            dict_val = {6:[request.POST.get('near6'),quant_6 - int(request.POST.get('near6'))]}
            value.append(dict_val)
        if request.POST.get('near7'):
            dict_val = {7:[request.POST.get('near7'),quant_7 - int(request.POST.get('near7'))]}
            value.append(dict_val)
        if request.POST.get('near8'):
            dict_val = {8:[request.POST.get('near8'),quant_8 - int(request.POST.get('near8'))]}
            value.append(dict_val)
        if request.POST.get('near9'):
            dict_val = {9:[request.POST.get('near9'),quant_9 - int(request.POST.get('near9'))]}
            value.append(dict_val)

        if request.POST.get('r2c1'):
            dict_val = {11:[request.POST.get('r2c1'),quant_11 - int(request.POST.get('r2c1'))]}
            value.append(dict_val)
        if request.POST.get('r2c2'):
            dict_val = {12:[request.POST.get('r2c2'),quant_12 - int(request.POST.get('r2c2'))]}
            value.append(dict_val)
        if request.POST.get('r2c3'):
            dict_val = {13:[request.POST.get('r2c3'),quant_13 - int(request.POST.get('r2c3'))]}
            value.append(dict_val)
        if request.POST.get('r2c4'):
            dict_val = {14:[request.POST.get('r2c4'),quant_14 - int(request.POST.get('r2c4'))]}
            value.append(dict_val)
        if request.POST.get('r2c5'):
            dict_val = {15:[request.POST.get('r2c5'),quant_15 - int(request.POST.get('r2c5'))]}
            value.append(dict_val)
        if request.POST.get('r2c6'):
            dict_val = {16:[request.POST.get('r2c6'),quant_16 - int(request.POST.get('r2c6'))]}
            value.append(dict_val)
        if request.POST.get('r2c7'):
            dict_val = {17:[request.POST.get('r2c7'),quant_17 - int(request.POST.get('r2c7'))]}
            value.append(dict_val)
        if request.POST.get('r2c8'):
            dict_val = {18:[request.POST.get('r2c8'),quant_18 - int(request.POST.get('r2c8'))]}
            value.append(dict_val)
        # if request.POST.get('r2c9'):
        #     dict_val = {19:[request.POST.get('r2c9'),quant_19 - int(request.POST.get('r2c9'))]}
        #     value.append(dict_val)
        # if request.POST.get('r2c10'):
        #     dict_val = {20:[request.POST.get('r2c10'),quant_20 - int(request.POST.get('r2c10'))]}
        #     value.append(dict_val)
        



        for val in value:
            for rd in val.keys():
                obj, created = OrderDeliveryDetails.objects.update_or_create(
                    order_request_id=order.id,
                    product_id=prod_id,
                    rrv=rd,
                    defaults={
                        'received_quantity': val[rd][0],
                        'damaged_quantity': val[rd][1]
                    })
                obj.save()
        # import ipdb; ipdb.set_trace();
        values_meta = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        near_value = []
        for val_meta in values_meta: 
            found = False 
            for val in value:    
                if val_meta in val: 
                    near_value.append(val)
                    found = True 
                    break
            if not found: 
                d_dict = {val_meta: []} 
                near_value.append(d_dict)
        
        values_meta_r2c = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        r2c_value = []
        for val_meta in values_meta_r2c: 
            found = False 
            for val in value:    
                if val_meta in val: 
                    r2c_value.append(val)
                    found = True 
                    break
            if not found: 
                d_dict = {val_meta: []} 
                r2c_value.append(d_dict)
                    
        frame = []    
        if request.POST.get('R2CCM015'):
            frame_val = {1:[request.POST.get('R2CCM015'),frame_1 - int(request.POST.get('R2CCM015'))]}
            frame.append(frame_val)

        if request.POST.get('R2CCM021'):
            frame_val = {2:[request.POST.get('R2CCM021'),frame_2 - int(request.POST.get('R2CCM021'))]}
            frame.append(frame_val)
        # import ipdb; ipdb.set_trace();
        
        for frm in frame:
            for ft in frm.keys():
                obj, created = OrderDeliveryDetails.objects.update_or_create(
                    order_request_id = order.id,
                    product_id=prod_id,
                    frame_type=ft,
                    defaults={
                    "received_quantity" : frm[ft][0],
                    "damaged_quantity" : frm[ft][1]
                    })

                obj.save() 
        values_meta_frame = [1,2]
        frame_value = []
        for val_meta in values_meta_frame: 
            found = False 
            for val in frame:    
                if val_meta in val: 
                    frame_value.append(val)
                    found = True 
                    break
            if not found: 
                d_dict = {val_meta: []} 
                frame_value.append(d_dict)
        order.order_status = 6  
        order.save()
        if order.order_status == 6:
            order_dvdel = OrderDeliveryDetails.objects.filter(order_request_id=order.id)
            # partner =order.vision_center.partner
            odq_list = list(order_dvdel.values_list('damaged_quantity', flat=True))
            odq_v = [i for i in odq_list if i >= 1]  
            dear = 'Dear Sir/Madam, '
            if odq_v:
                body = 'We have received custom made spectacles for '+str(order.donor)
            else: 
                body =  'We have received Readers/R2C spectacles for '+str(order.donor)+'. Kindly do the needful for the replacement.'      
            html_message =  render(request, 'mailer/order_received_mail.html', locals()).content.decode("utf-8")
            received_mail(order_id,order.order_status,html_message)
        return redirect('/orderdelivery_list/')
    return render(request, 'inventory/order_receipt/calculate_damagedetails.html', locals())


def received_mail(order_id,order_status_id,html_message,isTls=True):
    import smtplib
    import os
    from weasyprint import HTML, CSS
    from email.mime.image import MIMEImage

    try:
        msg = MIMEMultipart()
        msg2 = MIMEMultipart()
        order = OrderRequest.objects.get(id=order_id)
        order_del = OrderRequestDetails.objects.filter(order_request_id=order.id)
        order_dvdel = OrderDeliveryDetails.objects.filter(order_request_id=order.id)
        admin_id = UserProfile.objects.get(role_id=3, status=2).user.id
        admin_eid = User.objects.get(id=admin_id).email
        vendor_id = UserProfile.objects.get(role_id=6, status=2).user.id
        vendor_eid = User.objects.get(id=vendor_id).email
        product_name = order_del.first().product.name
        vendor_emails = Vendor.objects.filter(status=2).values_list('email_id', 'alternative_email_id_1', 'alternative_email_id_2', 'alternative_email_id_3', 'alternative_email_id_4')
        valid_email_addresses = [email for sublist in vendor_emails for email in sublist if email]
        valid_email_addresses = list(filter(None, valid_email_addresses))

        try:
            user_id = UserPartnerLinkage.objects.get(user_id=order.created_by.id)
        except:
            user_id = ''
        odq_list = list(order_dvdel.values_list('damaged_quantity', flat=True))
        odq_v = [i for i in odq_list if i >= 1]
        
        

        if odq_v:
            final_qv = odq_v
            msg['From'] = "misindia@sightsaversindia.org"
            msg['To'] = ", ".join(valid_email_addresses)
            msg['Subject'] = 'Damage goods received. Order #: ' + str(order_id) + ' ' + user_id.partner.name
            msg2['From'] = "misindia@sightsaversindia.org"
            msg2['To'] = admin_eid 
            msg2['Subject'] = 'Damage goods received. Order #: ' + str(order_id) + ' ' + user_id.partner.name
        else:
            msg2['From'] = "misindia@sightsaversindia.org"
            msg2['To'] = admin_eid 
            msg2['Subject'] = 'Order received by ' + user_id.partner.name + '. Order #: '+str(order_id)
            final_qv = None

        part1=MIMEText(html_message, 'html')
        html_content = html_message
        html = HTML(string=html_content)
        pdf_options = {
        'page-size': 'A3',
        'margin-top': '0mm',
        'margin-right': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        }
        css = CSS(string='''
        .a6T {
            width: 80px;
            height: 45px;
        }
        h1, p, td, th {
            font-size: 10pt;
        }
        table {
            border-collapse: collapse;
            width: 100%;
        }

        th, td {
            border: 1px solid black;
            padding: 8px;
        }
        .text-center {
            text-align: center!important;
        }
        ''')


        # Export the HTML object to a PDF file
        
        pdf_file = settings.MEDIA_ROOT + '/' + user_id.partner.name + '-' + str(order_id) +'.pdf'
        html.write_pdf(pdf_file, stylesheets=[css], **pdf_options)
        # img_dir = settings.MEDIA_ROOT + '/send_logo'
        # image = 'maillogo.png'
        # file_path = os.path.join(img_dir, image)
        # fp = open(file_path, 'rb')
        # msgImage = MIMEImage(fp.read())
        # fp.close()
        # msgImage.add_header('Content-ID', '<image1>')
    
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(pdf_file, "rb").read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "inline" ,filename= user_id.partner.name + '-' + str(order_id) +'.pdf')
        msg.attach(part)
        msg.attach(part1)
        msg2.attach(part)
        msg2.attach(part1)
        smtp = smtplib.SMTP(settings.EMAIL_HOST,settings.EMAIL_PORT)

        if isTls:
            smtp.starttls()
        smtp.login(settings.EMAIL_HOST_USER,settings.EMAIL_HOST_PASSWORD)
        if final_qv == None:
            msg_send_status = smtp.sendmail(msg2['From'], msg2['To'] ,msg2.as_string())
        else:
            msg_send_status = smtp.sendmail(msg2['From'], msg2['To'] ,msg2.as_string())
            msg_send_status = smtp.sendmail(msg['From'], valid_email_addresses ,msg.as_string())
        
        smtp.quit()

        os.remove(pdf_file)

        return msg_send_status
    except Exception as e:
        # logger.error(e.args[0])
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        errors = 'product id: ' +str(order_id) +str(error_stack) 
        logger.error(errors)


@login_required(login_url='/login/')
def edit_orders(request,id):
    heading = 'Edit Order '
    order = OrderRequest.objects.get(id=id)
    try:
        user= UserProfile.objects.get(user__username= request.user, role__id=3)
        role=user.role.id
    except:
        role= None
    products = OrderRequestDetails.objects.filter(order_request_id=order.id)
    delivery = OrderDeliveryDetails.objects.filter(order_request_id=order.id)
    if request.user.id == 2:
        partner = UserPartnerLinkage.objects.get(id = request.user.id)
        donor = Donor.objects.get(id = request.user.id )

    else:
        partner = UserPartnerLinkage.objects.get(user = request.user )
        donor = Donor.objects.get(id=partner.id )
        # return redirect('/orders/')
    return render (request, 'inventory/edit_orders_new.html', locals())

@login_required(login_url='/login/')
def reject_remark(request, reject_id, remark):
    order_obj = OrderRequest.objects.get(id=reject_id)
    order_obj.remark = remark
    order_obj.order_status = 4
    order_obj.approved_by_id = request.user.id
    order_obj.approved_on = datetime.datetime.now()
    order_obj.save()
    if order_obj.get_product():
        send_mail_res = edit_orders_new(request,reject_id, mail=True)
    else:
        send_mail_res = generate_order_details(request,reject_id, mail=True)
    html_content = send_mail_res.content.decode("utf-8")
    send_mail_response = send_mail(reject_id,4, html_content)
    return redirect('/orders/')


@login_required(login_url='/login/')
def approve_remark(request, order_id, remark):
    order_obj = OrderRequest.objects.get(id=order_id)
    order_obj.order_status = 3
    order_obj.approved_by_id = request.user.id
    order_obj.approved_on = datetime.datetime.now()
    order_obj.save()
    if order_obj.get_product().product.id != 5:
        send_mail_res = edit_orders_new(request,order_id, mail=True)
    else:
        send_mail_res = generate_order_details(request,order_id, mail=True)
    html_content = send_mail_res.content.decode("utf-8")
    send_mail_response = send_mail(order_id,3, html_content)
    return redirect('/orders/')


@login_required(login_url='/login/')
def update_order_status(request,order_id,order_status_id):
    order = OrderRequest.objects.get(id=order_id)
    order.order_status = order_status_id
    order.approved_by_id = request.user.id
    order.approved_on = datetime.datetime.now()
    order.save()
    if order.get_product().product.id != 5:
        send_mail_res = edit_orders_new(request,order_id, mail=True)
    else:
        send_mail_res = generate_order_details(request,order_id, mail=True)
    html_content = send_mail_res.content.decode("utf-8")
    send_mail_response = send_mail(order_id,order_status_id, html_content)
    return redirect('/orders/')


@login_required(login_url='/login/')
def orders(request):
    
    heading = 'Order List'
    search = request.GET.get('search', '')
    products = Product.objects.filter(status=2).order_by('name')

    product_names = request.GET.get('product_name', '')
    order_names = request.GET.get('order', '')
    state= State.objects.filter(status=2).order_by('name')
    state_name = request.GET.get('state_name','')
    state_names= int(state_name) if state_name != '' else ''
    start_filter = request.GET.get('start_filter', '')
    end_filter = request.GET.get('end_filter', '')

    try:
        user= UserProfile.objects.get(user__username= request.user, role__id=4)
        role=user.role.id
    except:
        role= None
    if request.session.get('role_id') == 4:
        user_vision = UserPartnerLinkage.objects.get(user=request.user)
        partner_user = Partner.objects.filter(id=user_vision.partner.id)
        partner_details = Partner.objects.filter(id=user_vision.partner.id).values_list('id', flat=True)
        vision_center_details = VisionCenter.objects.filter(partner_id__in=partner_details).values_list('id', flat=True)
        user_vision_details = UserVisionCenterLinkage.objects.filter(vision_center_id__in=vision_center_details).values_list('vision_center__id', flat=True)
        camp_partner = Camp.objects.filter(partner__in=partner_user).values_list('id', flat=True)
        
        order = OrderRequest.objects.filter(Q(vision_center__in=user_vision_details)|Q(camp__in=camp_partner)|Q(created_by=request.user),order_status__range = [1,4],status=2).order_by('-server_created_on')
    elif request.session.get('role_id') == 6:
        order = OrderRequest.objects.filter(order_status__in=[3,5], status=2).order_by('-server_created_on')
    elif request.session.get('role_id') in [8,9,10]:
        apl_obj = ApplicationUserStateLinkage.objects.filter(user=request.user).values_list('state',flat=True)
        partner_user = Partner.objects.filter(state_id__in=apl_obj).values_list('id', flat=True)
        vision_center_details = VisionCenter.objects.filter(partner_id__in=partner_user).values_list('id', flat=True)
        user_vision_details = UserVisionCenterLinkage.objects.filter(vision_center_id__in=vision_center_details).values_list('vision_center__id', flat=True)
        user_partner_details = UserPartnerLinkage.objects.filter(partner_id__in=partner_user).values_list('user_id', flat=True)
        camp_partner = Camp.objects.filter(partner_id__in=partner_user).values_list('id', flat=True)
        order = OrderRequest.objects.filter(Q(vision_center__in=user_vision_details)|Q(camp__in=camp_partner)|Q(created_by__in=user_partner_details),order_status__range=[2,4], status=2).order_by('-server_created_on')
    else:
        order = OrderRequest.objects.filter(order_status__range=[2,4], status=2).order_by('-server_created_on')
    
    if product_names:
        if request.session.get('role_id') == 4:
            order_details = OrderRequestDetails.objects.filter(order_request__status=2,product_id__in=product_names)
            order_ids = order_details.values_list('order_request__id', flat=True).distinct()
            order = OrderRequest.objects.filter(id__in=order_ids,created_by=request.user, order_status__range = [1,4]).order_by('-server_created_on')
        elif request.session.get('role_id') in [8, 9, 10]:
            apl_obj = ApplicationUserStateLinkage.objects.filter(user=request.user).values_list('state', flat=True)
            partner_user = Partner.objects.filter(state_id__in=apl_obj).values_list('id', flat=True)
            vision_center_details = VisionCenter.objects.filter(partner_id__in=partner_user).values_list('id', flat=True)
            user_vision_details = UserVisionCenterLinkage.objects.filter(vision_center_id__in=vision_center_details).values_list('vision_center__id', flat=True)
            user_partner_details = UserPartnerLinkage.objects.filter(partner_id__in=partner_user).values_list('user_id', flat=True)  
            camp_partner = Camp.objects.filter(partner_id__in=partner_user).values_list('id', flat=True)
            order_req = OrderRequest.objects.filter(Q(vision_center__in=user_vision_details) | Q(camp__in=camp_partner)|Q(created_by__in=user_partner_details),order_status__range=[2, 4],status=2).order_by('-server_created_on')
            order_details = OrderRequestDetails.objects.filter(order_request__in=order_req,order_request__status=2,product_id__in=product_names)
            order_ids = order_details.values_list('order_request__id', flat=True).distinct()
            order = OrderRequest.objects.filter(id__in=order_ids,order_status__range=[2, 4]).order_by('-server_created_on')
        elif request.session.get('role_id') == 6:
            order_details = OrderRequestDetails.objects.filter(order_request__status=2,product_id__in=product_names).values_list('order_request__id', flat=True).distinct()
            order = OrderRequest.objects.filter(id__in=order_details, order_status__in=[3,5]).order_by('-server_created_on')
        else:
            order_details = OrderRequestDetails.objects.filter(order_request__status=2,product_id__in=product_names)
            order_ids = order_details.values_list('order_request__id', flat=True).distinct()
            order = OrderRequest.objects.filter(id__in=order_ids, order_status__range = [2,4]).order_by('-server_created_on')
        
    if order_names:
        order = order.filter(order_status=order_names).order_by('-server_created_on')

    if state_name:
        order=order.filter(id=state_name)

    if search.isdigit():
        order = order.filter(Q(created_by__username__icontains=search) | Q(id=int(search))).order_by('-server_created_on')
    else:
        order = order.filter(created_by__username__icontains=search).order_by('-server_created_on')
    
    if start_filter != '' and end_filter != '':
        order = order.filter(server_created_on__gte=start_filter, server_created_on__lte=end_filter).order_by('-server_created_on')

    data = pagination_function(request, order)
    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)
    return render (request, 'inventory/orders/orders.html', locals())


@login_required(login_url='/login/')
def add_orders(request):
    heading = 'Add Order'
    order_requests = OrderRequest.objects.filter(status=2)
    partner_users = UserPartnerLinkage.objects.filter(user_id=request.user.id).values_list('partner_id',flat=True)
    # vision_centers = VisionCenter.objects.filter(partner_id__in=partner_users)
    partner_users = UserPartnerLinkage.objects.get(user_id=request.user.id) 
    donor_partner = DonorPartnerLinkage.objects.filter(status=2,partner_id=partner_users.partner.id).values_list('donor_id',flat=True)
    donors = Donor.objects.filter(status=2,id__in=donor_partner)
    vision_centers = VisionCenter.objects.filter(partner_id=partner_users.partner.id)

    # vision_centers = UserVisionCenterLinkage.objects.filter(status=2,user=request.user)
    camps = Camp.objects.filter(status=2)
    # donors = Donor.objects.filter(status=2)
    user = User.objects.all()
    products = Product.objects.all()
    time= datetime.datetime.now()
   
    if request.method == 'POST':
        value = [] 
        shippment_address = request.POST.get('shippment_address')
        table_choose = request.POST.get('table_choose')
        # camp = request.POST.get('camp')
        vision_center = request.POST.get('vision_center')
        address = request.POST.get('address')
        product_id = request.POST.get('table_selection')
        donor = request.POST.get('donor')
        district = request.POST.get('district')
        other_address = request.POST.get('other_address')

        if request.POST.get('near1'):
            dict_val = {1:request.POST.get('near1')}
            value.append(dict_val)
        if request.POST.get('near2'):
            dict_val = {2:request.POST.get('near2')}
            value.append(dict_val)
        if request.POST.get('near3'):
            dict_val = {3:request.POST.get('near3')}
            value.append(dict_val)
        if request.POST.get('near4'):
            dict_val = {4:request.POST.get('near4')}
            value.append(dict_val)
        if request.POST.get('near5'):
            dict_val = {5:request.POST.get('near5')}
            value.append(dict_val)
        if request.POST.get('near6'):
            dict_val = {6:request.POST.get('near6')}
            value.append(dict_val)
        if request.POST.get('near7'):
            dict_val = {7:request.POST.get('near7')}
            value.append(dict_val)
        if request.POST.get('near8'):
            dict_val = {8:request.POST.get('near8')}
            value.append(dict_val)
        if request.POST.get('near9'):
            dict_val = {9:request.POST.get('near9')}
            value.append(dict_val)

        if request.POST.get('r2c1'):
            dict_val = {11:request.POST.get('r2c1')}
            value.append(dict_val)
        if request.POST.get('r2c2'):
            dict_val = {12:request.POST.get('r2c2')}
            value.append(dict_val)
        if request.POST.get('r2c3'):
            dict_val = {13:request.POST.get('r2c3')}
            value.append(dict_val)
        if request.POST.get('r2c4'):
            dict_val = {14:request.POST.get('r2c4')}
            value.append(dict_val)
        if request.POST.get('r2c5'):
            dict_val = {15:request.POST.get('r2c5')}
            value.append(dict_val)
        if request.POST.get('r2c6'):
            dict_val = {16:request.POST.get('r2c6')}
            value.append(dict_val)
        if request.POST.get('r2c7'):
            dict_val = {17:request.POST.get('r2c7')}
            value.append(dict_val)
        if request.POST.get('r2c8'):
            dict_val = {18:request.POST.get('r2c8')}
            value.append(dict_val)
        # if request.POST.get('r2c9'):
        #     dict_val = {19:request.POST.get('r2c9')}
        #     value.append(dict_val)
        # if request.POST.get('r2c10'):
        #     dict_val = {20:request.POST.get('r2c10')}
        #     value.append(dict_val)
        
        frame = []    
        if request.POST.get('R2CCM015'):
            frame_val = {1:request.POST.get('R2CCM015')}
            frame.append(frame_val)
        if request.POST.get('R2CCM021'):
            frame_val = {2:request.POST.get('R2CCM021')}
            frame.append(frame_val)
            
        if value or frame:
            order_obj = OrderRequest.objects.create(
                vision_center_id=vision_center or None,
                # camp_id = camp or None,
                order_status=1,
                created_by=request.user,
                modified_by=request.user, 
                approved_on=time,
                order_for = table_choose,
                shippment_address =shippment_address,
                other_address = other_address,
                donor_id= donor,
                district_id= district

            )
            order_obj.save()
        
            for val in value:
                for key,value in val.items():
                    key = key
                    value = value
                    
                    order = OrderRequestDetails.objects.create(
                        order_request_id = order_obj.id,
                        product_id = product_id,
                        quantity = value ,
                        rrv = key,
                    )
                    order.save()

            for frm in frame:
                for key,value in frm.items():
                    key = key
                    value = value
                    frame_obj = OrderRequestDetails.objects.create(
                        order_request_id = order_obj.id,
                        product_id = product_id,
                        quantity = value ,
                        frame_type = key
                    )
                    frame_obj.save()
            
            return redirect('/edit_orders_new/'+str(order_obj.id))
        else:
            errors_view ="Please Select Atleast One Spectacle"
            print(errors_view)

    return render(request, 'inventory/orders/add_orders_new.html', locals())


@login_required(login_url='/login/')
def edit_orders_new(request, id , mail=None):
    heading = 'Edit Order'
    order = OrderRequest.objects.get(id=id)
    partner_id=UserPartnerLinkage.objects.get(user_id=order.created_by.id).partner.id
    partner_contact=UserPartnerLinkage.objects.get(user_id=order.created_by.id).partner
    details = OrderRequestDetails.objects.filter(order_request_id=order.id)
    prod_id = details.first().product.id
    date = order.server_created_on.strftime("%d-%m-%Y")
    heading_vpl = f'order # : {id} , date : {date}'
    
    try:
        ptr_vlu = Partner.objects.get(status=2, id=partner_id)
    except:
        ptr_vlu = ''
    donor_linked = DonorPartnerLinkage.objects.filter(donor__id = order.donor.id,partner_id=ptr_vlu.id).values_list('district__name',flat=True)
    donor_dist = ', '.join(list(donor_linked))
    
    vision_centers = VisionCenter.objects.filter(status=2)
    camps = Camp.objects.filter(status=2)
    donors = Donor.objects.filter(status=2)

    qty = details.first().quantity
    frame_type = details.first().frame_type
    # values = []
    for value in details:
        quant = value.quantity
        rrv = value.rrv
        frame_type = value.frame_type
        if rrv == 1:
            quant_1 = value.quantity
        if rrv == 2:
            quant_2 = value.quantity
        if rrv == 3:
            quant_3 = value.quantity
        if rrv == 4:
            quant_4 = value.quantity
        if rrv == 5:
            quant_5 = value.quantity
        if rrv == 6:
            quant_6 = value.quantity
        if rrv == 7:
            quant_7 = value.quantity
        if rrv == 8:
            quant_8 = value.quantity
        if rrv == 9:
            quant_9 = value.quantity
        if rrv == 11:
            quant_11 = value.quantity
        if rrv == 12:
            quant_12 = value.quantity
        if rrv == 13:
            quant_13 = value.quantity
        if rrv == 14:
            quant_14 = value.quantity
        if rrv == 15:
            quant_15 = value.quantity
        if rrv == 16:
            quant_16 = value.quantity
        if rrv == 17:
            quant_17 = value.quantity
        if rrv == 18:
            quant_18 = value.quantity
        # if rrv == 19:
        #     quant_19 = value.quantity
        # if rrv == 20:
        #     quant_20 = value.quantity
        if frame_type == 1:
            frame_1 = value.quantity
        if frame_type == 2:
            frame_2 = value.quantity

    user = User.objects.all()
    time = datetime.datetime.now()
    
    if mail == True:
        if order.order_status == 2:
            dear = 'Dear Sir/Madam'
            body = 'We require Readers/R2C spectacles for '+str(order.donor)+'. Kindly do the needful'
        elif order.order_status == 4:
            dear = 'Dear Partner'
            body = 'Your order is rejected due to '+str(order.remark)
        elif order.order_status == 5:
            dear = 'Dear Both,'
            body = 'The above mentioned order is dispatched. Kindly update the status once received.'
        return render(request, 'mailer/order_send_mail.html', locals())
    return render(request, 'inventory/orders/edit_orders_new.html', locals())


@login_required(login_url='/login/')
def order_details_edit(request, id):
    heading = 'Edit Order'
    order_obj = OrderRequest.objects.get(id=id)
    details_obj = OrderRequestDetails.objects.filter(order_request_id=order_obj.id)
    prod_id = details_obj.first().product.id
    
    camps = Camp.objects.filter(status=2)
    # donors = Donor.objects.filter(status=2)
    qty = details_obj.first().quantity
    order_requests = OrderRequest.objects.filter(status=2)
    partner_users = UserPartnerLinkage.objects.filter(user_id=request.user.id).values_list('partner_id',flat=True)
    vision_centers = VisionCenter.objects.filter(partner_id__in=partner_users)
    partner_users = UserPartnerLinkage.objects.get(user_id=request.user.id) 
    donor_partner = DonorPartnerLinkage.objects.filter(status=2,partner_id=partner_users.partner.id).values_list('donor_id',flat=True)
    donors = Donor.objects.filter(status=2,id__in=donor_partner)
    districts = District.objects.filter(id=order_obj.district.id)

    user = User.objects.all()
    products = Product.objects.all()
    for value in details_obj:
        quant = value.quantity
        rrv = value.rrv
        frame_type = value.frame_type
        if rrv == 1:
            quant_1 = value.quantity
        if rrv == 2:
            quant_2 = value.quantity
        if rrv == 3:
            quant_3 = value.quantity
        if rrv == 4:
            quant_4 = value.quantity
        if rrv == 5:
            quant_5 = value.quantity
        if rrv == 6:
            quant_6 = value.quantity
        if rrv == 7:
            quant_7 = value.quantity
        if rrv == 8:
            quant_8 = value.quantity
        if rrv == 9:
            quant_9 = value.quantity
        if rrv == 11:
            quant_11 = value.quantity
        if rrv == 12:
            quant_12 = value.quantity
        if rrv == 13:
            quant_13 = value.quantity
        if rrv == 14:
            quant_14 = value.quantity
        if rrv == 15:
            quant_15 = value.quantity
        if rrv == 16:
            quant_16 = value.quantity
        if rrv == 17:
            quant_17 = value.quantity
        if rrv == 18:
            quant_18 = value.quantity
        # if rrv == 19:
        #     quant_19 = value.quantity
        # if rrv == 20:
        #     quant_20 = value.quantity
        if frame_type == 1:
            frame_1 = value.quantity
        if frame_type == 2:
            frame_2 = value.quantity


    if request.method == 'POST':
        value = [] 
        shippment_address = request.POST.get('shippment_address')
        table_choose = request.POST.get('table_choose')
        vision_center = request.POST.get('vision_center')
        address = request.POST.get('address')
        product_id = request.POST.get('table_selection')
        donor = request.POST.get('donor')
        district = request.POST.get('district')
        other_address = request.POST.get('other_address')
        
        dict_val = {1:request.POST.get('near1')}
        value.append(dict_val)
        dict_val = {2:request.POST.get('near2')}
        value.append(dict_val)
        
        dict_val = {3:request.POST.get('near3')}
        value.append(dict_val)
        
        dict_val = {4:request.POST.get('near4')}
        value.append(dict_val)
       
        dict_val = {5:request.POST.get('near5')}
        value.append(dict_val)
       
        dict_val = {6:request.POST.get('near6')}
        value.append(dict_val)
        
        dict_val = {7:request.POST.get('near7')}
        value.append(dict_val)
        
        dict_val = {8:request.POST.get('near8')}
        value.append(dict_val)
        
        dict_val = {9:request.POST.get('near9')}
        value.append(dict_val)
        
        dict_val = {11:request.POST.get('r2c1')}
        value.append(dict_val)

        dict_val = {12:request.POST.get('r2c2')}
        value.append(dict_val)
        
        dict_val = {13:request.POST.get('r2c3')}
        value.append(dict_val)
       
        dict_val = {14:request.POST.get('r2c4')}
        value.append(dict_val)
        
        dict_val = {15:request.POST.get('r2c5')}
        value.append(dict_val)
     
        dict_val = {16:request.POST.get('r2c6')}
        value.append(dict_val)
       
        dict_val = {17:request.POST.get('r2c7')}
        value.append(dict_val)
        
        dict_val = {18:request.POST.get('r2c8')}
        value.append(dict_val)
      
        # dict_val = {19:request.POST.get('r2c9')}
        # value.append(dict_val)
        
        # dict_val = {20:request.POST.get('r2c10')}
        # value.append(dict_val)
        
        if request.POST.get('R2CCM015'):
            dict_val = {1:request.POST.get('R2CCM015')}
            value.append(dict_val)
        if request.POST.get('R2CCM021'):
            dict_val = {2:request.POST.get('R2CCM021')}
            value.append(dict_val)
        order_obj.vision_center_id=vision_center or None
        order_obj.order_for = table_choose 
        order_obj.modified_by_id = request.user.id
        order_obj.shippment_address =shippment_address 
        order_obj.other_address = other_address 
        order_obj.donor_id= donor 
        order_obj.district_id= district 
        order_obj.save()
        
        for val in value:
            for key, val_value in val.items():
                if val_value != '' and int(val_value) != 0:
                    obj, created = OrderRequestDetails.objects.update_or_create(
                        order_request_id = order_obj.id,
                        product_id = product_id,
                        rrv = key,
                        defaults = {
                        "quantity" : val_value
                        })
                    obj.save()
                else:
                    obj_req = OrderRequestDetails.objects.filter(order_request=order_obj.id,rrv = key )
                    obj_req.delete()
                    
        
        frame = []
        frame_val = {1: request.POST.get('R2CCM015')}
        frame.append(frame_val)
       
        frame_val = {2: request.POST.get('R2CCM021')}
        frame.append(frame_val)
        
        for frm in frame:
            for key, val_value in frm.items():
                if val_value != '' and int(val_value) != 0:
                    obj, created = OrderRequestDetails.objects.update_or_create(
                        order_request_id = order_obj.id,
                        product_id = product_id,
                        frame_type = key,
                        defaults = {
                        "quantity" : val_value
                        })
                        
                    obj.save()
                else:
                    obj_req = OrderRequestDetails.objects.filter(order_request=order_obj.id,frame_type = key )
                    obj_req.delete()
            
        return redirect('/edit_orders_new/'+str(order_obj.id))
    return render(request, 'inventory/orders/order_details_edit.html', locals())



@login_required(login_url='/login/')
def add_invoice_awb_no(request, order_id, invoice_date = None, invoice_no = None,  invoice_value = None, courier_name = None, awb_no = None):
    order = OrderRequest.objects.get(id=order_id)
    date_field = datetime.datetime.now().date()
    if invoice_date is not None and invoice_date.strip() != '':
        invoice_date = invoice_date.strip()
    else:
        invoice_date = date_field
    invoice_no = invoice_no.strip() if invoice_no else None
    invoice_value = invoice_value.strip() if invoice_value else None
    courier_name = courier_name.strip() if courier_name else None
    awb_no = awb_no.strip() if awb_no else None

    order.invoice_date = invoice_date
    order.invoice_no = invoice_no
    order.invoice_value = invoice_value
    order.courier_name = courier_name
    order.awb_no = awb_no
    order.order_status = 5 
    order.save()
    if order.get_product().product.id != 5:
        send_mail_res = edit_orders_new(request,order_id, mail=True)
    else:
        send_mail_res = generate_order_details(request,order_id, mail=True)
    html_content = send_mail_res.content.decode("utf-8")
    send_mail_response = send_mail(order_id,5, html_content)
    return redirect('/orders/')


# def add_invoice_awb_no(request, order_id, invoice_no, awb_no,invoice_date,invoice_value,courier_name):
#     order = OrderRequest.objects.get(id=order_id)
#     order.invoice_no = invoice_no
#     order.awb_no = awb_no
#     order.invoice_date = request.POST.get('invoice_date')
#     order.invoice_value = request.POST.get('invoice_value')
#     order.courier_name = request.POST.get('courier_name')
#     order.order_status = 5
#     order.save()

#     # Send the email
#     if order.get_product().product.id != 5:
#         send_mail_res = edit_orders_new(request,order_id, mail=True)
#     else:
#         send_mail_res = generate_order_details(request,order_id, mail=True)
#     html_content = send_mail_res.content.decode("utf-8")
#     send_mail_response = send_mail(order_id,5, html_content)
#     return redirect('/orders/')


@login_required(login_url='/login/')
def delete_orders(request, id):
    order = OrderRequest.objects.get(id=id)
    products = OrderRequestDetails.objects.filter(order_request_id=order.id)
    products.delete()
    order.delete()
    return redirect('/orders/')




@login_required(login_url='/login/')
def order_receipt(request):
    heading = 'Order Receipt'
    search = request.GET.get('search', '')
    try:
        user= UserProfile.objects.get(user__username= request.user, role__id=4)
        role=user.role.id
    except:
        role= None
    # if request.session.get('role_id') == 3:
    #     order = OrderRequest.objects.filter(order_status__range=[2,4], status=2).order_by('-server_created_on')
    # elif request.session.get('role_id') == 6:
    #     order = OrderRequest.objects.filter(order_status__in=[3,5], status=2).order_by('-server_created_on')

    # else:
        # order = OrderRequest.objects.filter(status=2).order_by('-server_created_on')
    if request.session.get('role_id') == 3:
        order = OrderRequest.objects.filter(order_status=5 ,status=2).order_by('-server_created_on')
    else:
        order = OrderRequest.objects.filter(order_status=5 ,status=2, created_by=request.user).order_by('-server_created_on')

    if search :
        order=order.filter(created_by__username__icontains=search).order_by('-server_created_on')
    
    data = pagination_function(request, order)
    current_page = request.GET.get('page', 1)
    page_number_start = int(current_page) - 2 if int(current_page) > 2 else 1
    page_number_end = page_number_start + 5 if page_number_start + \
        5 < data.paginator.num_pages else data.paginator.num_pages+1
    display_page_range = range(page_number_start, page_number_end)
    return render (request, 'inventory/order_receipt/order_receipt_list.html', locals())


@login_required(login_url='/login/')
def edit_order_receipt(request, id):
    heading = 'Edit Order'
    order = OrderRequest.objects.get(id=id)
    partner_id=UserPartnerLinkage.objects.get(user_id=order.created_by.id).partner.id
    
    try:
        ptr_vlu = Partner.objects.get(status=2, id=partner_id)
    except:
        ptr_vlu = ''

    donor_linked = DonorPartnerLinkage.objects.filter(donor__id = order.donor.id,partner_id=ptr_vlu.id).values_list('district__name',flat=True)
    donor_dist = ', '.join(list(donor_linked))
    products = OrderRequestDetails.objects.filter(order_request_id=order.id)

    
    details = OrderRequestDetails.objects.filter(order_request_id=order.id)
    prod_id = details.first().product.id
   
    vision_centers = VisionCenter.objects.filter(status=2)
    camps = Camp.objects.filter(status=2)
    donors = Donor.objects.filter(status=2)
    qty = details.first().quantity
    # values = []
    for value in details:
        quant = value.quantity
        rrv = value.rrv
        frame_type = value.frame_type
        if rrv == 1:
            quant_1 = value.quantity
        if rrv == 2:
            quant_2 = value.quantity
        if rrv == 3:
            quant_3 = value.quantity
        if rrv == 4:
            quant_4 = value.quantity
        if rrv == 5:
            quant_5 = value.quantity
        if rrv == 6:
            quant_6 = value.quantity
        if rrv == 7:
            quant_7 = value.quantity
        if rrv == 8:
            quant_8 = value.quantity
        if rrv == 9:
            quant_9 = value.quantity
        if rrv == 11:
            quant_11 = value.quantity
        if rrv == 12:
            quant_12 = value.quantity
        if rrv == 13:
            quant_13 = value.quantity
        if rrv == 14:
            quant_14 = value.quantity
        if rrv == 15:
            quant_15 = value.quantity
        if rrv == 16:
            quant_16 = value.quantity
        if rrv == 17:
            quant_17 = value.quantity
        if rrv == 18:
            quant_18 = value.quantity
        # if rrv == 19:
        #     quant_19 = value.quantity
        # if rrv == 20:
        #     quant_20 = value.quantity
        if frame_type == 1:
            frame_1 = value.quantity
        if frame_type == 2:
            frame_2 = value.quantity


    order_requests = OrderRequest.objects.filter(status=2)
    vision_centers = VisionCenter.objects.filter(status=2)
    camps = Camp.objects.filter(status=2)
    donors = Donor.objects.filter(status=2)
    user = User.objects.all()
    time = datetime.datetime.now()

    if request.method == 'POST':
        value = []
        shippment_address = request.POST.get('shippment_address')
        table_choose = request.POST.get('table_choose')
        camp = request.POST.get('camp')
        vision_center = request.POST.get('vision_center')
        address = request.POST.get('address')
        product_id = request.POST.get('table_selection')
        donor = request.POST.get('donor')
        other_address= request.POST.get('other_address')
        # Update order details
        order.vision_center_id = vision_center or None
        order.camp_id = camp or None
        order.order_for = table_choose
        order.order_status = 2
        order.shippment_address = shippment_address
        order.modified_by = request.user
        order.modified_on = time
        order.save()

        for val in value:
            for key, value in val.items():
                order_detail = OrderRequestDetails.objects.create(
                    order_request=order,
                    product_id=product_id,
                    quantity=value,
                    rrv=key
                )
                order_detail.save()

        return redirect('/order_receipt/')

    return render(request, 'inventory/order_receipt/edit_order_receipt.html', locals())



def send_mail(order_id,order_status_id,html_message,isTls=True):
    import smtplib
    import os
    from weasyprint import HTML, CSS
    from email.mime.image import MIMEImage
    
    try:
        msg = MIMEMultipart()
        msg2 = MIMEMultipart()
        msg3 = MIMEMultipart()
        order = OrderRequest.objects.get(id=order_id)
        order_del = OrderRequestDetails.objects.filter(order_request_id=order.id).first()
        admin_id = UserProfile.objects.get(role_id=3, status=2).user.id
        admin_eid = User.objects.get(id=admin_id).email
        vendor_id = UserProfile.objects.get(role_id=6, status=2).user.id
        vendor_eid = User.objects.get(id=vendor_id).email
        vendor_emails = Vendor.objects.filter(status=2).values_list('email_id', 'alternative_email_id_1', 'alternative_email_id_2', 'alternative_email_id_3', 'alternative_email_id_4')
        valid_email_addresses = [email for sublist in vendor_emails for email in sublist if email]
        valid_email_addresses = list(filter(None, valid_email_addresses))

        user_part_ids = UserPartnerLinkage.objects.filter(user_id=order.created_by.id).values_list('partner_id', flat=True)
        partner_obj = Partner.objects.filter(id__in=user_part_ids).values_list('state_id', flat=True)
        app_obj = ApplicationUserStateLinkage.objects.filter(state__in=partner_obj).values_list('user_id', flat=True)
        user_coordnator = UserProfile.objects.filter(role_id=9, status=2, user_id__in=app_obj)
        user_incharge = UserProfile.objects.filter(role_id=10, status=2, user_id__in=app_obj)

        user_coor_email_id = None
        user_incharge_email = None

        if user_coordnator.exists():
            user_coor_email_id = user_coordnator.first().user.email

        if user_incharge.exists():
            user_incharge_email = user_incharge.first().user.email

        if order.get_product().product.id != 5:
            product_name = order_del.product.name
        else:
            product_name = 'Custom made'
        try:
            user_id = UserPartnerLinkage.objects.get(user_id=order.created_by.id)
            partner_email_id = User.objects.get(id=user_id.user.id).email
        except:
            user_id = ''
        # order.
        msg['From'] = "misindia@sightsaversindia.org"
        msg2['From'] = "misindia@sightsaversindia.org"
        msg3['From'] = "misindia@sightsaversindia.org"
        if int(order_status_id) == 2:
            admin_cont = product_name + ' order request from ' + user_id.partner.name + '. Order #: '+str(order_id)
            zonal_coor = product_name + ' order request from ' + user_id.partner.name + '. Order #: '+str(order_id)
            zonal_inch = product_name + ' order request from ' + user_id.partner.name + '. Order #: '+str(order_id)
            msg['To'] = admin_eid
            msg['Subject'] = admin_cont
            msg2['To'] = user_coor_email_id
            msg2['Subject'] = zonal_coor
            msg3['To'] = user_incharge_email
            msg3['Subject'] = zonal_inch
        elif int(order_status_id) == 3:
            partner_sub = product_name + ' is approved. Order #: '+str(order_id)
            vender_sub = 'You have received an approved. Order #: ' +str(order_id)+ ' from '+user_id.partner.name
            msg['To'] = ", ".join(valid_email_addresses)
            msg['Subject'] = vender_sub
            msg2['To'] = partner_email_id
            msg2['Subject'] = partner_sub 
            text1 = "Dear vendor, \n \nThe attached order is approved. Kindly do the needful. \n"
            text2 = "Dear Partner, \n \nThe Your order is approved. \n"
            partbp=MIMEText(text1, 'plain')
            partbv=MIMEText(text2, 'plain')
            msg.attach(partbp)
            msg2.attach(partbv)
        elif int(order_status_id) == 4:
            msg['To'] = partner_email_id
            msg['Subject'] = product_name + ' order request is rejected. Order #: '+ str(order_id) 
        elif int(order_status_id) == 5:
            subject = product_name + ' order is shipped. Order #: '+ str(order_id) + ' - ' + user_id.partner.name
            msg['To'] = partner_email_id
            msg['Subject'] = subject
            msg2['To'] = admin_eid
            msg2['Subject'] = subject
        
        part1=MIMEText(html_message, 'html')
        html_content = html_message
        html = HTML(string=html_content)
        pdf_options = {
        'page-size': 'A3',
        'margin-top': '0mm',
        'margin-right': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        }
        css = CSS(string='''
        .a6T {
            width: 80px!important;
            height: 45px!important;
        }
        h1, p, td, th {
            font-size: 8pt!important;
        }
        table {
            border-collapse: collapse;
            width: 100%;
        }

        th, td {
            border: 1px solid black;
            padding: 4px!important;
        }
        .text-center {
            text-align: center!important;
        }
        ''')


        # Export the HTML object to a PDF file
        
        pdf_file = settings.MEDIA_ROOT + '/' + user_id.partner.name + '-' + str(order_id) +'.pdf'
        html.write_pdf(pdf_file, stylesheets=[css], **pdf_options)

        # img_dir = settings.MEDIA_ROOT + '/send_logo'
        # image = 'maillogo.png'
        # file_path = os.path.join(img_dir, image)
        # fp = open(file_path, 'rb')
        # msgImage = MIMEImage(fp.read())
        # fp.close()
        # msgImage.add_header('Content-ID', '<image1>')
    
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(pdf_file, "rb").read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "inline" ,filename= user_id.partner.name + '-' + str(order_id) +'.pdf')
        if int(order_status_id) != 4:
            msg.attach(part)
        msg.attach(part1)
        if int(order_status_id) != 3:
            msg2.attach(part)
        msg2.attach(part1)

        smtp = smtplib.SMTP(settings.EMAIL_HOST,settings.EMAIL_PORT)
        if isTls:
            smtp.starttls()
        smtp.login(settings.EMAIL_HOST_USER,settings.EMAIL_HOST_PASSWORD)
        if int(order_status_id) == 3:
            msg_send_status = smtp.sendmail(msg['From'], valid_email_addresses ,msg.as_string())
        else:
            msg_send_status = smtp.sendmail(msg['From'], msg['To'] ,msg.as_string())
        if int(order_status_id) == 3 or int(order_status_id) == 5 or int(order_status_id) == 2:
            msg_send_status = smtp.sendmail(msg2['From'], msg2['To'] ,msg2.as_string())
        if int(order_status_id) == 2:
            msg_send_status = smtp.sendmail(msg3['From'], msg3['To'] ,msg3.as_string())
        smtp.quit()

        os.remove(pdf_file)

        return msg_send_status
    except Exception as e:
        # logger.error(e.args[0])
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        errors = 'product id: ' +str(order_id) +str(error_stack) 
        logger.error(errors)


import io
import xlsxwriter

def export_order_details_to_excel(request, order_id):
    try:
        order = OrderRequest.objects.get(id=order_id)
        spectacletype_obj = SpectacleType.objects.filter(status=2, spectacle_name='Custom made', order_id=order_id).order_by('-server_created_on')
        if spectacletype_obj:
            try:
                detail_view = spectacletype_obj.first()
                districts=DonorPartnerLinkage.objects.filter(partner_id=detail_view.get_partner_shippment_address()[0].partner.id,donor__id = order.donor.id).values_list('district__name', flat=True)
                donor_linakage_list = ', '.join(list(districts))
            except:
                detail_view = spectacletype_obj.first()
                districts=DonorPartnerLinkage.objects.filter(partner_id=detail_view.get_partner_shippment_address()[1].partner.id,donor__id = order.donor.id).values_list('district__name', flat=True)
                donor_linakage_list = ', '.join(list(districts))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        vc_name = detail_view.get_pnt_details()[0].get_vision_center().name if detail_view.get_pnt_details()[0].get_vision_center() else detail_view.get_pnt_details()[0].camp.name
        shippment = order.camp.partner.address if order.order_for == 2 else order.vision_center.address
        # contact = detail_view.get_pnt_details()[0].camp.partner.name + ' | ' + detail_view.get_pnt_details()[0].camp.partner.contact_no if order.order_for == 2 else detail_view.get_partner_shippment_address()[0].partner + ' | ' + (detail_view.get_partner_shippment_address()[0].partner.contact_no)
        contact = str(detail_view.get_pnt_details()[0].camp.partner.name) + ' | ' + str(detail_view.get_pnt_details()[0].camp.partner.contact_no) if order.order_for == 2 else str(detail_view.get_partner_shippment_address()[0].partner) + ' | ' + str(detail_view.get_partner_shippment_address()[0].partner.contact_no)
        
        partner = detail_view.get_pnt_details()[0].camp.partner if order.order_for == 2 else detail_view.get_partner_shippment_address()[0].partner
        user_partner_linkages = UserPartnerLinkage.objects.filter(partner=partner)
        user_ids = user_partner_linkages.values_list('user_id', flat=True)
        users = UserProfile.objects.filter(user_id__in=user_ids)

        user_data = [f"{user.user.username} | {partner.contact_no}" for user in users]
        user_info = ', '.join(user_data)

        loc = ['Location name : ', vc_name + ' - ' + str(detail_view.get_pnt_details()[0].donor)] 
        part = ['Partner/ Shipment address : ', shippment] 
        cont = ['Contact person name and Contact number : ', user_info]
        form = ['Order Id : ',order.id]
        order_date = ['Order date : ', order.server_created_on.strftime("%Y-%m-%d")]

        bold_format = workbook.add_format({'bold': True})

        # Set borders for bold cells
        bold_format.set_border()

        worksheet.write(0, 0, loc[0], bold_format)
        worksheet.write(0, 1, loc[1])

        worksheet.write(1, 0, part[0], bold_format)
        worksheet.write(1, 1, part[1])

        worksheet.write(2, 0, cont[0], bold_format)  
        worksheet.write(2, 1, cont[1])

        worksheet.write(3, 0, form[0], bold_format)  
        worksheet.write(3, 1, form[1])

        worksheet.write(4, 0, order_date[0], bold_format)
        worksheet.write(4, 1, order_date[1])

        worksheet.write(5, 0, '')
        worksheet.write(6, 0, '')

        headers = ['S.No', 'UID', 'Vision Center/Partner', 'Name of Patient', 'Mobile number', 'Vision', 'Right Eye', 'Left Eye', 'Frame Code', 'Frame Size', 'Type and Coating']
        subheaders = ['Sph', 'Cyl', 'Axis', 'V/A', 'Sph', 'Cyl', 'Axis', 'V/A']

        for col_num, header in enumerate(headers):
            worksheet.write(7, col_num, header, bold_format)

        worksheet.merge_range(7, 6, 7, 9, 'Right Eye', bold_format)
        for col_num, subheader in enumerate(subheaders[:4]):
            worksheet.write(8, col_num + 6, subheader, bold_format)

        worksheet.merge_range(7, 10, 7, 13, 'Left Eye', bold_format)
        for col_num, subheader in enumerate(subheaders[:4]):
            worksheet.write(8, col_num + 10, subheader, bold_format)

        frame_headers = ['Frame Code', 'Frame Size', 'Type and Coating']
        for col_num, frame_header in enumerate(frame_headers):
            worksheet.write(7, col_num + 14, frame_header, bold_format)

        row = 9
        s_no = 1
        for district in spectacletype_obj:
            worksheet.write(row, 0, s_no)
            worksheet.write(row, 1, district.get_pnt_details()[0].unique_id)
            vision_center_name = district.get_pnt_details()[0].get_vision_center().name if district.get_pnt_details()[0].get_vision_center() else district.get_pnt_details()[0].camp.partner.name
            worksheet.write(row, 2, vision_center_name)
            worksheet.write(row, 3, district.get_pnt_details()[0].name)
            worksheet.write(row, 4, district.get_pnt_details()[0].contact_no_1)
            worksheet.write(row, 5, 'Distance')
            worksheet.write(row + 1, 5, 'Near')

            pnt_details = district.get_pnt_details()
            if len(pnt_details) > 1:
                worksheet.write(row, 6, pnt_details[1].sph_distance_re)
                worksheet.write(row + 1, 6, pnt_details[1].sph_near_re)
                worksheet.write(row, 7, pnt_details[1].cyl_distance_re)
                worksheet.write(row + 1, 7, pnt_details[1].cyl_near_re)
                worksheet.write(row, 8, pnt_details[1].axis_distance_re)
                worksheet.write(row + 1, 8, pnt_details[1].axis_near_re)
                worksheet.write(row, 9, str(pnt_details[1].va_distance_re))
                worksheet.write(row + 1, 9, str(pnt_details[1].va_near_re))
                worksheet.write(row, 10, pnt_details[1].sph_distance_le)
                worksheet.write(row + 1, 10, pnt_details[1].sph_near_le)
                worksheet.write(row, 11, pnt_details[1].cyl_distance_le)
                worksheet.write(row + 1, 11, pnt_details[1].cyl_near_le)
                worksheet.write(row, 12, pnt_details[1].axis_distance_le)
                worksheet.write(row + 1, 12, pnt_details[1].axis_near_le)
                worksheet.write(row, 13, str(pnt_details[1].va_distance_le))
                worksheet.write(row + 1, 13, str(pnt_details[1].va_near_le))
                
            worksheet.write(row, 14, str(district.frame_code))
            worksheet.write(row, 15, str(district.frame_size))
            worksheet.write(row, 16, str(district.type_of_coating))

            row += 2
            s_no += 1

        workbook.close()

        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        username = vision_center_name[:8]
        filename = f"order_details_{username}_{current_date}.xlsx"

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        output.seek(0)
        response.write(output.read())

        return response

    except Exception as e:
        # Handle exceptions
        print(e)
        return HttpResponse("An error occurred while exporting the order details.")
