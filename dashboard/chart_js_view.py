from __future__ import unicode_literals
from schedule import every, repeat
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import HttpResponseRedirect, HttpResponse
from django.conf import settings
import requests
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import ChartMeta, DashboardWidgetSummaryLog
from django.contrib.auth.models import User, auth
from django.db.models import Subquery
from master_data.models import *
from master_data . views import *
from django.http import JsonResponse
from django.db import connection
from django.utils.encoding import smart_str
from datetime import datetime
import csv
from django.core.management import call_command
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)
# ****************************************************************************
# Login Function
# ****************************************************************************

def filter_location_data(request):
    zone_id = request.POST.get('zone', '')
    state_id = request.POST.get('state', '')
    donor_id = request.POST.get('donor','')
    partner_id = request.POST.get('partner','')
    # zone_list,state_list,partner_list,donor_list=[],[],[],[]
    partner_filter,zone_filter,state_filter,district_filter,donor_filter = None,None,None,None,None
    selected_items = []
    user_filter_data = []
    user_role = request.session.get('role_id')
    # 8 - ppa , 9 - zonal-coordinator , 10 - zonal incharge
    if request.session.get('role_id')in (8,9,10):
        get_state_partner_linkage = ApplicationUserStateLinkage.objects.filter(status=2,user_id=request.user.id).values_list('state',flat=True)
        zone_list = State.objects.filter(status=2,id__in=get_state_partner_linkage).values_list('zone',flat=True).distinct()
        zone_filter = Zone.objects.filter(status=2,id__in=zone_list).order_by('name')
        state_filter = State.objects.filter(status=2,id__in=get_state_partner_linkage,zone__in=zone_list).order_by('name')
        partner_list = Partner.objects.filter(status=2,state_id__in=get_state_partner_linkage).values_list('id',flat=True)
        partner_filter = Partner.objects.filter(status=2,id__in=partner_list).order_by('name')
        donor_list = DonorPartnerLinkage.objects.filter(status=2,partner_id__in=partner_list).values_list('donor_id',flat=True)
        donor_filter = Donor.objects.filter(status=2,id__in=donor_list).order_by('name')
        if len(zone_list) == 1:
            zone_id = str(zone_list[0])
        if state_id != '' and donor_id == '':
            partner_filter = Partner.objects.filter(status=2,state_id=int(state_id)).order_by('name')
            donor_list = DonorPartnerLinkage.objects.filter(status=2,partner_id__in=partner_list).values_list('donor_id',flat=True)
            donor_filter = Donor.objects.filter(status=2,id__in=donor_list).order_by('name')
        if state_id != '' and donor_id != '':
            partner_list = DonorPartnerLinkage.objects.filter(status=2,donor_id=int(donor_id)).values_list('partner_id',flat=True)
            partner_filter = Partner.objects.filter(status=2,state_id=int(state_id),id__in=partner_list).order_by('name')
            donor_list = DonorPartnerLinkage.objects.filter(status=2,partner_id__in=partner_list).values_list('donor_id',flat=True)
            donor_filter = Donor.objects.filter(status=2,id__in=donor_list).order_by('name')
        if state_id == '':
            state_id = str(list(get_state_partner_linkage))[1:-1]
    # 4 partner
    elif request.session.get('role_id') == 4:
        partner_users = UserPartnerLinkage.objects.get(user_id=request.user.id)
        partner_id = str(partner_users.partner_id)
        partner_filter=Partner.objects.filter(status=2,id=partner_users.partner_id).order_by('name')
        part_state_list = Partner.objects.filter(status=2,id=partner_users.partner_id).values_list('state_id',flat=True)
        state_filter =State.objects.filter(status=2,id__in=part_state_list).order_by('name')
        part_zone_list = State.objects.filter(status=2,id__in=part_state_list).values_list('zone',flat=True)
        zone_filter = Zone.objects.filter(status=2,id__in=part_zone_list).order_by('name')
        if len(part_state_list) == 1 and len(part_zone_list) == 1:
            state_id = str(part_state_list[0])
            zone_id = str(part_zone_list[0])
        part_donor_list = DonorPartnerLinkage.objects.filter(status=2,partner_id=partner_users.partner_id).values_list('donor_id',flat=True)
        donor_filter = Donor.objects.filter(status=2,id__in=part_donor_list).order_by('name')
        if len(part_donor_list) == 1:
            donor_id = str(part_donor_list[0])
    elif request.session.get('role_id') == 11:
        donor_list = UserDonorLinkage.objects.filter(status=2,user_id=request.user.id).values_list('donor_id',flat=True)
        donor_part_dist = DonorPartnerLinkage.objects.filter(status=2,donor_id__in=donor_list).values_list('partner_id','district_id')
        donor_filter = Donor.objects.filter(status=2,id__in=donor_list).order_by('name') 
        part_list = [part[0] for part in donor_part_dist]
        dist_list = [dist[1] for dist in donor_part_dist]
        state_list = District.objects.filter(status=2,id__in=dist_list).values_list('state_id',flat=True).distinct()
        state_filter = State.objects.filter(status=2,id__in=state_list).order_by('name')
        zone_list = State.objects.filter(status=2,id__in=state_list).values_list('zone_id',flat=True)
        zone_filter = Zone.objects.filter(status=2,id__in=zone_list).order_by('name')
        partner_filter = Partner.objects.filter(status=2,state_id__in=state_list).order_by('name')    
        if len(donor_list) == 1:
            donor_id = donor_list[0]
        if len(zone_list) == 1:
            zone_id = zone_list[0]
        if len(state_list) == 1:
            state_id = state_list[0]
    else:
        zone_filter = Zone.objects.filter(status=2).order_by('name')
        partner_filter=Partner.objects.filter().order_by('name')
        donor_filter=Donor.objects.filter(status=2).order_by('name')
        if zone_id != '' and state_id == '' and donor_id =='' and partner_id == '':
            state_list = State.objects.filter(status=2,zone_id=int(zone_id)).values_list('id',flat=True)
            state_filter = State.objects.filter(status=2,id__in=state_list).order_by('name')
            district_list = District.objects.filter(status=2,state_id__in=state_list).values_list('id',flat=True)
            donor_list = DonorPartnerLinkage.objects.filter(status=2,district_id__in=district_list).values_list('donor_id',flat=True)
            donor_filter = Donor.objects.filter(status=2,id__in=donor_list).order_by('name')
            partner_filter = Partner.objects.filter(status=2,state_id__in=state_list).order_by('name')
        elif zone_id != '' and state_id != '' and donor_id == '' and partner_id == '':
            state_list = State.objects.filter(status=2,zone_id=int(zone_id)).values_list('id',flat=True)
            state_filter = State.objects.filter(status=2,id__in=state_list).order_by('name')
            district_list = District.objects.filter(status=2,state_id=state_id).values_list('id',flat=True)
            donor_list = DonorPartnerLinkage.objects.filter(status=2,district_id__in=district_list).values_list('donor_id',flat=True)
            donor_filter = Donor.objects.filter(status=2,id__in=donor_list).order_by('name')
            partner_filter = Partner.objects.filter(status=2,state_id=int(state_id)).order_by('name')
        elif (zone_id != '' and state_id == '' and donor_id !='' and partner_id == '') or (zone_id != '' and state_id != '' and donor_id !='' and partner_id == '') or (zone_id != '' and state_id != '' and donor_id !='' and partner_id != ''):
            state_list = State.objects.filter(status=2,zone_id=int(zone_id)).values_list('id',flat=True)
            state_filter = State.objects.filter(status=2,id__in=state_list).order_by('name')
            district_list = District.objects.filter(status=2,state_id__in=state_list).values_list('id',flat=True)
            donor_part_list = DonorPartnerLinkage.objects.filter(status=2,district_id__in=district_list,donor_id=donor_id).values_list('donor_id','partner_id')
            donor_list = [don[0] for don in donor_part_list]
            part_list = [part[1] for part in donor_part_list]
            donor_filter = Donor.objects.filter(status=2,id__in=donor_list).order_by('name')
            partner_filter = Partner.objects.filter(status=2,state_id__in=state_list,id__in=part_list).order_by('name')
        elif zone_id == '' and state_id == '' and donor_id !='' and partner_id == '':
            donor_part_list = DonorPartnerLinkage.objects.filter(status=2,donor_id=donor_id).values_list('donor_id','partner_id')
            donor_list = [don[0] for don in donor_part_list]
            part_list = [part[1] for part in donor_part_list]
            partner_filter = Partner.objects.filter(status=2,id__in=part_list).order_by('name')
    selected_items.insert(0, zone_id)
    user_filter_data.insert(0, zone_id)
    selected_items.insert(1, state_id)
    user_filter_data.insert(1, state_id)
    if state_id != '':
        selected_items[1] = "["+str(state_id)+"]"
    selected_items.insert(2,donor_id)
    user_filter_data.insert(2,donor_id) 
    selected_items.insert(3, partner_id) 
    user_filter_data.insert(3, partner_id)
    if partner_id != '':
        selected_items[3] = "["+str(partner_id)+"]" 
    from_date = request.POST.get('from_date', '') 
    to_date = request.POST.get('to_date', '')
    selected_items.insert(4,from_date)
    user_filter_data.insert(4,from_date)
    selected_items.insert(5,to_date)  
    user_filter_data.insert(5,to_date)
    return zone_filter,partner_filter,state_filter,district_filter,donor_filter,selected_items,user_filter_data,user_role

