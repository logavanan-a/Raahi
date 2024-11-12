import os
from django.conf import settings
from sims.views import *
import pandas as pd
import traceback
import csv
import zipfile
import sys
import io
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_list_or_404,redirect,get_object_or_404 
from django.contrib.auth.decorators import login_required
from django.db import connection
from .models import ReportMeta,ReportExport
from master_data.models import *
from sims.models import *
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from dateutil.relativedelta import relativedelta
import copy
import json
import re
import csv
import logging
from master_data.models import Config
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from . models import *
from dateutil import parser
import datetime


logger = logging.getLogger(__name__) 
# ****************************************************************************
# execute Raw SQL
# ****************************************************************************


def return_sql_results(sql, conn=None, params=None):
    # logger.error('query:'+ sql)
    if conn == None:
        conn = connection
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    rows = cursor.fetchall()
    return rows


def return_sql_results_columns(sql, conn=None, params=None):
    if conn is None:
        conn = connection  # Assuming `connection` is defined somewhere in your code
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    return column_names, rows




#******************************************************************************
# Truckers Monthly Report 
#******************************************************************************
def mpr_filter_condition(request,req_data,state_list,donor_list,partner_list):
    mpr_month,mpr_year = None,None
    mpr_month_name,month_filter =None, None
    filter_conditions = ''
    vc_open_mon_filter_conditions = ''
    # selected_items = [req_data['state'] if req_data['state'] else '',req_data['donor_name'] if req_data['donor_name'] else '',req_data['hospital_name'] if req_data['hospital_name'] else '',req_data['from_month'] if req_data['from_month'] else '']
    selected_items = [
            req_data.get('state', ''),
            req_data.get('donor_name', ''),
            req_data.get('hospital_name', ''),
            req_data.get('from_month', ''),
        ]
    state_list = [i[0] for i in state_list]
    partner_list = [i[0] for i in partner_list]
    donor_list = [i[0] for i in donor_list]
    mpr_filter_values = {}
    if request.session.get('role_id') in (8,9,10):
        get_state_partner_linkage = ApplicationUserStateLinkage.objects.filter(status=2,user_id=request.user.id).values_list('state',flat=True)
        zone_list_filter = State.objects.filter(status=2,id__in=get_state_partner_linkage).values_list('zone',flat=True).distinct()
        zone_list = [i for i in zone_list_filter]
        filter_conditions += f' and zone_id in ({str(zone_list)[1:-1]})' 
    #     if selected_items[2] != '':
    #         partner_name = Partner.objects.filter(status=2,id=int(req_data['hospital_name'])).values('name')
    #         mpr_filter_values['partner_name']=partner_name[0]['name']
    #         partner_id = req_data['hospital_name']
    #         filter_conditions += f' and partner_id = {partner_id}'
    #     else:
    #         mpr_filter_values['partner_name']='All Hospitals'
    #         filter_conditions += f' and partner_id in ({str(partner_list)[1:-1]})'
    #     if selected_items[0] != '':
    #         state_name = State.objects.filter(status=2,id=int(req_data['state'])).values('name')
    #         mpr_filter_values['state_name']=state_name[0]['name']
    #         state_id = req_data['state']
    #         filter_conditions += f' and state_id = {state_id}'
    #     else:
    #         mpr_filter_values['state_name']='All States'
    #         filter_conditions += f' and state_id in ({str(state_list)[1:-1]})'
    #     if selected_items[1] != '':
    #         donor_name = Donor.objects.filter(status=2,id=int(req_data['donor_name'])).values('name')
    #         mpr_filter_values['donor_name']=donor_name[0]['name']
    #         donor_id = req_data['donor_name']
    #         filter_conditions += f' and donor_id = {donor_id}'
    #     else:
    #         mpr_filter_values['donor_name']='All Donor'
    #         filter_conditions += f' and donor_id in ({str(donor_list)[1:-1]})'        
    
    # else:
    if selected_items[2] != '':
            partner_name = Partner.objects.filter(id=int(req_data['hospital_name'])).values('name')
            mpr_filter_values['partner_name']=partner_name[0]['name']
            partner_id = req_data['hospital_name']
            filter_conditions += f' and partner_id = {partner_id}'
            vc_open_mon_filter_conditions += f' and partner_id = {partner_id}'
    else:
        mpr_filter_values['partner_name']='All Hospitals'
    if selected_items[0] != '':
        state_name = State.objects.filter(status=2,id=int(req_data['state'])).values('name')
        mpr_filter_values['state_name']=state_name[0]['name']
        state_id = req_data['state']
        filter_conditions += f' and state_id = {state_id}'
    else:
        mpr_filter_values['state_name']='All States'
    if selected_items[1] != '':
        donor_name = Donor.objects.filter(status=2,id=int(req_data['donor_name'])).values('name')
        mpr_filter_values['donor_name']=donor_name[0]['name']
        donor_id = req_data['donor_name']
        filter_conditions += f' and donor_id = {donor_id}'
        vc_open_mon_filter_conditions += f' and donor_id = {donor_id}' 
    else:
        mpr_filter_values['donor_name']='All Donor'
    if selected_items[3] != '':
        month_filter = req_data['from_month']
        mpr_year = month_filter.split('-')[0]
        mpr_month = str(int(month_filter.split('-')[1]))
        filter_conditions += f' and mpr_month::int = {mpr_month}'
        filter_conditions += f' and mpr_year::int = {mpr_year}'
        mpr_month_name = datetime.datetime.strptime(mpr_month, "%m").strftime("%B")
        vc_open_mon_filter_conditions += f" and to_char(app_created_at,'YYYY-MM') = '{month_filter}'"
    return mpr_filter_values,vc_open_mon_filter_conditions,filter_conditions,mpr_month,mpr_year,mpr_month_name,month_filter



