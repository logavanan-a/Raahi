from django.contrib import admin
from . models import *
from  master_data. admin import *
import uuid
from import_export.admin import ImportExportModelAdmin, ImportExportMixin
from import_export.formats import base_formats
from import_export import resources, fields
from import_export.fields import Field



class ImportExportFormat(ImportExportMixin):
    def get_export_formats(self):
        formats = (base_formats.CSV, base_formats.XLSX, base_formats.XLS,)
        return [f for f in formats if f().can_export()]

    def get_import_formats(self):
        formats = (base_formats.CSV, base_formats.XLSX, base_formats.XLS,)
        return [f for f in formats if f().can_import()]

# Register your models here.
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ['id','name','server_created_on','server_modified_on','status']
    fields = ['name','status']
    search_fields = ['id','name']
    list_per_page = 100

@admin.register(OrderRequest)
class OrderRequestAdmin(ImportExportModelAdmin):
    list_display = ['id','vision_center', 'order_status','created_by','approved_by', 'approved_on','camp','order_for','shippment_address', 'other_address', 'remark', 'donor', 'district', 'invoice_date', 'invoice_no', 'invoice_value', 'courier_name', 'awb_no',
    'server_created_on','server_modified_on', 'status']
    fields = ['vision_center', 'order_status','created_by','approved_by', 'approved_on','camp','order_for','shippment_address', 'other_address', 'remark', 'donor', 'district', 'invoice_date', 'invoice_no', 'invoice_value', 'courier_name', 'awb_no', 'status']
    search_fields = ['id','vision_center__name','order_status']
    list_per_page = 100

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'camp':
            kwargs['queryset'] = Camp.objects.order_by('name')
        elif db_field.name == 'vision_center':
            kwargs['queryset'] = VisionCenter.objects.order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    


@admin.register(OrderRequestDetails)
class OrderRequestDetailsAdmin(ImportExportModelAdmin):
    list_display = ['id','order_request','product','created_by','modified_by', 'quantity','rrv','frame_type',
    'server_created_on','server_modified_on', 'status']
    fields = ['order_request', 'product','created_by','modified_by', 'quantity','rrv','frame_type','status']
    search_fields = ['id','product__name','status']
    list_filter = ['order_request','product']
    list_per_page = 100

    def get_order_request_order_status(self, obj):
        return obj.order_request.order_status
    get_order_request_order_status.short_description = 'Order_status'


@admin.register(OrderDeliveryDetails)
class OrderDeliveryDetailsAdmin(ImportExportModelAdmin):
    list_display = ['id','order_request','product', 'received_quantity','damaged_quantity','created_by','server_created_on', 'server_modified_on','status']
    fields = ['order_request','product', 'received_quantity','damaged_quantity','created_by','status']
    search_fields = ['id','product__name','status']
    date_hierarchy = 'server_created_on'
    list_per_page = 100

@admin.register(Camp)
class CampAdmin(ImportExportModelAdmin):
    list_display = ['id','ssmis_id','uuid', 'name','code', 'date','location','address','village','block','district',
    'expected_glass_prescription','expected_refer_surgeries','expected_camp_OPD','donor',
    'exclusive_camp', 'partner', 'vision_center','coordinator_name','coordinator_mobile_no', 'delay_reason','start_time','end_time',
    'created_by', 'modified_by', 'server_created_on','server_modified_on', 'status']
    fields = ['ssmis_id','uuid', 'name','code', 'date','location','address','village','block','district',
    'expected_glass_prescription','expected_refer_surgeries','expected_camp_OPD','donor',
    'exclusive_camp', 'partner','vision_center','coordinator_name','coordinator_mobile_no', 'delay_reason','start_time','end_time','created_by',
    'status']
    search_fields = ['id','name','donor__name','village']
    list_filter = ['district__name']
    date_hierarchy = 'server_created_on'
    list_per_page = 100

    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'district':
            kwargs['queryset'] = District.objects.order_by('name')
        elif db_field.name == 'vision_center':
            kwargs['queryset'] = VisionCenter.objects.order_by('name')
        elif db_field.name == 'partner':
            kwargs['queryset'] = Partner.objects.order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    


