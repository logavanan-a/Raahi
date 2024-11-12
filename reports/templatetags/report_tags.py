from django import template
from master_data.models import *
from reports.models import *
register = template.Library()


@register.filter
def get_item(dictionary, key):
    value = dictionary.get(key) if dictionary.get(key) is not None else ''
    return value

# return the item at index i from an indexable type like list
# if item not indexable then return ""
@register.simple_tag
def get_target_mpr_data(target_mpr_value,code,target_col):
    for tar in target_mpr_value:
        if int(tar['code']) == int(code) and int(target_col)==1:
            value = tar['target_1']
        if int(tar['code']) == int(code) and int(target_col)==2:  
            value = tar['target_2'] 
    return value


@register.simple_tag
def get_mpr_data(mpr_value,index,ind_key,val_key):
    if mpr_value[index] != None:
        value = mpr_value[index][ind_key][val_key]
    else:
        value = 0
    return value

    
@register.filter
def index(indexable, i):
    # TODO: check if i is > lenght of indexable and return "" or error
    if indexable:
        return indexable[i]
    else:
        return ""

# function to return count of keys in the dictionary


@register.filter
def dict_len(dict):
    if dict:
        return len(dict)
    else:
        return 0
    
@register.filter       
def next(value, arg):
    try:
        return value[int(arg)-1]['zone_id']
    except:
        return None
    
@register.filter       
def get_partner_by_zone(value, zone_id):
    try:
        for item in value:
            if item.get('zone_id') == zone_id:
                state=State.objects.filter(zone_id=item.get('zone_id'))
                zone_value=ApplicationUserStateLinkage.objects.filter(state__in=state)
                partner_user = Partner.objects.filter(state_id__in=zone_value.values_list('state', flat=True))
                user_partner_details = UserPartnerLinkage.objects.filter(partner_id__in=partner_user.values_list('id', flat=True))
                mpr_count = MprStatusUpdate.objects.filter(created_by_id__in=user_partner_details.values_list('user_id',flat=True), month=item.get('month'), year=item.get('year'))
                # print(mpr_count.count(), mpr_count.filter(zonal_coordinator_date__isnull=False).exclude(mpr_status=3).count(), 'mlll')
                if mpr_count.count() ==  mpr_count.filter(zonal_coordinator_date__isnull=False).exclude(mpr_status=3).count():
                    mprs = True
                else:
                    mprs = False
                return mprs
    except:
        return None
    return None

@register.filter       
def get_zone_by_ppa(value, zone_id):
    try:
        for item in value:
            if item.get('zone_id') == zone_id:
                state=State.objects.filter(zone_id=item.get('zone_id'))
                zone_value=ApplicationUserStateLinkage.objects.filter(state__in=state)
                partner_user = Partner.objects.filter(state_id__in=zone_value.values_list('state', flat=True))
                user_partner_details = UserPartnerLinkage.objects.filter(partner_id__in=partner_user.values_list('id', flat=True))
                mpr_count = MprStatusUpdate.objects.filter(created_by_id__in=user_partner_details.values_list('user_id',flat=True), month=item.get('month'), year=item.get('year'))
                # print(mpr_count.count(), mpr_count.filter(zonal_coordinator_date__isnull=False).exclude(mpr_status=3).count(), 'mlll')
                if mpr_count.count() ==  mpr_count.filter(ppa_date__isnull=False).count():
                    mprs = True
                else:
                    mprs = False
                return mprs
    except:
        return None
    return None
