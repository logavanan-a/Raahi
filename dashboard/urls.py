from django.urls import path
from dashboard.views import *
from dashboard.views_v2 import *
from dashboard.chart_js_view import *


app_name = "dashboard"
urlpatterns = [
    path('old_dashboard/', dashboard, name="dashboard"),
    path('dashboard/v3/', google_map, name="dashboard_v3"),
    path('dashboard/v4/', dashboard_v2, name="dashboard_v2"),
    path('dashboard/', dashboard_v4, name="dashboard_v4"),
    # path('ajax/state-values/', get_state_values, name="get_state_values"),
    path('ajax/dash_state/',get_state_values , name="get_state"),
    path('ajax/dash_donor/',get_donor_values, name="get_donor"),
    path('ajax/dash_hospital/',get_partner_values, name="get_partner"),
    path('patient_map/', patient_map, name="patient_map"),

]