@admin.register(Patient)
class PatientAdmin(ImportExportModelAdmin):
    list_display = ['id','uuid', 'partner_id', 'vision_center_id', 'unique_id', 'patient_id', 'language', 'created_by', 'name', 'donor', 'camp', 'user', 'district', 'age', 'qr_code', 'gender',
    'contact_no_1', 'contact_no_2', 'permanent_address', 'aadhaar_pan_no', 'drivers_license_no', 'renewal_date',
    'type_of_job', 'time_since_driving', 'type_of_vehicle', 'type_of_route', 'monthly_income',
    'life_insurance_policy', 'vehicle_insurance_policy', 'health_insurance_policy', 
    'how_do_you_know_about_camp', 'educational_qualification', 'no_of_months_employed_in_a_year', 'residence_type', 'feedback',
    'approved_by','approved_on','remarks', 'data_freeze_status',
    'app_created_at', 'app_updated_at', 'sync_status', 'latitude', 'longitude','server_created_on','server_modified_on','status']
    fields = ['uuid', 'unique_id', 'patient_id', 'partner_id', 'vision_center_id', 'language','name', 'donor', 'camp', 'user', 'district', 'age', 'qr_code', 'gender',
    'contact_no_1', 'contact_no_2', 'permanent_address', 'aadhaar_pan_no', 'drivers_license_no', 'renewal_date',
    'type_of_job', 'time_since_driving', 'type_of_vehicle', 'type_of_route', 'monthly_income',
    'life_insurance_policy', 'vehicle_insurance_policy', 'health_insurance_policy', 'feedback','approved_by','approved_on','remarks', 'data_freeze_status',
    'how_do_you_know_about_camp', 'educational_qualification', 'no_of_months_employed_in_a_year','app_created_at', 'app_updated_at', 'residence_type', 'latitude', 'longitude','status']
    search_fields = ['id','name', 'uuid','patient_id','contact_no_1','unique_id', 'user__user__username']
    list_filter = ['district', 'gender','user','status']
    date_hierarchy = 'server_created_on'
    list_per_page = 100

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'type_of_job':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=1)
        if db_field.name == 'type_of_vehicle':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=2)
        if db_field.name == 'type_of_route':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=3)
        if db_field.name == 'monthly_income':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=5)
        if db_field.name == 'how_do_you_know_about_camp':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=6)
        if db_field.name == 'educational_qualification':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=7)
        if db_field.name == 'residence_type':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=8)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'district':
            kwargs['queryset'] = District.objects.order_by('name')
        elif db_field.name == 'camp':
            kwargs['queryset'] = Camp.objects.order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    


    
@admin.register(Screening)
class ScreeningAdmin(ImportExportModelAdmin):
    list_display = ['id','uuid', 'patient_uuid', 'partner_id', 'vision_center_id', 'code_description', 'blood_pressure', 'blood_sugar', 'weight', 'height',
    'family_details', 'total_family_members', 'salary_calculated', 'owner_holding_amount',
    'non_working_months', 'alter_employment', 'learn_alter_livelihood_skill',
    'family_support_financially', 'medical_checkup_past_1_year', 'diabetes', 'hypertension', 'diabetes',
    'alcohol', 'eye_examination', 'seeing_distant_objects', 'judging_distance_while_driving',
    'traffic_colors', 'seeing_while_night_driving', 'wear_glasses_ever', 'wearing_glasses_currently', 'nearby_hospital',
    'type_of_hospital', 'accident_while_driving_commercial_vehicle_before', 'accident_vehicle_in_last_twelve_months',
    'first_aid_kit', 'you_happy_with_your_profession', 'if_you_are_happy_specify_in_what_way',
    'waist_circumference', 'physical_activity', 'family_history_of_diabetes', 'which_training',
    'medication_hypertension', 'cough_for_more_than_two_weeks', 'night_sweats', 'fever_for_more_than_2_weeks',
    'unexplained_weight_loss_or_loss_of_appetite', 'have_you_attended_awarness_training', 'dosage_of_insulin',
    'duration_since_last_meal', 'when_was_it_diagnosed_number_of_years', 'when_was_it_diagnosed_years', 'data_freeze_status',
    'app_created_at', 'app_updated_at', 'sync_status', 'latitude', 'longitude', 'server_created_on','server_modified_on','status']
    fields = ['uuid', 'patient_uuid', 'partner_id', 'vision_center_id', 'code_description', 'blood_pressure', 'blood_sugar', 'weight', 'height',
    'family_details', 'total_family_members', 'salary_calculated', 'owner_holding_amount',
    'employed_in_year', 'non_working_months', 'alter_employment', 'learn_alter_livelihood_skill',
    'family_support_financially', 'medical_checkup_past_1_year', 'diabetes', 'hypertension', 'smoke',
    'alcohol', 'eye_examination', 'seeing_distant_objects', 'judging_distance_while_driving',
    'traffic_colors', 'seeing_while_night_driving', 'wear_glasses_ever', 'wearing_glasses_currently', 'nearby_hospital',
    'type_of_hospital', 'accident_while_driving_commercial_vehicle_before', 'accident_vehicle_in_last_twelve_months',
    'first_aid_kit', 'you_happy_with_your_profession', 'if_you_are_happy_specify_in_what_way',
    'waist_circumference', 'physical_activity', 'family_history_of_diabetes', 'which_training',
    'medication_hypertension', 'cough_for_more_than_two_weeks', 'night_sweats', 'fever_for_more_than_2_weeks',
    'unexplained_weight_loss_or_loss_of_appetite', 'have_you_attended_awarness_training', 'dosage_of_insulin',
    'duration_since_last_meal', 'when_was_it_diagnosed_number_of_years', 'when_was_it_diagnosed_years', 'latitude', 'longitude', 'data_freeze_status',
    'status']
    search_fields = ['id','uuid', 'patient_uuid']
    list_filter = [ 'patient_uuid']
    date_hierarchy = 'server_created_on'
    list_per_page = 100


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'code_description':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=9)
        if db_field.name == 'salary_calculated':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=10)
        if db_field.name == 'employed_in_year':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=11)
        if db_field.name == 'non_working_months':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=12)
        if db_field.name == 'type_of_hospital':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=13)
        if db_field.name == 'you_happy_with_your_profession':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=14)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(VisualAcuity)