# ****************************************************************************
# Function to load user details to session
# ****************************************************************************


def load_user_details_to_sessions(request):
    # Getting the user role config if not it will raise exception
    try:
        user_role_location_level_config = UserRoleLocationLevelConfig.objects.get(
            user=request.user, status=2)
    except UserRoleLocationLevelConfig.DoesNotExist:
        # user_role_location_level_config = None
        configure_error = 'Username not configured . Please contact administrator.'
        return configure_error

    # User group for checking group permission with menu permission
    user_group = user_role_location_level_config.group
    location_hierarchy_type_id = user_role_location_level_config.location_hierarchy_type.id

    # Return user location relation id and object id list , if user mapped with multiple location.
    user_object_id = UserLocationRelation.objects.filter(
        UserRoleLocationLevelConfig=user_role_location_level_config, content_type__id=location_hierarchy_type_id, status=2).values_list('object_id', flat=True)

    menus = Menu.objects.filter(status=2)
    menu_to_display = []

    for menu in menus:
        if user_group.permissions.filter(id=menu.model_permission.id).exists():
            menu_to_display.append(
                (menu.name, menu.slug, menu.icon, menu.feature_link))

    request.session['menus'] = menu_to_display
    # request.session['user_group_id'] = user_group.id
    request.session['location_hierarchy_type_id'] = location_hierarchy_type_id
    request.session['user_object_id'] = list(
        user_object_id)

# #****************************************************************************
# # update stackabar chart data to replace dummy data with actual values
# #****************************************************************************


