from django.contrib import admin

# Register your models here.

from import_export.admin import ImportExportModelAdmin
from import_export import fields
from reports.models import *
from sims.admin import ImportExportFormat


@admin.register(ReportMeta)
class ReportMetaAdmin(ImportExportModelAdmin, ImportExportFormat):
    list_display = ['id','report_title', 'page_slug', 'report_slug',
                    'display_order','status']
    fields = ['page_slug', 'report_slug',  'report_title', 'report_header',
              'report_query', 'display_order', 'filter_info', 'sort_info', 'custom_export_header', 'status']
    list_filter = ['report_title', 'report_slug']
    search_fields = ['id','report_title', 'report_slug']


@admin.register(MprIndicator)
class MprIndicatorAdmin(ImportExportModelAdmin):
    list_display = ['id','ssmis_id','category', 'sub_category', 'code', 'type','server_created_on', 'server_modified_on', 'status']
    fields = ['ssmis_id','category', 'sub_category', 'code', 'type', 'status']
    list_per_page = 15
    search_fields = ['id']

    def has_add_permission(self, request):
        return False

    # This will help you to disable delete functionaliyt
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(TruckerMprData)
class TruckerMprDataAdmin(ImportExportModelAdmin):
    list_display = ['id','mpr_indicator', 'partner_id', 'partner_name', 'vision_center_id',
    'vision_center_name', 'donor_id', 'donor_name', 'state_id', 'district_id',
    'indicator_month', 'indicator_year', 'priority', 'male_target',
    'female_target', 'total_target', 'current_month_achievement_male',
    'current_month_achievement_female', 'current_month_achievement_total', 'till_date_achievement',
    'one_column_value', 'two_column_value', 'three_column_value', 'four_column_value',
    'server_created_on', 'server_modified_on', 'status']
    fields = ['mpr_indicator', 'partner_id', 'partner_name', 'vision_center_id',
    'vision_center_name', 'donor_id', 'donor_name', 'state_id', 'district_id',
    'indicator_month', 'indicator_year', 'priority', 'male_target',
    'female_target', 'total_target', 'current_month_achievement_male',
    'current_month_achievement_female', 'current_month_achievement_total', 'till_date_achievement', 
    'one_column_value', 'two_column_value', 'three_column_value', 'four_column_value',
    'status']
    list_per_page = 15
    search_fields = ['id']


    # def has_add_permission(self, request):
    #     return False

    # # This will help you to disable delete functionaliyt
    # def has_delete_permission(self, request, obj=None):
        # return False


@admin.register(ReportExport)
class ReportExportAdmin(ImportExportModelAdmin):
    list_display = ['id','user', 'report', 'downloaded_at', 'export_status','server_created_on', 'server_modified_on', 'status']
    fields = ['user', 'report',  'export_status', 'status']
    list_per_page = 15
    search_fields = ['id']

@admin.register(ReportTracket)
class ReportTracketAdmin(ImportExportModelAdmin):
    list_display = ['id','partner', 'year', 'code', 'tracket_col_1', 'tracket_col_2', 'server_created_on', 'server_modified_on', 'status']
    fields = ['partner', 'year',  'code', 'tracket_col_1', 'tracket_col_2', 'status']
    list_per_page = 15
    search_fields = ['id']

@admin.register(MprStatusUpdate)
class MprStatusUpdateAdmin(ImportExportModelAdmin):
    list_display = ['id','month','year','partner','approved_by','forward_by','forward_to_super_admin_by','forward_by', 'ssims_user',
    'mpr_report_code','mpr_status','remark','national_remark','partner_date','zonal_coordinator_date','ppa_date','national_coordinator_date',
    'super_admin_date', 'forward_nc_command', 'server_created_on','server_modified_on', 'created_by', 'modified_by', 'status']
    list_per_page = 15
    list_filter= ['mpr_report_code', 'mpr_status']
    search_fields = ['id', 'created_by__username']


    