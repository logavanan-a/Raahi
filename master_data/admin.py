from django.contrib import admin
from . models import *
from import_export import resources
# from import_export.admin import ImportExportModelAdmin, ImportExportMixin
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from import_export import resources, fields
from import_export.fields import Field
from sims.admin import ImportExportFormat

# Register your models here.
# admin.site.site_url = '/orders/'

@admin.register(MasterLookup)
class MasterLookupAdmin(ImportExportModelAdmin):
    list_display = ['id','name', 'parent', 'order','server_created_on','server_modified_on', 'status']
    fields = ['name', 'parent', 'order', 'status']
    search_fields = ['id','name']
    # list_per_page = 15
    list_filter = ['parent__name']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = MasterLookup.objects.filter(
                parent__name=None)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
@admin.register(Zone)
class ZoneAdmin(ImportExportModelAdmin):
    list_display = ['id','ssmis_id','name', 'code', 'server_created_on','server_modified_on','status']
    fields = ['ssmis_id','name', 'code', 'status']
    search_fields = ['id','name']
    list_per_page = 15

@admin.register(State)
class StateAdmin(ImportExportModelAdmin):
    list_display = ['id','ssmis_id','name', 'code', 'zone', 'server_created_on','server_modified_on','status']
    fields = ['ssmis_id','name', 'code', 'zone', 'status']
    search_fields = ['id','name']
    list_filter = ['zone' ]
    list_per_page = 15

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'zone':
            kwargs['queryset'] = Zone.objects.order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(District)
class DistrictAdmin(ImportExportModelAdmin):
    list_display = ['id','ssmis_id','name','code','state','server_created_on','server_modified_on','status']
    fields = ['ssmis_id','name','state','code','status']
    search_fields = ['id','name','code','state__name']
    list_filter = ['state' ]
    list_per_page = 100

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'state':
            kwargs['queryset'] = State.objects.order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Partner)
class PartnerAdmin(ImportExportModelAdmin):
    list_display = ['id','ssmis_id','name', 'code', 'address', 'contact_no', 'email_id', 'otp_verification', 'state','server_created_on','server_modified_on', 'latitude','longitude', 'status']
    fields = ['ssmis_id','name','address', 'code', 'contact_no', 'email_id', 'state', 'otp_verification', 'latitude','longitude', 'status']
    search_fields = ['id','name', 'code','state__name']
    list_filter = ['state', 'status']
    date_hierarchy = 'server_created_on'
    list_per_page = 15

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'state':
            kwargs['queryset'] = State.objects.order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Role)
class RoleAdmin(ImportExportModelAdmin):
    list_display = ['id','name','role_type','role_slug','status']
    fields = ['name','role_type','role_slug','status']
    search_fields = ['id','name']
    list_per_page = 15

@admin.register(UserProfile)
class UserProfileAdmin(ImportExportModelAdmin):
    list_display = ['id','user', 'role','server_created_on','server_modified_on', 'status']
    fields = ['user', 'role', 'status']
    search_fields = ['id','user__username','role__name']
    list_filter = ['role']
    list_per_page = 15

@admin.register(VisionCenter)
class VisionCenterAdmin(ImportExportModelAdmin):
    list_display = ['id','ssmis_id','name','address', 'partner', 'donor','contact_no', 'vc_type', 'latitude','longitude', 'server_created_on','server_modified_on','status']
    fields = ['ssmis_id','name','address', 'partner', 'donor','contact_no', 'vc_type', 'latitude','longitude', 'status']
    search_fields = ['id','name','partner__name']
    list_filter = ['partner']
    list_per_page = 15

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'partner':
            kwargs['queryset'] = Partner.objects.order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
@admin.register(TeleCalling)
class TeleCallingAdmin(ImportExportModelAdmin):
    list_display = ['id','feedback','feedback_by', 'feedback_date','server_created_on','server_modified_on','status']
    fields = ['feedback','feedback_by', 'feedback_date','status']
    search_fields = ['id','feedback', 'feedback_by']
    list_per_page = 15

@admin.register(Donor)
class DonorAdmin(ImportExportModelAdmin):
    list_display = ['id','ssmis_id','name','mobile_number', 'email_id', 'code','server_created_on','server_modified_on','status']
    fields = ['ssmis_id','name','mobile_number', 'email_id', 'code', 'status']
    search_fields = ['id','name']
    list_per_page = 15

    

@admin.register(Vendor)
class VendorAdmin(ImportExportModelAdmin):
    list_display = ['id','ssmis_id','name','address', 'contact_no', 'email_id', 'alternative_email_id_1', 'alternative_email_id_2', 'alternative_email_id_3', 'alternative_email_id_4', 'district','server_created_on','server_modified_on','status']
    fields = ['ssmis_id','name','address', 'contact_no', 'email_id', 'alternative_email_id_1', 'alternative_email_id_2', 'alternative_email_id_3', 'alternative_email_id_4', 'district','status']
    search_fields = ['id','name','district__name']
    list_per_page = 15
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'district':
            kwargs['queryset'] = District.objects.order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(PartnerVendorLinkage)
