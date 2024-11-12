from django.urls import path, include
from .views import *


app_name = "reports"
urlpatterns = [
    path('report/<page_slug>/', custom_report, name="custom_report"),
    path('report/truc-month-report/month/',truckers_month_report , name="truckers_month"),
    path('ajax/custom_report_reload/<page_slug>/<report_slug>/', custom_report_reload, name="custom_report_reload"),
    path('ajax/report_district/', get_district, name="get_district"),
    path('ajax/report_camp/', get_camp, name="get_camp"),
    path('ajax/report_donor/', get_donor, name="get_donor"),
    path('ajax/report_partner/', get_partner, name="get_partner"),
    path('report/download-excel/<report_id>/',download_excel,name ="download_excel"),
    path('mpr/report/mpr-review/',mpr_review,name ="mpr_review"),

    path('national_status_approve/<status_id>/<month_year>/<zone_id>/', national_status_approve, name='national_status_approve'),
    path('national_status_reject/<status_id>/<month_year>/<remark>/<zone_id>/', national_status_reject, name='national_status_reject'),
    path('mpr_status_update/<status_id>/<month_year>/', mpr_status_update, name='mpr_status_update'),
    path('mpr_status_approve/<status_id>/<id>/', mpr_status_approve, name='mpr_status_approve'),
    path('mpr_status_reject/<reject_id>/<id>/<remark>/', mpr_status_reject, name='mpr_status_reject'),
    path('approve-all/<key>/<month_year>/', approve_all, name='approve_all'),
    
    path('ppa_mpr_status_update/<zone_id>/<month_year>/<command>/', ppa_mpr_status_update, name='ppa_mpr_status_update'),


]