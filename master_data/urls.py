from django.urls import path
from .views import *
from .android_api import *

urlpatterns = [
    
    path('list/<model>/', master_list_form),
    path('add/<model>/', master_add_form),
    path('edit/<model>/<id>/', master_edit_form),
    path('details/<model>/<id>/', master_details_form),
    path('<model>/<id>/delete/', delete_record,name='delete_record'),
    # path('user_list/', user_list,name='user_list'),
    path('add_user/userprofile/', user_add),
    path('edit_user/userprofile/<id>/', user_edit),
    path('edit_password/<id>/', edit_password),
    path('ajax/district/<state_id>/', get_district, name="get_district"),
    path('ajax/state/<zone_id>/', get_state, name="id_state"),
    path('vendor_partner_user_mapping/<vendor_partner_id>/<model>/', vendor_partner_user_mapping, name="vendor_partner_user_mapping"),
    path('ajax/donor/<partner_id>/', get_donor, name="id_donor"),
    path('ajax/partner_state/<state_id>/', get_partner_state, name="id_partner"),
    path('ajax/donor_district/<donor_id>/', get_donor_district, name="donor_id"),
    path('ajax/get_district_donor/<district_id>/<partner_id>/', get_district_donor, name="district_id"),

    path('donor-location-listing/<partner_id>/', donor_partner_location_listing, name="donor_partner_location_listing"),
    path('donor-location-mapping/<partner_id>/', donor_partner_location_mapping, name="donor_partner_location_mapping"),
    path('partner-donor-status/<dpl_id>/', partner_donor_status_update, name="partner_donor_status_update"),
    path('user-state-status/<usl_id>/', user_status_status_update, name="user_status_status_update"),

    path('application-user-state-linkage/list/<user_id>/', application_user_state_linkage_list, name="application_user_state_linkage_list"),
    path('add/application-user-state-linkage/<user_id>/', add_application_user_state_linkage, name="add_application_user_state_linkage"),
    path('edit/application-user-state-linkage/<user_id>/<id>/', edit_application_user_state_linkage, name="edit_application_user_state_linkage"),

    path('master-data/', MasterData.as_view()),
    path('app-login/', LoginAPIView.as_view()),
    path('pull-api/', PullAPIView.as_view()),
    path('push-api/', PushAPIView.as_view()),
    path('patient-details-api/', PatientDetailsAPIView.as_view()),
    path('otp-verification-api/', OTPVerificationAPIView.as_view()),
    path('mpr/data/', MPRData.as_view()),
    path('patient/data/', PatientData.as_view()),
    path('screening/data/', ScreeningData.as_view()),
    path('glass-prescription/data/', GlassPrescriptionData.as_view()),
    path('family-members/data/', FamilyData.as_view()),
    path('wrong/data/', WrongPushAPIView.as_view()),
    path('version-release-notes/', VersionReleaseNote.as_view()),

    # user password change
    path('change-user-password/', change_user_password),
    path('otp-sms/',send_sms),


]