def set_dynamic_column_stack_chart_data(sql, headers):
    cursor = None
    try:
        chart_row_id_value = []
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        newdata = []
        newdata.append(headers)
        for row in rows:
            row_data = list(row)
            chart_id_val = row_data.pop(0)
            chart_row_id_value.append(chart_id_val)
            newdata.append(row_data)
            #new_row_data = []
    finally:
        if cursor:
            cursor.close()
    return newdata, chart_row_id_value


# #****************************************************************************
# # update pie chart data to replace dummy data with actual values
# #****************************************************************************


def set_pie_chart_data(sql, labels=None):
    cursor = connection.cursor()
    cursor.execute(sql)
    descr = cursor.description
    rows = cursor.fetchall()
    data = []
    if labels:
        data = [dict(zip([column for column in labels], row))for row in rows]
        return data[0].items()
    else:
        return rows


def set_card_chart_data(sql, labels=None):
    cursor = connection.cursor()
    cursor.execute(sql)
    descr = cursor.description
    rows = cursor.fetchall()
    data = []
    if labels:
        data =[(labels[idx],row[0]) for idx,row in enumerate(rows)]
        return data
    else:
        return rows

# #****************************************************************************
# # update column chart data  and labels to replace dummy data with actual values
# # labels only for dynamic bars - last 6 months kind of charts
# #****************************************************************************


def set_column_chart_data(sql, labels):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        descr = cursor.description
        counter = 0
        data = []
        if rows:
            # data = [dict(zip([column for column in labels], row))for row in rows]
            # row = rows[0]
            for i in range(0,len(rows)):
                value = (labels[i],rows[i][1])
                data.append(value)

            return data
        else:
            data = []
            row = None
    finally:
        if cursor:
            cursor.close()
    return data[0].items()

def normal_query(sqlquery,labels):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(sqlquery)
        rows = cursor.fetchall()
        total_data = ""
        for idx,header in enumerate(labels):
            total_data+=' '+header +' : '+str(rows[0][idx]) + ';'
        total_data = '[' + total_data[:-1] + ']'
    finally:
        if cursor:
            cursor.close()
    return total_data

def set_bar_chart_dynamic_lable(sql):
    cursor = None
    try:
        # query output strucutre - "location name", location_id, data values
        # location_id not required in chart_data so remove and add it to dict 
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        #descr = cursor.description
        data = []
        chart_row_id_value = []
        for idx,i in enumerate(rows):
            i = list(i)
            #i[1] = int(i[1])
            loc_id = i.pop(0)
            chart_row_id_value.append(int(loc_id))
            data.append(i)
    finally:
        if cursor:
            cursor.close()
    return data, chart_row_id_value

# {'sql_query': 'select mc.name as colony_name, coalesce(approved_count,0) as approved_count from masterdata_colony as mc left outer join dash_board_benefits_enrollment_view dbev on dbev.colony_id = mc.id order by trim(lower(mc.name))', 'col_headers': ['Colony Name', 'Board Benefits']}

def normal_return_rows(sql):
    cursor = None
    try:
        # query output strucutre - "location name", location_id, data values
        # location_id not required in chart_data so remove and add it to dict 
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        #descr = cursor.description
        
    finally:
        if cursor:
            cursor.close()
    return rows

def filter_conditions(request, sql_query, filter_info,selected_items):
    user_id = request.user.id
    filter_cond = filter_info.get('filter_cond','')
    zone_cond,state_cond,dist_cond,partner_cond,donor_cond,from_month_cond,to_month_cond = "","","","","","",""
    for key in filter_info['filter_cond'].keys():
        if key == 'zone':
            if selected_items[0] != '':
                zone_cond = filter_info['filter_cond'][key].replace('@@filter_value',f"{selected_items[0]}")
        elif key == 'state':
            if selected_items[1] != '':
                state_cond = filter_info['filter_cond'][key].replace('@@filter_value',f"{selected_items[1][1:-1]}")
        elif key == 'donor':
            if selected_items[2] != '':
                donor_cond = filter_info['filter_cond'][key].replace('(@@filter_value)',f"({selected_items[2]})")
        elif key == 'partner':
            if selected_items[3] != '':
                partner_cond = filter_info['filter_cond'][key].replace('@@filter_value',f"{selected_items[3][1:-1]}")
        elif key == 'from_date':
            if selected_items[4] != '':
                from_month_cond = filter_info['filter_cond'][key].replace('@@filter_value',selected_items[4])
        elif key == 'to_date':
            if selected_items[5] != '':
                to_month_cond = filter_info['filter_cond'][key].replace('@@filter_value',selected_items[5]) 
    sql_query = sql_query.replace('@@zone_filter',zone_cond).replace('@@state_filter',state_cond).replace('@@district_filter',dist_cond).replace('@@partner_filter',partner_cond).replace('@@donor_filter',donor_cond).replace('@@from_date_filter',from_month_cond).replace('@@to_date_filter',to_month_cond)
    return sql_query
    
# #****************************************************************************
# # update table chart data to replace dummy data with actual values
# #****************************************************************************

def set_dynamic_table_chart_data(sql, headers):
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    newdata = []
    chart_row_id_value = []
    newdata.append(headers)
    data = []
    data.insert(0,tuple(headers))
    for idx,row in enumerate(rows):
        # newdata.append(list(map(str, list(row))))
       data.insert(idx+1,row)
    return data

# #****************************************************************************
# # Dashboard
# #****************************************************************************