import calendar
@login_required(login_url='/login/')
def truckers_month_report(request):
    heading = 'Truckers Monthly Report'
    no_data = True
    mpr_month,mpr_year = None,None
    data_query_list = []
    section_title = []
    table_header = []
    custom_export_headers = []
    total_header_cols = []
    report_slug_list = []
    data = []
    # nowrap_cols = []
    user_sort_field = []
    user_sort_order = []
    page_info = []
    sorting_field = []
    # user_filter_values = {}
    user_location_data = None
    filter_values = None
    user_id = request.user.id
    mpr_order = MprStatusUpdate.objects.filter(created_by=user_id,month=mpr_month,year=mpr_year)
    rows_per_page= int(Config.objects.get(code='report_records_per_page').value)
    page_reports = ReportMeta.objects.filter(
            page_slug='truc-month-report', status=2).order_by('display_order')
    req_data = request.POST
    for idx, report in enumerate(page_reports):
        r_slug = report.report_slug
        s_title = report.report_title
        f_info = report.filter_info
        s_info = report.sort_info
        # if idx == 0:
        page_slug = report.page_slug
        user_location_data, filter_values, user_filter_values,state_list,donor_list,partner_list = get_filter_data(request, req_data, f_info,r_slug,pagination=False)
    if request.method == "POST":
        mpr_filter_values,vc_open_mon_filter_conditions,filter_conditions,mpr_month,mpr_year,mpr_month_name,month_filter = mpr_filter_condition(request,req_data,state_list,donor_list,partner_list)
    export_flag = True if req_data.get('export') and req_data.get(
        'export').lower() == 'true' else False
    if mpr_month != None and mpr_year != None:
        no_data = False
        month = mpr_month
        year = mpr_year
        sql =f'''select mpr.month, mpr.year, to_char(to_date (mpr.month::text, 'MM'), 'Month') ||' '|| mpr.year as month_year, mpr.year||to_char(to_date (mpr.month::text, 'MM'), 'mm') as code, 
        pnt.name as patner_name, to_char(mpr.partner_date at time zone 'Asia/Kolkata', 'DD-MM-YYYY HH12:MI:SS AM') as partner_date,
        to_char(mpr.zonal_coordinator_date at time zone 'Asia/Kolkata', 'DD-MM-YYYY HH12:MI:SS AM') as zonal_coordinator_date, 
        to_char(mpr.national_coordinator_date at time zone 'Asia/Kolkata', 'DD-MM-YYYY HH12:MI:SS AM') as national_coordinator_date, 
        to_char(mpr.super_admin_date at time zone 'Asia/Kolkata', 'DD-MM-YYYY HH12:MI:SS AM') as super_admin_date, 
        mpr.mpr_status as mpr_status_id, us.username, mpr.remark, mpr.national_remark, mpr.super_admin_remark, zrus.username as zrj_username, 
        nrus.username as nrj_username, srus.username as srj_username  
        from reports_mprstatusupdate mpr 
        inner join master_data_userpartnerlinkage upl on mpr.created_by_id=upl.user_id 
        inner join master_data_partner pnt on upl.partner_id=pnt.id
        inner join auth_user us on upl.user_id=us.id 
        left join auth_user zrus on mpr.approved_by_id=zrus.id
        left join auth_user nrus on mpr.forward_to_super_admin_by_id=nrus.id
        left join auth_user srus on mpr.ssims_user_id=srus.id
        where mpr.month={mpr_month} and mpr.year={mpr_year} and mpr.created_by_id={request.user.id}
        '''
        mpr_order = SqlHeader(sql)
        

        target_mpr_value = return_sql_results("""
                    select json_agg(json_build_object('code',code,'target_1',target_1,'target_2',target_2))
                from(
                select code,sum(tracket_col_1) as target_1 ,sum(tracket_col_2) as target_2 from reports_reporttracket group by code order by code
                ) as x
                    """)
        # return_sql_results(f"select generate_truckers_mpr({year}, {month});")
        mpr_data = return_sql_results(f"""SELECT *
        FROM (
        SELECT
        json_object_agg('Total number of Camps conducted during the month-1', jsonb_build_object('male', coalesce(i_1_male,0), 'female', coalesce(i_1_female,0), 'monthly_total', coalesce(i_1_total,0), 'till_month_total', coalesce(i_1_till_date,0))) AS i_1_agg,
        json_object_agg('1b. Total number of days the Vision Centre was open during the reporting month- 2 ', jsonb_build_object('male', i_2_male, 'female', i_2_female, 'monthly_total', i_2_total, 'till_month_total', i_2_till_date)) AS i_2_agg,
        json_object_agg('Category of persons screened - Total number of Persons screened (mention only total target and not category wise)- 3 ', jsonb_build_object('male', i_3_male, 'female', i_3_female, 'monthly_total', i_3_total, 'till_month_total', i_3_till_date)) AS i_3_agg,
        json_object_agg('2a. Categor2a. Category of persons screened - Total number of persons screened at camps y of persons screened - Total number of persons screened at camps- 4 ', jsonb_build_object('male', i_4_male, 'female', i_4_female, 'monthly_total', i_4_total, 'till_month_total', i_4_till_date)) AS i_4_agg,
        json_object_agg('2a. Category of persons screened - Total number of persons screened at camps - Driver- 5 ', jsonb_build_object('male', i_5_male, 'female', i_5_female, 'monthly_total', i_5_total, 'till_month_total', i_5_till_date)) AS i_5_agg,
        json_object_agg('2a. Category of persons screened - Total number of persons screened at camps - Cleaner- 6 ', jsonb_build_object('male', i_6_male, 'female', i_6_female, 'monthly_total', i_6_total, 'till_month_total', i_6_till_date)) AS i_6_agg,
        json_object_agg('2a. Category of persons screened - Total number of persons screened at camps - Mechanics- 7 ', jsonb_build_object('male', i_7_male, 'female', i_7_female, 'monthly_total', i_7_total, 'till_month_total', i_7_till_date)) AS i_7_agg,
        json_object_agg('2a. Category of persons screened - Total number of persons screened at camps - Others- 8 ', jsonb_build_object('male', i_8_male, 'female', i_8_female, 'monthly_total', i_8_total, 'till_month_total', i_8_till_date)) AS i_8_agg,
        json_object_agg('2a. Category of persons screened - Total number of persons screened at static centers- 9 ', jsonb_build_object('male', i_9_male, 'female', i_9_female, 'monthly_total', i_9_total, 'till_month_total', i_9_till_date)) AS i_9_agg,
        json_object_agg('2a. Category of persons screened - Total number of persons screened at static centers - Driver- 10 ', jsonb_build_object('male', i_10_male, 'female', i_10_female, 'monthly_total', i_10_total, 'till_month_total', i_10_till_date)) AS i_10_agg,
        json_object_agg('2a. Category of persons screened - Total number of persons screened at static centers - Cleaner- 11 ', jsonb_build_object('male', i_11_male, 'female', i_11_female, 'monthly_total', i_11_total, 'till_month_total', i_11_till_date)) AS i_11_agg,
        json_object_agg('2a. Category of persons screened - Total number of persons screened at static centers - Mechanics- 12 ', jsonb_build_object('male', i_12_male, 'female', i_12_female, 'monthly_total', i_12_total, 'till_month_total', i_12_till_date)) AS i_12_agg,
        json_object_agg('2a. Category of persons screened - Total number of persons screened at static centers - Others- 13 ', jsonb_build_object('male', i_13_male, 'female', i_13_female, 'monthly_total', i_13_total, 'till_month_total', i_13_till_date)) AS i_13_agg,
        json_object_agg('2b. Screening Details - No of people with Distance Vision problem (Category C+G) - Totals- 14 ', jsonb_build_object('male', i_14_male, 'female', i_14_female, 'monthly_total', i_14_total, 'till_month_total', i_14_till_date)) AS i_14_agg,
        json_object_agg('2b. Screening Details - No of people with Near Vision problem(Category D+ H) - Total- 15 ', jsonb_build_object('male', i_15_male, 'female', i_15_female, 'monthly_total', i_15_total, 'till_month_total', i_15_till_date)) AS i_15_agg,
        json_object_agg('2b. Screening Details - No of people with both Near & Distance Vision problem(Category F) - Total- 16 ', jsonb_build_object('male', i_16_male, 'female', i_16_female, 'monthly_total', i_16_total, 'till_month_total', i_16_till_date)) AS i_16_agg,
        json_object_agg('2b. Screening Details - No of people with Colour Vision problem(Category E+G+H) - Total- 17 ', jsonb_build_object('male', i_17_male, 'female', i_17_female, 'monthly_total', i_17_total, 'till_month_total', i_17_till_date)) AS i_17_agg,
        json_object_agg('2b. Screening Details - No of people with Distance Vision problem (Category C+G) - Driver- 18 ', jsonb_build_object('male', i_18_male, 'female', i_18_female, 'monthly_total', i_18_total, 'till_month_total', i_18_till_date)) AS i_18_agg,
        json_object_agg('2b. Screening Details - No of people with Distance Vision problem (Category C+G) - Others- 19 ', jsonb_build_object('male', i_19_male, 'female', i_19_female, 'monthly_total', i_19_total, 'till_month_total', i_19_till_date)) AS i_19_agg,
        json_object_agg('2b. Screening Details - No of people with Near Vision problem(Category D+ H) - Driver- 20 ', jsonb_build_object('male', i_20_male, 'female', i_20_female, 'monthly_total', i_20_total, 'till_month_total', i_20_till_date)) AS i_20_agg,
        json_object_agg('2b. Screening Details - No of people with Near Vision problem(Category D+ H) - Others- 21 ', jsonb_build_object('male', i_21_male, 'female', i_21_female, 'monthly_total', i_21_total, 'till_month_total', i_21_till_date)) AS i_21_agg,
        json_object_agg('2b. Screening Details - No of people with both Near & Distance Vision problem(Category F) - Driver- 22 ', jsonb_build_object('male', i_22_male, 'female', i_22_female, 'monthly_total', i_22_total, 'till_month_total', i_22_till_date)) AS i_22_agg,
        json_object_agg('2b. Screening Details - No of people with both Near & Distance Vision problem(Category F) - Others- 23 ', jsonb_build_object('male', i_23_male, 'female', i_23_female, 'monthly_total', i_23_total, 'till_month_total', i_23_till_date)) AS i_23_agg,
        json_object_agg('2b. Screening Details - No of people with Colour Vision problem(Category E+G+H) - Driver- 24 ', jsonb_build_object('male', i_24_male, 'female', i_24_female, 'monthly_total', i_24_total, 'till_month_total', i_24_till_date)) AS i_24_agg,
        json_object_agg('2b. Screening Details - No of people with Colour Vision problem(Category E+G+H) - Others- 25 ', jsonb_build_object('male', i_25_male, 'female', i_25_female, 'monthly_total', i_25_total, 'till_month_total', i_25_till_date)) AS i_25_agg,
        json_object_agg('Visual Impairment identified (No of people identified with any VI (Distance)) - Early VI (6/12-6/18) (Better eye PV) - Total- 26 ', jsonb_build_object('male', i_26_male, 'female', i_26_female, 'monthly_total', i_26_total, 'till_month_total', i_26_till_date)) AS i_26_agg,
        json_object_agg('Visual Impairment identified (No of people identified with any VI (Distance)) - Moderate VI (6/18-6/60) (Better eye PV) - Total- 27 ', jsonb_build_object('male', i_27_male, 'female', i_27_female, 'monthly_total', i_27_total, 'till_month_total', i_27_till_date)) AS i_27_agg,
        json_object_agg('Visual Impairment identified (No of people identified with any VI (Distance)) - Severe VI (6/60-3/60) (Better eye PV) - Total- 28 ', jsonb_build_object('male', i_28_male, 'female', i_28_female, 'monthly_total', i_28_total, 'till_month_total', i_28_till_date)) AS i_28_agg,
        json_object_agg('Visual Impairment identified (No of people identified with any VI (Distance)) - Blind (less than 3/60) (Better eye PV) - Total- 29 ', jsonb_build_object('male', i_29_male, 'female', i_29_female, 'monthly_total', i_29_total, 'till_month_total', i_29_till_date)) AS i_29_agg,
    json_object_agg('Visual Impairment identified (No of people identified with any VI (Distance)) - Early VI (6/12-6/18) (Better eye PV) - Driver- 30 ', jsonb_build_object('male', i_30_male, 'female', i_30_female, 'monthly_total', i_30_total, 'till_month_total', i_30_till_date)) AS i_30_agg,
    json_object_agg('Visual Impairment identified (No of people identified with any VI (Distance)) - Moderate VI (6/18-6/60) (Better eye PV) - Driver- 31 ', jsonb_build_object('male', i_31_male, 'female', i_31_female, 'monthly_total', i_31_total, 'till_month_total', i_31_till_date)) AS i_31_agg,
    json_object_agg('Visual Impairment identified (No of people identified with any VI (Distance)) - Severe VI (6/60-3/60) (Better eye PV) - Driver- 32 ', jsonb_build_object('male', i_32_male, 'female', i_32_female, 'monthly_total', i_32_total, 'till_month_total', i_32_till_date)) AS i_32_agg,
    json_object_agg('Visual Impairment identified (No of people identified with any VI (Distance)) - Blind (less than 3/60) (Better eye PV) - Driver- 33 ', jsonb_build_object('male', i_33_male, 'female', i_33_female, 'monthly_total', i_33_total, 'till_month_total', i_33_till_date)) AS i_33_agg,
    json_object_agg('Visual Impairment identified (No of people identified with any VI (Distance)) - Early VI (6/12-6/18) (Better eye PV) - Others- 34 ', jsonb_build_object('male', i_34_male, 'female', i_34_female, 'monthly_total', i_34_total, 'till_month_total', i_34_till_date)) AS i_34_agg,
    json_object_agg('Visual Impairment identified (No of people identified with any VI (Distance)) - Moderate VI (6/18-6/60) (Better eye PV) - Others- 35 ', jsonb_build_object('male', i_35_male, 'female', i_35_female, 'monthly_total', i_35_total, 'till_month_total', i_35_till_date)) AS i_35_agg,
    json_object_agg('Visual Impairment identified (No of people identified with any VI (Distance)) - Severe VI (6/60-3/60) (Better eye PV) - Others- 36 ', jsonb_build_object('male', i_36_male, 'female', i_36_female, 'monthly_total', i_36_total, 'till_month_total', i_36_till_date)) AS i_36_agg,
    json_object_agg('Visual Impairment identified (No of people identified with any VI (Distance)) - Blind (less than 3/60) (Better eye PV) - Others- 37 ', jsonb_build_object('male', i_37_male, 'female', i_37_female, 'monthly_total', i_37_total, 'till_month_total', i_37_till_date)) AS i_37_agg,
    json_object_agg('Glass prescription - Total number of people prescribed glasses - Total- 38 ', jsonb_build_object('male', i_38_male, 'female', i_38_female, 'monthly_total', i_38_total, 'till_month_total', i_38_till_date)) AS i_38_agg,
    json_object_agg('Glass prescription - Distance vision glasses - Total- 39 ', jsonb_build_object('male', i_39_male, 'female', i_39_female, 'monthly_total', i_39_total, 'till_month_total', i_39_till_date)) AS i_39_agg,
    json_object_agg('Glass prescription - Near vision glasses - Total       - 40 ', jsonb_build_object('male', i_40_male, 'female', i_40_female, 'monthly_total', i_40_total, 'till_month_total', i_40_till_date)) AS i_40_agg,
    json_object_agg('Glass prescription - Bifocals - Total- 41 ', jsonb_build_object('male', i_41_male, 'female', i_41_female, 'monthly_total', i_41_total, 'till_month_total', i_41_till_date)) AS i_41_agg,
    json_object_agg('Glass prescription - Total number of people prescribed glasses - Driver- 42 ', jsonb_build_object('male', i_42_male, 'female', i_42_female, 'monthly_total', i_42_total, 'till_month_total', i_42_till_date)) AS i_42_agg,
    json_object_agg('Glass prescription - Distance vision glasses - Driver- 43 ', jsonb_build_object('male', i_43_male, 'female', i_43_female, 'monthly_total', i_43_total, 'till_month_total', i_43_till_date)) AS i_43_agg,
    json_object_agg('Glass prescription - Near vision glasses - Driver       - 44 ', jsonb_build_object('male', i_44_male, 'female', i_44_female, 'monthly_total', i_44_total, 'till_month_total', i_44_till_date)) AS i_44_agg,
    json_object_agg('Glass prescription - Bifocals - Driver- 45 ', jsonb_build_object('male', i_45_male, 'female', i_45_female, 'monthly_total', i_45_total, 'till_month_total', i_45_till_date)) AS i_41_agg,
    json_object_agg('Glass prescription - Total number of people prescribed glasses - Others- 46 ', jsonb_build_object('male', i_46_male, 'female', i_46_female, 'monthly_total', i_46_total, 'till_month_total', i_46_till_date)) AS i_46_agg,
    json_object_agg('Glass prescription - Distance vision glasses - Others- 47 ', jsonb_build_object('male', i_47_male, 'female', i_47_female, 'monthly_total', i_47_total, 'till_month_total', i_47_till_date)) AS i_47_agg,
    json_object_agg('Glass prescription - Near vision glasses - Others       - 48 ', jsonb_build_object('male', i_48_male, 'female', i_48_female, 'monthly_total', i_48_total, 'till_month_total', i_48_till_date)) AS i_48_agg,
    json_object_agg('Glass prescription - Bifocals - Others- 49 ', jsonb_build_object('male', i_49_male, 'female', i_49_female, 'monthly_total', i_49_total, 'till_month_total', i_49_till_date)) AS i_49_agg,
    json_object_agg('Glass Dispensed - Total number of glasses dispensed - Total- 50 ', jsonb_build_object('male', i_50_male, 'female', i_50_female, 'monthly_total', i_50_total, 'till_month_total', i_50_till_date)) AS i_50_agg,
    json_object_agg('Glass Dispensed - Total number of glasses dispensed - Driver- 51 ', jsonb_build_object('male', i_51_male, 'female', i_51_female, 'monthly_total', i_51_total, 'till_month_total', i_51_till_date)) AS i_51_agg,
    json_object_agg('Glass Dispensed - Total number of glasses dispensed - Others- 52 ', jsonb_build_object('male', i_52_male, 'female', i_52_female, 'monthly_total', i_52_total, 'till_month_total', i_52_till_date)) AS i_52_agg,
    json_object_agg('Glass Dispensed - Total number of glasses dispensed - Ready made glasses - Total- 53 ', jsonb_build_object('male', i_53_male, 'female', i_53_female, 'monthly_total', i_53_total, 'till_month_total', i_53_till_date)) AS i_53_agg,
    json_object_agg('Glass Dispensed - Total number of glasses dispensed - Ready made glasses - Driver- 54 ', jsonb_build_object('male', i_54_male, 'female', i_54_female, 'monthly_total', i_54_total, 'till_month_total', i_54_till_date)) AS i_54_agg,
    json_object_agg('Glass Dispensed - Total number of glasses dispensed - Ready made glasses - Others- 55 ', jsonb_build_object('male', i_55_male, 'female', i_55_female, 'monthly_total', i_55_total, 'till_month_total', i_55_till_date)) AS i_51_agg,
    json_object_agg('Glass Dispensed - Total number of glasses dispensed - Custom made glasses - Total- 56 ', jsonb_build_object('male', i_56_male, 'female', i_56_female, 'monthly_total', i_56_total, 'till_month_total', i_56_till_date)) AS i_56_agg,
    json_object_agg('Glass Dispensed - Total number of glasses dispensed - Custom made glasses - Driver- 57 ', jsonb_build_object('male', i_57_male, 'female', i_57_female, 'monthly_total', i_57_total, 'till_month_total', i_57_till_date)) AS i_57_agg,
    json_object_agg('Glass Dispensed - Total number of glasses dispensed - Custom made glasses - Others- 58 ', jsonb_build_object('male', i_58_male, 'female', i_58_female, 'monthly_total', i_58_total, 'till_month_total', i_58_till_date)) AS i_58_agg,
    json_object_agg('Glass Dispensed - Total number of glasses pending for delivery - Total- 59 ', jsonb_build_object('male', i_59_male, 'female', i_59_female, 'monthly_total', i_59_total, 'till_month_total', i_59_till_date)) AS i_59_agg,
    json_object_agg('Glass Dispensed - Total number of glasses pending for delivery - Driver- 60 ', jsonb_build_object('male', i_60_male, 'female', i_60_female, 'monthly_total', i_60_total, 'till_month_total', i_60_till_date)) AS i_60_agg,
    json_object_agg('Glass Dispensed - Total number of glasses pending for delivery - Others- 61 ', jsonb_build_object('male', i_61_male, 'female', i_61_female, 'monthly_total', i_61_total, 'till_month_total', i_61_till_date)) AS i_61_agg,
    json_object_agg('Glass Dispensed - Total number of glasses pending for delivery - Glasses with status In-process - Total- 62 ', jsonb_build_object('male', i_62_male, 'female', i_62_female, 'monthly_total', i_62_total, 'till_month_total', i_62_till_date)) AS i_62_agg,
    json_object_agg('Glass Dispensed - Total number of glasses pending for delivery - Glasses with status In-process - Driver- 63 ', jsonb_build_object('male', i_63_male, 'female', i_63_female, 'monthly_total', i_63_total, 'till_month_total', i_63_till_date)) AS i_63_agg,
    json_object_agg('Glass Dispensed - Total number of glasses pending for delivery - Glasses with status In-process - Others- 64 ', jsonb_build_object('male', i_64_male, 'female', i_64_female, 'monthly_total', i_64_total, 'till_month_total', i_64_till_date)) AS i_64_agg,
    json_object_agg('Glass Dispensed - Total number of glasses pending for delivery - Glasses with status Ready - Total- 65 ', jsonb_build_object('male', i_65_male, 'female', i_65_female, 'monthly_total', i_65_total, 'till_month_total', i_65_till_date)) AS i_65_agg,
    json_object_agg('Glass Dispensed - Total number of glasses pending for delivery - Glasses with status Ready - Driver- 66 ', jsonb_build_object('male', i_66_male, 'female', i_66_female, 'monthly_total', i_66_total, 'till_month_total', i_66_till_date)) AS i_66_agg,
    json_object_agg('Glass Dispensed - Total number of glasses pending for delivery - Glasses with status Ready - Others- 67 ', jsonb_build_object('male', i_67_male, 'female', i_67_female, 'monthly_total', i_67_total, 'till_month_total', i_67_till_date)) AS i_67_agg,
    json_object_agg('Referral - Total number of referrals made - Total- 68 ', jsonb_build_object('male', i_68_male, 'female', i_68_female, 'monthly_total', i_68_total, 'till_month_total', i_68_till_date)) AS i_68_agg,
    json_object_agg('Referral - Total number of referrals made - Driver- 69 ', jsonb_build_object('male', i_69_male, 'female', i_69_female, 'monthly_total', i_69_total, 'till_month_total', i_69_till_date)) AS i_69_agg,
    json_object_agg('Referral - Total number of referrals made - Others- 70 ', jsonb_build_object('male', i_70_male, 'female', i_70_female, 'monthly_total', i_70_total, 'till_month_total', i_70_till_date)) AS i_70_agg,
    json_object_agg('Referral - Cataract - Total- 71 ', jsonb_build_object('male', i_71_male, 'female', i_71_female, 'monthly_total', i_71_total, 'till_month_total', i_71_till_date)) AS i_71_agg,
    json_object_agg('Referral - Cataract - Driver- 72 ', jsonb_build_object('male', i_72_male, 'female', i_72_female, 'monthly_total', i_72_total, 'till_month_total', i_72_till_date)) AS i_72_agg,
    json_object_agg('Referral - Cataract - Others- 73 ', jsonb_build_object('male', i_73_male, 'female', i_73_female, 'monthly_total', i_73_total, 'till_month_total', i_73_till_date)) AS i_73_agg,
    json_object_agg('Referral - Others - Total- 74 ', jsonb_build_object('male', i_74_male, 'female', i_74_female, 'monthly_total', i_74_total, 'till_month_total', i_74_till_date)) AS i_74_agg,
    json_object_agg('Referral - Others - Driver- 75 ', jsonb_build_object('male', i_75_male, 'female', i_75_female, 'monthly_total', i_75_total, 'till_month_total', i_75_till_date)) AS i_75_agg,
    json_object_agg('Referral - Others - Others- 76 ', jsonb_build_object('male', i_76_male, 'female', i_76_female, 'monthly_total', i_76_total, 'till_month_total', i_76_till_date)) AS i_76_agg,
     json_object_agg('Glass Dispensed - Total number of glasses dispensed - R2C glasses - Total- 77 ', jsonb_build_object('male', i_77_male, 'female', i_77_female, 'monthly_total', i_77_total, 'till_month_total', i_77_till_date)) AS i_77_agg,
    json_object_agg('Glass Dispensed - Total number of glasses dispensed - R2C glasses - Driver- 78 ', jsonb_build_object('male', i_78_male, 'female', i_78_female, 'monthly_total', i_78_total, 'till_month_total', i_78_till_date)) AS i_78_agg
       FROM (
            SELECT
                mpr_month,
                mpr_year,
                coalesce(sum(i_1_achive_male),0) AS i_1_male,
                coalesce(sum(i_1_achive_female),0) AS i_1_female,
                coalesce(sum(i_1_achive_total),0) AS i_1_total,
                coalesce(sum(i_1_achive_till_date),0) AS i_1_till_date,
                sum(i_2_achive_male) AS i_2_male,
                sum(i_2_achive_female) AS i_2_female,
                sum(i_2_achive_total) AS i_2_total,
                sum(i_2_achive_till_date) AS i_2_till_date,
                sum(i_3_achive_male) AS i_3_male,
                sum(i_3_achive_female) AS i_3_female,
                sum(i_3_achive_total) AS i_3_total,
                sum(i_3_achive_till_date) AS i_3_till_date,
                sum(i_4_achive_male) AS i_4_male,
                sum(i_4_achive_female) AS i_4_female,
                sum(i_4_achive_total) AS i_4_total,
                sum(i_4_achive_till_date) AS i_4_till_date,
                sum(i_5_achive_male) AS i_5_male,
                sum(i_5_achive_female) AS i_5_female,
                sum(i_5_achive_total) AS i_5_total,
                sum(i_5_achive_till_date) AS i_5_till_date,
                sum(i_6_achive_male) AS i_6_male,
                sum(i_6_achive_female) AS i_6_female,
                sum(i_6_achive_total) AS i_6_total,
                sum(i_6_achive_till_date) AS i_6_till_date,
                sum(i_7_achive_male) AS i_7_male,
                sum(i_7_achive_female) AS i_7_female,
                sum(i_7_achive_total) AS i_7_total,
                sum(i_7_achive_till_date) AS i_7_till_date,
                sum(i_8_achive_male) AS i_8_male,
                sum(i_8_achive_female) AS i_8_female,
                sum(i_8_achive_total) AS i_8_total,
                sum(i_8_achive_till_date) AS i_8_till_date,
                sum(i_9_achive_male) AS i_9_male,
                sum(i_9_achive_female) AS i_9_female,
                sum(i_9_achive_total) AS i_9_total,
                sum(i_9_achive_till_date) AS i_9_till_date,
                sum(i_10_achive_male) AS i_10_male,
                sum(i_10_achive_female) AS i_10_female,
                sum(i_10_achive_total) AS i_10_total,
                sum(i_10_achive_till_date) AS i_10_till_date,
                sum(i_11_achive_male) AS i_11_male,
                sum(i_11_achive_female) AS i_11_female,
                sum(i_11_achive_total) AS i_11_total,
                sum(i_11_achive_till_date) AS i_11_till_date,
                sum(i_12_achive_male) AS i_12_male,
                sum(i_12_achive_female) AS i_12_female,
                sum(i_12_achive_total) AS i_12_total,
                sum(i_12_achive_till_date) AS i_12_till_date,
                sum(i_13_achive_male) AS i_13_male,
                sum(i_13_achive_female) AS i_13_female,
                sum(i_13_achive_total) AS i_13_total,
                sum(i_13_achive_till_date) AS i_13_till_date,
                sum(i_14_achive_male) AS i_14_male,
                sum(i_14_achive_female) AS i_14_female,
                sum(i_14_achive_total) AS i_14_total,
                sum(i_14_achive_till_date) AS i_14_till_date,
                sum(i_15_achive_male) AS i_15_male,
                sum(i_15_achive_female) AS i_15_female,
                sum(i_15_achive_total) AS i_15_total,
                sum(i_15_achive_till_date) AS i_15_till_date,
                sum(i_16_achive_male) AS i_16_male,
                sum(i_16_achive_female) AS i_16_female,
                sum(i_16_achive_total) AS i_16_total,
                sum(i_16_achive_till_date) AS i_16_till_date,
                sum(i_17_achive_male) AS i_17_male,
                sum(i_17_achive_female) AS i_17_female,
                sum(i_17_achive_total) AS i_17_total,
                sum(i_17_achive_till_date) AS i_17_till_date,
                sum(i_18_achive_male) AS i_18_male,
                sum(i_18_achive_female) AS i_18_female,
                sum(i_18_achive_total) AS i_18_total,
                sum(i_18_achive_till_date) AS i_18_till_date,
                sum(i_19_achive_male) AS i_19_male,
                sum(i_19_achive_female) AS i_19_female,
                sum(i_19_achive_total) AS i_19_total,
                sum(i_19_achive_till_date) AS i_19_till_date,
                sum(i_20_achive_male) AS i_20_male,
                sum(i_20_achive_female) AS i_20_female,
                sum(i_20_achive_total) AS i_20_total,
                sum(i_20_achive_till_date) AS i_20_till_date,
                sum(i_21_achive_male) AS i_21_male,
                sum(i_21_achive_female) AS i_21_female,
                sum(i_21_achive_total) AS i_21_total,
                sum(i_21_achive_till_date) AS i_21_till_date,
                sum(i_22_achive_male) AS i_22_male,
                sum(i_22_achive_female) AS i_22_female,
                sum(i_22_achive_total) AS i_22_total,
                sum(i_22_achive_till_date) AS i_22_till_date,
                sum(i_23_achive_male) AS i_23_male,
                sum(i_23_achive_female) AS i_23_female,
                sum(i_23_achive_total) AS i_23_total,
                sum(i_23_achive_till_date) AS i_23_till_date,
                sum(i_24_achive_male) AS i_24_male,
                sum(i_24_achive_female) AS i_24_female,
                sum(i_24_achive_total) AS i_24_total,
                sum(i_24_achive_till_date) AS i_24_till_date,
                sum(i_25_achive_male) AS i_25_male,
                sum(i_25_achive_female) AS i_25_female,
                sum(i_25_achive_total) AS i_25_total,
                sum(i_25_achive_till_date) AS i_25_till_date,
                sum(i_26_achive_male) AS i_26_male,
                sum(i_26_achive_female) AS i_26_female,
                sum(i_26_achive_total) AS i_26_total,
                sum(i_26_achive_till_date) AS i_26_till_date,
                sum(i_27_achive_male) AS i_27_male,
                sum(i_27_achive_female) AS i_27_female,
                sum(i_27_achive_total) AS i_27_total,
                sum(i_27_achive_till_date) AS i_27_till_date,
                sum(i_28_achive_male) AS i_28_male,
                sum(i_28_achive_female) AS i_28_female,
                sum(i_28_achive_total) AS i_28_total,
                sum(i_28_achive_till_date) AS i_28_till_date,
                sum(i_29_achive_male) AS i_29_male,
                sum(i_29_achive_female) AS i_29_female,
                sum(i_29_achive_total) AS i_29_total,
                sum(i_29_achive_till_date) AS i_29_till_date,
    sum(i_30_achive_male) as i_30_male,sum(i_30_achive_female) as i_30_female,sum(i_30_achive_total) as i_30_total,sum(i_30_achive_till_date) as i_30_till_date,
    sum(i_31_achive_male) as i_31_male,sum(i_31_achive_female) as i_31_female,sum(i_31_achive_total) as i_31_total,sum(i_31_achive_till_date) as i_31_till_date,
    sum(i_32_achive_male) as i_32_male,sum(i_32_achive_female) as i_32_female,sum(i_32_achive_total) as i_32_total,sum(i_32_achive_till_date) as i_32_till_date,
    sum(i_33_achive_male) as i_33_male,sum(i_33_achive_female) as i_33_female,sum(i_33_achive_total) as i_33_total,sum(i_33_achive_till_date) as i_33_till_date,
    sum(i_34_achive_male) as i_34_male,sum(i_34_achive_female) as i_34_female,sum(i_34_achive_total) as i_34_total,sum(i_34_achive_till_date) as i_34_till_date,
    sum(i_35_achive_male) as i_35_male,sum(i_35_achive_female) as i_35_female,sum(i_35_achive_total) as i_35_total,sum(i_35_achive_till_date) as i_35_till_date,
    sum(i_36_achive_male) as i_36_male,sum(i_36_achive_female) as i_36_female,sum(i_36_achive_total) as i_36_total,sum(i_36_achive_till_date) as i_36_till_date,
    sum(i_37_achive_male) as i_37_male,sum(i_37_achive_female) as i_37_female,sum(i_37_achive_total) as i_37_total,sum(i_37_achive_till_date) as i_37_till_date,
    sum(i_38_achive_male) as i_38_male,sum(i_38_achive_female) as i_38_female,sum(i_38_achive_total) as i_38_total,sum(i_38_achive_till_date) as i_38_till_date,
    sum(i_39_achive_male) as i_39_male,sum(i_39_achive_female) as i_39_female,sum(i_39_achive_total) as i_39_total,sum(i_39_achive_till_date) as i_39_till_date,
    sum(i_40_achive_male) as i_40_male,sum(i_40_achive_female) as i_40_female,sum(i_40_achive_total) as i_40_total,sum(i_40_achive_till_date) as i_40_till_date,
    sum(i_41_achive_male) as i_41_male,sum(i_41_achive_female) as i_41_female,sum(i_41_achive_total) as i_41_total,sum(i_41_achive_till_date) as i_41_till_date,
    sum(i_42_achive_male) as i_42_male,sum(i_42_achive_female) as i_42_female,sum(i_42_achive_total) as i_42_total,sum(i_42_achive_till_date) as i_42_till_date,
    sum(i_43_achive_male) as i_43_male,sum(i_43_achive_female) as i_43_female,sum(i_43_achive_total) as i_43_total,sum(i_43_achive_till_date) as i_43_till_date,
    sum(i_44_achive_male) as i_44_male,sum(i_44_achive_female) as i_44_female,sum(i_44_achive_total) as i_44_total,sum(i_44_achive_till_date) as i_44_till_date,
    sum(i_45_achive_male) as i_45_male,sum(i_45_achive_female) as i_45_female,sum(i_45_achive_total) as i_45_total,sum(i_45_achive_till_date) as i_45_till_date,
    sum(i_46_achive_male) as i_46_male,sum(i_46_achive_female) as i_46_female,sum(i_46_achive_total) as i_46_total,sum(i_46_achive_till_date) as i_46_till_date,
    sum(i_47_achive_male) as i_47_male,sum(i_47_achive_female) as i_47_female,sum(i_47_achive_total) as i_47_total,sum(i_47_achive_till_date) as i_47_till_date,
    sum(i_48_achive_male) as i_48_male,sum(i_48_achive_female) as i_48_female,sum(i_48_achive_total) as i_48_total,sum(i_48_achive_till_date) as i_48_till_date,
    sum(i_49_achive_male) as i_49_male,sum(i_49_achive_female) as i_49_female,sum(i_49_achive_total) as i_49_total,sum(i_49_achive_till_date) as i_49_till_date,
    sum(i_50_achive_male) as i_50_male,sum(i_50_achive_female) as i_50_female,sum(i_50_achive_total) as i_50_total,sum(i_50_achive_till_date) as i_50_till_date,
    sum(i_51_achive_male) as i_51_male,sum(i_51_achive_female) as i_51_female,sum(i_51_achive_total) as i_51_total,sum(i_51_achive_till_date) as i_51_till_date,
    sum(i_52_achive_male) as i_52_male,sum(i_52_achive_female) as i_52_female,sum(i_52_achive_total) as i_52_total,sum(i_52_achive_till_date) as i_52_till_date,
    sum(i_53_achive_male) as i_53_male,sum(i_53_achive_female) as i_53_female,sum(i_53_achive_total) as i_53_total,sum(i_53_achive_till_date) as i_53_till_date,
    sum(i_54_achive_male) as i_54_male,sum(i_54_achive_female) as i_54_female,sum(i_54_achive_total) as i_54_total,sum(i_54_achive_till_date) as i_54_till_date,
    sum(i_55_achive_male) as i_55_male,sum(i_55_achive_female) as i_55_female,sum(i_55_achive_total) as i_55_total,sum(i_55_achive_till_date) as i_55_till_date,
    sum(i_56_achive_male) as i_56_male,sum(i_56_achive_female) as i_56_female,sum(i_56_achive_total) as i_56_total,sum(i_56_achive_till_date) as i_56_till_date,
    sum(i_57_achive_male) as i_57_male,sum(i_57_achive_female) as i_57_female,sum(i_57_achive_total) as i_57_total,sum(i_57_achive_till_date) as i_57_till_date,
    sum(i_58_achive_male) as i_58_male,sum(i_58_achive_female) as i_58_female,sum(i_58_achive_total) as i_58_total,sum(i_58_achive_till_date) as i_58_till_date,
    sum(i_59_achive_male) as i_59_male,sum(i_59_achive_female) as i_59_female,sum(i_59_achive_total) as i_59_total,sum(i_59_achive_till_date) as i_59_till_date,
    sum(i_60_achive_male) as i_60_male,sum(i_60_achive_female) as i_60_female,sum(i_60_achive_total) as i_60_total,sum(i_60_achive_till_date) as i_60_till_date,
    sum(i_61_achive_male) as i_61_male,sum(i_61_achive_female) as i_61_female,sum(i_61_achive_total) as i_61_total,sum(i_61_achive_till_date) as i_61_till_date,
    sum(i_62_achive_male) as i_62_male,sum(i_62_achive_female) as i_62_female,sum(i_62_achive_total) as i_62_total,sum(i_62_achive_till_date) as i_62_till_date,
    sum(i_63_achive_male) as i_63_male,sum(i_63_achive_female) as i_63_female,sum(i_63_achive_total) as i_63_total,sum(i_63_achive_till_date) as i_63_till_date,
    sum(i_64_achive_male) as i_64_male,sum(i_64_achive_female) as i_64_female,sum(i_64_achive_total) as i_64_total,sum(i_64_achive_till_date) as i_64_till_date,
    sum(i_65_achive_male) as i_65_male,sum(i_65_achive_female) as i_65_female,sum(i_65_achive_total) as i_65_total,sum(i_65_achive_till_date) as i_65_till_date,
    sum(i_66_achive_male) as i_66_male,sum(i_66_achive_female) as i_66_female,sum(i_66_achive_total) as i_66_total,sum(i_66_achive_till_date) as i_66_till_date,
    sum(i_67_achive_male) as i_67_male,sum(i_67_achive_female) as i_67_female,sum(i_67_achive_total) as i_67_total,sum(i_67_achive_till_date) as i_67_till_date,
    sum(i_68_achive_male) as i_68_male,sum(i_68_achive_female) as i_68_female,sum(i_68_achive_total) as i_68_total,sum(i_68_achive_till_date) as i_68_till_date,
    sum(i_69_achive_male) as i_69_male,sum(i_69_achive_female) as i_69_female,sum(i_69_achive_total) as i_69_total,sum(i_69_achive_till_date) as i_69_till_date,
    sum(i_70_achive_male) as i_70_male,sum(i_70_achive_female) as i_70_female,sum(i_70_achive_total) as i_70_total,sum(i_70_achive_till_date) as i_70_till_date,
    sum(i_71_achive_male) as i_71_male,sum(i_71_achive_female) as i_71_female,sum(i_71_achive_total) as i_71_total,sum(i_71_achive_till_date) as i_71_till_date,
    sum(i_72_achive_male) as i_72_male,sum(i_72_achive_female) as i_72_female,sum(i_72_achive_total) as i_72_total,sum(i_72_achive_till_date) as i_72_till_date,
    sum(i_73_achive_male) as i_73_male,sum(i_73_achive_female) as i_73_female,sum(i_73_achive_total) as i_73_total,sum(i_73_achive_till_date) as i_73_till_date,
    sum(i_74_achive_male) as i_74_male,sum(i_74_achive_female) as i_74_female,sum(i_74_achive_total) as i_74_total,sum(i_74_achive_till_date) as i_74_till_date,
    sum(i_75_achive_male) as i_75_male,sum(i_75_achive_female) as i_75_female,sum(i_75_achive_total) as i_75_total,sum(i_75_achive_till_date) as i_75_till_date,
    sum(i_76_achive_male) as i_76_male,sum(i_76_achive_female) as i_76_female,sum(i_76_achive_total) as i_76_total,sum(i_76_achive_till_date) as i_76_till_date,
    sum(i_77_achive_male) as i_77_male,sum(i_77_achive_female) as i_77_female,sum(i_77_achive_total) as i_77_total,sum(i_77_achive_till_date) as i_77_till_date,
    sum(i_78_achive_male) as i_78_male,sum(i_78_achive_female) as i_78_female,sum(i_78_achive_total) as i_78_total,sum(i_78_achive_till_date) as i_78_till_date
                FROM
                reports_truckermpr where 1=1 {filter_conditions}
            GROUP BY
                mpr_month,
                mpr_year
        ) AS x

    ) AS y;
    """) 
        vision_center_open_during_month = return_sql_results(f"""
        select coalesce(count(distinct(to_char(app_created_at,'YYYY-MM-DD'))),0) as achive_total from sims_patient
        where 1=1 and vision_center_id != 0 {vc_open_mon_filter_conditions}
        """)
        if mpr_data:
            mpr_value = mpr_data[0]
            if mpr_value[1] != None and vision_center_open_during_month[0][0] != None:
                mpr_value[1]['1b. Total number of days the Vision Centre was open during the reporting month- 2 ']['monthly_total'] = vision_center_open_during_month[0][0]
                mpr_value[1]['1b. Total number of days the Vision Centre was open during the reporting month- 2 ']['till_month_total'] = vision_center_open_during_month[0][0]
            target_mpr_value = target_mpr_value[0][0]
    return render(request, 'reports/truckers_monthly_report.html', locals())