class VisualAcuityAdmin(ImportExportModelAdmin):
    list_display = ['id','uuid', 'screening_uuid', 'partner_id', 'vision_center_id', 'aided_near_re', 'aided_near_le', 'aided_distance_re', 'aided_distance_le', 'pinhole_distance_re',
    'pinhole_distance_le', 'pinhole_near_re', 'pinhole_near_le', 'color_re',
    'color_le', 'unaided_distance_re', 'unaided_distance_le', 'unaided_near_re',
    'unaided_near_le', 'treatment_for_refraction', 'do_you_want_to_refer', 'refer_for', 'refer_to', 'data_freeze_status',
    'app_created_at', 'app_updated_at', 'sync_status', 'latitude', 'longitude', 'server_created_on', 'server_modified_on', 'status']
    fields = ['uuid', 'screening_uuid', 'partner_id', 'vision_center_id', 'aided_near_re', 'aided_near_le', 'aided_distance_re', 'aided_distance_le', 'pinhole_distance_re',
    'pinhole_distance_le', 'pinhole_near_re', 'pinhole_near_le', 'color_re',
    'color_le', 'unaided_distance_re', 'unaided_distance_le', 'unaided_near_re', 'data_freeze_status',
    'unaided_near_le', 'treatment_for_refraction', 'do_you_want_to_refer', 'refer_for', 'refer_to', 'latitude', 'longitude', 'status']
    search_fields = ['id','uuid', 'screening_uuid']
    date_hierarchy = 'server_created_on'
    list_per_page = 100


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'aided_near_re':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=76)
        if db_field.name == 'aided_near_le':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=76)
        if db_field.name == 'aided_distance_re':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=75)
        if db_field.name == 'aided_distance_le':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=75)
        if db_field.name == 'pinhole_distance_re':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=75)
        if db_field.name == 'pinhole_distance_le':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=75)
        if db_field.name == 'pinhole_near_re':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=76)
        if db_field.name == 'pinhole_near_le':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=75)
        if db_field.name == 'color_re':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=115)
        if db_field.name == 'color_le':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=115)
        if db_field.name == 'unaided_distance_re':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=75)
        if db_field.name == 'unaided_distance_le':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=75)
        if db_field.name == 'unaided_near_re':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=76)
        if db_field.name == 'unaided_near_le':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=76)
        if db_field.name == 'treatment_for_refraction':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=118)
        if db_field.name == 'refer_for':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=122)
        if db_field.name == 'refer_to':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=134)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(GlassPrescription)
