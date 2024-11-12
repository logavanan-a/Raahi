from django.urls import path
from .views import *
from . telecalling import *
from . orders import *

urlpatterns = [
    path('orderrequest_list/', orderrequest_list,name='orderrequest_list'),
    path('add_orderdetails/', add_orderdetails,name='add_orderdetails'),
    path('change_order_status/<str:model>/<int:id>/<str:action>/', change_order_status, name='change_order_status'),
    path('orderdelivery_list/', orderdelivery_list,name='orderdelivery_list'),
    path('add_deliverydetails/', add_deliverydetails,name='add_deliverydetails'),
    path('orders/', orders,name='orders'),
    path('edit_orders/<id>/', edit_orders,name='edit_orders'),
    path('update_order_status/<order_id>/<order_status_id>/', update_order_status,name='update_order_status'),
    path('add_orders/', add_orders,name='add_orders'),
    path('edit_orders_new/<id>/', edit_orders_new,name='edit_orders_new'),
    path('delete_orders/<id>/', delete_orders,name='delete_orders'),
    path('order_details_edit/<id>/', order_details_edit,name='order_details_edit'),
    path("ajax-reject/<reject_id>/<remark>", reject_remark, name="reject_remark"),
    path("add_invoice_awb_no/<order_id>/<invoice_no>/<awb_no>/<invoice_date>/<invoice_value>/<courier_name>/", add_invoice_awb_no, name="add_invoice_awb_no"),

    path('camp_list/', camp_list,name='camp_list'),
    path('camp_date_update/<camp_id>/<date>/<reason>/', camp_date_update,name='camp_date_update'),
    path('add_camp/', add_camp,name='add_camp'),
    path('edit_camp/<id>', edit_camp,name='edit_camp'),
    path('<id>/delete_camp/', delete_camp,name='delete_camp'),

    path('drop_check/', drop_check,name='drop_check'),
    path('order_receipt/', order_receipt,name='order_receipt'),
    path('edit_order_receipt/<id>/', edit_order_receipt,name='edit_order_receipt'),
    path('edit_deliverydetails/<id>/', edit_deliverydetails,name='edit_deliverydetails'),
    path('calculate_damagedetails/<order_id>/', calculate_damagedetails,name='calculate_damagedetails'),

    path('custom-order-request/', custom_order_request,name='custom_order_request'),
    path('generate-order-details/', generate_order_details,name='generate_order_details'),
    path('edit_orders_custom/<order_id>/', generate_order_details,name='edit_orders_custom'),
    path('update_custom_received/<order_id>/<invoice_nos>/', update_custom_received,name='update_custom_received'),
    
    # Patient
    path('patient_list/', patient_list,name='patient_list'),
    path('patient-details/<uuid>/', patient_details,name='patient_details'),
    path('screening_list/', screening_list,name='screening_list'),

    # Telecalling
    path('spectacle-list/', spectacle_list,name='spectacle_list'),
    path('spectacle-details/<uuid>/', spectacle_details,name='spectacle_details'),
    path('add-questions/', add_questions,name='add_questions'),
    path('cataract-list/', cataract_list,name='cataract_list'),
    path('cataract-details/<uuid>/', cataract_details,name='cataract_details'),
    path('cataract_patient-details/<uuid>/', cataract_patient_details,name='cataract_patient_details'),
    path('spectacle_patient-details/<uuid>/', spectacle_patient_details,name='spectacle_patient_details'),

    # Glass
    path('glass-list-pending/', glass_list_pending,name='glass_list_pending'),
    path('glass-list-ready/', glass_list_ready,name='glass_list_ready'),
    path('glass-list-delivered/', glass_list_delivered,name='glass_list_delivered'),
    path('update_glass_followup_status/<patient_id>/<followup_status_id>/', update_glass_followup_status,name='update_glass_followup_status'),

    path('qr-code/',qr_code_generation, name='qr_code_generation'),
    path('data-freeze/',data_freeze, name='data_freeze'),
    path('data-freeze-patients/<data_freeze_id>/',data_freezed_patients, name='data_freezed_patients'),
    path('approve-patient/<data_freeze_id>/', approve_patient,name='approve_patient'),
    path('export_order_details_to_excel/<int:order_id>/', export_order_details_to_excel, name='export_order_details_to_excel'),

]