class PartnerVendorLinkageAdmin(ImportExportModelAdmin):
    list_display = ['id','partner','vendor', 'deactivated_date','server_created_on','server_modified_on', 'status']
    fields = ['partner','vendor', 'deactivated_date','status']
    search_fields = ['id','partner__name','vendor__name']
    list_per_page = 15

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'partner':
            kwargs['queryset'] = Partner.objects.order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(UserPartnerLinkage)
class UserPartnerLinkageAdmin(ImportExportModelAdmin):
    list_display = ['id','partner','user','server_created_on','server_modified_on', 'status']
    fields = ['partner','user','status']
    list_filter = ['partner']
    search_fields = ['id','partner__name','user__username']
    list_per_page = 15

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'partner':
            kwargs['queryset'] = Partner.objects.order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    

@admin.register(UserVendorLinkage)
class UserVendorLinkageAdmin(ImportExportModelAdmin):
    list_display = ['id','vendor','user','server_created_on','server_modified_on', 'status']
    fields = ['vendor','user','status']
    list_filter = ['vendor']
    search_fields = ['id','vendor__name','user__username']
    list_per_page = 15

@admin.register(UserVisionCenterLinkage)
class UserVisionCenterLinkageAdmin(ImportExportModelAdmin):
    list_display = ['id','vision_center','user','server_created_on','server_modified_on', 'status']
    fields = ['vision_center','user','status']
    list_filter = ['vision_center']
    search_fields = ['id','vision_center__name','user__username']
    list_per_page = 15

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'vision_center':
            kwargs['queryset'] = VisionCenter.objects.order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(UserDonorLinkage)
class UserDonorLinkageAdmin(ImportExportModelAdmin):
    list_display = ['id','donor','user','server_created_on','server_modified_on', 'status']
    fields = ['donor','user','status']
    list_filter = ['donor']
    search_fields = ['id','donor__name','user__username']
    list_per_page = 15

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'donor':
            kwargs['queryset'] = Donor.objects.order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
@admin.register(DonorPartnerLinkage)
class DonorPartnerLinkageAdmin(ImportExportModelAdmin):
    list_display = ['id','donor','partner','district','server_created_on','server_modified_on', 'status']
    fields = ['donor','partner','district', 'status']
    list_filter = ['donor']
    search_fields = ['id','donor__name','partner__name','district__name']
    list_per_page = 15

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'district':
            kwargs['queryset'] = District.objects.order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ApplicationUserStateLinkage)
class ApplicationUserStateLinkageAdmin(ImportExportModelAdmin):
    list_display = ['id', 'user', 'get_state_names','server_created_on','server_modified_on', 'status']
    fields = ['user', 'state', 'status']
    list_filter = ['state']
    search_fields = ['id']
    list_per_page = 15


    def get_state_names(self, obj):
        return ", ".join([state.name for state in obj.state.all()])

    get_state_names.short_description = 'state'

@admin.register(Config)
class ConfigAdmin(ImportExportModelAdmin, ImportExportFormat):
    list_display = ['id','code', 'value', 'status']
    fields = ['code', 'value', 'status']
    search_fields = ['code']


@admin.register(Language)
class LanguageAdmin(ImportExportModelAdmin, ImportExportFormat):
    list_display = ['id','name', 'code', 'status']
    fields = ['name', 'code', 'status']
    search_fields = ['name']

@admin.register(OtpVerificationDetails)
class OtpVerificationDetailsAdmin(ImportExportModelAdmin, ImportExportFormat):
    list_display = ['id', 'user', 'language', 'mobile_no', 'otp_value', 'otp_status', 'otp_created_at', 'otp_verified_at', 'no_of_verified', 'server_created_on','server_modified_on', 'status']
    fields = ['user', 'language', 'mobile_no', 'otp_value', 'otp_status', 'otp_created_at', 'otp_verified_at', 'no_of_verified', 'status']
    search_fields = ['user__user__username','mobile_no']

@admin.register(DailyRecordsCalculation)
class DailyRecordsCalculationAdmin(ImportExportModelAdmin, ImportExportFormat):
    list_display = ['id', 'date', 'record', 'uuid', 'error', 'saved_records', 'not_saved_records', 'total_records', 'server_created_on','server_modified_on', 'status']
    fields = ['record','error', 'uuid', 'saved_records', 'not_saved_records', 'total_records', 'status']
    list_filter = ['record']
    date_hierarchy = 'server_created_on'
    search_fields = ['uuid','error','record']


@admin.register(VersionUpdate)
class VersionUpdateAdmin(ImportExportModelAdmin, ImportExportFormat):
    list_display = ['id','version_code', 'version_name', 'force_update', 'interface', 'releasenotes', 'release_date', 'status']
    fields = ['version_code', 'version_name', 'force_update', 'interface', 'releasenotes', 'release_date', 'status']
    search_fields = ['version_code']


@admin.register(CronJobSummaryLog)
class CronJobSummaryLog(ImportExportModelAdmin, ImportExportFormat):
    list_display = ['id','log_key', 'last_successful_update',
                    'most_recent_update','most_recent_update_status', 'most_recent_update_time_taken_millis', 'error', 'server_created_on', 'server_modified_on', 'status']
    fields = ['log_key', 'last_successful_update', 'most_recent_update',
              'most_recent_update_time_taken_millis', 'error', 'most_recent_update_status', 'status']
    search_fields = ['id','log_key','last_successful_update', 'most_recent_update']