@login_required(login_url='/login/')
def dashboard_v4(request):
    heading = 'Dashboard'
    try:
        if request.session.get('role_id') == 11:
            cht = ChartMeta.objects.filter(
                status=2,page_slug='dashboard_v4').exclude(chart_slug__in=['cat-calling-spectacles_v4','tele-calling-spectacles_v4','no-people-undergo-cataract_v4']).order_by('display_order')
        else:
            cht = ChartMeta.objects.filter(
                status=2,page_slug='dashboard_v4').order_by('display_order')
        zones = Zone.objects.filter(status=2).order_by('name')
        partners = Partner.objects.filter(status=2).order_by('name')
        donors = Donor.objects.filter(status=2).order_by('name')
        chart_list = []
        zone_filter,partner_filter,state_filter,district_filter,donor_filter,selected_items,user_filter_data,user_role = filter_location_data(request)
        for i in cht:
            if i.chart_type == 8:
                # chart_type values: 
                # 1=Column Chart, 2=Pie Chart, 3=Table Chart, 4=Bar Chart, 5=Column Stack, 6=Bar Dynamic Chart, 7=Column Dynamic Stack,
                # 8=Card Chart
                cht_info = {}
                chart_row_id_value = []
                data = []
                filtered_query = filter_conditions(
                    request, i.chart_query.get('sql_query'), i.filter_info, selected_items)
                chart_data = list(set_card_chart_data(
                    filtered_query, i.chart_query.get('labels')))
                cht_info = {"chart_type": "CARDCHART"}
                cht_info["chart_title"] = i.chart_title
                # cht_info.update({"colours": [
                                # {'role': 'style'}, '#FF3333', '#32B517', '#FFEA00', '#FFAA00', '#FF3333']})
                # chart_data = [('Male',96), ('Female',45), ('TG',32)]
                cht_info["datas"] = chart_data
                cht_info["bx_bg"] = i.chart_options.get('bx_bg',[])
                cht_info["bx_icon"] = i.chart_options.get('bx_icon',[])
                cht_info["bx_text"] = i.chart_options.get('bx_text',[])
                cht_info["bx_div"] = i.chart_options.get('bx_div',[])
                cht_info.update({"tooltip": i.chart_tooltip})
                cht_info.update({"chart_note": i.chart_note})
                cht_info.update({"chart_name": i.chart_slug})
                cht_info["chart_height"] = i.chart_height
                cht_info.update({"div": i.div_class})
                cht_info.update({"click_url_template":i.chart_query.get("click_url","")})
                chart_list.append(cht_info)
            elif i.chart_type == 1:
                # chart_type values: 
                # 1=Column Chart, 2=Pie Chart, 3=Table Chart, 4=Bar Chart, 5=Column Stack, 6=Bar Dynamic Chart, 7=Column Dynamic Stack,
                cht_info = {}
                # list to hold chart row id value - location id or classification id, etc based for the row
                # row/chart number mapps to the index in the list
                # used for dynamic charts where click handling is required
                chart_row_id_value = []
                filtered_query = filter_conditions(
                    request, i.chart_query.get('sql_query'), i. filter_info, selected_items)
                chart_data = list(set_column_chart_data(
                    filtered_query, i.chart_query.get('labels')))
                cht_info = {"chart_type": "COLUMNCHART"}
                cht_info["chart_title"] = i.chart_title
                chart_data.insert(0, ('', ''))
                cht_info["datas"] = chart_data
                # cht_info["datas"] = [('', ''), ('Ordered', 60), ('Pending', 30), ('Ready', 40), ('Delivered', 50), (' Received', 25),('Examined',55),('Prescibed',10)] 
                cht_info.update({"options": i.chart_options})
                cht_info.update({"colours": [
                                {'role': 'style'}, '#FF3333', '#32B517', '#FFEA00', '#FFAA00', '#FF3333']})
                cht_info.update({"tooltip": i.chart_tooltip})
                cht_info.update({"chart_note": i.chart_note})
                cht_info.update({"chart_name": i.chart_slug})
                cht_info["chart_height"] = i.chart_height
                cht_info.update({"div": i.div_class})
                cht_info.update({"click_url_template":i.chart_query.get("click_url","")})
                cht_info.update({"chart_row_id_value":chart_row_id_value})
                chart_list.append(cht_info)
            elif i.chart_type == 2:
                # chart_type values: 
                # 1=Column Chart, 2=Pie Chart, 3=Table Chart, 4=Bar Chart, 5=Column Stack, 6=Bar Dynamic Chart, 7=Column Dynamic Stack,
                cht_info = {}
                # list to hold chart row id value - location id or classification id, etc based for the row
                # row/chart number mapps to the index in the list
                # used for dynamic charts where click handling is required
                chart_row_id_value = []
                data = []
                filtered_query = filter_conditions(
                    request, i.chart_query.get('sql_query'), i. filter_info, selected_items)

                chart_data = list(set_pie_chart_data(
                    filtered_query, i.chart_query.get('labels')))
                cht_info = {"chart_type": "PIECHART"}
                cht_info["chart_title"] = i.chart_title
                # cht_info.update({"colours": [
                #                 {'role': 'style'}, '#FF3333', '#32B517', '#FFEA00', '#FFAA00', '#FF3333']})
                # chart_data.insert(0, ('', ''))
                cht_info["datas"] = chart_data
                cht_info["label"] = i.chart_query.get("labels","")
                # cht_info["datas"] = [('', ''), ('Male', 60), ('Female', 50), ('Transgender', 40)]
                cht_info["options"] = i.chart_options

                cht_info["options"].update({"sliceVisibilityThreshold":0.0001})
                cht_info.update({"tooltip": i.chart_tooltip})
                cht_info.update({"chart_note": i.chart_note})
                cht_info.update({"chart_name": i.chart_slug})
                cht_info["chart_height"] = i.chart_height
                cht_info.update({"div": i.div_class})
                cht_info.update({"click_url_template":i.chart_query.get("click_url","")})
                chart_list.append(cht_info)
                
            elif i.chart_type == 3:
                # chart_type values: 
                # 1=Column Chart, 2=Pie Chart, 3=Table Chart, 4=Bar Chart, 5=Column Stack, 6=Bar Dynamic Chart, 7=Column Dynamic Stack,
                cht_info = {"chart_type": "TABLECHART"}
                # list to hold chart row id value - location id or classification id, etc based for the row
                # row/chart number mapps to the index in the list
                # used for dynamic charts where click handling is required
                # chart_row_id_value = []
                headers = i.chart_query.get('col_headers')
                filtered_query = filter_conditions(
                    request, i.chart_query.get('sql_query'), i. filter_info, selected_items)
                chart_data = set_dynamic_table_chart_data(
                    filtered_query, headers)
                cht_info["chart_title"] = i.chart_title
                cht_info["options"] = i.chart_options
                cht_info["datas"] = chart_data
                # cht_info["datas"] = [('Visual impairment', 'Total No. of <br/>Patients'), ('Early VI (6/12-6/18) (Better eye PV)', 4), ('Moderate VI(6/18-6/60) (Better eye PV)', 6), ('Severe VI(6/60-3/60) (Better eye PV)', 5), ('Blind (less than 3/60) (Better eye PV)', 0)]
                # cht_info["datas"] = [('Spectacle Type', 'gender','Ordered','Pending','Ready','Delivered','Received'), ('Near','Male', 60, 12, 18, 45, 19), ('R2C','Female', 50,80,22,44,10), ('R2C','Transgender', 40,44,19,25,16), ('Near','Male', 60, 12, 18, 45, 19), ('R2C','Male', 60, 12, 18, 45, 19),('R2C','Female', 60, 12, 19, 45, 52),('R2C','Male', 45, 12, 18, 45, 19)]
                cht_info["tooltip"] = i.chart_tooltip
                cht_info["chart_height"] = i.chart_height
                cht_info["chart_name"] = i.chart_slug
                cht_info["div"] = i.div_class
                cht_info.update({"click_url_template":i.chart_query.get("click_url","")})
                # cht_info.update({"chart_row_id_value":chart_row_id_value})
                chart_list.append(cht_info)
            elif i.chart_type == 4 or i.chart_type == 6:
                # chart_type values: 
                # 1=Column Chart, 2=Pie Chart, 3=Table Chart, 4=Bar Chart, 5=Column Stack, 6=Bar Dynamic Chart, 7=Column Dynamic Stack,
                cht_info = {}
                # list to hold chart row id value - location id or classification id, etc based for the row
                # row/chart number mapps to the index in the list
                # used for dynamic charts where click handling is required
                chart_row_id_value = []
                filtered_query = filter_conditions(
                    request, i.chart_query.get('sql_query'), i. filter_info, selected_items)
                if i.chart_type == 4:
                    chart_data = list(set_pie_chart_data(
                        filtered_query, i.chart_query.get('labels')))
                else:
                    # chart_data, chart_row_id_value = list(set_bar_chart_dynamic_lable(filtered_query))
                    first_tuple, *rest_of_data = [('Place', 'Value'), ('Vision Center', 180), ('Camp', 220), ('Both', 60)]
                cht_info = {"chart_type": "BARCHART"}
                cht_info["chart_title"] = i.chart_title
                chart_data.insert(0, ('', ''))
                cht_info.update({"colours": [
                                {'role': 'style'}, '#FFEA00', '#FF3333', '#32B517', '#FFAA00', '#FF3333']})
                cht_info["datas"] = chart_data
                cht_info.update({"tooltip": i.chart_tooltip})
                cht_info.update({"options": i.chart_options})
                cht_info.update({"chart_note": i.chart_note})
                cht_info.update({"chart_name": i.chart_slug})
                cht_info["chart_height"] = i.chart_height
                cht_info["label"] = i.chart_query.get("labels","")
                cht_info["label_1"] = i.chart_title
                cht_info.update({"div": i.div_class})
                cht_info.update({"click_url_template":i.chart_query.get("click_url","")})
                cht_info.update({"chart_row_id_value":chart_row_id_value})
                chart_list.append(cht_info)
            elif i.chart_type == 9:
                cht_info = {}
                filtered_query = filter_conditions(
                    request, i.chart_query.get('sql_query'), i.filter_info,selected_items)
                chart_data = list(normal_return_rows(filtered_query))
                chart_label = i.chart_query.get('labels')
                cht_info = {"chart_type": "GEOCHART"}
                # cht_info["datas"] = chart_data
                chart_data.insert(0, tuple(chart_label))
                geo_data = chart_data
                cht_info["chart_title"] = i.chart_title
                cht_info["datas"] = [tuple(str(x).lower() if not isinstance(x, int) else x for x in item) for item in chart_data]

                # cht_info["chart_title"] = i.chart_title
                # cht_info["datas"] = [list(item) for item in chart_data]
                cht_info.update({"tooltip": i.chart_tooltip})
                cht_info.update({"options": i.chart_options})
                cht_info.update({"chart_note": i.chart_note})
                cht_info.update({"chart_name": i.chart_slug})
                cht_info["chart_height"] = i.chart_height
                cht_info["label"] = i.chart_query.get("labels","")
                cht_info.update({"div": i.div_class})
                cht_info.update({"click_url_template":i.chart_query.get("click_url","")})
                cht_info.update({"chart_row_id_value":chart_row_id_value})
                chart_list.append(cht_info)
            elif i.chart_type == 8:
                cht_info = {}
                filtered_query = filter_conditions(
                    request, i.chart_query.get('sql_query'), i.filter_info,selected_items)
                
                chart_data = list(set_column_chart_data(
                    filtered_query,i.chart_query.get('labels')))
                if i.chart_query.get('count_query'):
                    count_query = filter_conditions(
                        request, i.chart_query.get('count_query'), i.filter_info)
                    labels= i.chart_query.get('count_labels')
                    total_count = normal_query(count_query,labels)
                # chart_data = list(set_column_chart_data(
                #     i.chart_query.get('sql_query'), i.chart_query.get('labels')))
                cht_info = {"chart_type": "LINECHART"}
                cht_info["chart_title"] = i.chart_title
                cht_info["total"] = total_count
                # chart_data.insert(0, ('','','','',''))
                cht_info["datas"] = chart_data
                
                cht_info.update({"options": i.chart_options})
                cht_info.update({"tooltip": i.chart_tooltip})
                cht_info.update({"chart_note": i.chart_note})
                cht_info.update({"chart_name": i.chart_slug})
                cht_info["chart_height"] = i.chart_height
                cht_info.update({"div": i.div_class})
                chart_list.append(cht_info)

            elif i.chart_type == 5:
                # chart_type values: 
                # 1=Column Chart, 2=Pie Chart, 3=Table Chart, 4=Bar Chart, 5=Column Stack, 6=Bar Dynamic Chart, 7=Column Dynamic Stack,
                cht_info = {"chart_type": "COLUMNSTACK"}
                # list to hold chart row id value - location id or classification id, etc based for the row
                # row/chart number mapps to the index in the list
                # used for dynamic charts where click handling is required
                chart_row_id_value = []
                filtered_query = filter_conditions(
                    request, i.chart_query.get('sql_query'), i.filter_info, selected_items)
                chart_data = set_dynamic_table_chart_data(
                    filtered_query, headers)
                cht_info["chart_title"] = i.chart_title
                cht_info["datas"] = chart_data
                cht_info["options"] = i.chart_options
                # chart_type values: 1=Column Chart, 2=Pie Chart, 3=Table Chart , 4- Column Stack
                cht_info["chart_height"] = i.chart_height
                cht_info["chart_name"] = i.chart_slug
                cht_info["div"] = i.div_class
                cht_info.update({"tooltip": i.chart_tooltip})
                cht_info.update({"chart_note": i.chart_note})
                cht_info.update({"click_url_template":i.chart_query.get("click_url","")})
                cht_info.update({"chart_row_id_value":chart_row_id_value})
                chart_list.append(cht_info)
            elif i.chart_type == 10:
                cht_info = {}
                filtered_query = filter_conditions(
                    request, i.chart_query.get('sql_query'), i.filter_info,selected_items)
                # chart_data = list(set_pie_chart_data(
                        # filtered_query, i.chart_query.get('labels')))
                chart_data = list(normal_return_rows(filtered_query))
                if i.chart_query.get('count_query'):
                    count_query = filter_conditions(
                        request, i.chart_query.get('count_query'), i.filter_info)
                    labels= i.chart_query.get('count_labels')
                    total_count = normal_query(count_query,labels)
                cht_info = {"chart_type": "LINECHART"}
                cht_info["datas"] = [item[0] for item in chart_data]
                cht_info["datas2"] = [item[1] for item in chart_data]
                cht_info["chart_title"] = i.chart_title
                cht_info["chart_name"] = i.chart_slug

                cht_info.update({"tooltip": i.chart_tooltip})
                cht_info.update({"options": i.chart_options})
                cht_info.update({"chart_note": i.chart_note})
                # cht_info.update({"chart_name": i.chart_slug})
                cht_info["chart_height"] = i.chart_height
                cht_info["label"] = i.chart_query.get("labels","")
                cht_info.update({"div": i.div_class})
                cht_info.update({"click_url_template":i.chart_query.get("click_url","")})
                cht_info.update({"chart_row_id_value":chart_row_id_value})
                chart_list.append(cht_info)
            
            elif i.chart_type == 11:
                cht_info = {}
                filtered_query = filter_conditions(
                    request, i.chart_query.get('sql_query'), i.filter_info,selected_items)
                # chart_data = list(set_pie_chart_data(
                        # filtered_query, i.chart_query.get('labels')))
                chart_data = list(normal_return_rows(filtered_query))
                if i.chart_query.get('count_query'):
                    count_query = filter_conditions(
                        request, i.chart_query.get('count_query'), i.filter_info)
                    labels= i.chart_query.get('count_labels')
                    total_count = normal_query(count_query,labels)
                cht_info = {"chart_type": "PROGRESSIVEBARCHART"}
                cht_info["chart_title"] = i.chart_title
                cht_info["chart_name"] = i.chart_slug
                cht_info["datas"] = chart_data
                cht_info.update({"tooltip": i.chart_tooltip})
                cht_info.update({"options": i.chart_options})
                cht_info.update({"chart_note": i.chart_note})
                # cht_info.update({"chart_name": i.chart_slug})
                cht_info["chart_height"] = i.chart_height
                cht_info["label"] = i.chart_query.get("labels","")
                cht_info.update({"div": i.div_class})
                cht_info.update({"click_url_template":i.chart_query.get("click_url","")})
                cht_info.update({"chart_row_id_value":chart_row_id_value})
                chart_list.append(cht_info)

            elif i.chart_type == 12:
                cht_info = {}
                filtered_query = filter_conditions(
                    request, i.chart_query.get('sql_query'), i.filter_info,selected_items)
                # chart_data = list(set_pie_chart_data(
                        # filtered_query, i.chart_query.get('labels')))
                chart_data = list(normal_return_rows(filtered_query))
                if i.chart_query.get('count_query'):
                    count_query = filter_conditions(
                        request, i.chart_query.get('count_query'), i.filter_info)
                    labels= i.chart_query.get('count_labels')
                    total_count = normal_query(count_query,labels)
                cht_info = {"chart_type": "DOUGHNUT"}
                cht_info["datas"] = [item[0] for item in chart_data]
                cht_info["datas2"] = [item[1] for item in chart_data]
                # cht_info["datas2"] = [{'x':item[2],'y':item[0   ]} for item in chart_data]
                cht_info.update({"tooltip": i.chart_tooltip})
                cht_info.update({"options": i.chart_options})
                cht_info.update({"chart_note": i.chart_note})
                cht_info.update({"chart_name": i.chart_slug})
                cht_info["chart_height"] = i.chart_height
                cht_info["chart_title"] = i.chart_title
                cht_info["chart_name"] = i.chart_slug

                cht_info["label"] = i.chart_query.get("labels","")
                cht_info.update({"div": i.div_class})
                cht_info.update({"click_url_template":i.chart_query.get("click_url","")})
                cht_info.update({"chart_row_id_value":chart_row_id_value})
                chart_list.append(cht_info)
            elif i.chart_type == 13:
                cht_info = {}
                filtered_query = filter_conditions(
                    request, i.chart_query.get('sql_query'), i.filter_info,selected_items)
                # chart_data = list(set_pie_chart_data(
                        # filtered_query, i.chart_query.get('labels')))
                chart_data = list(normal_return_rows(filtered_query))
                if i.chart_query.get('count_query'):
                    count_query = filter_conditions(
                        request, i.chart_query.get('count_query'), i.filter_info)
                    labels= i.chart_query.get('count_labels')
                    total_count = normal_query(count_query,labels)
                cht_info = {"chart_type": "AREALINECHART"}
                cht_info["datas"] = [item[0] for item in chart_data]
                cht_info["datas2"] = [item[1] for item in chart_data]
                cht_info["datas3"] = [item[2] for item in chart_data]
                # cht_info["datas2"] = [{'x':item[2],'y':item[0   ]} for item in chart_data]
                cht_info.update({"tooltip": i.chart_tooltip})
                cht_info.update({"options": i.chart_options})
                cht_info.update({"chart_note": i.chart_note})
                cht_info.update({"chart_name": i.chart_slug})
                cht_info["chart_height"] = i.chart_height
                cht_info["chart_title"] = i.chart_title
                cht_info["chart_name"] = i.chart_slug
                cht_info["label_1"] = i.chart_query.get("labels","")[0]
                cht_info["label_2"] = i.chart_query.get("labels","")[1]
                cht_info.update({"div": i.div_class})
                cht_info.update({"click_url_template":i.chart_query.get("click_url","")})
                cht_info.update({"chart_row_id_value":chart_row_id_value})
                chart_list.append(cht_info)



        data = {"chart": chart_list}
        #store the dashboard filter values for handling chart click events
        mat_view_last_updated = DashboardWidgetSummaryLog.objects.get(
            status=2, log_key='meta_dashboard_reports_views').last_successful_update
        request_data = None
            
        context = {
            'data': json.dumps(data, cls=DateTimeEncoder),
            'data_html': data,
            'selected_items': selected_items,
            'user_filter_data':user_filter_data,
            'heading': 'Dashboard',
            'districts': district_filter,
            # 'geo_datas' : geo_data,
            'zones': zone_filter,
            'states': state_filter,
            # 'district_obj': district_obj,
            'partners':partner_filter,
            'user_role':user_role,
            'donors':donor_filter,
            'mat_view_last_updated': mat_view_last_updated
        }
        return render(request, 'dashboard/dashboard_v4.html', context)
    except KeyError:
        return redirect('/login/')