class GlassPrescriptionAdmin(ImportExportModelAdmin):
    list_display = ['id','uuid', 'screening_uuid', 'partner_id', 'vision_center_id',
    'sph_distance_re', 'sph_distance_le', 'cyl_distance_re', 'cyl_distance_le', 'axis_distance_re',
    'axis_distance_le', 'va_distance_re', 'va_distance_le', 'sph_near_re', 'sph_near_le', 'cyl_near_re',
    'cyl_near_le', 'axis_near_re', 'axis_near_le', 'va_near_re', 'va_near_le', 'spectacle_type', 'data_freeze_status',
    'app_created_at', 'app_updated_at', 'sync_status', 'latitude', 'longitude', 'server_created_on', 'server_modified_on', 'status']
    fields = ['uuid', 'screening_uuid', 'partner_id', 'vision_center_id',
    'sph_distance_re', 'sph_distance_le', 'cyl_distance_re', 'cyl_distance_le', 'axis_distance_re',
    'axis_distance_le', 'va_distance_re', 'va_distance_le', 'sph_near_re', 'sph_near_le', 'cyl_near_re',
    'cyl_near_le', 'axis_near_re', 'axis_near_le', 'va_near_re', 'va_near_le', 'spectacle_type', 'latitude', 'longitude', 'data_freeze_status',
    'status']
    search_fields = ['id','uuid', 'screening_uuid']
    date_hierarchy = 'server_created_on'
    list_per_page = 100

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'va_distance_re':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=75)
        if db_field.name == 'va_distance_le':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=75)
        if db_field.name == 'va_near_re':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=76)
        if db_field.name == 'va_near_le':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=76)
        if db_field.name == 'spectacle_type':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=77)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(SpectacleType)
class SpectacleTypeAdmin(ImportExportModelAdmin):
    list_display = ['id','uuid', 'glass_prescription_uuid', 'partner_id', 'spectacle_name',
    'spectacle_type', 'has_the_glass_collected', 'glass_collecting_location', 'data_freeze_status',
    'vision_center', 'frame_code', 'frame_size', 'lens_type', 'type_of_coating','model_type','spectacle_status', 'order_id',
    'r2c_eligible','r2c_remark','app_created_at', 'app_updated_at', 'sync_status', 'server_created_on', 'server_modified_on', 'status']
    fields = ['uuid', 'glass_prescription_uuid',  'partner_id', 'spectacle_name',
    'spectacle_type', 'has_the_glass_collected', 'glass_collecting_location', 'data_freeze_status',
    'r2c_eligible','r2c_remark','vision_center', 'frame_code', 'frame_size', 'lens_type', 'type_of_coating', 'model_type','spectacle_status', 'order_id',
    'status']
    search_fields = ['id','uuid', 'glass_prescription_uuid']
    list_filter = ['spectacle_name']
    date_hierarchy = 'server_created_on'
    list_per_page = 100
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'spectacle_type':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=77)
        if db_field.name == 'frame_code':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=78)
        if db_field.name == 'frame_size':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=79)
        if db_field.name == 'lens_type':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=80)
        if db_field.name == 'type_of_coating':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=81)
        if db_field.name == 'model_type':
            kwargs["queryset"] = MasterLookup.objects.filter(
                status=2,parent__id=82)
        
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



@admin.register(TellicallingQuestionsAndAnswers)
class TellicallingQuestionsAndAnswersAdmin(ImportExportModelAdmin):
    list_display = ['id','patient','receive_your_spectacles','receiver_spectacles_reason','ahmd_spectacles_received','currently_using_spectacles','satisfied_with_spectacle',
    'any_problems_raised','satisfied_with_our_service','any_charges_while_collecting','rate_our_services','ad','disposition_name','call_disposition_group','comments','agent_comments','server_created_on' ,'server_modified_on','status']
    fields = ['patient','receive_your_spectacles','receiver_spectacles_reason','ahmd_spectacles_received','currently_using_spectacles','satisfied_with_spectacle',
    'any_problems_raised','satisfied_with_our_service','any_charges_while_collecting','rate_our_services','ad','disposition_name','call_disposition_group','comments','agent_comments','status']
    search_fields = ['id','patient__name']
    list_per_page = 100

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'disposition_name':
            kwargs["queryset"] = MasterLookup.objects.filter(status=2, parent__id=137)
        if db_field.name == 'comments':
            kwargs["queryset"] = MasterLookup.objects.filter(status=2, parent__id=138)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(CataractQuestions)
