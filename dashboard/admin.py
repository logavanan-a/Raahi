from django.contrib import admin
from .models import ChartMeta, DashboardWidgetSummaryLog
from import_export.admin import ImportExportModelAdmin
from master_data.admin import ImportExportFormat
from import_export import fields


@admin.register(ChartMeta)
class ChartMetaAdmin(ImportExportModelAdmin, ImportExportFormat):
    list_display = ['id','page_slug','chart_title', 'chart_type',
                    'chart_note', 'div_class', 'display_order', 'server_created_on', 'server_modified_on', 'status']
    fields = ['chart_type', 'chart_slug', 'page_slug',
              'chart_title', 'vertical_axis_title', 'horizontal_axis_title',
              'chart_note', 'chart_tooltip', 'chart_height',
              'click_handler', 'chart_options', 'div_class',
              'chart_query', 'filter_info', 'display_order', 'status']
    list_filter = ['chart_type', 'page_slug']
    search_fields = ['id','chart_type', 'chart_title']


@admin.register(DashboardWidgetSummaryLog)
class DashboardWidgetSummaryLogAdmin(ImportExportModelAdmin, ImportExportFormat):
    list_display = ['id','log_key', 'last_successful_update',
                    'most_recent_update', 'most_recent_update_status', 'most_recent_update_time_taken_millis', 'error', 'server_created_on', 'server_modified_on', 'status']
    fields = ['log_key', 'last_successful_update', 'most_recent_update', 'most_recent_update_status',
              'most_recent_update_time_taken_millis', 'error', 'status']
    search_fields = ['id','last_successful_update', 'most_recent_update']