# ****************************************************************************
# Excel function for export
# ****************************************************************************

def generate_export_excel(report_title, data_query_list, table_headers, custom_export_headers, sheet_names):
    from django.conf import settings
    excelWriter = None
    try:
        # Excel path
        rows_in_chunk = 20000
        db_name = settings.DATABASES['default'].get('NAME')
        username = settings.DATABASES['default'].get('USER')
        password = settings.DATABASES['default'].get('PASSWORD')
        hostname = settings.DATABASES['default'].get('HOST')
        # IMPORTANT : Please ensure @ not used in the username and password. This will affect the connection string
        conn_str = "postgresql+psycopg2://" + username + ":" + password + \
            "@" + hostname + "/" + db_name + "?client_encoding=UTF8"
        MEDIA_ROOT = str(settings.MEDIA_ROOT) + '/temp_export_data/'
        import datetime
        file_name = re.sub("(\s)|(')|(-)|(\()|(\))|(’)", '_', report_title)
        folder_file_name = file_name + "_" + \
            datetime.datetime.today().strftime("%d%m%y%H%M%S%f") + ".xlsx"
        attachment_name = file_name + "_" + \
            datetime.datetime.today().strftime("%d%m%y%H%M") + ".xlsx"
        excelWriter = pd.ExcelWriter(MEDIA_ROOT+folder_file_name, mode='w', date_format='DD/MM/YYYY')
        for idx, sql_query in enumerate(data_query_list):
            # sheetname is limited to 30 chars othewise excel gives an error while opening
            sht_name = re.sub("(')|\s","_",sheet_names[idx][0:30])
            write_to_excel_from_normalized_table(
                conn_str, sql_query, table_headers[idx], custom_export_headers[idx], rows_in_chunk, sht_name, excelWriter)
    finally:
        if excelWriter:
            excelWriter.close()  # Corrected save method
    if os.path.exists(MEDIA_ROOT+folder_file_name):
        excel = open(MEDIA_ROOT+folder_file_name, "rb")
        data = excel.read()
        response = HttpResponse(
            data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s' % attachment_name
        os.remove(MEDIA_ROOT+folder_file_name)
        return response


def write_to_excel_from_normalized_table(conn_str, sql_query, headers_list, custom_export_header, rows_in_chunk, sheetname, excelWriter):
    # read from sql table into the pandas dataframe in chucks, this returns a list of dataframes - one for each chunk
    # create headers rows and write to excel sheet
    header_row_count = 1
    row_data = {}
    if headers_list:
        headers_list[0].pop(0)
    if custom_export_header:
        # custom export header is used to add custom header info - mostly multi level headers like the child classification report
        for i in custom_export_header:
            row_data.update({tuple(i): {}})
        header_row_count = len(custom_export_header[0])
        header_df = pd.DataFrame.from_dict(row_data)
    else:
        # when custom export header is None, then add the report headers as the export excel headers
        col_list = []
        for i in headers_list[0]:
            # remove any <br/> added in the header as formatting on the html pages
            header_text = i.get('label', '').replace('<br/>', '')
            col_list.append(header_text)
        header_df = pd.DataFrame([], columns=col_list)
        header_row_count = 1
    normalized_df_list = pd.read_sql_query(
        sql_query, con=conn_str, chunksize=rows_in_chunk)
    start_row = header_row_count
    # set header to False indicating not to add the header data/row
    header_info = False
    df_count = 0
    # index_heading = 'S.No'
    try:
        for chunk_df in normalized_df_list:
            chunk_df.index += (df_count * rows_in_chunk)+1
            df_count = df_count + 1
            chunk_df.to_excel(excelWriter, sheet_name=sheetname,
                            startrow=start_row, header=header_info)
            # add the dataframe size (rows read from table/ chunk size) and header rows count (1 for first iteration and 0 for further iterations)
            start_row = start_row + chunk_df.shape[0] #+ header_row_count
            # set flags to indicate first dataframe is written to excel
            # set header row count used in the calcuation of start row to 0 as no further header rows will be added
            header_row_count = 0
            # unset flag for header info to false as no further header details will be written to sheet
            header_info = False
        # add the header row rowas at row 0 - insert it as a new data frame with empty data and the header rows
        header_df.to_excel(excelWriter, sheet_name=sheetname,startrow=0)
    except Exception as e:
        df_count = 0
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_stack = repr(traceback.format_exception(
            exc_type, exc_value, exc_traceback))
        logger.error(error_stack)
        raise

def get_cholas_meta(r_slug):
    if r_slug == 'donor-report':
        sql_query =   {"sql_query": "select to_char(p.camp_date::date,'DD-MM-YYYY'),p.patient_unique_id,p.name,p.age,p.gender,coalesce(contact_1,contact_2),(case when p.address is null or p.address = '' then '-' else p.address end),p.state_name,p.district_name,(case when p.aadhar_pan_no is null or p.aadhar_pan_no = '' then '-' else p.aadhar_pan_no end),p.residence_type_name,p.job,coalesce(p.drivers_license_no, '-'),coalesce(to_char(p.renewal_date,'DD-MM-YYYY'), '-'),p.qualification,p.no_of_months_employed_in_a_year,coalesce(p.time_since_driving, '-'),coalesce(p.type_of_vehicle, '-'),coalesce(p.type_of_route, '-'),p.vechicle_insurance,p.monthly_income,p.life_insurance,p.health_insurance,p.how_do_you_know_about_camp,coalesce(scr.unaided_distance_re, '-'),coalesce(scr.unaided_near_re, '-'),coalesce(scr.aided_distance_re, '-'),coalesce(scr.aided_near_re, '-'),coalesce(scr.pinhole_distance_re, '-'),coalesce(scr.pinhole_near_re, '-'),coalesce(scr.color_re, '-'),coalesce(scr.unaided_distance_le, '-'),coalesce(scr.unaided_near_le, '-'),coalesce(scr.aided_distance_le, '-'),coalesce(scr.aided_near_le, '-'),coalesce(scr.pinhole_distance_le, '-'),coalesce(scr.pinhole_near_le, '-'),coalesce(scr.color_le, '-'),coalesce(scr.diabetes, '-'), coalesce(scr.hypertension, '-'), coalesce(scr.smoke, '-'), coalesce(scr.alcohol, '-'),coalesce(scr.eye_examination, '-'), coalesce(scr.seeing_distant_objects, '-'), scr.judging_distance_while_driving, scr.traffic_colors, scr.seeing_while_night_driving,scr.wear_glasses_ever, scr.wearing_glasses_currently,scr.first_aid_kit, scr.accident_while_driving_commercial_vehicle_before, coalesce(scr.accident_vehicle_in_last_twelve_months, '-'),coalesce(scr.are_you_happy_with_your_profession, '-'),coalesce(scr.if_you_are_happy_specify_in_what_way, '-'),scr.salary_calculated,coalesce(scr.owner_holding_amount, '-'),coalesce(scr.non_working_months, '-'),coalesce(scr.what_do_non_working_months, '-'), coalesce(scr.alter_employment, '-'),COALESCE(CAST(scr.learn_alter_livelihood_skill AS text), '-') AS result_column,coalesce(scr.family_support_financially, '-'),p.partner_name,p.camp_name from dash_repo_patient_basic_info_view p left join dash_repo_screening_info_view scr on p.patient_uuid = scr.patient_uuid where 1=1 and camp_id is not null @@from_date_filter @@to_date_filter @@state_filter @@district_filter @@model_type_filter @@donor_name_filter @@hospital_name_filter @@LIMITS", "count_query": "select count(x) FROM (select p.camp_date,p.patient_unique_id,p.name,p.age,p.gender,coalesce(contact_1,contact_2),p.address,p.state_name,p.district_name,p.aadhar_pan_no,p.residence_type_name,p.job,p.drivers_license_no,p.renewal_date,p.qualification,p.no_of_months_employed_in_a_year,p.time_since_driving,p.type_of_vehicle,p.type_of_route,p.vechicle_insurance,p.monthly_income,p.life_insurance,p.health_insurance,p.how_do_you_know_about_camp,scr.unaided_distance_re,scr.unaided_near_re,scr.aided_distance_re,scr.aided_near_re,scr.pinhole_distance_re,scr.pinhole_near_re,scr.color_re,scr.unaided_distance_le,scr.unaided_near_le,scr.aided_distance_le,scr.aided_near_le,scr.pinhole_distance_le,scr.pinhole_near_le,scr.color_le,scr.diabetes, scr.hypertension, scr.smoke, scr.alcohol,scr.eye_examination, scr.seeing_distant_objects, scr.judging_distance_while_driving, scr.traffic_colors, scr.seeing_while_night_driving,scr.wear_glasses_ever, scr.wearing_glasses_currently,scr.first_aid_kit, scr.accident_while_driving_commercial_vehicle_before, scr.accident_vehicle_in_last_twelve_months,scr.are_you_happy_with_your_profession,scr.if_you_are_happy_specify_in_what_way,scr.salary_calculated,scr.owner_holding_amount,scr.non_working_months,scr.what_do_non_working_months, scr.alter_employment,scr.learn_alter_livelihood_skill,scr.family_support_financially,p.partner_name,p.camp_name from dash_repo_patient_basic_info_view p left join dash_repo_screening_info_view scr on p.patient_uuid = scr.patient_uuid where 1=1 and camp_id is not null @@from_date_filter @@to_date_filter @@state_filter @@district_filter @@model_type_filter @@donor_name_filter @@hospital_name_filter) as x", "default_sort": {"sort_field ": " ", "sort_order ": "asc"}}
        header = [[{"label": "S.No", "colspan": 0, "rowspan": 0},{"label": "Camp/Hub Date", "colspan": 0, "rowspan": 0}, {"label": "UID", "colspan": 0, "rowspan": 0}, {"label": "Name", "colspan": 0, "rowspan": 0}, {"label": "Age", "colspan": 0, "rowspan": 0}, {"label": "Gender", "colspan": 0, "rowspan": 0}, {"label": "Contact No. (+91)", "colspan": 0, "rowspan": 0}, {"label": "Address", "colspan": 0, "rowspan": 0}, {"label": "State", "colspan": 0, "rowspan": 0}, {"label": "District", "colspan": 0, "rowspan": 0}, {"label": "Aadhaar No", "colspan": 0, "rowspan": 0}, {"label": "Residence Type", "colspan": 0, "rowspan": 0}, {"label": "Type of job", "colspan": 0, "rowspan": 0}, {"label": "Driver License<br/>No", "colspan": 0, "rowspan": 0}, {"label": "Renewal Date", "colspan": 0, "rowspan": 0}, {"label": "Educational<br/>qualification", "colspan": 0, "rowspan": 0}, {"label": "No of months Employed<br/>in a year", "colspan": 0, "rowspan": 0}, {"label": "Time since<br/>driving", "colspan": 0, "rowspan": 0}, {"label": "Vehicle", "colspan": 0, "rowspan": 0}, {"label": "Route", "colspan": 0, "rowspan": 0}, {"label": "Vehicle<br/>Insurance", "colspan": 0, "rowspan": 0}, {"label": "Monthly Income", "colspan": 0, "rowspan": 0}, {"label": "Life<br/>Insurance", "colspan": 0, "rowspan": 0}, {"label": "Health<br/>Insurance", "colspan": 0, "rowspan": 0}, {"label": "how you came<br/>to know about<br/>the camp/hub", "colspan": 0, "rowspan": 0}, {"label": "UnAided<br/>Distance(RE)", "colspan": 0, "rowspan": 0}, {"label": "UnAided<br/>Near(RE)", "colspan": 0, "rowspan": 0}, {"label": "Aided<br/>Distance(RE)", "colspan": 0, "rowspan": 0}, {"label": "Aided<br/>Near(RE)", "colspan": 0, "rowspan": 0}, {"label": "Pinhole<br/>Distance(RE)", "colspan": 0, "rowspan": 0}, {"label": "Pinhole<br/>Near(RE)", "colspan": 0, "rowspan": 0}, {"label": "Color(RE)", "colspan": 0, "rowspan": 0}, {"label": "UnAided<br/>Distance(LE)", "colspan": 0, "rowspan": 0}, {"label": "UnAided<br/>Near(LE)", "colspan": 0, "rowspan": 0}, {"label": "Aided<br/>Distance(LE)", "colspan": 0, "rowspan": 0}, {"label": "Aided Near(LE)", "colspan": 0, "rowspan": 0}, {"label": "Pinhole Distance(LE)", "colspan": 0, "rowspan": 0}, {"label": "Pinhole Near(LE)", "colspan": 0, "rowspan": 0}, {"label": "Color(LE)", "colspan": 0, "rowspan": 0}, {"label": "Diabetes", "colspan": 0, "rowspan": 0}, {"label": "Hyper Tension", "colspan": 0, "rowspan": 0}, {"label": "Smoke", "colspan": 0, "rowspan": 0}, {"label": "Alcohol", "colspan": 0, "rowspan": 0}, {"label": "Have you ever<br/>had eye examination", "colspan": 0, "rowspan": 0}, {"label": "Do you have any difficulty in seeing<br/>distant object", "colspan": 0, "rowspan": 0}, {"label": "Do you have any difficulty in judging<br/>distance while driving", "colspan": 0, "rowspan": 0}, {"label": "Are you able to identify the traffic<br/>light colours easily?", "colspan": 0, "rowspan": 0}, {"label": "Do you have any<br/>difficulty in seeing<br/>while night driving?", "colspan": 0, "rowspan": 0}, {"label": "Have you been<br/>advised to wear<br/>glasses ever?", "colspan": 0, "rowspan": 0}, {"label": "Are you using<br/>any glasses<br/>currently", "colspan": 0, "rowspan": 0}, {"label": "Do you have<br/>proper first-aid<br/>kit in you truck?", "colspan": 0, "rowspan": 0}, {"label": "Have you ever involved<br/>in road accident while driving<br/>your commercial vehicle before", "colspan": 0, "rowspan": 0}, {"label": "Have you been involved<br/>in road accident while<br/>driving your commercial<br/>vehicle in last<br/>twelve months", "colspan": 0, "rowspan": 0}, {"label": "Are you happy with<br/>your profession?", "colspan": 0, "rowspan": 0}, {"label": "If you are happy, specify in what way?", "colspan": 0, "rowspan": 0}, {"label": "On what basis you salary Is calculated?<br/>1. Monthly 2. Weekly<br/>3. Daily 4. Per Trip<br/>5. Distance", "colspan": 0, "rowspan": 0}, {"label": "Is your owner holding back any money please specify", "colspan": 0, "rowspan": 0}, {"label": "which are the months that you are unemployed", "colspan": 0, "rowspan": 0}, {"label": "What do you do when you are unemployed", "colspan": 0, "rowspan": 0}, {"label": "Are you equipped<br/>with any alternate<br/>employment", "colspan": 0, "rowspan": 0}, {"label": "If No, will you<br/>be willing to learn<br/>an alternative livelihood skill", "colspan": 0, "rowspan": 0}, {"label": "Do your family<br/>members (Spouse / Children / Siblings) <br/>earn and support you financially", "colspan": 0, "rowspan": 0}, {"label": "Hospital Name", "colspan": 0, "rowspan": 0}, {"label": "Camp Name", "colspan": 0, "rowspan": 0}]]
    if r_slug == 'patient-summary-report':
        sql_query = {"sql_query": "select p.patient_unique_id,p.name,p.age,p.gender,p.contact_1,(case when p.contact_2 is null or p.contact_2 = '' then '-' else p.contact_2 end),(case when p.address is null or p.address = '' then '-' else p.address end),p.state_name,p.district_name,(case when p.aadhar_pan_no is null or p.aadhar_pan_no = '' then '-' else p.aadhar_pan_no end),p.job,coalesce(p.drivers_license_no, '-'),coalesce(to_char(p.renewal_date,'DD-MM-YYYY'), '-'),coalesce(p.time_since_driving, '-'),p.qualification,p.no_of_months_employed_in_a_year,p.residence_type_name,coalesce(p.type_of_vehicle, '-'),coalesce(p.type_of_route, '-'),p.monthly_income,p.life_insurance,p.vechicle_insurance,p.health_insurance,p.how_do_you_know_about_camp,scr.code_description,scr.blood_pressure,scr.blood_sugar,scr.weight,scr.height,scr.total_family_members,scr.salary_calculated,coalesce(scr.owner_holding_amount, '-'),coalesce(scr.non_working_months, '-'),scr.what_do_non_working_months,scr.alter_employment,COALESCE(CAST(scr.learn_alter_livelihood_skill AS text), '-') AS result_column,scr.family_support_financially,scr.medical_checkup_past_1_year,coalesce(scr.diabetes, '-'),coalesce((scr.when_was_it_diagnosed_years)::char,'-') as diabetes_diagnosed,coalesce(scr.insulin_dependent_or_non_insulin_dependent, '-') as insulin,COALESCE(CAST(scr.dosage_of_insulin AS text), '-') AS result_column,scr.hypertension,coalesce((scr.when_was_it_diagnosed_years)::char,'-') as diagnosed_hypertension,scr.medication_hypertension,scr.smoke,scr.alcohol,coalesce(scr.waist_circumference, '-'),coalesce(scr.physical_activity, '-'),coalesce(scr.family_history_of_diabetes, '-'),COALESCE(CAST(scr.duration_since_last_meal AS text), '-') AS result_column ,scr.cough_for_more_than_two_weeks,scr.night_sweats,scr.fever_for_more_than_2_weeks,scr.unexplained_weight_loss_or_loss_of_appetite,scr.eye_examination,scr.seeing_distant_objects,scr.judging_distance_while_driving,scr.traffic_colors,scr.seeing_while_night_driving,scr.wear_glasses_ever,scr.wearing_glasses_currently,scr.nearby_hospital,coalesce(scr.type_of_hospital,'-'),scr.accident_while_driving_commercial_vehicle_before,scr.accident_vehicle_in_last_twelve_months,scr.first_aid_kit,scr.are_you_happy_with_your_profession,coalesce(scr.if_you_are_happy_specify_in_what_way, '-'),coalesce(scr.unaided_distance_re, '-'),coalesce(scr.unaided_near_re, '-'),coalesce(scr.aided_distance_re, '-'),coalesce(scr.aided_near_re, '-'),coalesce(scr.pinhole_distance_re, '-'),coalesce(scr.pinhole_near_re, '-'),coalesce(scr.color_re, '-'),coalesce(scr.unaided_distance_le, '-'),coalesce(scr.unaided_near_le, '-'),coalesce(scr.aided_distance_le, '-'),coalesce(scr.aided_near_le, '-'),coalesce(scr.pinhole_distance_le, '-'),coalesce(scr.pinhole_near_le, '-'),coalesce(scr.color_le, '-'),coalesce(scr.treatment_for_refraction_name, ''),coalesce(scr.want_to_refer_1_yes_2_no, '-'),coalesce(scr.refer_for, '-'),coalesce(scr.refer_to, '-'),coalesce(gp.sph_distance_re, '-'),coalesce(gp.sph_near_re, '-'),coalesce(gp.cyl_distance_re, '-'),coalesce(gp.cyl_near_re, '-'),coalesce(gp.axis_distance_re, '-'),coalesce(gp.axis_near_re, '-'),coalesce(gp.va_distance_re, '-'),coalesce(gp.va_near_re, '-'),coalesce(gp.sph_distance_le, '-'),coalesce(gp.sph_near_le, '-'),coalesce(gp.cyl_distance_le, '-'),coalesce(gp.cyl_near_le, '-'),coalesce(gp.axis_distance_le, '-'),coalesce(gp.axis_near_le, '-'),coalesce(gp.va_distance_le, '-'),coalesce(gp.va_near_le, '-'),'-' AS R2CEligible,'-' as DeliverR2C,'-' as R2CRemark,'-' as R2C_SPH_RE,'-' as R2C_VA_RE,'-' as R2C_SPH_LE,'-' as R2C_VA_LE,coalesce(gp.spec_type, '-'),gp.has_the_glass_collected,gp.spec_status,coalesce(p.camp_location, '-'),coalesce(scr.username, '-'),coalesce(gp.glass_collecting_location, '-'),coalesce(gp.frame_size, '-'),coalesce(gp.frame_code, '-'),coalesce(gp.lens_type, '-'),coalesce(gp.type_of_coating, '-'),p.created_date,p.partner_name,p.feedback,p.model_type_name,coalesce(p.camp_name,p.vision_center_name),COALESCE(p.camp_id, p.vision_center_id) AS result_column,coalesce(p.camp_date, p.vc_created_date),coalesce(p.camp_location, '-'),coalesce(p.camp_address, '-'),coalesce(p.camp_village, '-'),coalesce(p.camp_block, '-'),coalesce(p.camp_state,'-'),coalesce(p.camp_district, '-'),coalesce(p.exe_gp, '-'),coalesce(p.exe_rs, '-'),coalesce(p.camp_opd, '-'),coalesce(p.camp_donor_name, p.vc_donor_name),coalesce(p.camp_donor_mobile_num, p.vc_don_mobile_number),coalesce(p.camp_co_name, '-'),coalesce(p.camp_co_mobile_no, '-') from dash_repo_patient_basic_info_view p left join dash_repo_screening_info_view scr on p.patient_uuid = scr.patient_uuid left join dash_repo_glass_prescription_view gp on gp.scr_uuid = scr.scr_uuid where 1=1  @@from_date_filter @@to_date_filter @@state_filter @@model_type_filter @@donor_name_filter @@hospital_name_filter  @@camp_name_filter @@gender_filter @@patient_id_filter @@patient_name_filter @@occupation_filter @@refractive_error_filter @@eye_problem_filter @@vc_name_filter @@LIMITS", "count_query": "select count(x) FROM (select p.patient_unique_id,p.name,p.age,p.gender,p.contact_1,(case when p.contact_2 is null or p.contact_2 = '' then '-' else p.contact_2 end),(case when p.address is null or p.address = '' then '-' else p.address end),p.state_name,p.district_name,(case when p.aadhar_pan_no is null or p.aadhar_pan_no = '' then '-' else p.aadhar_pan_no end),p.job,coalesce(p.drivers_license_no, '-'),coalesce(to_char(p.renewal_date,'DD-MM-YYYY'), '-'),coalesce(p.time_since_driving, '-'),p.qualification,p.no_of_months_employed_in_a_year,p.residence_type_name,coalesce(p.type_of_vehicle, '-'),coalesce(p.type_of_route, '-'),p.monthly_income,p.life_insurance,p.vechicle_insurance,p.health_insurance,p.how_do_you_know_about_camp,scr.code_description,scr.blood_pressure,scr.blood_sugar,scr.weight,scr.height,scr.total_family_members,scr.salary_calculated,coalesce(scr.owner_holding_amount, '-'),coalesce(scr.non_working_months, '-'),scr.what_do_non_working_months,scr.alter_employment,COALESCE(CAST(scr.learn_alter_livelihood_skill AS text), '-') AS result_column,scr.family_support_financially,scr.medical_checkup_past_1_year,coalesce(scr.diabetes, '-'),coalesce((scr.when_was_it_diagnosed_years)::char,'-') as diabetes_diagnosed,coalesce(scr.insulin_dependent_or_non_insulin_dependent, '-') as insulin,COALESCE(CAST(scr.dosage_of_insulin AS text), '-') AS result_column,scr.hypertension,coalesce((scr.when_was_it_diagnosed_years)::char,'-') as diagnosed_hypertension,scr.medication_hypertension,scr.smoke,scr.alcohol,coalesce(scr.waist_circumference, '-'),coalesce(scr.physical_activity, '-'),coalesce(scr.family_history_of_diabetes, '-'),COALESCE(CAST(scr.duration_since_last_meal AS text), '-') AS result_column ,scr.cough_for_more_than_two_weeks,scr.night_sweats,scr.fever_for_more_than_2_weeks,scr.unexplained_weight_loss_or_loss_of_appetite,scr.eye_examination,scr.seeing_distant_objects,scr.judging_distance_while_driving,scr.traffic_colors,scr.seeing_while_night_driving,scr.wear_glasses_ever,scr.wearing_glasses_currently,scr.nearby_hospital,coalesce(scr.type_of_hospital,'-'),scr.accident_while_driving_commercial_vehicle_before,scr.accident_vehicle_in_last_twelve_months,scr.first_aid_kit,scr.are_you_happy_with_your_profession,coalesce(scr.if_you_are_happy_specify_in_what_way, '-'),coalesce(scr.unaided_distance_re, '-'),coalesce(scr.unaided_near_re, '-'),coalesce(scr.aided_distance_re, '-'),coalesce(scr.aided_near_re, '-'),coalesce(scr.pinhole_distance_re, '-'),coalesce(scr.pinhole_near_re, '-'),coalesce(scr.color_re, '-'),coalesce(scr.unaided_distance_le, '-'),coalesce(scr.unaided_near_le, '-'),coalesce(scr.aided_distance_le, '-'),coalesce(scr.aided_near_le, '-'),coalesce(scr.pinhole_distance_le, '-'),coalesce(scr.pinhole_near_le, '-'),coalesce(scr.color_le, '-'),scr.treatment_for_refraction_id,coalesce(scr.want_to_refer_1_yes_2_no, '-'),coalesce(scr.refer_for, '-'),coalesce(scr.refer_to, '-'),coalesce(gp.sph_distance_re, '-'),coalesce(gp.sph_near_re, '-'),coalesce(gp.cyl_distance_re, '-'),coalesce(gp.cyl_near_re, '-'),coalesce(gp.axis_distance_re, '-'),coalesce(gp.axis_near_re, '-'),coalesce(gp.va_distance_re, '-'),coalesce(gp.va_near_re, '-'),coalesce(gp.sph_distance_le, '-'),coalesce(gp.sph_near_le, '-'),coalesce(gp.cyl_distance_le, '-'),coalesce(gp.cyl_near_le, '-'),coalesce(gp.axis_distance_le, '-'),coalesce(gp.axis_near_le, '-'),coalesce(gp.va_distance_le, '-'),coalesce(gp.va_near_le, '-'),'' AS R2CEligible,'' as DeliverR2C,'' as R2CRemark,'' as R2C_SPH_RE,'' as R2C_VA_RE,'' as R2C_SPH_LE,'' as R2C_VA_LE,coalesce(gp.spec_type, '-'),gp.has_the_glass_collected,gp.spec_status,coalesce(p.camp_location, '-'),coalesce(scr.username, '-'),coalesce(gp.glass_collecting_location, '-'),coalesce(gp.frame_size, '-'),coalesce(gp.frame_code, '-'),coalesce(gp.lens_type, '-'),coalesce(gp.type_of_coating, '-'),p.created_date,p.partner_name,p.feedback,p.model_type_name,coalesce(p.camp_name,p.vision_center_name),COALESCE(p.camp_id, p.vision_center_id) AS result_column,coalesce(p.camp_date, p.vc_created_date),coalesce(p.camp_location, '-'),coalesce(p.camp_address, '-'),coalesce(p.camp_village, '-'),coalesce(p.camp_block, '-'),coalesce(p.camp_state,'-'),coalesce(p.camp_district, '-'),coalesce(p.exe_gp, '-'),coalesce(p.exe_rs, '-'),coalesce(p.camp_opd, '-'),coalesce(p.camp_donor_name, p.vc_donor_name),coalesce(p.camp_donor_mobile_num, p.vc_don_mobile_number),coalesce(p.camp_co_name, '-'),coalesce(p.camp_co_mobile_no, '-') from dash_repo_patient_basic_info_view p left join dash_repo_screening_info_view scr on p.patient_uuid = scr.patient_uuid left join dash_repo_glass_prescription_view gp on gp.scr_uuid = scr.scr_uuid where 1=1  @@from_date_filter @@to_date_filter @@state_filter @@model_type_filter @@donor_name_filter @@hospital_name_filter  @@camp_name_filter @@gender_filter @@patient_id_filter @@patient_name_filter @@occupation_filter @@refractive_error_filter @@eye_problem_filter @@vc_name_filter) as x", "default_sort": {"sort_field": " ", "sort_order": "asc"},"unique_count_query": "select count(distinct(p.patient_unique_id)) from dash_repo_patient_basic_info_view p left join dash_repo_screening_info_view scr on p.patient_uuid = scr.patient_uuid left join dash_repo_glass_prescription_view gp on gp.scr_uuid = scr.scr_uuid where 1=1 @@from_date_filter @@to_date_filter @@state_filter @@model_type_filter @@donor_name_filter @@hospital_name_filter  @@camp_name_filter @@gender_filter @@patient_id_filter @@patient_name_filter @@occupation_filter @@refractive_error_filter @@eye_problem_filter @@vc_name_filter"}
        header = [[ {"label": "S.No", "colspan": 0, "rowspan": 0},{"label": "Unique ID", "colspan": 0, "rowspan": 0}, {"label": "Name", "colspan": 0, "rowspan": 0}, {"label": "Age", "colspan": 0, "rowspan": 0}, {"label": "Gender", "colspan": 0, "rowspan": 0}, {"label": "Contact No. 1 (+91)", "colspan": 0, "rowspan": 0}, {"label": "Contact No. 2 (+91)", "colspan": 0, "rowspan": 0}, {"label": "Permanent Address", "colspan": 0, "rowspan": 0}, {"label": "State", "colspan": 0, "rowspan": 0}, {"label": "District", "colspan": 0, "rowspan": 0}, {"label": "Aadhaar/PAN Number", "colspan": 0, "rowspan": 0}, {"label": "Type of Job", "colspan": 0, "rowspan": 0}, {"label": "Drivers license number", "colspan": 0, "rowspan": 0}, {"label": "Renewal Date", "colspan": 0, "rowspan": 0}, {"label": "Time Since Driving", "colspan": 0, "rowspan": 0}, {"label": "Educational qualification", "colspan": 0, "rowspan": 0}, {"label": "No of months Employed in a year", "colspan": 0, "rowspan": 0}, {"label": "Residence Type", "colspan": 0, "rowspan": 0}, {"label": "Type of Vehicle", "colspan": 0, "rowspan": 0}, {"label": "Type of Route", "colspan": 0, "rowspan": 0}, {"label": "Monthly Income", "colspan": 0, "rowspan": 0}, {"label": "Do you have a Life Insurance Policy", "colspan": 0, "rowspan": 0}, {"label": "Do you have a Vehicle Insurance Policy", "colspan": 0, "rowspan": 0}, {"label": "Do you have a Health Insurance Policy", "colspan": 0, "rowspan": 0}, {"label": "How do you Know About Camp?", "colspan": 0, "rowspan": 0}, {"label": "Screening Response Code", "colspan": 0, "rowspan": 0}, {"label": "Blood pressure", "colspan": 0, "rowspan": 0}, {"label": "Blood sugar", "colspan": 0, "rowspan": 0}, {"label": "Weight", "colspan": 0, "rowspan": 0}, {"label": "Height", "colspan": 0, "rowspan": 0}, {"label": "Total Family Members", "colspan": 0, "rowspan": 0}, {"label": "On what basis your salary is calculated", "colspan": 0, "rowspan": 0}, {"label": "If your owner is holding back any amount from your salary, Please specify(in Rupees)", "colspan": 0, "rowspan": 0}, {"label": "Which are the months you are normally not employed in a year", "colspan": 0, "rowspan": 0}, {"label": "What do you do during non-working months", "colspan": 0, "rowspan": 0}, {"label": "Are you equipped with any alternative employment", "colspan": 0, "rowspan": 0}, {"label": "If No, will you be willing to learn an alternative livelihood skill", "colspan": 0, "rowspan": 0}, {"label": "Do your family members (Spouse / Children / Siblings) earn and support you financially", "colspan": 0, "rowspan": 0}, {"label": "Have you had a medical check up in the past 1 year", "colspan": 0, "rowspan": 0}, {"label": "Do you have Diabetes", "colspan": 0, "rowspan": 0}, {"label": "When was it diagnosed", "colspan": 0, "rowspan": 0}, {"label": "Insulin-dependent / non-insulin dependent", "colspan": 0, "rowspan": 0}, {"label": "Dosage of Insulin (If Insulin dependent)", "colspan": 0, "rowspan": 0}, {"label": "Do you have Hypertension", "colspan": 0, "rowspan": 0}, {"label": "When was it diagnosed.1", "colspan": 0, "rowspan": 0}, {"label": "Are you on medication for Hypertension", "colspan": 0, "rowspan": 0}, {"label": "Do you Smoke", "colspan": 0, "rowspan": 0}, {"label": "Do you consume Alcohol", "colspan": 0, "rowspan": 0}, {"label": "Waist Circumference ", "colspan": 0, "rowspan": 0}, {"label": "Physical activity ", "colspan": 0, "rowspan": 0}, {"label": "Family history of Diabetes", "colspan": 0, "rowspan": 0}, {"label": "Duration since last meal - hrs", "colspan": 0, "rowspan": 0}, {"label": "Cough for more than two weeks", "colspan": 0, "rowspan": 0}, {"label": "Night Sweats ", "colspan": 0, "rowspan": 0}, {"label": "Fever for more than 2 weeks", "colspan": 0, "rowspan": 0}, {"label": "Unexplained Weight Loss / Loss of appetite", "colspan": 0, "rowspan": 0}, {"label": "Have you ever had eye examination", "colspan": 0, "rowspan": 0}, {"label": "Do you have any difficulty in seeing distant objects", "colspan": 0, "rowspan": 0}, {"label": "Do you have any difficulty in judging distance while driving", "colspan": 0, "rowspan": 0}, {"label": "Are you able to identify the traffic colors easily", "colspan": 0, "rowspan": 0}, {"label": "Do you have any difficulty in seeing while night driving", "colspan": 0, "rowspan": 0}, {"label": "Have you been advised to wear glasses ever", "colspan": 0, "rowspan": 0}, {"label": "Are you wearing glasses currently", "colspan": 0, "rowspan": 0}, {"label": "Are you aware of any nearby hospital", "colspan": 0, "rowspan": 0}, {"label": "Type of Hospital", "colspan": 0, "rowspan": 0}, {"label": "Have you ever involved in road accident while driving your commercial vehicle before", "colspan": 0, "rowspan": 0}, {"label": "Have you been involved in road accident while driving your commercial vehicle in last twelve months", "colspan": 0, "rowspan": 0}, {"label": "Do you have proper First-Aid Kit in your truck", "colspan": 0, "rowspan": 0}, {"label": "Are you generally happy with your profession", "colspan": 0, "rowspan": 0}, {"label": "If you are happy, Specify in what way", "colspan": 0, "rowspan": 0}, {"label": "UnAided Distance(RE)", "colspan": 0, "rowspan": 0}, {"label": "UnAided Near(RE)", "colspan": 0, "rowspan": 0}, {"label": "Aided Distance(RE)", "colspan": 0, "rowspan": 0}, {"label": "Aided Near(RE)", "colspan": 0, "rowspan": 0}, {"label": "Pinhole Distance(RE)", "colspan": 0, "rowspan": 0}, {"label": "Pinhole Near(RE)", "colspan": 0, "rowspan": 0}, {"label": "Color(RE)", "colspan": 0, "rowspan": 0}, {"label": "UnAided Distance(LE)", "colspan": 0, "rowspan": 0}, {"label": "UnAided Near(LE)", "colspan": 0, "rowspan": 0}, {"label": "Aided Distance(LE)", "colspan": 0, "rowspan": 0}, {"label": "Aided Near(LE)", "colspan": 0, "rowspan": 0}, {"label": "Pinhole Distance(LE)", "colspan": 0, "rowspan": 0}, {"label": "Pinhole Near(LE)", "colspan": 0, "rowspan": 0}, {"label": "Color(LE)", "colspan": 0, "rowspan": 0}, {"label": "Treatment for refraction", "colspan": 0, "rowspan": 0}, {"label": "Do you want to refer ?", "colspan": 0, "rowspan": 0}, {"label": "Refer for", "colspan": 0, "rowspan": 0}, {"label": "Referred To", "colspan": 0, "rowspan": 0}, {"label": "SPH Distance(RE)", "colspan": 0, "rowspan": 0}, {"label": "SPH Near(RE)", "colspan": 0, "rowspan": 0}, {"label": "CYL Distance(RE)", "colspan": 0, "rowspan": 0}, {"label": "CYL Near(RE)", "colspan": 0, "rowspan": 0}, {"label": "AXIS Distance(RE)", "colspan": 0, "rowspan": 0}, {"label": "AXIS Near(RE)", "colspan": 0, "rowspan": 0}, {"label": "V/A Distance(RE)", "colspan": 0, "rowspan": 0}, {"label": "V/A Near(RE)", "colspan": 0, "rowspan": 0}, {"label": "SPH Distance(LE)", "colspan": 0, "rowspan": 0}, {"label": "SPH Near(LE)", "colspan": 0, "rowspan": 0}, {"label": "CYL Distance(LE)", "colspan": 0, "rowspan": 0}, {"label": "CYL Near(LE)", "colspan": 0, "rowspan": 0}, {"label": "AXIS Distance(LE)", "colspan": 0, "rowspan": 0}, {"label": "AXIS Near(LE)", "colspan": 0, "rowspan": 0}, {"label": "V/A Distance(LE)", "colspan": 0, "rowspan": 0}, {"label": "V/A Near(LE)", "colspan": 0, "rowspan": 0}, {"label": "R2CEligible", "colspan": 0, "rowspan": 0}, {"label": "DeliverR2C", "colspan": 0, "rowspan": 0}, {"label": "R2CRemark", "colspan": 0, "rowspan": 0}, {"label": "R2C_SPH_RE", "colspan": 0, "rowspan": 0}, {"label": "R2C_VA_RE", "colspan": 0, "rowspan": 0}, {"label": "R2C_SPH_LE", "colspan": 0, "rowspan": 0}, {"label": "R2C_VA_LE", "colspan": 0, "rowspan": 0}, {"label": "Spectacle_Type", "colspan": 0, "rowspan": 0}, {"label": "Has the glass collected at the camp?", "colspan": 0, "rowspan": 0}, {"label": "Glass Status", "colspan": 0, "rowspan": 0}, {"label": "Screened Location", "colspan": 0, "rowspan": 0}, {"label": "Screened By", "colspan": 0, "rowspan": 0}, {"label": "Glass Collecting Location", "colspan": 0, "rowspan": 0}, {"label": "Frame Code", "colspan": 0, "rowspan": 0}, {"label": "Frame Size", "colspan": 0, "rowspan": 0}, {"label": "Lens Type", "colspan": 0, "rowspan": 0}, {"label": "Type Of Coating", "colspan": 0, "rowspan": 0}, {"label": "CreatedDate", "colspan": 0, "rowspan": 0},{"label": "Hospital Name", "colspan": 0, "rowspan": 0}, {"label": "Feedback", "colspan": 0, "rowspan": 0}, {"label": "Model Type", "colspan": 0, "rowspan": 0}, {"label": "Hub / Spoke Camp Name", "colspan": 0, "rowspan": 0}, {"label": "Hub / Spoke CampID", "colspan": 0, "rowspan": 0}, {"label": "Hub / Spoke Camp Date", "colspan": 0, "rowspan": 0}, {"label": "Hub / Spoke Camp Location", "colspan": 0, "rowspan": 0}, {"label": "Hub / Spoke Address", "colspan": 0, "rowspan": 0}, {"label": "Hub / Spoke Village", "colspan": 0, "rowspan": 0}, {"label": "Hub / Spoke_Block/ Mandal", "colspan": 0, "rowspan": 0}, {"label": "Hub/ Spoke Information State", "colspan": 0, "rowspan": 0}, {"label": "Hub / Spoke Camp District", "colspan": 0, "rowspan": 0}, {"label": "Hub / Spoke Expected Glass Prescription", "colspan": 0, "rowspan": 0}, {"label": "Hub / Spoke Expected Refer Surgeries", "colspan": 0, "rowspan": 0}, {"label": "Hub / Spoke Expected Camp OPD", "colspan": 0, "rowspan": 0}, {"label": "Hub / Spoke Donor Name", "colspan": 0, "rowspan": 0}, {"label": "Hub / Spoke Donor No. (+91)", "colspan": 0, "rowspan": 0}, {"label": "Hub / Spoke Camp Coordinator", "colspan": 0, "rowspan": 0}, {"label": "Hub / Spoke Camp Coordinator Mobile No. (+91)", "colspan": 0, "rowspan": 0}]]
    if r_slug == 'tele-calling':
        sql_query = {"sql_query": "SELECT p.patient_uuid, p.name, p.age, p.gender, coalesce(p.contact_2, '-'),coalesce(p.contact_1,'-'),'' as cat,p.camp_name,p.camp_date,gp.spec_status,coalesce(p.camp_location,p.partner_location) as screened_location,p.username as screened_by,coalesce(p.camp_location,p.partner_location) as delivery_location,p.username as delivery_by,'-' as delivery_date,'-' as eye_problem ,'-' as refractive_error , (case when gp.spec_status_id in (1,2) then 'Ordered' when gp.spec_status_id =3 then 'Given' else '-' end) as spectacles,scr.want_to_refer_1_yes_2_no as want_refer,scr.refer_to as refer_to,'-' as R2C_Eligible,'-' as R2C_Remark, gp.spec_type as spec_type_name,p.partner_name as hos_name ,ml.name, cat.call_disposition_group,'' as rating,ml_1.name as comments ,cat.agent_comments as agent_comments,'' as rating  FROM sims_cataractquestions cat LEFT JOIN dash_repo_patient_basic_info_view p ON p.patient_table_id = cat.patient_id LEFT JOIN dash_repo_screening_info_view scr ON scr.patient_uuid = p.patient_uuid LEFT JOIN dash_repo_glass_prescription_view gp on gp.scr_uuid = scr.scr_uuid LEFT JOIN master_data_masterlookup ml ON ml.id = cat.disposition_name_id LEFT JOIN master_data_masterlookup ml_1 ON ml_1.id = cat.comments_id WHERE 1 = 1 @@from_date_filter @@to_date_filter @@state_filter @@district_filter @@model_type_filter @@donor_name_filter @@hospital_name_filter @@LIMITS", "count_query": "SELECT COUNT(x) FROM (SELECT p.patient_uuid, p.name, p.age, p.gender, coalesce(p.contact_2, '-'),coalesce(p.contact_1,'-'),'' as cat,p.camp_name,p.camp_date,gp.spec_status,coalesce(p.camp_location,p.partner_location) as screened_location,p.username as screened_by,coalesce(p.camp_location,p.partner_location) as delivery_location,p.username as delivery_by,'-' as delivery_date,'-' as eye_problem ,'-' as refractive_error , (case when gp.spec_status_id in (1,2) then 'Ordered' when gp.spec_status_id =3 then 'Given' else '-' end) as spectacles,scr.want_to_refer_1_yes_2_no as want_refer,scr.refer_to as refer_to,'-' as R2C_Eligible,'-' as R2C_Remark, gp.spec_type as spec_type_name,p.partner_name as hos_name ,ml.name, cat.call_disposition_group,'' as rating,ml_1.name as comments ,cat.agent_comments as agent_comments,'' as rating  FROM sims_cataractquestions cat LEFT JOIN dash_repo_patient_basic_info_view p ON p.patient_table_id = cat.patient_id LEFT JOIN dash_repo_screening_info_view scr ON scr.patient_uuid = p.patient_uuid LEFT JOIN dash_repo_glass_prescription_view gp on gp.scr_uuid = scr.scr_uuid LEFT JOIN master_data_masterlookup ml ON ml.id = cat.disposition_name_id LEFT JOIN master_data_masterlookup ml_1 ON ml_1.id = cat.comments_id WHERE 1 = 1 @@from_date_filter @@to_date_filter @@state_filter @@district_filter @@model_type_filter @@donor_name_filter @@hospital_name_filter) AS x", "default_sort": {"sort_field": "", "sort_order": "asc"}}
        header = [[{"label": "S.No", "colspan": 0, "rowspan": 0},{"label": "UID", "colspan": 0, "rowspan": 0}, {"label": "Name", "colspan": 0, "rowspan": 0}, {"label": "Occupation \n(Driver, Cleaner, Mechanic, staff etc.)", "colspan": 0, "rowspan": 0}, {"label": "Age", "colspan": 0, "rowspan": 0}, {"label": "Gender", "colspan": 0, "rowspan": 0}, {"label": "Alternate Number", "colspan": 0, "rowspan": 0}, {"label": "Contact Number", "colspan": 0, "rowspan": 0}, {"label": "ADS", "colspan": 0, "rowspan": 0}, {"label": "Camp Name", "colspan": 0, "rowspan": 0}, {"label": "Camp Date", "colspan": 0, "rowspan": 0}, {"label": "Glass Status", "colspan": 0, "rowspan": 0}, {"label": "Screened Location", "colspan": 0, "rowspan": 0}, {"label": "Screened By", "colspan": 0, "rowspan": 0}, {"label": "Delivery Location", "colspan": 0, "rowspan": 0}, {"label": "Delivery By", "colspan": 0, "rowspan": 0}, {"label": "Delivery Date", "colspan": 0, "rowspan": 0}, {"label": "Mention Eye Problem Identified (mention name eg. RE, Cataract, etc.)", "colspan": 0, "rowspan": 0}, {"label": "Type of Refractive Error Identified (Near, Distance, Presbyopia, etc.)", "colspan": 0, "rowspan": 0}, {"label": "Spectacles Given/ Ordered", "colspan": 0, "rowspan": 0}, {"label": "Referred for Eye Problem (Y/N)", "colspan": 0, "rowspan": 0}, {"label": "Referred to", "colspan": 0, "rowspan": 0}, {"label": "R2C Eligible", "colspan": 0, "rowspan": 0}, {"label": "R2C Remarks", "colspan": 0, "rowspan": 0}, {"label": "Spectacle Type", "colspan": 0, "rowspan": 0}, {"label": "Hospital Name", "colspan": 0, "rowspan": 0}, {"label": "Disposition Name", "colspan": 0, "rowspan": 0}, {"label": "Disposition Group", "colspan": 0, "rowspan": 0}, {"label": "Rating", "colspan": 0, "rowspan": 0}, {"label": "Comments", "colspan": 0, "rowspan": 0}, {"label": "Agent Comments", "colspan": 0, "rowspan": 0}, {"label": "Rating.1", "colspan": 0, "rowspan": 0}]]
    return sql_query,header

@ login_required(login_url='/login/')
def custom_report(request, page_slug):
    # rows_per_page = 5
    report_meta = ReportMeta.objects.get(page_slug=page_slug)
    heading = report_meta.report_title
    rows_per_page= int(Config.objects.get(code='report_records_per_page').value)
    user_role_id = request.session.get('role_id')
    if request.method == "POST":
        req_data = request.POST
        summit=req_data.dict()
        more_view=summit.get('more_name')
    elif request.method == "GET":
        req_data = request.GET
    export_flag = True if req_data.get('export') and req_data.get(
        'export').lower() == 'true' else False
    if export_flag == True:
            export_report = ReportExport.objects.create(
                user=request.user, report=report_meta, downloaded_at=datetime.datetime.now(), export_status=1)
            export_report.save()
    page_reports = ReportMeta.objects.filter(
        page_slug=page_slug, status=2).order_by('display_order')
    # temp veriableg
    data_query_list = []
    #report_tabs = []
    section_title = []
    table_header = []
    custom_export_headers = []
    total_header_cols = []
    report_slug_list = []
    data = []
    # nowrap_cols = []
    user_sort_field = []
    user_sort_order = []
    page_info = []
    sorting_field = []
    user_filter_values = {}
    user_location_data = None
    filter_values = None
    unique_count_query = ''
    # get user selected filter data and merge with the user configured location heirarcy
    hidden_filters = []
    for idx, report in enumerate(page_reports):
        r_slug = report.report_slug
        s_title = report.report_title
        f_info = report.filter_info
        s_info = report.sort_info
        if req_data and req_data.get('donor_name') in ('4','12') and r_slug in ['donor-report','patient-summary-report','tele-calling']:
            r_query, headers = get_cholas_meta(r_slug)
        else:
            r_query = report.report_query
            headers = report.report_header
        d_query = r_query['sql_query']
        c_query = r_query['count_query'] if r_query['count_query'] else ''
        if 'unique_count_query' in r_query:
            unique_count_query = r_query['unique_count_query'] if r_query['unique_count_query'] else ''
        e_header = report.custom_export_header
        if idx == 0:
            page_slug = report.page_slug
            #logger.error("hidden_filtes: " + str(hidden_filters))
            user_location_data, filter_values, user_filter_values,state_list,donor_list,partner_list = get_filter_data(request, req_data, f_info,r_slug,pagination=False)
        # update any variable_location_names  - in query, count query, sort and headers
        default_sort = r_query['default_sort'] if 'default_sort' in r_query else None
        sort_field, sort_order = set_sort_options(
            req_data, idx, s_info, default_sort)
        user_sort_field.append(sort_field)
        user_sort_order.append(sort_order)
        #Adding fixed_sort_order
        # page reloads on click of filter, so current page is always set to 1
        current_page = 1
        custom_model_type = f_info['custom_filter']['model_type']
        data_query, count_query , unique_count_query= apply_filters_to_query(d_query, c_query,unique_count_query,f_info,sort_field, sort_order, user_filter_values, current_page, rows_per_page, export_flag)
        # table header details
        print(data_query,'----------')
        table_header.append(headers)
        # get total columns count (colspan sum) - used to display the no records found row
        header_col_count = 0
        for item in headers[0]:
            colspan = item.get('colspan', 0)
            header_col_count += colspan if colspan > 0 else 1
        data_query_list.append(data_query)
        data.append(return_sql_results(data_query))
        total_header_cols.append(header_col_count)
        report_slug_list.append(r_slug)
        custom_export_headers.append(e_header)
        section_title.append(s_title)
        # nowrap_cols.append(nw_cols)
        sorting_field.append(s_info)
        # if not for export, prepare pagination details
        if export_flag == False:
            # fetch record count and calcualte pagination info
            total_records = 0
            count_result = return_sql_results(count_query)
            if count_result:
                total_records = count_result[0][0]
            p_info = calculate_pagination_info(total_records, 1, rows_per_page)
            page_info.append(p_info)
            # pagination_range will be same for all reports in the page
            pagination_range = range(p_info.get(
                'start_page'), p_info.get('end_page')+1)
    sidebar_active = 'Report'
    # add the dashboard chart title to report if the report is displayed on click of chart in dashboard
    addln_dashboard_title = ''
    # if export button click, create excel and return as response
    if export_flag == True and page_slug != 'patient-summary-report':
        export_report = ReportExport.objects.get(id = export_report.id)
        export_report.export_status=2
        export_report.save()
        return generate_export_excel(section_title[0], data_query_list, table_header, custom_export_headers, section_title)
    if export_flag == True and page_slug == 'patient-summary-report':
        return generate_custom_export_excel(section_title[0], data_query_list,unique_count_query, table_header, custom_export_headers, section_title)
    
    return render(request, 'reports/multitab_report.html', locals())


def generate_custom_export_excel(report_title, data_query_list,unique_count_query, table_header, custom_export_headers, section_title):
    import csv
    import datetime
    from django.http import HttpResponse
    from django.db import connection
    from django.conf import settings
    import os

    MEDIA_ROOT = settings.MEDIA_ROOT
    file_name = re.sub("(\s)|(')|(-)", '_', report_title)
    attachment_name = file_name + "_" + datetime.datetime.today().strftime("%d%m%y%H%M") + ".csv"
    attachment_path = os.path.join(MEDIA_ROOT, 'temp_export_data', attachment_name)
    cursor = connection.cursor()
    cursor.execute(data_query_list[0])
    data = cursor.fetchall()
    cursor.close()
    cursor = connection.cursor()
    cursor.execute(unique_count_query)
    unique_cnt = cursor.fetchall()
    cursor.close()
    header = [i['label'] for i in table_header[0][0]]
    header.pop(0)
    header_unique_cnt = ['Patient_unique_count',unique_cnt[0][0]]
    with open(attachment_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(header_unique_cnt)
        csv_writer.writerow(header)
        csv_writer.writerows(data)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
    with open(attachment_path, 'r', newline='', encoding='utf-8') as csv_file:
        csv_content = csv_file.read().replace('+', '+ ')
        response.write(csv_content)
    os.remove(attachment_path)
    return response

            
def calculate_pagination_info(total_records, current_page, rows_per_page):
    display_page_range = settings.PAGE_NUMBER_DISPLAY_COUNT#DISPLAY_PAGE_RANGE
    num_pages = int(total_records/rows_per_page)
    num_pages = num_pages if total_records % rows_per_page == 0 else num_pages + 1
    start_page = (current_page - int(display_page_range/2))
    start_page = 1 if start_page < 1 else start_page
    end_page = start_page + display_page_range - 1
    end_page = num_pages if end_page > num_pages else end_page
    first_row = ((current_page-1)*rows_per_page) + 1
    last_row = (current_page*rows_per_page)
    last_row = total_records if last_row > total_records else last_row
    dicta = {"rec_count": total_records, "current_page": current_page, "rows_per_page": rows_per_page, "display_page_range": display_page_range,
             "num_pages": num_pages, "start_page": start_page, "end_page": end_page, "first_row": first_row, "last_row": last_row}
    return {"rec_count": total_records, "current_page": current_page, "rows_per_page": rows_per_page, "display_page_range": display_page_range,
            "num_pages": num_pages, "start_page": start_page, "end_page": end_page, "first_row": first_row, "last_row": last_row}


@ login_required(login_url='/login/')
def custom_report_reload(request, page_slug, report_slug):
    import sys
    import traceback
    html = ''
    # TODO:settings reports_row_per_page
    # rows_per_page = 5
    rows_per_page= int(Config.objects.get(code='report_records_per_page').value)
    user_role_id = request.session.get('role_id')
    try:
        if request.method == 'POST':# and request.is_ajax():
            if request.method == "POST":
                req_data = request.POST
            elif request.method == "GET":
                req_data = request.GET
            # order of reports is specified in the ReportMeta default ordering
            # page_reports = get_list_or_404(ReportMeta, page_slug=page_slug, status=2)
            page_reports = ReportMeta.objects.filter(
                page_slug=page_slug, status=2).order_by('display_order')
            table_header = []
            report_slug_list = []
            data = []
            nowrap_cols = []
            user_sort_field = []
            user_sort_order = []
            sorting_field = []
            page_info = []
            user_filter_values = {}
            total_header_cols = []
            unique_count_query = ''
            report_idx = 0
            for idx, report in enumerate(page_reports):
                if report.report_slug == report_slug:
                    report_idx = idx
                else:
                    continue
                report_slug_list.append(report.report_slug)
                if req_data and req_data.get('donor_name') == '4' and report_slug in ['donor-report','patient-summary-report','tele-calling']:
                    r_query, headers = get_cholas_meta(report.report_slug)
                else:
                    r_query = report.report_query
                    headers = report.report_header
                d_query = r_query['sql_query']
                c_query = r_query['count_query'] if r_query['count_query'] else ''
                if 'unique_count_query' in r_query:
                    unique_count_query = r_query['unique_count_query'] if r_query['unique_count_query'] else ''
                f_info = report.filter_info
                s_info = report.sort_info
                e_header = report.custom_export_header
                r_slug = report.report_slug
                custom_model_type = f_info['custom_filter']['model_type']
                # nowrap_cols.append(report.report_query['nowrap_cols'])
                user_location_data, filter_values, user_filter_values,state_list,donor_list,partner_list = get_filter_data(request, req_data, f_info,r_slug,pagination=True)
                # update any variable_location_names  - in query, count query, sort and headers
                default_sort = r_query['default_sort'] if 'default_sort' in r_query else None
                sort_field, sort_order = set_sort_options(
                    req_data, report_idx, s_info, default_sort)
                current_page = int(req_data.get('page_'+str(report_idx), '0'))
                data_query, count_query , unique_count_query = apply_filters_to_query(d_query, c_query,unique_count_query,f_info, sort_field, sort_order, user_filter_values, current_page, rows_per_page, False)
                data.append(return_sql_results(data_query))
                # table header details
                table_header.append(headers)
                # get total columns count (colspan sum) - used to display the no records found row
                total_records = int(req_data.get(
                    'rec_count_'+str(report_idx), '0'))
                total_header_cols.append(total_records)
                p_info = calculate_pagination_info(
                    total_records, current_page, rows_per_page)
                pagination_range = range(p_info.get(
                    'start_page'), p_info.get('end_page')+1)
                page_info.append(p_info)
                sorting_field.append(s_info)
            html = render_to_string('reports/report_ajax_reload.html', {"req_data": req_data, "report_idx": report_idx, "table_header": table_header, "data": data,
                                                                        "nowrap_cols": nowrap_cols, "user_sort_field": user_sort_field, "user_sort_order": user_sort_order, "page_info": page_info,
                                                                        "pagination_range": pagination_range,"user_role_id":user_role_id})
    except Exception as ex1:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_stack = repr(traceback.format_exception(
            exc_type, exc_value, exc_traceback))
        logger.error(error_stack)
    return HttpResponse(html)


@ login_required(login_url='/login/')
def get_district(request):
    if request.method == 'GET': #and request.is_ajax():
        selected_state = request.GET.get('selected_state', '')
        result_set = []
        district = District.objects.filter(state_id=int(
            selected_state), status=2).order_by('name').values_list('id', 'name')
        for dist in district:
            result_set.append(
                {'id': dist[0], 'name': dist[1], })
        return HttpResponse(json.dumps(result_set))

@ login_required(login_url='/login/')
def get_camp(request):
    if request.method == 'GET': #and request.is_ajax():
        selected_hospital = request.GET.getlist('selected_hospital[]', '')
        selected_model = request.GET.get('selected_model_type', '')
        selected_state = request.GET.get('selected_state','')
        selected_donor = request.GET.get('selected_donor','')
        result_set = []
        if selected_hospital != '' and selected_hospital != ['']:
            camp_details = Camp.objects.filter(status=2,partner_id__in=selected_hospital).order_by('name').values_list(Concat(F('id'), Value('-2'), output_field=CharField()), 'name')
            vision_details = VisionCenter.objects.filter(status=2,partner_id__in=selected_hospital).order_by('name').values_list(Concat(F('id'), Value('-3'), output_field=CharField()), 'name')
            if selected_model == "'2'":
                append_list = [i for i in camp_details]
            elif selected_model == "'3'":
                append_list = [i for i in vision_details]
            else:
                append_list = [i for i in camp_details] + [i for i in vision_details]
        elif selected_state != '':
            part_list = Partner.objects.filter(state_id=int(selected_state)).values_list('id',flat=True)
            camp_details = Camp.objects.filter(status=2,partner__in=part_list).order_by('name').values_list(Concat(F('id'), Value('-2'), output_field=CharField()), 'name')
            vision_details = VisionCenter.objects.filter(status=2,partner_id__in=part_list).order_by('name').values_list(Concat(F('id'), Value('-3'), output_field=CharField()), 'name')
            if selected_model == "'2'":
                    append_list = [i for i in camp_details]
            elif selected_model == "'3'":
                append_list = [i for i in vision_details]
            else:
                append_list = [i for i in camp_details] + [i for i in vision_details] 
        elif selected_donor != '':
            part_list = DonorPartnerLinkage.objects.filter(status=2,donor=int(selected_donor)).values_list('partner_id',flat=True)
            camp_details = Camp.objects.filter(status=2,partner_id__in=part_list).order_by('name').values_list(Concat(F('id'), Value('-2'), output_field=CharField()), 'name')
            vision_details = VisionCenter.objects.filter(status=2,partner_id__in=part_list).order_by('name').values_list(Concat(F('id'), Value('-3'), output_field=CharField()), 'name')
            if selected_model == "'2'":
                    append_list = [i for i in camp_details]
            elif selected_model == "'3'":
                append_list = [i for i in vision_details]
            else:
                append_list = [i for i in camp_details] + [i for i in vision_details]
        else:
            camp_details = Camp.objects.filter(status=2).order_by('name').values_list(Concat(F('id'), Value('-2'), output_field=CharField()), 'name')
            vision_details = VisionCenter.objects.filter(status=2).order_by('name').values_list(Concat(F('id'), Value('-3'), output_field=CharField()), 'name')
            if selected_model == "'2'":
                append_list = [i for i in camp_details]
            elif selected_model == "'3'":
                append_list = [i for i in vision_details]
            else:
                append_list = [i for i in camp_details] + [i for i in vision_details] 
        for vc in append_list:
            result_set.append(
                {'id': vc[0], 'name': vc[1], })
        return HttpResponse(json.dumps(result_set))

# @ login_required(login_url='/login/')
# def get_vision_camp(request):
#     if request.method == 'GET': #and request.is_ajax():
#         selected_model = request.GET.get('selected_model_type', '')

#         result_set = []
#         if request.session.get('role_id') == 4:
#             partner_users = UserPartnerLinkage.objects.get(user_id=request.user.id)
#             camp_details = Camp.objects.filter(partner_id=partner_users.partner.id, status=2).order_by('name').values_list(str('id'), 'name')
#             vision_details = VisionCenter.objects.filter(partner_id=partner_users.partner.id, status=2).order_by('name').values_list(str('id'), 'name')
#             if selected_model == "'2'":
#                 append_list = [i for i in camp_details]
#             elif selected_model == "'3'":
#                 append_list = [i for i in vision_details]
#             else:
#                 append_list = [i for i in camp_details] + [i for i in vision_details]
#         else:
#             camp_details = Camp.objects.filter(status=2).order_by('name').values_list(str('id'), 'name')
#             vision_details = VisionCenter.objects.filter(status=2).order_by('name').values_list(str('id'), 'name')
#             if selected_model == "'2'":
#                 append_list = [i for i in camp_details]
#             elif selected_model == "'3'":
#                 append_list = [i for i in vision_details]
#             else:
#                 append_list = [i for i in camp_details] + [i for i in vision_details] 
#         for vc in append_list:
#             result_set.append(
#                 {'id': vc[0], 'name': vc[1], })
#         return HttpResponse(json.dumps(result_set))

@ login_required(login_url='/login/')
def get_partner(request):
    if request.method == 'GET': #and request.is_ajax():
        result_set = []
        selected_donor = request.GET.get('selected_donor', '')
        selected_state = request.GET.get('selected_state','') 
        if selected_donor != '' and selected_state == '' and request.session.get('role_id') in (8,9,10):
            get_state_partner_linkage = ApplicationUserStateLinkage.objects.filter(status=2,user_id=request.user.id).values_list('state',flat=True)
            partner_id = Partner.objects.filter(state_id__in=get_state_partner_linkage).values_list('id',flat=True)
            donor_partner = DonorPartnerLinkage.objects.filter(status=2,partner__in=partner_id,donor=int(selected_donor)).values_list('partner_id',flat=True)
            partner_details = Partner.objects.filter(id__in=donor_partner,status=2).order_by('name').values_list('id', 'name')
        elif selected_donor != '' and selected_state == '' and request.session.get('role_id') not in (8,9,10):
            donor_partner = DonorPartnerLinkage.objects.filter(status=2,donor_id=selected_donor).values_list('partner_id',flat=True)
            partner_details = Partner.objects.filter(id__in=donor_partner,status=2).order_by('name').values_list('id', 'name')
        elif selected_donor == '' and selected_state != '' and request.session.get('role_id') in (8,9,10):
            get_state_partner_linkage = ApplicationUserStateLinkage.objects.filter(status=2,user_id=request.user.id).values_list('state',flat=True)
            partner_id = Partner.objects.filter(state_id__in=get_state_partner_linkage).values_list('id',flat=True)
            donor_partner = DonorPartnerLinkage.objects.filter(status=2,partner__in=partner_id,donor=int(selected_donor)).values_list('partner_id',flat=True)
            partner_details = Partner.objects.filter(id__in=donor_partner,status=2,state_id = int(selected_state)).order_by('name').values_list('id', 'name')
        elif selected_donor == '' and selected_state != '' and request.session.get('role_id') not in (8,9,10):
            partner_details = Partner.objects.filter(state_id=int(selected_state)).order_by('name').values_list('id', 'name')
        elif selected_donor != '' and selected_state != '':
            donor_partner = DonorPartnerLinkage.objects.filter(status=2,donor=int(selected_donor)).values_list('partner_id',flat=True)
            partner_details = Partner.objects.filter(id__in=donor_partner,status=2,state_id = int(selected_state)).order_by('name').values_list('id', 'name')
        elif selected_donor == '' and selected_state == '':
            partner_details = Partner.objects.filter().order_by('name').values_list('id', 'name')
        for part in partner_details:
            result_set.append(
                {'id': part[0], 'name': part[1], })
        return HttpResponse(json.dumps(result_set))

def get_donor(request):
    if request.method == 'GET': #and request.is_ajax():
        result_set = []
        if ('selected_hospital') in  request.GET.keys() or ('selected_hospital[]') in  request.GET.keys():
            selected_hospital = request.GET.getlist('selected_hospital[]')
            donor_id = DonorPartnerLinkage.objects.filter(status=2,partner__in=selected_hospital).values_list('donor_id',flat=True)
            donor_details = Donor.objects.filter(status=2,id__in=donor_id).values_list(str('id'),'name').order_by('name')
        elif 'selected_state' in request.GET.keys() and request.GET.get('selected_state') != '':
            selected_state = request.GET.get('selected_state','')
            district_list = District.objects.filter(status=2,state_id=int(selected_state)).values_list('id',flat=True)
            donor_id = DonorPartnerLinkage.objects.filter(status=2,district_id__in=district_list).values_list('donor_id',flat=True)
            donor_details = Donor.objects.filter(status=2,id__in=donor_id).values_list(str('id'),'name').order_by('name')
        elif 'selected_state' in request.GET.keys() and request.GET.get('selected_state') == '':
            district_list = District.objects.filter(status=2).values_list('id',flat=True)
            donor_id = DonorPartnerLinkage.objects.filter(status=2,district_id__in=district_list).values_list('donor_id',flat=True)
            donor_details = Donor.objects.filter(status=2,id__in=donor_id).values_list(str('id'),'name').order_by('name')
        for donor in donor_details:
                result_set.append(
                    {'id': donor[0], 'name': donor[1], })
        return HttpResponse(json.dumps(result_set))


def get_location_data(request,user_filter_values):
    zone_list,state_list,district_list,donor_list,partner_list,camp_list,vision_center_list = [],[],[],[],[],[],[]
    selected_state = user_filter_values['state'] if 'state' in user_filter_values.keys() else ''
    selected_camp = user_filter_values['camp_name'] if 'camp_name' in user_filter_values.keys() else ''
    selected_donor = user_filter_values['donor_name'] if 'donor_name' in user_filter_values.keys() else ''
    selected_hospital = user_filter_values['hospital_name'] if 'hospital_name' in user_filter_values.keys() else ''
    #8 - PPA,9 - Zonal Coordinator , 10 - Zonal Incharge
    if request.session.get('role_id') in (8,9,10):
        get_state_partner_linkage = ApplicationUserStateLinkage.objects.filter(status=2,user_id=request.user.id).values_list('state',flat=True)
        zone_list_filter = State.objects.filter(status=2,id__in=get_state_partner_linkage).values_list('zone',flat=True).distinct()
        zone_list = [i for i in zone_list_filter]
        state_id = ApplicationUserStateLinkage.objects.filter(status=2,user_id=request.user.id).values_list('state',flat=True)
        state_filter = State.objects.filter(status=2,id__in=state_id).values_list(str('id'),'name').order_by('name')
        append_state = [state_list.append(i) for i in state_filter]
        get_partners_list = Partner.objects.filter( state_id__in=([selected_state] if selected_state != '' else state_id)).values_list('id', flat=True)
        get_partner = Partner.objects.filter(id__in=get_partners_list).values_list(str('id'),'name').order_by('name')
        append_partner = [partner_list.append(i) for i in get_partner]
        if len(partner_list) == 1:
            selected_partner_list = [str(i[0]) for i in get_partner]
            user_filter_values.update({'hospital_name':selected_partner_list})
        camp_filter = Camp.objects.filter(status=2,partner_id__in=get_partners_list).values_list(Concat(F('id'), Value('-2'), output_field=CharField()), 'name').order_by('name')
        append_camp = [camp_list.append(i) for i in camp_filter]
        vision_center_filter = VisionCenter.objects.filter(status=2,partner_id__in=get_partners_list).values_list(Concat(F('id'), Value('-3'), output_field=CharField()), 'name').order_by('name')
        append_vc = [vision_center_list.append(i) for i in vision_center_filter]
        if len(zone_list) == 1:
            user_filter_values.update({'zone':f'{zone_list[0]}'})
        if len(state_id) == 1:
            user_filter_values.update({'state':f'{state_id[0]}'})
        #district
        state_id = user_filter_values.get('state','')
        if state_id != '':
            district_filter = District.objects.filter(status=2,state_id=state_id).values_list(str('id'),'name').order_by('name')
            append_district = [district_list.append(i) for i in district_filter]
            if len(district_list) == 1:
                user_filter_values.update({'district':f'{district_list[0]}'})
        if state_id == '':
            selected_state_list = [str(i[0]) for i in state_filter]
            user_filter_values.update({'state':str(selected_state_list)[1:-1]})
        #donor
        donor_id = DonorPartnerLinkage.objects.filter(status=2,partner__in=get_partners_list).values_list('donor_id',flat=True).distinct()
        donor_filter = Donor.objects.filter(status=2,id__in=donor_id).values_list(str('id'),'name').order_by('name')
        append_donor = [donor_list.append(i) for i in donor_filter]
        if len(donor_id) == 1:
            user_filter_values.update({'donor_name':f'{donor_id[0]}'})
    #4 - partner
    elif request.session.get('role_id') == 4:
        #partner
        partner_users = UserPartnerLinkage.objects.get(user_id=request.user.id)
        get_partner = Partner.objects.filter(status=2,id=partner_users.partner_id).values_list(str('id'),'name').order_by('name')
        append_partner = [partner_list.append(i) for i in get_partner]
        selected_partner_list = [str(i[0]) for i in get_partner]
        user_filter_values.update({'hospital_name':selected_partner_list})
        #state
        state_id = Partner.objects.filter(status=2,id=partner_users.partner_id).values_list('state_id',flat=True)
        state_filter = State.objects.filter(status=2,id__in=state_id).values_list(str('id'),'name').order_by('name')
        append_state = [state_list.append(i) for i in state_filter]
        #camp
        camp_filter = Camp.objects.filter(status=2,partner_id=partner_users.partner_id).values_list(Concat(F('id'), Value('-2'), output_field=CharField()), 'name').order_by('name')
        append_camp = [camp_list.append(i) for i in camp_filter]
        #vision center
        vision_center_filter = VisionCenter.objects.filter(status=2,partner_id=partner_users.partner_id).values_list(Concat(F('id'), Value('-3'), output_field=CharField()), 'name').order_by('name')
        append_vc = [vision_center_list.append(i) for i in vision_center_filter]
        if len(state_id) == 1:
            user_filter_values.update({'state':f'{state_id[0]}'})
        #district
        state_id = user_filter_values.get('state','')
        if state_id != '':
            # district_id = DonorPartnerLinkage.objects.filter(status=2,partner_id=partner_users.partner_id).values_list('district_id',flat=True).distinct()
            district_filter = District.objects.filter(status=2,state_id=state_id).values_list(str('id'),'name').order_by('name')
            append_district = [district_list.append(i) for i in district_filter]
            if len(district_list) == 1:
                user_filter_values.update({'district':f'{district_list[0]}'})
        #donor
        donor_id = DonorPartnerLinkage.objects.filter(status=2,partner_id=partner_users.partner_id).values_list('donor_id',flat=True)
        donor_filter = Donor.objects.filter(status=2,id__in=donor_id).values_list(str('id'),'name').order_by('name')
        append_donor = [donor_list.append(i) for i in donor_filter]
        if len(donor_id) == 1:
            user_filter_values.update({'donor_name':f'{donor_id[0]}'})
    #11 - Donor
    elif request.session.get('role_id') == 11:
        #get district and partner details 
        donor_id = UserDonorLinkage.objects.filter(status=2,user_id=request.user.id).values_list('donor_id',flat=True)
        donor_part_dist = DonorPartnerLinkage.objects.filter(status=2,donor_id__in=donor_id).values_list('partner_id','district_id')
        part_list = [part[0] for part in donor_part_dist]
        dist_list = [dist[1] for dist in donor_part_dist]
        #state
        state_id = District.objects.filter(status=2,id__in=dist_list).values_list('state_id',flat=True)
        state_filter = State.objects.filter(status=2,id__in=state_id).values_list(str('id'),'name').order_by('name')
        append_state = [state_list.append(i) for i in state_filter]
        #donor
        donor_filter = Donor.objects.filter(status=2,id__in=donor_id).values_list(str('id'),'name').order_by('name')
        append_donor = [donor_list.append(i) for i in donor_filter]
        if donor_id:
            user_filter_values.update({'donor_name':f'{donor_id[0]}'})
        #partner
        get_partner = Partner.objects.filter().values_list(str('id'),'name').order_by('name')
        append_partner = [partner_list.append(i) for i in get_partner]
        if len(partner_list) == 1:
            selected_partner_list = [str(i[0]) for i in get_partner]
            user_filter_values.update({'hospital_name':selected_partner_list})
        get_partners_list = Partner.objects.filter(id__in = part_list,state_id__in=([selected_state] if selected_state != '' else state_id)).values_list('id', flat=True)
        #camp vision center
        camp_filter = Camp.objects.filter(status=2,partner_id__in=([int(part) for part in selected_hospital] if selected_hospital != '' and selected_hospital != [''] else part_list),donor_id__in=donor_id).values_list(Concat(F('id'), Value('-2'), output_field=CharField()), 'name').order_by('name')
        vision_center_filter = VisionCenter.objects.filter(status=2,partner_id__in=([int(part) for part in selected_hospital] if selected_hospital != '' and selected_hospital != [''] else part_list),donor_id__in=donor_id).values_list(Concat(F('id'), Value('-3'), output_field=CharField()), 'name').order_by('name')
        append_camp = [camp_list.append(i) for i in camp_filter]
        append_vc = [vision_center_list.append(i) for i in vision_center_filter] 
        if len(state_id) == 1:
            user_filter_values.update({'state':f'{state_id[0]}'})
        
    else:#3 admin
        #state
        get_state_filter = State.objects.filter(status=2).values_list(str('id'),'name').order_by('name')
        append_state = [state_list.append(i) for i in get_state_filter]
        state_id = Partner.objects.filter().values_list('state_id',flat=True)
        #partner
        get_partners_list = Partner.objects.filter(state_id__in=([selected_state] if selected_state != '' else state_id)).values_list('id', flat=True)
        get_partner = Partner.objects.filter(id__in=get_partners_list).values_list(str('id'),'name').order_by('name')
        if selected_donor != '':
            donor_partner_districts = DonorPartnerLinkage.objects.filter(status=2,donor_id=int(selected_donor)).values_list('partner_id','district_id')
            part_list = [part[0] for part in donor_partner_districts]
            dist_list = [dist[1] for dist in donor_partner_districts]
            get_partners_list = Partner.objects.filter(status=2, id__in = part_list,state_id__in=([selected_state] if selected_state != '' else state_id)).values_list('id', flat=True)
            get_partner = Partner.objects.filter(status=2,id__in=get_partners_list).values_list(str('id'),'name').order_by('name')
        append_partner = [partner_list.append(i) for i in get_partner]
        district_list = District.objects.filter(status=2,state_id__in=([selected_state] if selected_state != '' else state_id)).values_list('id',flat=True)
        #donor
        donor_id = DonorPartnerLinkage.objects.filter(status=2,district_id__in=district_list).values_list('donor_id',flat=True)
        donor_details = Donor.objects.filter(status=2,id__in=donor_id).values_list(str('id'),'name').order_by('name')
        append_donor = [donor_list.append(i) for i in donor_details]
        #using state_id list method is not working , so used if condition
        #camp vision center
        camp_filter = Camp.objects.filter(status=2,partner_id__in=([int(part) for part in selected_hospital] if selected_hospital != '' and selected_hospital != [''] else get_partners_list)).values_list(Concat(F('id'), Value('-2'), output_field=CharField()), 'name').order_by('name')
        vision_center_filter = VisionCenter.objects.filter(status=2,partner_id__in=([int(part) for part in selected_hospital] if selected_hospital != '' and selected_hospital != [''] else get_partners_list)).values_list(Concat(F('id'), Value('-3'), output_field=CharField()), 'name').order_by('name')
        append_camp = [camp_list.append(i) for i in camp_filter]
        append_vc = [vision_center_list.append(i) for i in vision_center_filter] 
    return zone_list,state_list,district_list,donor_list,partner_list,camp_list,vision_center_list,user_filter_values

import ast
def get_filter_data(request, req_data, f_info,r_slug,pagination):
    filter_values = []
    filter_display_order = -1
    f_labels = f_info['filter_labels']
    custom_filter = f_info['custom_filter']
    filter_keys = f_info['filter_labels'].keys()
    user_filter_values = {}
    display_order = f_info['display_order']
    for key in filter_keys:
        if key not in ast.literal_eval(custom_filter['multi_select']):
            str_val = req_data.get(key, '')
            user_filter_values.update({key: str_val})
        else:
            if pagination == True:
                str_val = req_data.get(key, '')
                if str_val != '':
                    user_filter_values.update({key: ast.literal_eval(str_val)})
                else:
                    user_filter_values.update({key: str_val})
            else:
                str_val = req_data.getlist(key, '')
                user_filter_values.update({key: str_val})
    user_location_data = request.session['user_location_data'] if 'user_location_data' in request.session else None
    user_location_dict = request.session['user_location_dict'] if 'user_location_dict' in request.session else None
    zone_list,state_list,district_list,donor_list,partner_list,camp_list,vision_center_list,user_filter_values = get_location_data(request,user_filter_values)
    loc_data = None
    # print(user_location_data)
    for i in display_order:
        filter_values.append([])
    for k in filter_keys:
        data_list = []
        filter_display_order = -1
        if k in display_order:
            filter_display_order = display_order.index(k)
        if k == 'zone':
            data_id = user_filter_values.get('zone', '')
            data_list = zone_list    
            filter_type = 'select'
        elif k == 'state':
            data_id = ''
            if user_filter_values.get('state', '') != '':
                data_id_list = [id.strip("' ") for id in user_filter_values.get('state').split(',')]
                if len(data_id_list) == 1:
                    data_id = user_filter_values.get('state', '')
            data_list = state_list    
            filter_type = 'select'
        elif k == 'district':
            data_id = user_filter_values.get('district', '')
            state_id = user_filter_values.get('state', '')
            if state_id != '':
                state_id_list = [id.strip("' ") for id in user_filter_values.get('state').split(',')]
                get_district_filter = District.objects.filter(state_id__in=state_id_list, status=2).values_list('id', 'name').order_by('name')
                append_district =[data_list.append(i) for i in get_district_filter]
            filter_type = 'select'
        elif k == 'model_type':
            data_id = user_filter_values.get('model_type', '')
            if custom_filter[k] == '2':
                data_list = [("'2'",'Camp')]
                user_filter_values.update({'model_type':"'2'"})
            elif custom_filter[k] == '3':
                data_list = [("'3'",'Static Centre')]
                user_filter_values.update({'model_type':"'3'"})
            elif custom_filter[k] == '':
                data_list = [("'2','3'",'Both'),("'2'",'Camp'),("'3'",'Static Centre')]
            filter_type = 'select'
        elif k == 'donor_name':
            data_id = user_filter_values.get('donor_name', '')
            data_list = donor_list
            filter_type = 'select'
        elif k == 'camp_name':
            data_id = user_filter_values.get('camp_name', '') 
            model_type = user_filter_values.get('model_type', '')
            if model_type == '':
                if custom_filter[k] == '2':
                    data_list = camp_list
                elif custom_filter[k] == '3':
                    data_list = vision_center_list
                elif custom_filter[k] == '':
                    data_list = camp_list + vision_center_list
            else:
                if model_type == "'2'":
                    data_list = camp_list
                elif model_type == "'3'":
                    data_list = vision_center_list
                elif model_type == "'2','3'":
                    data_list = camp_list + vision_center_list
            filter_type = 'multi-select'
        elif k == 'vision_center':
            data_id = user_filter_values.get('vision_center', '')
            data_list = vision_center_list
            filter_type = 'multi-select'
        elif k == 'hospital_name':
            data_id = user_filter_values.get('hospital_name', '')
            data_list = partner_list
            filter_type = 'multi-select'
        elif k == 'from_date':
            data_id = user_filter_values.get('from_date', '')
            if data_id == '':
                if custom_filter[k] == 'today_date':
                    today_date_obj = datetime.datetime.now()
                    yes_date = today_date_obj - timedelta(days=1)
                    data_id = yes_date.strftime('%Y-%m-%d')
                    user_filter_values.update({'from_date': f'{data_id}'})
            user_filter_values.update({'from_date':f'{data_id}'})
            filter_type = 'date'
        elif k == 'to_date':
            data_id = user_filter_values.get('to_date', '')
            if data_id == '':
                today_date_obj = datetime.datetime.now()
                yes_date = today_date_obj - timedelta(days=1)
                data_id = yes_date.strftime('%Y-%m-%d')
                user_filter_values.update({'to_date': f'{data_id}'})
            filter_type = 'date'

        elif k == 'efrom_date':
            data_id = user_filter_values.get('efrom_date', '')
            if data_id == '':
                if custom_filter[k] == 'today_date':
                    today_date_obj = datetime.datetime.now()
                    data_id = today_date_obj.strftime('%Y-%m-%d')
                    user_filter_values.update({'efrom_date':f'{data_id}'})
            user_filter_values.update({'efrom_date':f'{data_id}'})
            filter_type = 'dates'
        elif k == 'eto_date':
            data_id = user_filter_values.get('eto_date', '')
            if data_id == '':
                today_date_obj = datetime.datetime.now()
                data_id = today_date_obj.strftime('%Y-%m-%d')
                user_filter_values.update({'eto_date':f'{data_id}'})
            filter_type = 'dates'
        elif k == 'mdfrom_month':
            data_id = user_filter_values.get('mdfrom_month', '')
            if data_id == '':
                today_date_obj = datetime.datetime.now()
                data_id = today_date_obj.strftime('%Y-%m')
                user_filter_values.update({'mdfrom_month':f'{data_id}'})
            filter_type = 'mmyy_date'
        elif k == 'mfrom_month':
            data_id = user_filter_values.get('mfrom_month', '')
            if data_id == '':
                today_date_obj = datetime.datetime.now()
                data_id = today_date_obj.strftime('%Y-%m')
                user_filter_values.update({'mfrom_month':f'{data_id}'})
            user_filter_values.update({'mdfrom_month':f'{data_id}'})
            filter_type = 'mmyy_date'
        elif k == 'mto_month':
            data_id = user_filter_values.get('mto_month', '')
            if data_id == '':
                today_date_obj = datetime.datetime.now()
                data_id = today_date_obj.strftime('%Y-%m')
                user_filter_values.update({'mto_month':f'{data_id}'})
            filter_type = 'mmyy_date'
        elif k == 'patient_id': 
            data_id = user_filter_values.get('patient_id', '')
            filter_type = 'hidden_text'
        elif k == 'patient_name':
            data_id = user_filter_values.get('patient_name', '')
            filter_type = 'hidden_text'
        elif k == 'gender':
            data_id = user_filter_values.get('gender', '')
            data_list = [('1','Male'),('2','Female')]
            filter_type = 'hidden_select'
        elif k == 'occupation':
            data_id = user_filter_values.get('occupation', '')
            data_list = [('15','Driver'),('16','Cleaner'),('17','Mechanic'),('18','Others')]
            filter_type = 'hidden_select'
        elif k == 'eye_problem':
            data_id = user_filter_values.get('eye_problem', '')
            data_list = [('123','Cataract'),('124','Cataract with spectacles'),('125','Conjunctivitis'),('126','Color blind'),('127','Corneal Ulcer'),('128','Foreign body'),('129','Infection'),
            ('130','Itching'),('131','Red Eye'),('132','NA'),('133','Refractive Error')]
            filter_type = 'hidden_select'
        elif k == 'refractive_error':
            data_id = user_filter_values.get('refractive_error', '')
            data_list = [('119','Near'),('120','Distance'),('121','Bi-focal')]
            filter_type = 'hidden_select'
        elif k == 'spectacle_status':
            data_id = user_filter_values.get('spectacle_status', '')
            data_list = [('1','Pending'),('2','Ready'),('3','Delivered')]
            filter_type = 'hidden_select'
        elif k == 'spectacles_type':
            data_id = user_filter_values.get('spectacles_type', '')
            data_list = [('99','Near only'),('100','Near + R2C'),('101','Near + Custom made'),('226','Custom'),('227','R2C')]
            filter_type = 'hidden_select'
        if filter_display_order == -1:
            filter_values.append([k, data_list, data_id, f_labels.get(k, ''), filter_type])
        else:
            filter_values[filter_display_order] = [k, data_list, data_id, f_labels.get(k, ''), filter_type]
    return user_location_data, filter_values, user_filter_values,state_list,donor_list,partner_list


def set_sort_options(req_data, idx, s_info, default_sort):
    sort_field = req_data.get('sort_field_'+str(idx), '')
    sort_order = req_data.get('sort_order_'+str(idx), 'asc')
    # set the default sort order if configured in the report_query section - key : default_sort and value is a dict with sort_order and sort_fields
    # "default_sort":{"sort_field":"classification","sort_order":"asc"}
    if default_sort:
        if 'sort_field' in default_sort and sort_field == '':
            sort_field = default_sort.get('sort_field', '')
        if 'sort_order' in default_sort and sort_field != '':
            sort_order = default_sort.get('sort_order', 'asc')
    elif sort_field == '':
        # when default sort not specified, set the sort field to first key in the list and order to asc
        for key in s_info:
            sort_field = s_info.get(key, '')
            sort_order = 'asc'
            break
    return sort_field, sort_order


def apply_filters_to_query(data_query, count_query,unique_count_query,filter_info, sort_field, sort_order,user_filter_values, current_page, rows_per_page, export_flag):
    # apply filters and sort conditions to query
    filter_cond = filter_info['filter_cond']
    for key in filter_cond.keys():
        if key not in ['camp_name','vc_name','hospital_name']:
            filter_value = user_filter_values.get(key)
            updated_cond = ''
            if filter_value != None and filter_value != '' and filter_value != '0':
                updated_cond = filter_cond[key].replace(
                    '@@filter_value', filter_value)
            data_query = data_query.replace('@@'+key+'_filter', updated_cond)
            count_query = count_query.replace('@@'+key+'_filter', updated_cond)
            unique_count_query = unique_count_query.replace('@@'+key+'_filter', updated_cond)
        elif key == 'hospital_name':
            filter_value = user_filter_values.get(key)
            updated_cond = ''
            if filter_value != None and filter_value != '' and filter_value != '0' and filter_value != [''] and filter_value != ['0']:
                updated_cond = filter_cond[key].replace(
                    '@@filter_value', str(filter_value)[1:-1])
            data_query = data_query.replace('@@'+key+'_filter', updated_cond)
            count_query = count_query.replace('@@'+key+'_filter', updated_cond)
            unique_count_query = unique_count_query.replace('@@'+key+'_filter', updated_cond)
        else:
            user_vc_camp_val = user_filter_values['camp_name']
            updated_cond = ''
            if user_vc_camp_val != None and user_vc_camp_val != '' and user_vc_camp_val != ['0'] and user_vc_camp_val != ['']:
                camp_val,vc_val =[],[]
                for val in user_vc_camp_val:
                    if val.split('-')[1] == '2':
                        camp_val.append(val.split('-')[0])
                    else:
                        vc_val.append(val.split('-')[0])
                if len(camp_val) != 0 and len(vc_val) == 0 and key == 'camp_name':
                    updated_cond = filter_cond[key].replace('@@filter_value', str(camp_val)[1:-1])
                    data_query = data_query.replace('@@'+key+'_filter', updated_cond).replace('@@vc_name_filter', '')
                    count_query = count_query.replace('@@'+key+'_filter', updated_cond).replace('@@vc_name_filter', '')
                    unique_count_query = unique_count_query.replace('@@'+key+'_filter', updated_cond).replace('@@vc_name_filter', '')
                if len(vc_val) != 0 and len(camp_val) == 0 and key == 'vc_name':
                    updated_cond = filter_cond['vc_name'].replace('@@filter_value', str(vc_val)[1:-1])
                    data_query = data_query.replace('@@'+key+'_filter', updated_cond).replace('@@camp_name_filter', '')
                    count_query = count_query.replace('@@'+key+'_filter', updated_cond).replace('@@camp_name_filter', '')
                    unique_count_query = unique_count_query.replace('@@'+key+'_filter', updated_cond).replace('@@camp_name_filter', '')
                if len(vc_val) != 0 and len(camp_val) != 0:
                    cam_vc_updated_cond = filter_cond['camp_vc'].replace('@@cfilter_value', str(camp_val)[1:-1]).replace('@@vfilter_value', str(vc_val)[1:-1])
                    data_query = data_query.replace('@@camp_name_filter', '').replace('@@vc_name_filter', cam_vc_updated_cond)
                    count_query = count_query.replace('@@camp_name_filter', '').replace('@@vc_name_filter', cam_vc_updated_cond)
                    unique_count_query = unique_count_query.replace('@@camp_name_filter', '').replace('@@vc_name_filter', cam_vc_updated_cond)
            else:
                data_query = data_query.replace('@@'+key+'_filter', updated_cond)
                count_query = count_query.replace('@@'+key+'_filter', updated_cond)
                unique_count_query = unique_count_query.replace('@@'+key+'_filter', updated_cond)
    limits_query = ''
    if export_flag is None or export_flag == False:
        limits_query = ' LIMIT ' + \
            str(rows_per_page) + ' OFFSET ' + \
            str(rows_per_page*(current_page-1))
    else:
        data_query = data_query.replace('<br/>', '')
    data_query = data_query.replace('@@LIMITS', limits_query)
    sortings = ''
    if sort_field != None and sort_field != '':
        sort_order = '' if sort_order == None else sort_order
        sortings = ' order by ' + sort_field + ' ' + sort_order + ' '
    data_query = data_query.replace('@@sortings', sortings)
    return data_query, count_query , unique_count_query


def download_excel(request,report_id):
    month=request.GET.get('month', '')
    year=request.GET.get('year', '')
    patient_registered_date = ''
    screening_registered_date = ''
    glass_registered_date = ''
    fm_registered_date = ''
    sight_registered_date = ''
    if month and year:
        filter_date = "'"+year +"-"+month+"'" if len(month) == 2 else "'"+year +"-0"+month+"'"
        patient_registered_date ='''and to_char(to_date(p.registered_date,'YYYY-MM-DD'),'YYYY-MM')='''+filter_date+''' '''
        dash_repo_date ='''and to_char(to_date(p.created_date,'YYYY-MM-DD'),'YYYY-MM')='''+filter_date+''' '''
        dash_gp_repo_date = '''and to_char(p.created_date,'YYYY-MM')='''+filter_date+''' '''
        screening_registered_date ='''and to_char(scr.created_date_scr,'YYYY-MM'::text)='''+filter_date+''' '''
        glass_registered_date ='''and to_char(gp.created_date_gp, 'YYYY-MM'::text)='''+filter_date+''' '''
        fm_registered_date ='''and to_char(fm.app_created_at, 'YYYY-MM'::text)='''+filter_date+''' '''
        sight_registered_date ='''and to_char(to_date(p.registered_date,'YYYY-MM-DD'),'YYYY-MM')='''+filter_date+''' '''
        testing_report_date = '''and to_char(p.app_created_at,'YYYY-MM')='''+filter_date+''' '''

            
    if report_id == '1':
        report_name = 'vision_camp_details'
        data = return_sql_results("""
        with vc as (select 1 as model_type,'VC' as model,vc.id as model_id,vc.name as model_name,vc.address as address,vc.partner_id,p.name as partner_name,p.state_id as state_id,s.name as state_name,s.zone_id as zonal_id,z.name as zonal_name from master_data_visioncenter vc inner join master_data_partner p on p.id = vc.partner_id inner join master_data_state s on s.id = p.state_id inner join master_data_zone z on z.id=s.zone_id), camp as (select 2 as model_type,'Camp' as model,c.id as model_id,c.name as model_name,c.address as address,c.partner_id,p.name,p.state_id,s.name,s.zone_id,z.name from sims_camp c left join master_data_partner p on p.id = c.partner_id left join master_data_state s on s.id = p.state_id left join master_data_zone z on z.id=s.zone_id)select * from vc union all select * from camp
        """)
        headers = ['Model Type','Model Type Name','Model ID','Model Name', 'Address', 'Partner ID', 'Partner Name', 'State ID', 'State Name', 'Zonal ID', 'Zonal Name']
    if report_id == '2':
        report_name = 'zonal_user_details'
        data = return_sql_results("""
        select u.username as user_name,(case when up.role_id=8 then 'PPA' when up.role_id =9 then 'Zonal Coordinator' when up.role_id = 10 then 'Zonal Incharge' else '-' end) as user_role,usl.user_id as user_id,z.id as zone_id,z.name as zonal_name,us.state_id as state_id,s.name as state_name,p.id as partner_id,p.name as partner_name from master_data_applicationuserstatelinkage_state us inner join master_data_applicationuserstatelinkage usl on usl.id = us.applicationuserstatelinkage_id inner join master_data_userprofile up on up.user_id = usl.user_id inner join auth_user u on u.id=usl.user_id inner join master_data_partner p on p.state_id = us.state_id inner join master_data_state s on s.id = us.state_id inner join master_data_zone z on z.id=s.zone_id
        """)
        headers = ['User Name','User Role','User ID','Zonal ID', 'Zonal Name','State ID', 'State Name','Partner ID', 'Partner Name']
    if report_id == '3':
        report_name = 'patient_details'
        p_headers,p_data = return_sql_results_columns("""
                            
                            SELECT p.patient_uuid,
                                p.patient_unique_id,
                                p.patient_id,
                                p.patient_table_id,
                                p.name,
                                p.gender,
                                p.age,
                                p.registered_date,
                                p.district_id,
                                p.district_ssmis_id,                                         
                                p.job,
                                p.contact_1,
                                p.contact_2,
                                p.address,
                                p.district_name,
                                p.state_ssmis_id,                    
                                p.state_id,
                                p.state_name,
                                p.aadhar_pan_no,
                                p.residence_type_id,
                                p.residence_type_name,
                                p.qualification,
                                p.no_of_months_employed_in_a_year,
                                p.time_since_driving,
                                p.drivers_license_no,
                                p.renewal_date,
                                p.type_of_vehicle_id,
                                p.type_of_vehicle,
                                p.type_of_route_id,
                                p.vechicle_insurance,
                                p.health_insurance,
                                p.life_insurance,
                                p.how_do_you_know_about_camp,
                                p.monthly_income,
                                p.type_of_route,
                                p.created_by,
                                p.donor_id,
                                p. donar_name,
                                '' as donor_partner_district_id,        
                                '' as donor_partner_district_ssmis_id,
                                '' as donor_partner_state_id,
                                '' as donor_partner_state_ssmis_id,                                                      
                                p.camp_id,
                                p.camp_name,
                                p.camp_date,
                                p.camp_code,
                                p.camp_district,
                                p.camp_district_id,
                                p.camp_district_ssmis_id,
                                p.camp_state_id,
                                p.camp_state_ssmis_id,
                                p.camp_state,
                                p.camp_location,
                                p.camp_address,
                                p.camp_village,
                                p.camp_block,
                                p.exe_gp, 
                                p.exe_rs,
                                p.camp_opd,
                                p.camp_co_name, 
                                p.camp_co_mobile_no,
                                p.camp_donor,
                                p.camp_donor_name,
                                p.camp_donor_mobile_num,
                                p.user_profile_id,
                                p.user_id,
                                p.username,
                                p.vision_center_id,
                                p.vision_center_name,
                                p.vision_center_location,
                                p.partner_id,
                                p.partner_ssmis_id,                      
                                p.partner_location,
                                p.partner_state,
                                p.model_type,
                                p.model_type_name,
                                p.feedback
                            FROM patient_basic_info_view p
                                where 1=1 """+patient_registered_date+""" """)
                   
        s_headers,s_data = return_sql_results_columns("""
                            SELECT
                                scr.scr_id,
                                scr.scr_uuid,
                                scr.patient_uuid,
                                to_char(scr.created_date_scr, 'YYYY-MM'),
                                scr.code_description_id,
                                scr.user_id,
                                scr.diabetes, 
                                scr.hypertension, 
                                scr.smoke, 
                                scr.alcohol,
                                scr.blood_pressure, 
                                scr.blood_sugar, 
                                scr.weight, 
                                scr.height,
                                scr.total_family_members,
                                p.camp_id,
                                scr.eye_examination, 
                                scr.seeing_distant_objects, 
                                scr.judging_distance_while_driving, 
                                scr.traffic_colors, 
                                scr.seeing_while_night_driving, 
                                scr.wear_glasses_ever, 
                                scr.nearby_hospital,
                                scr.wearing_glasses_currently,
                                scr.accident_while_driving_commercial_vehicle_before, 
                                scr.accident_vehicle_in_last_twelve_months, 
                                scr.first_aid_kit, 
                                scr.if_you_are_happy_specify_in_what_way,
                                scr.owner_holding_amount,
                                scr.alter_employment,
                                scr.learn_alter_livelihood_skill,
                                scr.family_support_financially,
                                scr.medical_checkup_past_1_year,
                                scr.username,
                                scr.code_description,
                                scr.unaided_distance_re,
                                scr.unaided_near_re,
                                scr.aided_distance_re,
                                scr.aided_near_re,
                                scr.pinhole_distance_re,
                                scr.pinhole_near_re,
                                scr.color_re,
                                scr.unaided_distance_le,
                                scr.unaided_near_le,
                                scr.aided_distance_le,
                                scr.aided_near_le,
                                scr.pinhole_distance_le,
                                scr.pinhole_near_le,
                                scr.color_le,
                                scr.salary_calculated,
                                scr.what_do_non_working_months,
                                scr.are_you_happy_with_your_profession,
                                scr.waist_circumference,
                                scr.insulin_dependent_or_non_insulin_dependent,
                                scr.physical_activity,
                                scr.family_history_of_diabetes,
                                scr.type_of_hospital,
                                scr.treatment_for_refraction_id,
                                scr.treatment_for_refraction_name,
                                scr.duration_since_last_meal,
                                scr.night_sweats, 
                                scr.unexplained_weight_loss_or_loss_of_appetite,
                                scr.when_was_it_diagnosed_years,
                                scr.dosage_of_insulin,
                                scr.medication_hypertension,
                                scr.cough_for_more_than_two_weeks,
                                scr.fever_for_more_than_2_weeks,
                                scr.non_working_months,
                                scr.vsa_uuid,
                                scr.refer_for_id,
                                scr.refer_for,
                                scr.refer_to_id,
                                scr.refer_to,
                                scr.want_to_refer_1_yes_2_no,
                                scr.vision_center_id,
                                scr.vision_center_name,
                                scr.vision_center_location,
                                scr.partner_id,
                                p.partner_ssmis_id,                                                                        
                                scr.partner_location,
                                scr.partner_state,
                                scr.partner_name
                            FROM screening_info_view scr left join patient_basic_info_view p on p.patient_uuid = scr.patient_uuid
                        where 1=1 """+screening_registered_date+"""""")

        g_headers,g_data = return_sql_results_columns("""
                        SELECT
                        gp.gp_id ,
                        gp.gp_uuid,
                        gp.scr_uuid,
                        gp.spec_vision_center_id,
                        gp.spec_vision_center_location,
                        gp.spec_partner_id,
                        gp.spec_partner_name,
                        gp.sph_distance_re,
                        gp.sph_near_re,
                        gp.cyl_distance_re,
                        gp.cyl_near_re,
                        gp.axis_distance_re,
                        gp.axis_near_re,
                        gp.va_distance_re,
                        gp.va_near_re,
                        gp.sph_distance_le,
                        gp.sph_near_le,
                        gp.cyl_distance_le,
                        gp.cyl_near_le,
                        gp.axis_distance_le,
                        gp.axis_near_le,
                        gp.va_distance_le,
                        gp.va_near_le,
                        gp.frame_size,
                        gp.frame_code,
                        gp.lens_type,
                        gp.type_of_coating,
                        gp.glass_collecting_location,
                        gp.spec_type_id,
                        gp.spec_type,
                        gp.has_the_glass_collected,
                        gp.spect_uuid,
                        gp.spec_status_id,
                        gp.spec_status,
                        gp.spec_created_date,
                        gp.spec_updated_date, 
                        gp.gp_vision_center_id,
                        gp.gp_vision_center_name,
                        gp.gp_vision_center_location,
                        gp.gp_partner_id,
                        gp.gp_partner_ssmis_id,                                                                        
                        gp.gp_partner_location,
                        gp.gp_partner_state,
                        gp.gp_partner_name,
                        to_char(gp.created_date_gp, 'YYYY-MM')                         
                        FROM glass_prescription_view gp
                    where 1=1 """+glass_registered_date+"""""")
    
        f_headers,f_data = return_sql_results_columns("""
                        WITH ml_lookup AS (
                        SELECT
                            id,
                            name
                        FROM master_data_masterlookup
                    ),
                    family_members AS (
                        SELECT
                        fm.id AS fm_id,
                        fm.uuid AS fm_uuid,
                        fm.screening_uuid AS scr_uuid,
                        fm.patient_uuid AS pnt_uuid,
                        fm.patient_uuid AS pnt_uuid,
                        fm.partner_id AS fm_partner_id,
                        part.ssmis_id AS fm_partner_ssmis_id,
                        part.name AS fm_partner_name,
                        fm.vision_center_id AS fm_vision_center_id,
                        vc.name AS fm_vision_center_name,
                        fm.name AS fm_name,
                        CASE
                            WHEN fm.sex = 1 THEN 'Male'
                            WHEN fm.sex = 2 THEN 'Female'
                            WHEN fm.sex = 3 THEN 'Third gender'
                            ELSE '-'
                        END AS fm_gender,                         
                        fm.age AS fm_age,
                        ml_36.name AS relationship_to_respondent,
                        ml_37.name AS educational_qualification,
                        ml_38.name AS occupation,
                        ml_39.name AS monthly_average_income,
                        to_char(fm.app_created_at,'DD-MM-YYYY') as fm_created_date,
                        to_char(fm.app_updated_at,'DD-MM-YYYY') as fm_updated_date                                                                                                
                        FROM sims_familymember fm
                        LEFT JOIN master_data_partner part ON part.id = fm.partner_id                                                  
                        LEFT JOIN master_data_visioncenter vc ON vc.id = fm.vision_center_id
                        LEFT JOIN ml_lookup ml_36 ON ml_36.id = fm.relationship_to_respondent_id
                        LEFT JOIN ml_lookup ml_37 ON ml_37.id = fm.educational_qualification_id
                        LEFT JOIN ml_lookup ml_38 ON ml_38.id = fm.occupation_id
                        LEFT JOIN ml_lookup ml_39 ON ml_39.id = fm.monthly_average_income_id
                                                  
                    where 1=1 """+fm_registered_date+""")
                    select * from family_members
    """)

    if report_id == '4':
        report_name = 'Patient Summary - SightSavers'

        sp_headers,sp_data = return_sql_results_columns("""select p.partner_id,p.state_id,p.district_id,p.camp_id,p.registered_date as month_year,p.patient_unique_id as patientuid,p.patient_id as patientid,p.name,
        p.gender,p.age,p.camp_name as campname,p.camp_date as campdate,gp.axis_distance_le as axisdistance_le,gp.axis_distance_re as axisdistance_re,gp.axis_near_le as axisnear_le,gp.axis_near_re as axisnear_re,
        '' as amountpaid,s.traffic_colors as areyouabletoidentifythetrafficcolorseasily,s.nearby_hospital as nearby_hospital,
        s.are_you_happy_with_your_profession as areyougenerallyhappy,s.wearing_glasses_currently as areyouwearingglasscurrently,
        p.camp_block as block,s.blood_pressure as bloodpressure,s.blood_sugar as bloodsugar,gp.cyl_distance_le as cyldistance_le,
        gp.cyl_distance_re as cyldistance_re,p.camp_location as camplocation,p.camp_state as campstate,p.camp_district as campdistrict,p.camp_co_name as campcoordinator,
        p.camp_donor_name as campdonorname,p.camp_donor_mobile_num as campcoordinatormobile,gp.cyl_near_le as cylnear_le,gp.cyl_near_re as cylnear_re,'' as caste,
        s.color_le,s.color_re,p.contact_1 as contactno1 ,p.contact_2 as contactno2,p.registered_date as created_date,p.district_name as district,s.smoke as doyousmoke,
        s.alcohol as doyouconsumealcohol,s.diabetes as doyouhavediabetes,s.hypertension as doyouhavehypertension,p.health_insurance as doyouhaveanyhealthinsurancepolicy ,
        p.life_insurance as doyouhaveanylifeinsurancepolicy, p.vechicle_insurance as doyouhaveanyvehicleinsurancepolicy,
        s.judging_distance_while_driving as doyouhaveanydifficultyinjudgingdistancewhiledriving,s.seeing_distant_objects as doyouhaveanydifficultyinseeingdistantobject,
        s.seeing_while_night_driving as doyouhaveanydifficultyinseeingwhilenightdriving,s.family_support_financially as doyourfamilymembers,
        s.want_to_refer_1_yes_2_no as doyouwanttorefer ,s.what_do_non_working_months as during12months,p.qualification as eduqualification,p.camp_opd as expectedcampopd,
        p.exe_gp as expectedglassprescription,p.exe_rs as expectedrefersurgeries,p.feedback,'' as feedbackby,'' as feedbackdate,s.first_aid_kit as firstaidkittruck, gp.frame_code as framecode,gp.frame_size as framesize,
        gp.glass_collecting_location as glasscollectinglocation,gp.spec_status as glassstatus,'' as glasscollectedcamp_hospital,'' as glasscollectedcampdate, 
        gp.gp_vision_center_name as glasscollectedhospital,'' as glasscollectednode,gp.has_the_glass_collected as hastheglasscollectedatthecamp,s.wear_glasses_ever as haveyoubeenadvisedtowearglassessever,
        s.eye_examination as haveyoueverhadeyeexamination, s.medical_checkup_past_1_year as haveyouhadamedicalcheckupinthepast1year,p.partner_name as hospitalname,p.how_do_you_know_about_camp as howdoyouknowaboutcamp,
        s.are_you_happy_with_your_profession as ifyouarehappy,gp.lens_type as lenstype , p.drivers_license_no as licensenumber,s.accident_vehicle_in_last_twelve_months as metwithaccident,p.model_type_name as modeltype,
        p.monthly_income as monthlyincome,'' as nodename,p.no_of_months_employed_in_a_year as noofmonthsemployed , s.salary_calculated as onwhatbasisyoursalaryiscalculated,'' as others,'' as paymenttype,
        p.address as permanentaddress,s.pinhole_distance_re as pinholedistance_re,s.pinhole_distance_le as pinholedistance_le,s.pinhole_near_le as pinholenear_le ,s.pinhole_near_re as pinhole_near_re,
        s.refer_for as referfor,s.refer_to as referto,p.renewal_date as renewaldate,gp.sph_distance_le as sphdistance_le,gp.sph_distance_re as sphdistance_re,
        gp.sph_near_le as sphnear_le,gp.sph_near_re as sphnear_re,s.username as screenedby, p.state_name as state, p.time_since_driving as timesincedriving, 
        s.total_family_members as totalfamilymembers, s.treatment_for_refraction_name as treatmentforrefraction, gp.type_of_coating as typeofcoating, s.type_of_hospital as typeofhospital, 
        p.job as typeofjob, p.type_of_route as typeofroute, p.type_of_vehicle as typeofvehicle, s.unaided_near_re, s.unaided_distance_re as unaideddistance_re, 
        s.unaided_near_le as unaidednear_le, s.unaided_distance_re as unaidednear_re, s.unaided_distance_le as unaidednear_le, gp.va_distance_le as vadistance_le, 
        gp.va_distance_re as vadistance_re, gp.va_near_le as vanear_le, gp.va_near_re as vanear_re, p.camp_village as village, s.weight as weight, s.height as height, 
        s.alter_employment as alternativeemployment, s.learn_alter_livelihood_skill as alternativelivelihoodkill, s.owner_holding_amount as holdingbackanyamountsalary, '' as monthsnormallynotemployed, 
        s.non_working_months as nonworkingmonths, p.residence_type_name as residencetype from patient_basic_info_view p 
        left join screening_info_view s on p.patient_uuid = s.patient_uuid left join glass_prescription_view gp on s.scr_uuid = gp.scr_uuid 
        where 1=1 """+sight_registered_date+"""""")
    if report_id == '6':
        report_name = 'Patient Summary - Dash-Report-Testing'
        dash_p_headers,dash_p_data = return_sql_results_columns("""select * from dash_repo_patient_basic_info_view p where 1=1 """+dash_repo_date+""" """)
        dash_s_headers,dash_s_data = return_sql_results_columns("""select * from dash_repo_screening_info_view p where 1=1 """+dash_repo_date+""" """)
        dash_g_headers,dash_g_data = return_sql_results_columns("""select * from dash_repo_glass_prescription_view p where 1=1 """+dash_gp_repo_date+""" """)
        ps_headers,ps_data = return_sql_results_columns(""" 
        select p.*,scr.*
        from dash_repo_patient_basic_info_view p left join dash_repo_screening_info_view scr on p.patient_uuid = scr.patient_uuid left join dash_repo_glass_prescription_view gp on gp.scr_uuid = scr.scr_uuid where 1=1 """+dash_repo_date+"""
        """)
    if report_id == '5':
        report_name = 'dasboard_report_meta_table'
        # dash_p_headers,dash_p_data = return_sql_results_columns("""select * from dash_repo_patient_basic_info_view p where 1=1 """+dash_repo_date+""" """)
        # dash_s_headers,dash_s_data = return_sql_results_columns("""select * from dash_repo_screening_info_view p where 1=1 """+dash_repo_date+""" """)
        # dash_g_headers,dash_g_data = return_sql_results_columns("""select * from dash_repo_glass_prescription_view p where 1=1 """+dash_gp_repo_date+""" """)
        dash_p_headers,dash_p_data = return_sql_results_columns("""select * from sims_patient p where 1=1 and p.status = 2 """+testing_report_date+""" """)
        dash_s_headers,dash_s_data = return_sql_results_columns("""select * from sims_screening p where 1=1 and p.status = 2 """+testing_report_date+""" """)
        dash_vis_headers,dash_vis_data = return_sql_results_columns("""select s.* from sims_screening p  left join  sims_visualacuity s on p.uuid = s.screening_uuid where 1=1 and s.status = 2 and p.status = 2 """+testing_report_date+""" """)
        dash_g_headers,dash_g_data = return_sql_results_columns("""select * from sims_glassprescription p where 1=1 and p.status = 2 """+testing_report_date+""" """)
        dash_spec_headers,dash_spec_data = return_sql_results_columns("""select * from sims_spectacletype p where 1=1 and p.status = 2 """+testing_report_date+""" """)
    if report_id == '4':
        df = pd.DataFrame(sp_data,columns=sp_headers)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, sheet_name='Sheet1', engine='openpyxl')
        excel_buffer.seek(0)
        response = HttpResponse(excel_buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={report_name}_{report_id}.xlsx'
    elif report_id == '6':
        csv_files = [
        ("Patient_details.csv", dash_p_headers, dash_p_data),
        ("Screening_details.csv", dash_s_headers, dash_s_data),
        ("Glass_prescription.csv", dash_g_headers, dash_g_data),
        ("Patient_summary_data.csv", ps_headers, ps_data)
        ]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="dashboard_reports_csvfiles.zip"'
        with io.BytesIO() as zip_buffer:
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for filename, headers, data in csv_files:
                    with io.StringIO() as csv_buffer:
                        writer = csv.writer(csv_buffer)
                        writer.writerow(headers)
                        writer.writerows(data)
                        zip_file.writestr(filename, csv_buffer.getvalue())
            response.write(zip_buffer.getvalue())
    elif report_id == '5':
        csv_files = [
        ("Patient_details.csv", dash_p_headers, dash_p_data),
        ("Screening_details.csv", dash_s_headers, dash_s_data),
        ("Glass_prescription.csv", dash_g_headers, dash_g_data),
        ("Visulaactivity_details.csv", dash_vis_headers,dash_vis_data),
        ("spectacle_details.csv",dash_spec_headers,dash_spec_data)
        ]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="dashboard_reports_csvfiles.zip"'
        with io.BytesIO() as zip_buffer:
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for filename, headers, data in csv_files:
                    with io.StringIO() as csv_buffer:
                        writer = csv.writer(csv_buffer)
                        writer.writerow(headers)
                        writer.writerows(data)
                        zip_file.writestr(filename, csv_buffer.getvalue())
            response.write(zip_buffer.getvalue())
    elif report_id == '1' or report_id == '2':
        df = pd.DataFrame(data,columns=headers)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, sheet_name='Sheet1', engine='openpyxl')
        excel_buffer.seek(0)
        response = HttpResponse(excel_buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={report_name}_{report_id}.xlsx'
    else:
        df1 = pd.DataFrame(p_data, columns=p_headers)
        df2 = pd.DataFrame(s_data, columns=s_headers)
        df3 = pd.DataFrame(g_data, columns=g_headers)
        df4 = pd.DataFrame(f_data, columns=f_headers)
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df1.to_excel(writer, index=False, sheet_name='Patient_details')
            df2.to_excel(writer, index=False, sheet_name='Screening_details')
            df3.to_excel(writer, index=False, sheet_name='Glass_prescription')
            df4.to_excel(writer, index=False, sheet_name='Family_members')
        excel_buffer.seek(0)
        response = HttpResponse(excel_buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={report_name}_{report_id}.xlsx'
    return response

import calendar

def convert_to_month_name(month_number):
    try:
        month_name = calendar.month_name[int(month_number)]
        return month_name
    except (ValueError, IndexError):
        return None
    
@ login_required(login_url='/login/')
def mpr_review(request,mpr_month_year=None,status_id=None, remark=None, zone_name=None, mail=None):
    heading = 'MPR Review'
    partner_id=""
    role_id = request.session.get('role_id')
    if role_id == 9 or role_id == 8:
        user_vlu = UserProfile.objects.filter(role_id=role_id, user_id=request.user.id, status=2).values_list('user_id',flat=True)
        state_list = ApplicationUserStateLinkage.objects.filter(status=2,user_id__in=user_vlu).values_list('state', flat=True)
        partner_obj= Partner.objects.filter(state_id__in=state_list, status=2).values_list('id',flat=True)
        pnr_list = [str(x) for x in partner_obj]
        result = ', '.join(pnr_list)
        partner_id = '''and pnt.id in ('''+result+''')'''
    month=""
    year=""
    if request.GET.get('month_year'):
        month_year = request.GET.get('month_year')
        parsed_date = parser.parse(month_year)
        month = '''and mpr.month='''+parsed_date.strftime("%m")
        year = '''and mpr.year='''+parsed_date.strftime("%Y")

    # if mail == True:
    #     parsed_date = parser.parse(mpr_month_year)
    #     month = '''and mpr.month='''+parsed_date.strftime("%m")
    #     year = '''and mpr.year='''+parsed_date.strftime("%Y")
    current_date = datetime.datetime.now()
    current_month = convert_to_month_name(int(current_date.month))
    current_year = str(current_date.year)
    current_month_year= current_month + ' ' +current_year

    # Main Query
    sql = '''select mpr.id, mpr.month, mpr.year, to_char(to_date (mpr.month::text, 'MM'), 'Month') ||' '|| mpr.year as month_year, mpr.year||to_char(to_date (mpr.month::text, 'MM'), 'mm') as code, 
    pnt.id as partner_id, pnt.name as patner_name, upl.user_id, 
    us.username, st.name as state_name, st.id as state_id, 
    zn.name as zone_name, zn.id as zone_id, 
    to_char(mpr.partner_date at time zone 'Asia/Kolkata', 'DD-MM-YYYY HH12:MI:SS AM') as partner_date, to_char(mpr.zonal_coordinator_date at time zone 'Asia/Kolkata', 'DD-MM-YYYY HH12:MI:SS AM') as zonal_coordinator_date, to_char(mpr.ppa_date at time zone 'Asia/Kolkata', 'DD-MM-YYYY HH12:MI:SS AM') as ppa_date,
    to_char(mpr.national_coordinator_date at time zone 'Asia/Kolkata', 'DD-MM-YYYY HH12:MI:SS AM') as national_coordinator_date, to_char(mpr.super_admin_date at time zone 'Asia/Kolkata', 'DD-MM-YYYY HH12:MI:SS AM') as super_admin_date, 
    mpr.mpr_status as mpr_status_id, case when mpr.mpr_status=0 then 'Pending' when mpr.mpr_status=1 then 'Pending for Approval' when mpr.mpr_status=2 then 'Approved' when  mpr.mpr_status=2 then 'Rejected' else '-' end as mpr_status, 
    mpr.remark, mpr.national_remark, mpr.super_admin_remark, mpr.forward_nc_command from reports_mprstatusupdate mpr 
    inner join master_data_userpartnerlinkage upl on mpr.created_by_id=upl.user_id 
    inner join master_data_partner pnt on upl.partner_id=pnt.id
    inner join auth_user us on upl.user_id=us.id 
    inner join master_data_state st on pnt.state_id=st.id 
    inner join master_data_zone zn on st.zone_id=zn.id where 1=1 ''' + partner_id + ' ' + month + ' ' + year + ''' order by zone_id, patner_name'''

    mpr_status_obj = SqlHeader(sql)

    # all ppa forward for all to national coordinator True & False value 
    approve_all_sql = '''with zone as ('''+sql+'''), mpr_true as (select coalesce(sum(case when mpr_status_id=1 or mpr_status_id=2 or mpr_status_id=7 then 1 else 0 end),0) as count, coalesce(sum(case when mpr_status_id=2 then 1 else 0 end),0) as mpr_count from zone) select coalesce(sum(case when count=mpr_count then 0 else count end),0) as count from mpr_true'''
    approve_all_obj = SqlHeader(approve_all_sql)
    approve_all_count = False if approve_all_obj[0]['count'] != len(mpr_status_obj) else True


    # all national coordinator approved for all to super-admin True & False value
    forward_total_len_sql = '''with zone as ('''+sql+'''), mpr_true as (select coalesce(sum(case when mpr_status_id=4 or mpr_status_id=6 or mpr_status_id=9 then 1 else 0 end),0) as count, coalesce(sum(case when mpr_status_id=6 then 1 else 0 end),0) as mpr_count from zone) 
    select coalesce(sum(case when count=mpr_count then 0 else count end),0) as count from mpr_true'''
    forward_len_obj = SqlHeader(forward_total_len_sql)
    forward_all_count = False if forward_len_obj[0]['count'] != len(mpr_status_obj) else True
    
    # all super-admin Sync to ssims server True & False value
    syn_total_len_sql = '''with zone as ('''+sql+''') select coalesce(sum(case when mpr_status_id=6 then 1 else 0 end),0) as count from zone'''
    syn_len_obj = SqlHeader(syn_total_len_sql)
    syn_all_count = False if syn_len_obj[0]['count'] != len(mpr_status_obj) else True
    # used to zone base rowspan in super-admin & nation coordinator login 
    zone_sql = '''with zone as ('''+sql+''') select zone_id, count(partner_id) as pnt_count from zone group by zone_id'''
    zone_obj = SqlHeader(zone_sql)
    data = {zn['zone_id']:zn['pnt_count'] for zn in zone_obj}
    if mail == True:
        dear = 'Dear Concerned,'
        if int(status_id) == 1:
            body = 'The MPR Report for '+ mpr_month_year +' has been Submitted by '+zone_name+'.' 
        elif int(status_id) == 6:
            body = 'The MPR Report for '+ mpr_month_year +' has been Approved by National Coordinator for '+zone_name+' zone.' 
        elif int(status_id) == 8:
            body = 'The MPR Report for '+ mpr_month_year +' has been Approved by Super Admin.' 
        elif int(status_id) == 9:
            body = 'The MPR Report for '+ mpr_month_year +' has been rejected by Super admin for '+zone_name+' zone citing the following reason.' 
        else:
            body = 'The MPR Report for '+ mpr_month_year +' has been rejected by National Coordinator for '+zone_name+' zone citing the following reason.' 
        return render (request,'mailer/mpr_mailer.html', locals())
    else:
        return render (request,'reports/referral_view.html', locals())


def mpr_status_update(request, status_id,month_year):
    parsed_date = parser.parse(month_year)
    month = parsed_date.strftime("%m")
    year = parsed_date.strftime("%Y")
    mpr_order = MprStatusUpdate.objects.filter(created_by=request.user, month=int(month), year=int(year))
    partner_state = UserPartnerLinkage.objects.get(user=request.user)
    apl_obj = ApplicationUserStateLinkage.objects.filter(state=partner_state.partner.state,status=2).values_list('user', flat=True)
    user_role = UserProfile.objects.get(role_id=9,user_id__in=apl_obj, status=2).user.email
    send_mail_res = mpr_review(request, month_year, status_id, None, partner_state.partner.name, mail=True)
    html_content = send_mail_res.content.decode("utf-8")
    send_mail_response = mpr_status_mailer(month_year, int(status_id),user_role, html_content)
    mpr_order.update(mpr_status = status_id,partner_date = datetime.datetime.now())
    return redirect('/report/truc-month-report/month/?month_year='+str(month_year))


def mpr_status_approve(request, status_id, id):
    month_year = request.GET.get('month_year') 
    mpr_order = MprStatusUpdate.objects.get(id=id)
    mpr_order.mpr_status = status_id
    mpr_order.approved_by = request.user
    mpr_order.modified_by=request.user
    mpr_order.remark = None
    mpr_order.zonal_coordinator_date = datetime.datetime.now()
    mpr_order.save()
    return redirect('/mpr/report/mpr-review/?month_year='+str(month_year))


def mpr_status_reject(request, reject_id, id, remark):
    month_year = request.GET.get('month_year') 
    mpr_order = MprStatusUpdate.objects.get(id=id)
    mpr_order.mpr_status = reject_id
    mpr_order.approved_by = request.user
    mpr_order.modified_by=request.user
    mpr_order.remark = remark
    mpr_order.zonal_coordinator_date = datetime.datetime.now()
    mpr_order.save()
    return redirect('/mpr/report/mpr-review/?month_year='+str(month_year))

    
def national_status_approve(request, status_id, month_year, zone_id):
    parsed_date = parser.parse(month_year)
    month = parsed_date.strftime("%m")
    year = parsed_date.strftime("%Y")
    user_vlu = UserProfile.objects.filter(role_id=9, status=2)
    apl_obj = ApplicationUserStateLinkage.objects.filter(user_id__in=user_vlu.values_list('user_id',flat=True),status=2)
    partner_user = Partner.objects.filter(state_id__in=apl_obj.values_list('state', flat=True),status=2)
    user_partner_details = UserPartnerLinkage.objects.filter(partner_id__in=partner_user.filter(state__zone_id=zone_id).values_list('id', flat=True))
    mpr_orders = MprStatusUpdate.objects.filter(created_by__in=user_partner_details.values_list('user_id', flat=True),month=int(month), year=int(year))
    if int(status_id) == 6:
        zone_name = Zone.objects.get(id=zone_id).name
        email = UserProfile.objects.get(role_id=12, status=2, id=9).user.email
        send_mail_res = mpr_review(request, month_year, status_id, None, zone_name, mail=True)
        html_content = send_mail_res.content.decode("utf-8")
        send_mail_response = mpr_status_mailer(month_year, int(status_id), email, html_content)
        mpr_orders.update(mpr_status=status_id, forward_to_super_admin_by=request.user,modified_by=request.user, national_coordinator_date=datetime.datetime.now(), national_remark=None)
    else:
        zone_name = Zone.objects.get(id=zone_id).name
        email = UserProfile.objects.get(role_id=3, status=2).user.email
        send_mail_res = mpr_review(request, month_year, status_id, None, zone_name, mail=True)
        html_content = send_mail_res.content.decode("utf-8")
        send_mail_response = mpr_status_mailer(month_year, int(status_id), email, html_content)
        mpr_orders.update(mpr_status=status_id, ssims_user=request.user,modified_by=request.user, super_admin_date=datetime.datetime.now(), super_admin_remark=None)
    return redirect('/mpr/report/mpr-review/?month_year='+str(month_year))

def national_status_reject(request, status_id, month_year, remark, zone_id):
    parsed_date = parser.parse(month_year)
    month = parsed_date.strftime("%m")
    year = parsed_date.strftime("%Y")
    user_vlu = UserProfile.objects.filter(role_id=9, status=2).values_list('user_id',flat=True)
    apl_obj = ApplicationUserStateLinkage.objects.filter(user_id__in=user_vlu,status=2)
    partner_user = Partner.objects.filter(state_id__in=apl_obj.filter(state__zone_id=zone_id).values_list('state', flat=True),status=2)
    user_partner_details = UserPartnerLinkage.objects.filter(partner_id__in=partner_user.values_list('id', flat=True))
    mpr_orders = MprStatusUpdate.objects.filter(created_by__in=user_partner_details.values_list('user_id', flat=True),month=int(month), year=int(year))
    if int(status_id) == 7:
        partner_value_list = UserPartnerLinkage.objects.filter(user_id__in=mpr_orders.values_list('created_by_id',flat=True)).values_list('partner_id', flat=True)
        state_list = Partner.objects.filter(id__in=partner_value_list).values_list('state_id',flat=True)
        apl_state_ids=ApplicationUserStateLinkage.objects.filter(state__in=state_list).values_list('state', flat=True)
        zone_list = State.objects.filter(id__in=apl_state_ids).distinct('zone_id')
        for zn in zone_list:
            state_ids = State.objects.filter(zone_id=zn.zone_id).values_list('id', flat=True)
            apl_user_ids=ApplicationUserStateLinkage.objects.filter(state__in=state_ids)
            user_zone_email = UserProfile.objects.filter(role_id=9, user_id__in=apl_user_ids.filter(state__zone_id=zone_id).values_list('user_id', flat=True), status=2).first().user.email
            user_ppa_email = UserProfile.objects.filter(role_id=8, user_id__in=apl_user_ids.filter(state__zone_id=zone_id).values_list('user_id', flat=True), status=2).first().user.email
            if user_vlu:
                send_mail_res = mpr_review(request, month_year, status_id, remark, zn.zone.name, mail=True)
                html_content = send_mail_res.content.decode("utf-8")
                send_mail_response = mpr_status_mailer(month_year, int(status_id),user_zone_email, html_content)
                mpr_orders.update(mpr_status=status_id, forward_to_super_admin_by=request.user, modified_by=request.user,national_coordinator_date=datetime.datetime.now(), national_remark=remark)

            if user_ppa_email:
                send_mail_res = mpr_review(request, month_year, status_id, remark, zn.zone.name, mail=True)
                html_content = send_mail_res.content.decode("utf-8")
                send_mail_response = mpr_status_mailer(month_year, int(status_id),user_ppa_email, html_content)
                mpr_orders.update(mpr_status=status_id, forward_to_super_admin_by=request.user, modified_by=request.user,national_coordinator_date=datetime.datetime.now(), national_remark=remark)

    else:
        try:
            user = UserProfile.objects.filter(role_id=3, status=2).first().user
        except:
            user = ''
        zone_name = Zone.objects.get(id=zone_id).name
        send_mail_res = mpr_review(request, month_year, status_id, remark, zone_name, mail=True)
        html_content = send_mail_res.content.decode("utf-8")
        send_mail_response = mpr_status_mailer(month_year, int(status_id), user.email, zone_name, html_content)
        mpr_orders.update(mpr_status=status_id, ssims_user= request.user,modified_by=request.user,super_admin_date=datetime.datetime.now(), super_admin_remark=remark)
    return redirect('/mpr/report/mpr-review/?month_year='+str(month_year))

def ppa_mpr_status_update(request, zone_id, month_year, command):
    forward_nc_command = command if command != '0' else None
    parsed_date = parser.parse(month_year)
    month = parsed_date.strftime("%m")
    year = parsed_date.strftime("%Y")
    user_vlu = UserProfile.objects.filter(role_id=9, status=2).values_list('user_id',flat=True)
    state_zone = State.objects.filter(zone_id=zone_id)
    apl_obj = ApplicationUserStateLinkage.objects.filter(state__in=state_zone, status=2, user_id__in=user_vlu,)
    partner_user = Partner.objects.filter(state_id__in=apl_obj.values_list('state', flat=True),status=2)
    user_partner_details = UserPartnerLinkage.objects.filter(partner_id__in=partner_user.values_list('id', flat=True))
    mpr_orders = MprStatusUpdate.objects.filter(created_by__in=user_partner_details.values_list('user_id', flat=True),month=int(month), year=int(year))
    mpr_orders.update(mpr_status=4, forward_by=request.user,modified_by=request.user, ppa_date=datetime.datetime.now(), forward_nc_command=forward_nc_command)
    return redirect('/mpr/report/mpr-review/?month_year='+str(month_year))

def approve_all(request, key, month_year):
    parsed_date = parser.parse(month_year)
    month = parsed_date.strftime("%m")
    year = parsed_date.strftime("%Y")
    if int(key) == 1:
        user_vlu = UserProfile.objects.filter(role_id=9, user_id=request.user.id, status=2).values_list('user_id',flat=True)
        apl_obj = ApplicationUserStateLinkage.objects.filter(status=2, user_id__in=user_vlu)
        partner_user = Partner.objects.filter(state_id__in=apl_obj.values_list('state', flat=True),status=2)
        user_partner_details = UserPartnerLinkage.objects.filter(partner_id__in=partner_user.values_list('id', flat=True))
        mpr_orders = MprStatusUpdate.objects.filter(created_by__in=user_partner_details.values_list('user_id', flat=True),month=int(month), year=int(year))
        mpr_orders.update(mpr_status=2, remark=None, approved_by=request.user, modified_by=request.user, zonal_coordinator_date=datetime.datetime.now())
    else:
        user_vlu = UserProfile.objects.filter(role_id=9, status=2).values_list('user_id',flat=True)
        apl_obj = ApplicationUserStateLinkage.objects.filter(status=2, user_id__in=user_vlu)
        partner_user = Partner.objects.filter(state_id__in=apl_obj.values_list('state', flat=True),status=2)
        user_partner_details = UserPartnerLinkage.objects.filter(partner_id__in=partner_user.values_list('id', flat=True))
        mpr_orders = MprStatusUpdate.objects.filter(created_by__in=user_partner_details.values_list('user_id', flat=True),month=int(month), year=int(year))
        if int(key) == 2:
            email = UserProfile.objects.get(role_id=12, status=2, id=9).user.email
            send_mail_res = mpr_review(request, month_year, 6, None, 'All', mail=True)
            html_content = send_mail_res.content.decode("utf-8")
            send_mail_response = mpr_status_mailer(month_year, 6,email, html_content)
            mpr_orders.update(mpr_status=6, national_remark=None, forward_to_super_admin_by=request.user, modified_by=request.user, national_coordinator_date=datetime.datetime.now())
        else:
            email = UserProfile.objects.get(role_id=3, status=2).user.email
            send_mail_res = mpr_review(request, month_year, 6, None, 'All', mail=True)
            html_content = send_mail_res.content.decode("utf-8")
            send_mail_response = mpr_status_mailer(month_year, 6,email, html_content)
            mpr_orders.update(mpr_status=8,  super_admin_date=datetime.datetime.now(), ssims_user=request.user, modified_by=request.user, super_admin_remark=None)
    return redirect('/mpr/report/mpr-review/?month_year='+str(month_year))


def mpr_status_mailer(month_year, status, email, html_message, isTls=True):
    import smtplib
    import os
    from django.conf import settings
    from weasyprint import HTML, CSS
    from email.mime.image import MIMEImage
    try:
        msg = MIMEMultipart()
        msg2 = MIMEMultipart()
        parsed_date = parser.parse(month_year)
        month = parsed_date.strftime("%m")
        year = parsed_date.strftime("%Y")
        
        

        msg['From'] = "misindia@sightsaversindia.org"
        msg['To'] = email
        if status in [6,8]:
            msg['Subject'] = 'MPR Approved'
        elif status == 1:
            msg['Subject'] = 'MPR Submitted'
        else: 
            msg['Subject'] = 'MPR Rejected' 
        
        part1=MIMEText(html_message, 'html')
        msg.attach(part1)
       
        smtp = smtplib.SMTP(settings.EMAIL_HOST,settings.EMAIL_PORT)

        if isTls:
            smtp.starttls()
        smtp.login(settings.EMAIL_HOST_USER,settings.EMAIL_HOST_PASSWORD)

        msg_send_status = smtp.sendmail(msg['From'], msg['To'] ,msg.as_string())
        smtp.quit()
        return msg_send_status
    except Exception as e:
        # logger.error(e.args[0])
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        errors = str(error_stack) 
        logger.error(errors)


def generate_trucker_mpr():
    from datetime import datetime
    start_time = datetime.now()
    try:
        year = datetime.now().year
        prev_month = datetime.now().month - 1 
        if prev_month == 0:
            year -= 1
            prev_month = 12
        truckers = return_sql_results(f"""
            select generate_truckers_mpr({year},{prev_month})
            """)
        print(' TRUCKERS MPR GENERATED ')
        end_time = datetime.now()
        duration = end_time - start_time
        time_output = format_duration(duration)

        logdata, created = CronJobSummaryLog.objects.get_or_create(
            log_key='generate_mpr')
        logdata.last_successful_update = start_time
        logdata.most_recent_update = end_time
        logdata.most_recent_update_status = 'Success'
        logdata.most_recent_update_time_taken_millis = time_output
        logdata.error = "-"
        logdata.save()
    except Exception as e:
        now = datetime.now()
        end_time = datetime.now()
        duration = end_time - start_time
        time_output = format_duration(duration)

        print(' TRUCKERS MPR NOT GENERATED ')
        logdata, created = CronJobSummaryLog.objects.get_or_create(
            log_key='generate_mpr')
        logdata.last_successful_update = start_time
        logdata.most_recent_update = end_time
        logdata.most_recent_update_status = 'False'
        logdata.most_recent_update_time_taken_millis = time_output
        logdata.error = e.args[0]
        logdata.save()