class CataractQuestionsAdmin(ImportExportModelAdmin):
    list_display = ['id','patient','referred_to_hospital_for_cataract','reason_for_cataract_no','visited_hospital','reason_for_visited_hospital_no',
    'hospital_recomand_cataract_surgery','reason_for_hospital_recomand_cataract_surgery_no','undergo_surgery','reason_for_undergo_surgery_no','place_cataract_surgery',
    'date_cataract_surgery','reason_for_notgone_cataract_surgery','treatment_free','how_it_paid','improvement_vision','helpful_for_driving','beneficiary_feed_back',
    'ad','disposition_name','call_disposition_group','comments','agent_comments', 'server_created_on', 'server_modified_on','status']
    fields = ['patient','referred_to_hospital_for_cataract','reason_for_cataract_no','visited_hospital','reason_for_visited_hospital_no',
    'hospital_recomand_cataract_surgery','reason_for_hospital_recomand_cataract_surgery_no','undergo_surgery','reason_for_undergo_surgery_no','place_cataract_surgery',
    'date_cataract_surgery','reason_for_notgone_cataract_surgery','treatment_free','how_it_paid','improvement_vision','helpful_for_driving','beneficiary_feed_back',
    'ad','disposition_name','call_disposition_group','comments','agent_comments','status']
    search_fields = ['id']
    list_per_page = 100

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'disposition_name':
            kwargs["queryset"] = MasterLookup.objects.filter(status=2, parent__id=137)
        if db_field.name == 'comments':
            kwargs["queryset"] = MasterLookup.objects.filter(status=2, parent__id=138)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(FamilyMember)
class FamilyMemberAdmin(ImportExportModelAdmin):
    list_display = ['id','uuid', 'screening_uuid', 'patient_uuid', 'name',
    'sex', 'age', 'relationship_to_respondent', 'educational_qualification', 'occupation', 'monthly_average_income',
    'app_created_at', 'app_updated_at', 'sync_status', 'server_created_on', 'server_modified_on', 'status']
    fields = ['uuid', 'screening_uuid', 'patient_uuid', 'name',
    'sex', 'age', 'relationship_to_respondent', 'educational_qualification', 'occupation', 'monthly_average_income',
    'status']
    search_fields = ['id','uuid', 'screening_uuid', 'patient_uuid', 'name']
    date_hierarchy = 'server_created_on'
    list_per_page = 100
    

@admin.register(QrCodeGeneration)
class QrCodeGenerationAdmin(ImportExportModelAdmin):
    list_display = ['id','user','unique_id', 'prefix', 'range_from', 'range_to',
    'server_created_on', 'server_modified_on', 'status']
    fields = ['user','unique_id', 'prefix', 'range_from', 'range_to',
    'status']
    search_fields = ['unique_id', 'user__user__username']
    list_per_page = 100
    # search_fields = ['id']



@admin.register(DataFreeze)
class DataFreezeAdmin(ImportExportModelAdmin):
    list_display = ['hospital_name','vision_center','camp','start_date','end_date',
    'no_of_patients_syn','no_of_patients_not_syn','not_syn_patients_ids',
    'no_of_screening_syn','no_of_screening_not_syn','not_syn_screening_ids',
    'no_of_family_member_syn','no_of_family_member_not_syn','not_syn_family_member_ids',
    'no_of_visual_acuity_syn','no_of_visual_acuity_not_syn','not_syn_visual_acuity_ids',
    'no_of_glass_prescription_syn','no_of_glass_prescription_not_syn','not_syn_glass_prescription_ids',
    'no_of_spectacle_type_syn','no_of_spectacle_type_not_syn','not_syn_spectacle_type_ids',
    'approved_by','approved_on','remarks','server_created_on', 'server_modified_on', 'status'
    ]
    fields = ['hospital_name','vision_center','camp','start_date','end_date',
    'no_of_patients_syn','no_of_patients_not_syn','not_syn_patients_ids',
    'no_of_screening_syn','no_of_screening_not_syn','not_syn_screening_ids',
    'no_of_family_member_syn','no_of_family_member_not_syn','not_syn_family_member_ids',
    'no_of_visual_acuity_syn','no_of_visual_acuity_not_syn','not_syn_visual_acuity_ids',
    'no_of_glass_prescription_syn','no_of_glass_prescription_not_syn','not_syn_glass_prescription_ids',
    'no_of_spectacle_type_syn','no_of_spectacle_type_not_syn','not_syn_spectacle_type_ids',
    'approved_by','approved_on','remarks',
    ]
    list_per_page = 15

@admin.register(ReceivedSMS)
class ReceivedSMSAdmin(ImportExportModelAdmin):
    list_display = ['id','mobile_no','languege', 'content', 'sms_status', 'no_of_times_attempt','error_info',
    'last_attempt_on','server_created_on', 'server_modified_on', 'status']
    fields = ['mobile_no','languege', 'content', 'sms_status', 'no_of_times_attempt',
    'last_attempt_on','error_info','status']
    list_filter = ['languege']
    search_fields = ['mobile_no','content']
    list_per_page = 100

    
    