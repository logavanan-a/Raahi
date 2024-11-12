from django.contrib import admin
from .models import *

# Register your models here.

# admin.site.unregister(MailTemplate)

@admin.register(MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ['id','template_name','description','subject','content','created_by','html_template','server_created_on','server_modified_on', 'status']
    fields = ['created_by','template_name','description','subject','content','html_template', 'status']
    # list_filter = ('created_by',)

    # SS

# admin.site.unregister(MailData)

@admin.register(MailData)
class MailDataAdmin(admin.ModelAdmin):
    list_display = ['id','template_name','subject','content', 'syn_content', 'cron_content', 'error_content', 'mail_status', 'created_by', 'mail_to',
                     'client_mail_to', 'syn_mail_to', 'cron_mail_to', 'server_created_on','server_modified_on','status']
    fields = ['template_name','subject','content', 'syn_content', 'error_content', 'mail_status','created_by', 'status']

#     def is_active(self, obj):
#         return obj.active == 2 
#     is_active.boolean = True