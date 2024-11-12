from django.template.defaulttags import register
from master_data.models import *
from datetime import datetime ,timedelta,date
today = datetime.today()

@register.simple_tag
def get_latest_release_notes():
    release_notes = {'releasenotes':'','releasedate':'','version':''}
    version_notes = VersionUpdate.objects.filter(interface=2)
    if version_notes:   
        version_notes = version_notes.latest('release_date')
        release_notes = {"version":version_notes.version_name if version_notes.version_name else '' ,"releasenotes":version_notes.releasenotes if version_notes.releasenotes else '',"releasedate":str(version_notes.release_date) if version_notes.release_date else ''}
    return release_notes

@register.filter
def break_after_unique(value, unique_values):
    if value not in unique_values:
        unique_values.add(value)
        return True
    return False