class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

# ****************************************************************************
# Function to refresh_materialized_view
# ****************************************************************************

def refresh_materialized_view(query):
    cursor = connection.cursor()
    cursor.execute(query)
    return True

from django.utils import timezone

def materialized_view_master():
    start_time = datetime.now()
    try:
        refresh_materialized_view('REFRESH MATERIALIZED VIEW dash_repo_patient_basic_info_view')
        refresh_materialized_view('REFRESH MATERIALIZED VIEW dash_repo_screening_info_view')
        refresh_materialized_view('REFRESH MATERIALIZED VIEW dash_repo_glass_prescription_view')
        refresh_materialized_view('REFRESH MATERIALIZED VIEW dash_repo_vision_center_list')
        refresh_materialized_view('REFRESH MATERIALIZED VIEW daily_login_base_summary')
        refresh_materialized_view('''update reports_truckermpr
        set mpr_status = x1.mpr_status
        from reports_mprstatusupdate x1
        where x1.partner_id = reports_truckermpr.partner_id::int and x1.month = reports_truckermpr.mpr_month::int and x1.year = reports_truckermpr.mpr_year::int''')

        print('MATERIALIZED VIEWS REFRESHED SUCCESS')
        end_time = datetime.now()
        duration = end_time - start_time
        time_output = format_duration(duration)
        logdata, created = DashboardWidgetSummaryLog.objects.get_or_create(
            log_key='meta_dashboard_reports_views')
        logdata.last_successful_update = start_time
        logdata.most_recent_update = end_time
        logdata.most_recent_update_status = 'Success'
        logdata.most_recent_update_time_taken_millis = time_output
        logdata.error = "-"
        logdata.save()
        
    except Exception as ex1:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_stack = repr(traceback.format_exception(
            exc_type, exc_value, exc_traceback))
        logger.error(error_stack)
        end_time = datetime.now()
        duration = end_time - start_time
        time_output = format_duration(duration)
        logdata, created = DashboardWidgetSummaryLog.objects.get_or_create(
            log_key='meta_dashboard_reports_views')
        logdata.last_successful_update = start_time
        logdata.most_recent_update = end_time
        logdata.most_recent_update_status = 'False'
        logdata.most_recent_update_time_taken_millis = time_output
        logdata.error = ex1.args[0]
        logdata.save()
    return True

def patient_map(request):
    heading = 'Dashboard'
    try:
        if request.session.get('role_id') == 11:
            cht = ChartMeta.objects.filter(
                status=2,page_slug='dashboard_v4').exclude(chart_slug__in=['cat-calling-spectacles_v4','tele-calling-spectacles_v4','no-people-undergo-cataract_v4']).order_by('display_order')
        else:
            cht = ChartMeta.objects.filter(
                status=2,page_slug='dashboard_v4').order_by('display_order')
        zones = Zone.objects.filter(status=2).order_by('name')
        partners = Partner.objects.filter(status=2).order_by('name')
        donors = Donor.objects.filter(status=2).order_by('name')
        chart_list = []
        zone_filter,partner_filter,state_filter,district_filter,donor_filter,selected_items,user_filter_data,user_role = filter_location_data(request)
        for i in cht:
            if i.chart_type == 9:
                cht_info = {}
                filtered_query = filter_conditions(
                    request, i.chart_query.get('sql_query'), i.filter_info,selected_items)
                chart_data = list(normal_return_rows(filtered_query))
                chart_label = i.chart_query.get('labels')
                cht_info = {"chart_type": "GEOCHART"}
                # cht_info["datas"] = chart_data
                # chart_data.insert(0, tuple(chart_label))
                geo_data = chart_data
                cht_info["chart_title"] = i.chart_title
                cht_info["datas"] = [tuple(str(x).lower() if not isinstance(x, int) else x for x in item) for item in chart_data]

                print(cht_info)
                print([tuple(str(x).lower() if not isinstance(x, int) else x for x in item) for item in chart_data][10])
                # cht_info["datas"] = [['madhya pradesh', 10, 12], 
                #         ['uttar pradesh', 11, 13], 
                #         ['karnataka', 12, 14],
                #         ['nagaland', 13, 15], 
                #         ['bihar', 14, 16], 
                #         ['lakshadweep', 15, 17],
                #         ['andaman and nicobar', 16, 18], 
                #         ['assam', 17, 19], 
                #         ['west bengal', 18, 20],
                #         ['puducherry', 19, 21], 
                #         ['daman and diu', 20, 22], 
                #         ['gujarat', 21, 23],
                #         ['rajasthan', 22, 24], 
                #         ['dadara and nagar havelli', 23, 25],
                #         ['chhattisgarh', 24, 26], 
                #         ['tamil nadu', 25, 27], 
                #         ['chandigarh', 26, 28],
                #         ['punjab', 27, 29], 
                #         ['haryana', 28, 30], 
                #         ['andhra pradesh', 29, 31],
                #         ['maharashtra', 30, 32], 
                #         ['himachal pradesh', 31, 33], 
                #         ['meghalaya', 32, 34],
                #         ['kerala', 33, 35], 
                #         ['telangana', 34, 36], 
                #         ['mizoram', 35, 37], 
                #         ['tripura', 36, 38],
                #         ['manipur', 37, 39], 
                #         ['arunanchal pradesh', 38, 40], 
                #         ['jharkhand', 39, 41],
                #         ['goa', 40, 42], 
                #         ['nct of delhi', 41, 43], 
                #         ['odisha', 42, 44],
                #         ['jammu and kashmir', 43, 45], 
                #         ['sikkim', 44, 46], 
                #         ['uttarakhand', 45, 47]]
                # print(cht_info)
                # print([list(item) for item in chart_data][3])
                cht_info.update({"tooltip": i.chart_tooltip})
                cht_info.update({"options": i.chart_options})
                cht_info.update({"chart_note": i.chart_note})
                cht_info.update({"chart_name": i.chart_slug})
                cht_info["chart_height"] = i.chart_height
                cht_info["label"] = i.chart_query.get("labels","")
                cht_info.update({"div": i.div_class})
                cht_info.update({"click_url_template":i.chart_query.get("click_url","")})
                # cht_info.update({"chart_row_id_value":chart_row_id_value})
                chart_list.append(cht_info)
        data = {"chart": chart_list}
        #store the dashboard filter values for handling chart click events
        mat_view_last_updated = DashboardWidgetSummaryLog.objects.get(
            status=2, log_key='meta_dashboard_reports_views').last_successful_update
        request_data = None
              
        context = {
            'data': json.dumps(data, cls=DateTimeEncoder),
            'data_html': data,
            'selected_items': selected_items,
            'user_filter_data':user_filter_data,
            'heading': 'Dashboard',
            'districts': district_filter,
            # 'geo_datas' : geo_data,
            'zones': zone_filter,
            'states': state_filter,
            # 'district_obj': district_obj,
            'partners':partner_filter,
            'user_role':user_role,
            'donors':donor_filter,
            'mat_view_last_updated': mat_view_last_updated
        }
        # return render(request, 'dashboard/dashboard_v4.html', context)
        return render(request, 'dashboard/patient_chart_india.html', context)
    except KeyError:
        return redirect('/login/')
    