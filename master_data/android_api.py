from . models import * 
from reports.models import * 
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
import json
from django.db import transaction
from rest_framework.views import APIView 
from rest_framework.response import Response
from django.conf import settings
from . serializer import * 
from django.http import JsonResponse
from datetime import datetime
import  logging
from django.db import connection
import sys, traceback
from datetime import datetime, timedelta
import requests
import random
import re

# from urllib2 import Request, urlopen

batch_rec = settings.BATCH_RECORDS

logger = logging.getLogger(__name__)
from django.utils import timezone

class MPRData(APIView):
    def post(self,request):
        data = request.data
        if data.get('year') and data.get('month'):
            month = data.get('month')
            year = data.get('year')
            # return_sql_results(f"select generate_truckers_mpr({year}, {month});")
            if data.get('type_of_column') == 1:
                mpr_data = return_sql_results(f""" SELECT
                jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_1_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_1_till_date
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_2_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_2_till_date
                    )
                ) AS mpr_data
            FROM (
                SELECT
                    vision_center_id,
                    partner_id,
                    ssmis_id,
                    state_id,
                    district_id,
                    donor_id,
                    mpr_month,
                    mpr_year,
                    i_1_metric_code,
                    i_2_metric_code,
                    sum(i_1_achive_till_date) AS i_1_till_date,
                    sum(i_2_achive_till_date) AS i_2_till_date
                FROM reports_truckermpr where 1=1 and mpr_month='{month}' and mpr_year='{year}' and mpr_status=8 and partner_id != 0
                GROUP BY
                    vision_center_id,
                    partner_id,
                    ssmis_id,
                    state_id,
                    district_id,
                    donor_id,
                    mpr_month,
                    mpr_year,
                    i_1_metric_code,
                    i_2_metric_code
            ) x
            GROUP BY
                vision_center_id,
                partner_id,
                ssmis_id,
                state_id,
                district_id,
                donor_id,
                mpr_month,
                mpr_year
            ORDER BY vision_center_id
            """)
            if data.get('type_of_column') == 2:
                mpr_data = return_sql_results(f""" SELECT
                jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_3_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_3_male,
                        'two_column_value', i_3_female
                        
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_4_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_4_male,
                        'two_column_value', i_4_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_5_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_5_male,
                        'two_column_value', i_5_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_6_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_6_male,
                        'two_column_value', i_6_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_7_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_7_male,
                        'two_column_value', i_7_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_8_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_8_male,
                        'two_column_value', i_8_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_9_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_9_male,
                        'two_column_value', i_9_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_10_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_10_male,
                        'two_column_value', i_10_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_11_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_11_male,
                        'two_column_value', i_11_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_12_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_12_male,
                        'two_column_value', i_12_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_13_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_13_male,
                        'two_column_value', i_13_female
                    )
                ) AS mpr_data
            FROM (
                SELECT
                    vision_center_id,
                    partner_id,
                    ssmis_id,
                    state_id,
                    district_id,
                    donor_id,
                    mpr_month,
                    mpr_year,
                    i_3_metric_code,
                    i_4_metric_code,
                    i_5_metric_code,
                    i_6_metric_code,
                    i_7_metric_code,
                    i_8_metric_code,
                    i_9_metric_code,
                    i_10_metric_code,
                    i_11_metric_code,
                    i_12_metric_code,
                    i_13_metric_code,
                    sum(i_3_achive_male) AS i_3_male,
                    sum(i_3_achive_female) AS i_3_female,
                    sum(i_4_achive_male) AS i_4_male,
                    sum(i_4_achive_female) AS i_4_female,
                    sum(i_5_achive_male) AS i_5_male,
                    sum(i_5_achive_female) AS i_5_female,
                    sum(i_6_achive_male) AS i_6_male,
                    sum(i_6_achive_female) AS i_6_female,
                    sum(i_7_achive_male) AS i_7_male,
                    sum(i_7_achive_female) AS i_7_female,
                    sum(i_8_achive_male) AS i_8_male,
                    sum(i_8_achive_female) AS i_8_female,
                    sum(i_9_achive_male) AS i_9_male,
                    sum(i_9_achive_female) AS i_9_female,
                    sum(i_10_achive_male) AS i_10_male,
                    sum(i_10_achive_female) AS i_10_female,
                    sum(i_11_achive_male) AS i_11_male,
                    sum(i_11_achive_female) AS i_11_female,
                    sum(i_12_achive_male) AS i_12_male,
                    sum(i_12_achive_female) AS i_12_female,
                    sum(i_13_achive_male) AS i_13_male,
                    sum(i_13_achive_female) AS i_13_female
                FROM reports_truckermpr 
                where 1=1 and mpr_month='{month}' and mpr_year='{year}' and mpr_status=8 and partner_id != 0
                GROUP BY
                    vision_center_id,
                    partner_id,
                    ssmis_id,
                    state_id,
                    district_id,
                    donor_id,
                    mpr_month,
                    mpr_year,
                    i_3_metric_code,
                    i_4_metric_code,
                    i_5_metric_code,
                    i_6_metric_code,
                    i_7_metric_code,
                    i_8_metric_code,
                    i_9_metric_code,
                    i_10_metric_code,
                    i_11_metric_code,
                    i_12_metric_code,
                    i_13_metric_code
            ) x
            GROUP BY
                vision_center_id,
                partner_id,
                ssmis_id,
                state_id,
                district_id,
                donor_id,
                mpr_month,
                mpr_year
            ORDER BY vision_center_id
            """)
            if data.get('type_of_column') == 3:
                mpr_data = return_sql_results(f"""SELECT
                jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_18_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_18_male,
                        'two_column_value', i_18_female,
                        'three_column_value', i_19_male,
                    'four_column_value', i_19_female

                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_20_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_20_male,
                        'two_column_value', i_20_female,
                        'three_column_value', i_21_male,
                    'four_column_value', i_21_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_22_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_22_male,
                        'two_column_value', i_22_female,
                        'three_column_value', i_23_male,
                    'four_column_value', i_23_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_24_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_24_male,
                        'two_column_value', i_24_female,
                        'three_column_value', i_25_male,
                    'four_column_value', i_25_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_30_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', 0,
                        'two_column_value', 0,
                        'three_column_value', i_30_male,
                    'four_column_value', i_30_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_31_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', 0,
                        'two_column_value', 0,
                        'three_column_value', i_31_male,
                    'four_column_value', i_31_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_32_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', 0,
                        'two_column_value', 0,
                        'three_column_value', i_32_male,
                    'four_column_value', i_32_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_33_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', 0,
                        'two_column_value', 0,
                        'three_column_value', i_33_male,
                    'four_column_value', i_33_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_33_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', 0,
                        'two_column_value', 0,
                        'three_column_value', i_33_male,
                    'four_column_value', i_33_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_38_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_38_male,
                        'two_column_value', i_38_female,
                        'three_column_value', i_42_male,
                    'four_column_value', i_42_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_39_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_39_male,
                        'two_column_value', i_39_female,
                        'three_column_value', i_43_male,
                    'four_column_value', i_43_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_40_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_40_male,
                        'two_column_value', i_40_female,
                        'three_column_value', i_44_male,
                    'four_column_value', i_44_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_41_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_41_male,
                        'two_column_value', i_41_female,
                        'three_column_value', i_45_male,
                    'four_column_value', i_45_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_47_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_47_male,
                        'two_column_value', i_47_female,
                        'three_column_value', i_48_male,
                    'four_column_value', i_48_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_50_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_50_male,
                        'two_column_value', i_50_female,
                        'three_column_value', i_51_male,
                    'four_column_value', i_51_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_53_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_53_male,
                        'two_column_value', i_53_female,
                        'three_column_value', i_54_male,
                    'four_column_value', i_54_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_56_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_56_male,
                        'two_column_value', i_56_female,
                        'three_column_value', i_57_male,
                    'four_column_value', i_57_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_59_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_59_male,
                        'two_column_value', i_59_female,
                        'three_column_value', i_60_male,
                    'four_column_value', i_60_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_62_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_62_male,
                        'two_column_value', i_62_female,
                        'three_column_value', i_63_male,
                    'four_column_value', i_63_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_65_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_65_male,
                        'two_column_value', i_65_female,
                        'three_column_value', i_66_male,
                    'four_column_value', i_66_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_68_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_68_male,
                        'two_column_value', i_68_female,
                        'three_column_value', i_69_male,
                    'four_column_value', i_69_female
                    )
                ) || jsonb_agg(
                    jsonb_build_object(
                        'metric_id', i_71_metric_code,
                        'partner_id', partner_id,
                        'state_id', state_id,
                        'district_id', district_id,
                        'vision_center_id', vision_center_id,
                        'donor_id', donor_id,
                        'indicator_month', mpr_month,
                        'indicator_year', mpr_year,
                        'one_column_value', i_71_male,
                        'two_column_value', i_71_female,
                        'three_column_value', i_72_male,
                    'four_column_value', i_72_female
                    )
                )
                AS mpr_data
            FROM (
                SELECT
                    vision_center_id,
                    partner_id,
                    ssmis_id,
                    state_id,
                    district_id,
                    donor_id,
                    mpr_month,
                    mpr_year,
                    i_14_metric_code,
                    i_15_metric_code,
                    i_16_metric_code,
                    i_17_metric_code,
                    i_18_metric_code,
                    i_19_metric_code,
                    i_20_metric_code,
                    i_21_metric_code,
                    i_22_metric_code,
                    i_23_metric_code,
                    i_24_metric_code,
                    i_25_metric_code,
                    i_26_metric_code,
                    i_27_metric_code,
                    i_28_metric_code,
                    i_29_metric_code,
                    i_30_metric_code,
                    i_31_metric_code,
                    i_32_metric_code,
                    i_33_metric_code,
                    i_34_metric_code,
                    i_35_metric_code,
                    i_36_metric_code,
                    i_37_metric_code,
                    i_38_metric_code,
                    i_39_metric_code,
                    i_40_metric_code,
                    i_41_metric_code,
                    i_42_metric_code,
                    i_43_metric_code,
                    i_44_metric_code,
                    i_45_metric_code,
                    i_46_metric_code,
                    i_47_metric_code,
                    i_48_metric_code,
                    i_49_metric_code,
                    i_50_metric_code,
                    i_51_metric_code,
                    i_52_metric_code,
                    i_53_metric_code,
                    i_54_metric_code,
                    i_55_metric_code,
                    i_56_metric_code,
                    i_57_metric_code,
                    i_58_metric_code,
                    i_59_metric_code,
                    i_60_metric_code,
                    i_61_metric_code,
                    i_62_metric_code,
                    i_63_metric_code,
                    i_64_metric_code,
                    i_65_metric_code,
                    i_66_metric_code,
                    i_67_metric_code,
                    i_68_metric_code,
                    i_69_metric_code,
                    i_70_metric_code,
                    i_71_metric_code,
                    i_72_metric_code,
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
            sum(i_72_achive_male) as i_72_male,sum(i_72_achive_female) as i_72_female,sum(i_72_achive_total) as i_72_total,sum(i_72_achive_till_date) as i_72_till_date
                FROM reports_truckermpr where 1=1 and mpr_month='{month}' and mpr_year='{year}' and mpr_status=8 and partner_id != 0
                GROUP BY
                    vision_center_id,
                    partner_id,
                    ssmis_id,
                    state_id,
                    district_id,
                    donor_id,
                    mpr_month,
                    mpr_year,
                    i_14_metric_code,
                    i_15_metric_code,
                    i_16_metric_code,
                    i_17_metric_code,
                    i_18_metric_code,
                    i_19_metric_code,
                    i_20_metric_code,
                    i_21_metric_code,
                    i_22_metric_code,
                    i_23_metric_code,
                    i_24_metric_code,
                    i_25_metric_code,
                    i_26_metric_code,
                    i_27_metric_code,
                    i_28_metric_code,
                    i_29_metric_code,
                    i_30_metric_code,
                    i_31_metric_code,
                    i_32_metric_code,
                    i_33_metric_code,
                    i_34_metric_code,
                    i_35_metric_code,
                    i_36_metric_code,
                    i_37_metric_code,
                    i_38_metric_code,
                    i_39_metric_code,
                    i_40_metric_code,
                    i_41_metric_code,
                    i_42_metric_code,
                    i_43_metric_code,
                    i_44_metric_code,
                    i_45_metric_code,
                    i_46_metric_code,
                    i_47_metric_code,
                    i_48_metric_code,
                    i_49_metric_code,
                    i_50_metric_code,
                    i_51_metric_code,
                    i_52_metric_code,
                    i_53_metric_code,
                    i_54_metric_code,
                    i_55_metric_code,
                    i_56_metric_code,
                    i_57_metric_code,
                    i_58_metric_code,
                    i_59_metric_code,
                    i_60_metric_code,
                    i_61_metric_code,
                    i_62_metric_code,
                    i_63_metric_code,
                    i_64_metric_code,
                    i_65_metric_code,
                    i_66_metric_code,
                    i_67_metric_code,
                    i_68_metric_code,
                    i_69_metric_code,
                    i_70_metric_code,
                    i_71_metric_code,
                    i_72_metric_code
            ) x
            GROUP BY
                vision_center_id,
                partner_id,
                ssmis_id,
                state_id,
                district_id,
                donor_id,
                mpr_month,
                mpr_year
            ORDER BY vision_center_id
            """)
            jsonresponse_full = {
                "status":2,
                "message":"Data sent successfully",
            }
            if mpr_data:
                mpr_data_list = json.loads(mpr_data[0][0])
                jsonresponse_full['mpr_data'] = mpr_data_list
            else:
                jsonresponse_full['mpr_data'] = []
        else:
            jsonresponse_full = {
                "status":0,
                "message":"Please, Should be fill out year and month",
            }
            jsonresponse_full['mpr_data'] = []
        return Response(jsonresponse_full)


def execute_to_dict(query, params=None):
    with connection.cursor() as c:
        c.execute(query, params or [])
        names = [col[0] for col in c.description]
        return [dict(list(zip(names, values))) for values in c.fetchall()]

def return_sql_results(sql, conn=None, params=None):
    # logger.error('query:'+ sql)
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows

class VersionReleaseNote(APIView):
    def post(self,request):
        data = request.data
        interface = int(data.get('interface'))
        version = data.get('version')
        if interface:
            status=2
            version_notes = VersionUpdate.objects.filter(version_name=version,interface=interface)
            if version_notes:
                version_notes = version_notes.latest('id')
                if version_notes.version_name and version_notes.version_code:
                    version_name = version_notes.version_name + " ({0})".format(version_notes.version_code)
                elif version_notes.version_name:
                    version_name = version_notes.version_name
                data = {"version": version_name,"releasenotes":version_notes.releasenotes if version_notes.releasenotes else '',"releasedate":version_notes.release_date if version_notes.release_date else ''}
        else:
            status = 0
            data = {"version":'',"releasenotes":'','releasedate':""}
        return Response({'status':status , 'data' :data})

class PatientData(APIView):
    def post(self,request):
        data = request.data
        if data.get('year') and data.get('month'):
            if str(data.get('month')) =='12':
                month = '01'
            else:
                month = int(data.get('month')) + 1 if int(data.get('month')) > 8 else '0'+ str(int(data.get('month')) + 1)
            start_date = str(data.get('year')) +'-'+ str(data.get('month')) + '-01'
            end_date = str(data.get('year')) +'-'+ str(month) + '-01'
            between_date = """and created_date >= '"""+start_date + \
            """' and created_date < '"""+end_date + \
            """' """
            patient_data = execute_to_dict("""select * from dash_repo_patient_basic_info_view where 1=1 and mpr_status=8 and partner_id != 0 """+between_date+"""""")
            jsonresponse_full = {
                "status":2,
                "message":"Data sent successfully",
            }
            jsonresponse_full['patient'] = patient_data
        else:
            jsonresponse_full = {
                "status":0,
                "message":"Please, Should be fill out year and month",
            }
            jsonresponse_full['patient'] = []
        return Response(jsonresponse_full)

class ScreeningData(APIView):
    def post(self,request):
        data = request.data
        if data.get('year') and data.get('month'):
            if str(data.get('month')) =='12':
                month = '01'
            else:
                month = int(data.get('month')) + 1 if int(data.get('month')) > 8 else '0'+ str(int(data.get('month')) + 1)
            start_date = str(data.get('year')) +'-'+ str(data.get('month')) + '-01'
            end_date = str(data.get('year')) +'-'+ str(month) + '-01'
            between_date = """and created_date >= '"""+ start_date + \
            """' and created_date < '"""+ end_date + \
            """' """
            screening_data = execute_to_dict("""select * from dash_repo_screening_info_view where 1=1 and mpr_status=8 and partner_id != 0 """+between_date+"""""")
            jsonresponse_full = {
                "status":2,
                "message":"Data sent successfully",
            }
            jsonresponse_full['screening'] = screening_data
        else:
            jsonresponse_full = {
                "status":0,
                "message":"Please, Should be fill out year and month",
            }
            jsonresponse_full['screening'] = []
        return Response(jsonresponse_full)

class FamilyData(APIView):
    def post(self,request):
        data = request.data
        mpr = MprStatusUpdate.objects.filter(year=int(data.get('year')), month=data.get('month'), mpr_status=8)
        if data.get('year') and data.get('month') and mpr:
            family_members=FamilyMember.objects.filter(status=2, partner_id__in=mpr.values_list('partner_id', flat=True),server_created_on__year=data.get('year'), server_created_on__month=data.get('month'))
            family_members_serializer=FamilyMemberOtherSerializers(family_members, many=True)
            jsonresponse_full = {
                "status":2,
                "message":"Data sent successfully",
            }
            jsonresponse_full['family_members'] = family_members_serializer.data
        else:
            jsonresponse_full = {
                "status":0,
                "message":"Please, Should be fill out year and month",
            }
            jsonresponse_full['family_members'] = []
        return Response(jsonresponse_full)

class GlassPrescriptionData(APIView):
    def post(self,request):
        data = request.data
        if data.get('year') and data.get('month'):
            if str(data.get('month')) =='12':
                month = '01'
            else:
                month = int(data.get('month')) + 1 if int(data.get('month')) > 8 else '0'+ str(int(data.get('month')) + 1)
            start_date = str(data.get('year')) +'-'+ str(data.get('month')) + '-01'
            end_date = str(data.get('year')) +'-'+ str(month) + '-01'
            
            between_date = """and created_date >= '"""+ start_date + \
            """'and created_date < '"""+ end_date + \
            """' """
            glass_prescription=execute_to_dict("""select * from dash_repo_glass_prescription_view where 1=1 and mpr_status=8 and partner_id != 0 """+between_date+"""""")
            jsonresponse_full = {
                "status":2,
                "message":"Data sent successfully",
            }
            jsonresponse_full['glass_prescription'] = glass_prescription
        else:
            jsonresponse_full = {
                "status":0,
                "message":"Please, Should be fill out year and month",
            }
            jsonresponse_full['glass_prescription'] = []
        return Response(jsonresponse_full)


class PatientDetailsAPIView(APIView):
    permission_classes = ()
    def post(self, request):
        data = request.build_absolute_uri()
        create_post_log(request,data)
        response = {}
        try:
            data = request.data
            create_post_log(request,data)
            valid_patient = Patient.objects.filter(Q(Q(unique_id =  data.get('patient_verification_id')) | Q(contact_no_1 =  data.get('patient_verification_id')) | Q(aadhaar_pan_no =  data.get('patient_verification_id')) | Q(drivers_license_no =  data.get('patient_verification_id')))).first()
            if not valid_patient:
                return Response({"message":"Invalid Patient verification ID"})
    
            if valid_patient:
                patient_uuid=valid_patient.uuid

                patient = Patient.objects.filter(status=2, uuid=patient_uuid).order_by('server_modified_on')
                if data.get('ptsdate'):
                    patient = patient.filter(server_modified_on__gt =datetime.strptime(data.get('ptsdate'), '%Y-%m-%dT%H:%M:%S.%f%z'))
                patient_serializers=PatientSerializers(patient[:batch_rec], many=True)

                screening = Screening.objects.filter(status=2, patient_uuid__in=patient.values_list('uuid', flat=True)).order_by('server_modified_on')
                if data.get('ssdate'):
                    screening = screening.filter(server_modified_on__gt =datetime.strptime(data.get('ssdate'), '%Y-%m-%dT%H:%M:%S.%f%z'))
                screening_serializers=ScreeningSerializers(screening[:batch_rec], many=True)

                family_member = FamilyMember.objects.filter(status=2, screening_uuid__in=screening.values_list('uuid', flat=True)).order_by('server_modified_on')
                if data.get('fmdate'):
                    family_member = family_member.filter(server_modified_on__gt =datetime.strptime(data.get('fmdate'), '%Y-%m-%dT%H:%M:%S.%f%z'))
                family_member_serializers=FamilyMemberSerializers(family_member[:batch_rec], many=True)

                visual_acuity = VisualAcuity.objects.filter(status=2, screening_uuid__in=screening.values_list('uuid', flat=True)).order_by('server_modified_on')
                if data.get('vsdate'):
                    visual_acuity = visual_acuity.filter(server_modified_on__gt =datetime.strptime(data.get('vsdate'), '%Y-%m-%dT%H:%M:%S.%f%z'))
                visual_acuity_serializers=VisualAcuitySerializers(visual_acuity[:batch_rec], many=True)

                glass_prescription = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening.values_list('uuid', flat=True)).order_by('server_modified_on')
                if data.get('gsdate'):
                    glass_prescription = glass_prescription.filter(server_modified_on__gt =datetime.strptime(data.get('gsdate'), '%Y-%m-%dT%H:%M:%S.%f%z'))
                glass_prescription_serializers=GlassPrescriptionSerializers(glass_prescription[:batch_rec], many=True)

                spectacle_type = SpectacleType.objects.filter(status=2, glass_prescription_uuid__in=glass_prescription.values_list('uuid', flat=True)).order_by('server_modified_on')
                if data.get('stdate'):
                    spectacle_type = spectacle_type.filter(server_modified_on__gt =datetime.strptime(data.get('gsdate'), '%Y-%m-%dT%H:%M:%S.%f%z'))
                spectacle_type_serializers=SpectacleTypeSerializers(spectacle_type[:batch_rec], many=True)

                

                message = 'Data sent successfully'
                response['status'] = 2 
                response['message'] = message #1
                response['patient'] = patient_serializers.data #2
                response['screening'] = screening_serializers.data #3
                response['family_members'] = family_member_serializers.data #3
                response['visual_acuity'] = visual_acuity_serializers.data #4
                response['glass_prescription'] = glass_prescription_serializers.data #5
                response['spectacle_type'] = spectacle_type_serializers.data #5
                return Response(response)
        except Exception as e:
            response['status'] = 0
            response['message'] = e.args[0]
            response['patient'] = []
            response['screening'] = []
            response['family_members'] = []
            response['visual_acuity'] = []
            response['glass_prescription'] = []
            response['spectacle_type'] = []
            logger.error(e.args[0])
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(error_stack)
        return JsonResponse(response)
    
class MasterData(APIView):
    def post(self,request):
        data = request.build_absolute_uri()
        create_post_log(request,data)
        data = request.data
        create_post_log(request,data)
        try:
            valid_user = UserProfile.objects.get(status=2, id =  data.get('user_id'))
        except:
            return Response({"message":"Invalid User ID"})

        partner_id = None    
        if valid_user:
            try:
                vc_obj = UserVisionCenterLinkage.objects.get(user=valid_user.user).vision_center
                vc_id = vc_obj.id
            except:
                vc_id = None
            if vc_id is None:
                try:
                    partner_id = UserPartnerLinkage.objects.get(user=valid_user.user).partner.id 
                except:
                    partner_id = None
            
            #Language
            language=Language.objects.filter(status=2).order_by('server_modified_on')
            if data.get('lgdate'):
                language=language.filter(server_modified_on__gt =datetime.strptime(data.get('lgdate'), '%Y-%m-%dT%H:%M:%S.%f%z'))
            language_serializer=LanguageSerializers(language, many=True)
            
            #State
            state=State.objects.filter(status=2).order_by('server_modified_on')
            if data.get('ssdate'):
                state=state.filter(server_modified_on__gt =datetime.strptime(data.get('ssdate'), '%Y-%m-%dT%H:%M:%S.%f%z'))
            state_serializer=StateSerializers(state, many=True)

            #district
            district=District.objects.filter(status=2).order_by('server_modified_on')
            if data.get('dsdate'):
                district=district.filter(server_modified_on__gt =datetime.strptime(data.get('dsdate'), '%Y-%m-%dT%H:%M:%S.%f%z')).order_by('id')
            district_serializers=DistrictSerializers(district, many=True)

            #Partner
            partner=Partner.objects.filter(status=2).order_by('server_modified_on')
            if data.get('psdate'):
                partner=partner.filter(server_modified_on__gt =datetime.strptime(data.get('psdate'), '%Y-%m-%dT%H:%M:%S.%f%z')).order_by('id')
            partner_serializers=PartnerSerializers(partner, many=True)

            #vision_center
            vision_center=VisionCenter.objects.filter(status=2).order_by('server_modified_on')
            if data.get('vsdate'):
                vision_center=vision_center.filter(server_modified_on__gt =datetime.strptime(data.get('vsdate'), '%Y-%m-%dT%H:%M:%S.%f%z')).order_by('id')
            vision_center_serializers=VisionCenterSerializers(vision_center, many=True)


            #Camp
            if vc_id:
                camp=Camp.objects.filter(status=2, vision_center_id=vc_id).order_by('server_modified_on')
                dornor_ids = VisionCenter.objects.filter(id=vc_id).values_list('donor__id')
            else:
                dornor_ids = DonorPartnerLinkage.objects.filter(partner_id=partner_id).values_list('donor__id')
                camp=Camp.objects.filter(status=2, partner_id=partner_id).order_by('server_modified_on')

            # camp=Camp.objects.filter(status=2, vision_center__id__in=vc_list_vlu).order_by('server_modified_on') 
            if data.get('csdate'):
                camp=camp.filter(server_modified_on__gt =datetime.strptime(data.get('csdate'), '%Y-%m-%dT%H:%M:%S.%f%z')).order_by('id')
            camp_serializers=CampSerializers(camp, many=True)


            #partner_donor_linkage
            donor_partner_linkage=DonorPartnerLinkage.objects.filter(status=2).order_by('server_modified_on')
            if data.get('dplsdate'):
                donor_partner=donor_partner_linkage.filter(server_modified_on__gt =datetime.strptime(data.get('dplsdate'), '%Y-%m-%dT%H:%M:%S.%f%z'))
            donor_partner_serializer=DonorPartnerLinkageSerializers(donor_partner_linkage, many=True)

            donor=Donor.objects.filter(status=2, id__in=dornor_ids).order_by('server_modified_on')
            if data.get('dnrsdate'):
                donor=donor.filter(server_modified_on__gt =datetime.strptime(data.get('dnrsdate'), '%Y-%m-%dT%H:%M:%S.%f%z')).order_by('id')
            donor_serializers=DonorSerializers(donor, many=True)
            donor_data=donor_serializers.data

            choices=MasterLookup.objects.filter(status=2)
            choices_serializers=MasterLookupSerializers(choices, many=True)

            if not partner_id:
                user_id = UserPartnerLinkage.objects.get(partner_id=vc_obj.partner.id).user.id 
            else:
                user_id = UserPartnerLinkage.objects.get(partner_id=partner_id).user.id 
            user_obj =UserProfile.objects.get(user_id=user_id)

        jsonresponse_full = {
            "status":2,
            "message":"Data sent successfully",
        }
        jsonresponse_full['state'] = state_serializer.data
        jsonresponse_full['district'] = district_serializers.data
        jsonresponse_full['partner'] = partner_serializers.data
        jsonresponse_full['vision_center'] = vision_center_serializers.data
        jsonresponse_full['camp'] = camp_serializers.data
        jsonresponse_full['donor'] = donor_data
        jsonresponse_full['choices'] = choices_serializers.data
        jsonresponse_full['language'] = language_serializer.data
        jsonresponse_full['donor_partner_linkage'] = donor_partner_serializer.data

        return Response(jsonresponse_full)

class OTPVerificationAPIView(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        mobile_no = data.get('mobile_no')
        otp_created_at = datetime.now()
        otp_verified_at = data.get('otp_verified_at')
        language_id = data.get('language_id')
        otp_value = data.get('otp_value')
        number = random.randint(1000,9999)
        verfication =OtpVerificationDetails.objects.filter(mobile_no=mobile_no, no_of_verified=3)
        # if otp_verified_at:
        if verfication.exists():
            return JsonResponse({
                    "message": "Maximum limit time is exit.",
                    "status": 0,
                })
        try:
            if otp_verified_at:
                try:
                    no_of_verfied_time=OtpVerificationDetails.objects.filter(mobile_no=mobile_no).order_by('-no_of_verified').first().no_of_verified 
                    otp_created_at = OtpVerificationDetails.objects.get(mobile_no=mobile_no,no_of_verified=no_of_verfied_time).otp_created_at
                    obj_get = OtpVerificationDetails.objects.get(user_id=user_id,language_id=language_id,
                    mobile_no=mobile_no,otp_created_at=otp_created_at,otp_value=8750,no_of_verified=no_of_verfied_time)
                    obj_get.otp_verified_at = otp_verified_at
                    obj_get.save()
                    otp_serialize=OtpVerificationDetailsSerializers(obj_get)
                    return JsonResponse({
                            "message": "OTP Verified is successfully",
                            "status": 2,
                            "otpverification":[otp_serialize.data]
                        })
                except OtpVerificationDetails.DoesNotExist:
                    return JsonResponse({
                            "message": "OTP Verified is not match",
                            "status": 0,
                        })
            else:
                verfied_time= OtpVerificationDetails.objects.filter(mobile_no=mobile_no).order_by('-no_of_verified') 
                if verfied_time: 
                    no_of_verfied_time = verfied_time.first().no_of_verified + 1
                else:
                    no_of_verfied_time = 1
                obj, created = OtpVerificationDetails.objects.update_or_create(
                user_id=user_id,language_id=language_id,no_of_verified=no_of_verfied_time,
                mobile_no=mobile_no,otp_created_at=otp_created_at,otp_status=1,otp_value=str(number))
                obj.save()
                send_sms(request, number, mobile_no,None,None,None,None, 1,obj.language.id, 0)
                otp_serialize=OtpVerificationDetailsSerializers(obj)
                return JsonResponse({
                        "message": "OTP Send in successfully",
                        "status": 2,
                        "otpverification":[otp_serialize.data]
                    })
        except Exception as e:
            logger.error(e.args[0])
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(error_stack)
            return JsonResponse({"message": e.args[0],"status": 0,})
        


class OTPVerification2APIView(APIView):
    def post(self, request):
        
       
        return JsonResponse({"message": "Hi, How r u","status": 0,})
        

class LoginAPIView(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')

        try:
            find_user_to_vc = UserVisionCenterLinkage.objects.get(user__username__iexact=username, status=2)
            findUservc = UserProfile._default_manager.get(user__username__iexact=find_user_to_vc.user.username, status=2) 

        except ObjectDoesNotExist:
            try:
                find_user_to_vc = UserVisionCenterLinkage.objects.get(user__username__iexact=username, status=2)
                findUservc = UserProfile._default_manager.get(user__username__iexact=find_user_to_vc.user.username, status__in=[1,3,4,5]) 
                return JsonResponse({
                        "message": "Username is Inactive",
                        "status": 0,
                    })
            except ObjectDoesNotExist:
                findUservc = None

        if findUservc is None:
            try:
                find_user_to_partner = UserPartnerLinkage.objects.get(user__username__iexact=username, status=2)
                findUser_Partner = UserProfile._default_manager.get(
                    user__username__iexact=find_user_to_partner.user.username,status=2) 

            except ObjectDoesNotExist:
                try:
                    find_user_to_partner = UserPartnerLinkage.objects.get(user__username__iexact=username, status=2)
                    findUser_Partner = UserProfile._default_manager.get(
                        user__username__iexact=find_user_to_partner.user.username, status__in=[1,3,4,5])
                    return JsonResponse({
                        "message": "Username is Inactive",
                        "status": 0,
                    })
                except ObjectDoesNotExist:
                    findUser_Partner = None

        if findUservc is not None:
            findUser = findUservc
        else:
            findUser = findUser_Partner

        if findUser is not None:
            username = findUser.user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                user_obj=User.objects.get(id=findUser.user.id)
                user_obj.last_login = datetime.now()
                user_obj.save()
                userprofileserialize=UserProfileSerializers(findUser)
                return JsonResponse({
                    "message": "Logged in successfully",
                    "status": 2,
                    "userprofile":[userprofileserialize.data]
                })
            else:
                return JsonResponse({
                    "message": "Invalid username and password",
                    "status": 0,
                })
        else:
            return JsonResponse({
                "message": "Invalid username and password",
                "status": 0,
            })


class PullAPIView(APIView):
    permission_classes = ()
    def post(self, request):
        data = request.build_absolute_uri()
        create_post_log(request,data)
        response = {}
        try:
            data = request.data
            create_post_log(request,data)
            try:
                valid_user = UserProfile.objects.get(id =  data.get('user_id'))
            except:
                return Response({"message":"Invalid User ID"})
            if valid_user:
                user_id=valid_user.user.id
                patient_user_id=valid_user.id
                try:
                    vision_center_id = UserVisionCenterLinkage.objects.get(user_id=user_id).vision_center.id
                except:
                    vision_center_id = None
                try:
                    partner = UserPartnerLinkage.objects.get(user_id=user_id).partner
                except:
                    partner = None
                if vision_center_id:
                    patient = Patient.objects.filter(status=2, vision_center_id=vision_center_id).order_by('server_modified_on')
                else:
                    patient = Patient.objects.filter(status=2, partner_id=partner.id).order_by('server_modified_on')
                if data.get('ptsdate'):
                    patient = patient.filter(server_modified_on__gt =datetime.strptime(data.get('ptsdate'), '%Y-%m-%dT%H:%M:%S.%f%z'))
                patient_serializers=PatientSerializers(patient[:batch_rec], many=True)

                screening = Screening.objects.filter(status=2, patient_uuid__in=patient.values_list('uuid', flat=True)).order_by('server_modified_on')
                if data.get('ssdate'):
                    screening = screening.filter(server_modified_on__gt =datetime.strptime(data.get('ssdate'), '%Y-%m-%dT%H:%M:%S.%f%z'))
                screening_serializers=ScreeningSerializers(screening[:batch_rec], many=True)

                family_member = FamilyMember.objects.filter(status=2, screening_uuid__in=screening.values_list('uuid', flat=True)).order_by('server_modified_on')
                if data.get('fmdate'):
                    family_member = family_member.filter(server_modified_on__gt =datetime.strptime(data.get('fmdate'), '%Y-%m-%dT%H:%M:%S.%f%z'))
                family_member_serializers=FamilyMemberSerializers(family_member[:batch_rec], many=True)

                visual_acuity = VisualAcuity.objects.filter(status=2, screening_uuid__in=screening.values_list('uuid', flat=True)).order_by('server_modified_on')
                if data.get('vsdate'):
                    visual_acuity = visual_acuity.filter(server_modified_on__gt =datetime.strptime(data.get('vsdate'), '%Y-%m-%dT%H:%M:%S.%f%z'))
                visual_acuity_serializers=VisualAcuitySerializers(visual_acuity[:batch_rec], many=True)

                glass_prescription = GlassPrescription.objects.filter(status=2, screening_uuid__in=screening.values_list('uuid', flat=True)).order_by('server_modified_on')
                if data.get('gsdate'):
                    glass_prescription = glass_prescription.filter(server_modified_on__gt =datetime.strptime(data.get('gsdate'), '%Y-%m-%dT%H:%M:%S.%f%z'))
                glass_prescription_serializers=GlassPrescriptionSerializers(glass_prescription[:batch_rec], many=True)

                spectacle_type = SpectacleType.objects.filter(status=2, glass_prescription_uuid__in=glass_prescription.values_list('uuid', flat=True)).order_by('server_modified_on')
                if data.get('stdate'):
                    spectacle_type = spectacle_type.filter(server_modified_on__gt =datetime.strptime(data.get('gsdate'), '%Y-%m-%dT%H:%M:%S.%f%z'))
                spectacle_type_serializers=SpectacleTypeSerializers(spectacle_type[:batch_rec], many=True)

                

                message = 'Data sent successfully'
                response['status'] = 2 
                response['message'] = message #1
                response['patient'] = patient_serializers.data #2
                response['screening'] = screening_serializers.data #3
                response['family_members'] = family_member_serializers.data #3
                response['visual_acuity'] = visual_acuity_serializers.data #4
                response['glass_prescription'] = glass_prescription_serializers.data #5
                response['spectacle_type'] = spectacle_type_serializers.data #5
                return Response(response)
        except Exception as e:
            response['status'] = 0
            response['message'] = e.args[0]
            response['patient'] = []
            response['screening'] = []
            response['family_members'] = []
            response['visual_acuity'] = []
            response['glass_prescription'] = []
            response['spectacle_type'] = []
            logger.error(e.args[0])
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(error_stack)
        return JsonResponse(response)
       

class PushAPIView(APIView):
    def post(self,request):
        patient_success =[]
        screening_success =[]
        visual_acuity_success =[]
        glass_prescription_success =[]
        spectacle_type_success =[]
        family_members_success =[]
        camp_success =[]
        response = {}
        saved_count = 0
        not_saved_count = 0
        created_count = 0
        today_date =  datetime.now().date()
        try:
            data = request.build_absolute_uri()
            data = request.data
            patient_response = {'data':[]}
            screening_response = {'data':[]}
            visual_acuity_response = {'data':[]}
            glass_prescription_response = {'data':[]}
            spectacle_type_response = {'data':[]}
            family_members_response = {'data':[]}
            camp_response = {'data':[]}
            try:
                valid_user = UserProfile.objects.get(id =  data.get('user_id'))
            except:
                return Response({"message":"Invalid User ID"})
            # #-TODO-valid user based on that village
            if  valid_user :
                user_id=valid_user.user.id
                with transaction.atomic():
                    patient_data  = patient_details(data)
                    s_count = 0

                    for obj in patient_data:
                        patient_info ={}
                        if type(obj) is not dict:
                            patient_info['uuid']=obj.uuid
                            patient_info['unique_id'] = obj.unique_id
                            patient_info['SCO'] = obj.server_created_on
                            patient_info['SMO'] = obj.server_modified_on
                            patient_info['sync_status'] = obj.sync_status
                             # import ipdb; ipdb.set_trace()
                            
                           
                        else:
                            if obj.get('msg_status') == 1:
                                message = "Invalid Unique ID"
                            if obj.get('msg_status') == 2:
                                message = 'Unique ID already exits'
                            if obj.get('msg_status') == 3:
                                message = 'Contact no 1 already exits'
                            if obj.get('msg_status') == 4:
                                message = 'Contact no 2 already exits'
                            if obj.get('msg_status') == 5:
                                message = 'Aadhaar & Pan card no already exits'
                            if obj.get('msg_status') == 6:
                                message = 'Drivers license no already exits'
                            patient_info['uuid']= obj.get('uuid')
                            patient_info['error_message'] = message
                            patient_info['sync_status'] = 0
                            s_count += 1 

                            last_daily_record = DailyRecordsCalculation.objects.filter(date=today_date, record="Patient", error=message).last()
                            total_records = None
                            if last_daily_record == None:
                                daily = s_count
                                created_count = daily 
                            else:
                                daily = last_daily_record.total_records
                                created_count = daily + s_count

                            if not DailyRecordsCalculation.objects.filter(date=today_date, record="Patient", uuid=obj.get('uuid')).exists():
                                not_saved_count = s_count
                                
                                daily_records_report, created = DailyRecordsCalculation.objects.update_or_create(
                                    date=today_date,
                                    record="Patient",
                                    uuid=obj.get('uuid'),
                                    defaults={
                                        'error' : message,
                                        'saved_records': 0,
                                        'not_saved_records': not_saved_count,
                                        'total_records': created_count
                                    }
                                )
                            else:
                                daily_records_report = DailyRecordsCalculation.objects.filter(date=today_date, record="Patient", uuid=obj.get('uuid')).last()
                                daily_records_report.error = message
                                not_saved_count = s_count
                                daily_records_report.not_saved_records = not_saved_count
                                daily_records_report.total_records = daily
                                
                                daily_records_report.save()

                        patient_response['data'].append(patient_info)
                        patient_success =  patient_response['data']
                            

                    
                    screening_data  = screening_details(data)
                    for obj in screening_data:
                        screening_info ={}
                        if type(obj) is not dict:
                            screening_info['uuid']=obj.uuid
                            screening_info['patient_uuid']=obj.patient_uuid
                            screening_info['SCO'] = obj.server_created_on
                            screening_info['SMO'] = obj.server_modified_on
                            screening_info['sync_status'] = obj.sync_status
                        else:
                            screening_info['uuid']= obj.get('uuid')
                            screening_info['patient_uuid']=obj.get('patient_uuid')
                            screening_info['sync_status'] = 0
                        screening_response['data'].append(screening_info)
                        screening_success =  screening_response['data']

                    visual_acuity_data  = visual_acuity_details(data)
                    for obj in visual_acuity_data:
                        visual_acuity_info ={}
                        if type(obj) is not dict:
                            visual_acuity_info['uuid']=obj.uuid
                            visual_acuity_info['screening_uuid']=obj.screening_uuid
                            visual_acuity_info['SCO'] = obj.server_created_on
                            visual_acuity_info['SMO'] = obj.server_modified_on
                            visual_acuity_info['sync_status'] = obj.sync_status
                        else:
                            visual_acuity_info['uuid']= obj.get('uuid')
                            visual_acuity_info['screening_uuid']=obj.get('screening_uuid')
                            visual_acuity_info['sync_status'] = 0
                        visual_acuity_response['data'].append(visual_acuity_info)
                        visual_acuity_success =  visual_acuity_response['data']

                    
                    glass_prescription_data  = glass_prescription_details(data)
                    for obj in glass_prescription_data:
                        glass_prescription_info ={}
                        if type(obj) is not dict:
                            glass_prescription_info['uuid']=obj.uuid
                            glass_prescription_info['screening_uuid']=obj.screening_uuid
                            glass_prescription_info['SCO'] = obj.server_created_on
                            glass_prescription_info['SMO'] = obj.server_modified_on
                            glass_prescription_info['sync_status'] = obj.sync_status
                        else:
                            glass_prescription_info['uuid']= obj.get('uuid')
                            glass_prescription_info['screening_uuid']=obj.get('screening_uuid')
                            glass_prescription_info['sync_status'] = 0
                        glass_prescription_response['data'].append(glass_prescription_info)
                        glass_prescription_success =  glass_prescription_response['data']

                    spectacle_type_data  = spectacle_type_details(data)
                    for obj in spectacle_type_data:
                        spectacle_type_info ={}
                        if type(obj) is not dict:
                            spectacle_type_info['uuid']=obj.uuid
                            spectacle_type_info['glass_prescription_uuid']=obj.glass_prescription_uuid
                            spectacle_type_info['SCO'] = obj.server_created_on
                            spectacle_type_info['SMO'] = obj.server_modified_on
                            spectacle_type_info['sync_status'] = obj.sync_status
                            
                        else:
                            spectacle_type_info['uuid']= obj.get('uuid')
                            spectacle_type_info['glass_prescription_uuid']=obj.get('glass_prescription_uuid')
                            spectacle_type_info['sync_status'] = 0
                        spectacle_type_response['data'].append(spectacle_type_info)
                        spectacle_type_success =  spectacle_type_response['data']

                    family_members_data  = family_members_details(data)
                    for obj in family_members_data:
                        family_members_info ={}
                        if type(obj) is not dict:
                            family_members_info['uuid']=obj.uuid
                            family_members_info['screening_uuid']=obj.screening_uuid
                            family_members_info['patient_uuid']=obj.patient_uuid
                            family_members_info['SCO'] = obj.server_created_on
                            family_members_info['SMO'] = obj.server_modified_on
                            family_members_info['sync_status'] = obj.sync_status
                        else:
                            family_members_info['uuid']= obj.get('uuid')
                            family_members_info['patient_uuid']=obj.get('patient_uuid')
                            family_members_info['sync_status'] = 0
                        family_members_response['data'].append(family_members_info)
                        family_members_success =  family_members_response['data']
                    
                    camp_data  = camp_details(data)
                    for obj in camp_data:
                        camp_info ={}
                        camp_info['uuid']=obj.uuid
                        camp_info['id']=obj.id
                        camp_info['code']=obj.code
                        camp_info['SCO'] = obj.server_created_on
                        camp_info['SMO'] = obj.server_modified_on
                        camp_info['sync_status'] = obj.sync_status
                        camp_response['data'].append(camp_info)
                        camp_success =  camp_response['data']

                    response['status'] = 2
                    response['message'] = "Data send successfully"
                    response['patient'] = patient_success
                    response['screening'] = screening_success
                    response['visual_acuity'] = visual_acuity_success
                    response['glass_prescription'] = glass_prescription_success
                    response['spectacle_type'] = spectacle_type_success
                    response['family_members'] = family_members_success
                    response['camp'] = camp_success
                
        except Exception as e:
            response['status'] = 0
            response['message'] = e.args[0]
            response['patient'] = []
            response['screening'] = []
            response['visual_acuity'] = []
            response['glass_prescription'] = []
            response['spectacle_type'] = []
            response['family_members'] = []
            response['camp'] = []
            logger.error(e.args[0])
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(error_stack)

             # Extract table name from the exception message
            match = re.search(r'"([^"]*)"', str(e.args[0]))
            table_name = match.group(1) if match else "Json parse error"

            match = re.search(r'Key \(uuid\)=\(([^)]+)\)', str(e.args[0]))
            uuid = match.group(1) if match else ""

            if "sims_patient" in table_name.lower():
                table_name = "Patient"
            elif "sims_screening" in table_name.lower():
                table_name = "Screening"
            elif "sims_visualacuity" in table_name.lower():
                table_name = "Visual Acuity"
            elif "sims_familymember" in table_name.lower():
                table_name = "Family Members"
            elif "sims_spectacletype" in table_name.lower():
                table_name = "Spectacle Type"
            elif "sims_glassprescription" in table_name.lower():
                table_name = "Glass Prescription"

            daily = DailyRecordsCalculation.objects.filter(date=today_date,record=table_name).count()
            created_count = daily + 1
            not_saved_count += 1

            if not DailyRecordsCalculation.objects.filter(date=today_date, record=table_name, uuid=uuid ).exists():
                daily_records_report = DailyRecordsCalculation.objects.create(
                    date=today_date,
                    record=table_name,
                    uuid = uuid,
                    error=e.args[0],
                    saved_records=0,
                    not_saved_records=not_saved_count,
                    total_records=created_count
                )
                daily_records_report.save()
        finally:
            if response:
                create_post_log(request, response)
        return JsonResponse(response)


def patient_details(self):
    objlist =[]
    datas = self.get('patient')
    create_post_log(self,datas)
    saved_count = 0
    not_saved_count = 0
    created_count = 0
    today_date = datetime.now().date()
    created = False
    s_count = 0
    uuid_list = []

    for data in datas: 
        if not QrCodeGeneration.objects.filter(unique_id=data.get('unique_id')).exists():
            obj = {}
            obj['msg_status'] = 1
            obj['uuid'] = data.get('uuid')
        elif Patient.objects.filter(unique_id=data.get('unique_id')).exclude(uuid=data.get('uuid')).exists():
            obj = {}
            obj['msg_status'] = 2
            obj['uuid'] = data.get('uuid')
        elif Patient.objects.filter(contact_no_1=data.get('contact_no_1')).exclude(Q(Q(uuid=data.get('uuid')) | Q(contact_no_1__in=['9999999999','0000000000']))).exists():
            obj = {}
            obj['msg_status'] = 3
            obj['uuid'] = data.get('uuid')
        elif data.get('contact_no_2') and Patient.objects.filter(contact_no_2=data.get('contact_no_2')).exclude(uuid=data.get('uuid')).exists():
            obj = {}
            obj['msg_status'] = 4
            obj['uuid'] = data.get('uuid')
        elif data.get('aadhaar_pan_no') and Patient.objects.filter(aadhaar_pan_no=data.get('aadhaar_pan_no')).exclude(uuid=data.get('uuid')).exists():
            obj = {}
            obj['msg_status'] = 5
            obj['uuid'] = data.get('uuid')
        elif data.get('drivers_license_no') and Patient.objects.filter(drivers_license_no=data.get('drivers_license_no')).exclude(uuid=data.get('uuid')).exists():
            obj = {}
            obj['msg_status'] = 6
            obj['uuid'] = data.get('uuid')
        else:
            obj, created = Patient.objects.update_or_create(
                uuid = data.get('uuid'),
                defaults= {
                            "app_created_at" : data.get('app_created_at'),
                            "partner_id" : data.get('partner_id'),
                            "vision_center_id" : data.get('vision_center_id'),
                            "unique_id" : data.get('unique_id'),
                            "patient_id" : data.get('patient_id') if data.get('patient_id') != '' else None,
                            "name" : data.get('name'),
                            "age" : data.get('age'),
                            "gender" : data.get('gender'),
                            "donor_id" : data.get('donor'),
                            "user_id" : data.get('user'),
                            "language_id" : data.get('language') if data.get('language') != 0 else None,
                            "camp_id" : data.get('camp') if data.get('camp') != 0 else None,
                            "district_id" : data.get('district'),
                            "contact_no_1": data.get('contact_no_1'),
                            "contact_no_2": data.get('contact_no_2') if data.get('contact_no_2') != '' else None,
                            "permanent_address":data.get('permanent_address') if data.get('permanent_address') != '' else None,
                            "aadhaar_pan_no":data.get('aadhaar_pan_no') if data.get('aadhaar_pan_no') != '' else None,
                            "drivers_license_no": data.get('drivers_license_no'),                        
                            "renewal_date":data.get('renewal_date') if data.get('renewal_date') != '' else None,
                            "type_of_job_id":data.get('type_of_job'),
                            "time_since_driving":data.get('time_since_driving') if data.get('time_since_driving') != '' else None,
                            "type_of_vehicle_id":data.get('type_of_vehicle') if data.get('type_of_vehicle') != 0 else None,
                            "type_of_route_id":data.get('type_of_route') if data.get('type_of_route') != 0 else None,
                            "monthly_income_id":data.get('monthly_income'),
                            "life_insurance_policy":data.get('life_insurance_policy'),
                            "vehicle_insurance_policy":data.get('vehicle_insurance_policy') if data.get('do_you_have_a_vehicle_insurance_policy') != 0 else None,
                            "health_insurance_policy":data.get('health_insurance_policy'),
                            "how_do_you_know_about_camp_id":data.get('how_do_you_know_about_camp'),
                            "educational_qualification_id":data.get('educational_qualification') if data.get('educational_qualification') != 0 else None,
                            "no_of_months_employed_in_a_year":data.get('no_of_months_employed_in_a_year') if data.get('no_of_months_employed_in_a_year') != '' else None,
                            "residence_type_id":data.get('residence_type') if data.get('residence_type') != 0 else None,
                            "feedback":data.get('feedback') if data.get('feedback') != '' else None,
                            "qr_code":data.get('qr_code') if data.get('qr_code') != '' else None,
                            "app_updated_at" : data.get('app_updated_at'),
                            "latitude" : data.get('latitude') if data.get('latitude') != '' else None,
                            "longitude" : data.get('longitude') if data.get('longitude') != '' else None,
                          })
            if created: 
                otp_vc_camp= None
                otp_vc_camp_location= None
                if obj.camp:
                    otp_vc_camp = obj.camp 
                    otp_vc_camp_location = obj.camp.location
                else:
                    vc_camp_obj = VisionCenter.objects.filter(id=obj.vision_center_id).first()
                    otp_vc_camp = vc_camp_obj.name 
                    otp_vc_camp_location = vc_camp_obj.address
                send_sms(self, None, obj.contact_no_1, obj.unique_id,otp_vc_camp,otp_vc_camp_location,None, 2, obj.language.id, 0)
        objlist.append(obj)
        uuid_list.append(data.get('uuid'))
        if created:
            s_count += 1  
            
    
    try:
        last_daily_record = DailyRecordsCalculation.objects.filter(date=today_date, record="Patient", error=None).last()
        total_records = None
        if last_daily_record is None:
            daily = s_count
            created_count = daily 
        else:
            daily = last_daily_record.total_records
            created_count = daily + s_count


        uuid_to_update = uuid_list[0] if len(uuid_list) == 1 else None
        if created and today_date:
            saved_count = s_count
            daily_update = DailyRecordsCalculation.objects.filter(date=today_date, record="Patient", uuid=uuid_to_update).first()

            if not daily_update:
                daily_records_report = DailyRecordsCalculation.objects.create(
                    date=today_date,
                    record="Patient",
                    error=None,
                    uuid=None,
                    saved_records=saved_count,
                    not_saved_records=0,
                    total_records=created_count
                )
                daily_records_report.save()
            else:
                daily_update.error = None
                daily_update.uuid = None
                daily_update.saved_records = saved_count
                daily_update.not_saved_records = 0
                daily_update.total_records = created_count
                        
                daily_update.save()
    except Exception as e:
        daily = DailyRecordsCalculation.objects.filter(date=today_date,record="Patient", error=e.args[0]).count()
        not_saved_count = s_count
        created_count = daily + not_saved_count
        error_uuid = DailyRecordsCalculation.objects.filter(status=2)
        for receive in error_uuid:
            if receive.error != e.args[0] and receive.uuid not in uuid_list and receive.date == today_date:
                daily_records_report = DailyRecordsCalculation.objects.create(
                    date=today_date,
                    record="Patient", 
                    error=e.args[0],
                    uuid=uuid_list,
                    saved_records=0,
                    not_saved_records=not_saved_count,
                    total_records=created_count
                )
                daily_records_report.save()
        

    return objlist


def screening_details(self):
    objlist =[]
    datas = self.get('screening')
    create_post_log(self,datas)
    saved_count = 0
    not_saved_count = 0
    created_count = 0
    today_date =  datetime.now().date()
    created = False
    s_count = 0
    uuid_list = []
    
    for data in datas:
        if not Patient.objects.filter(uuid=data.get('patient_uuid')).exists():
            obj = {}
            obj['uuid'] = data.get('uuid')
            obj['patient_uuid'] = data.get('patient_uuid')
        else:
            obj, created = Screening.objects.update_or_create(
                uuid = data.get('uuid'),
                patient_uuid = data.get('patient_uuid'),
                defaults= {
                            "app_created_at": data.get('app_created_at'),
                            "partner_id" : data.get('partner_id'),
                            "vision_center_id" : data.get('vision_center_id'),
                            # "code_description_id" : data.get('code_description'),
                            "blood_pressure" : data.get('blood_pressure_mmhg') if data.get('blood_pressure_mmhg') != '' else None,
                            "blood_sugar" : data.get('blood_sugar_mg_dl') if data.get('blood_sugar_mg_dl') != '' else None,
                            "weight" : data.get('weight_kg') if data.get('weight_kg') != '' else None,
                            "height": data.get('height_cm') if data.get('height_cm') != '' else None,
                            "family_details": data.get('family_details') if data.get('family_details') != '' else None,
                            "total_family_members":data.get('total_family_members') if data.get('total_family_members') != '' else None,
                            "salary_calculated_id":data.get('on_what_basis_your_salary_is_calculated')  if data.get('on_what_basis_your_salary_is_calculated') != 0 else None,
                            "owner_holding_amount":data.get('owner_holding_any_amount_from_your_salary') if data.get('owner_holding_any_amount_from_your_salary') != '' else None,
                            "non_working_months_id":data.get('what_do_you_do_during_non_working_months') if data.get('what_do_you_do_during_non_working_months') != 0 else None,
                            "alter_employment":data.get('you_equipped_with_any_alter_employment') if data.get('you_equipped_with_any_alter_employment') != 0 else None,
                            "learn_alter_livelihood_skill":data.get('you_willing_to_learn_alter_livelihood_skill') if data.get('you_willing_to_learn_alter_livelihood_skill') != 0 else None,
                            "family_support_financially":data.get('your_family_members_support_you_financially') if data.get('your_family_members_support_you_financially') != 0 else None,
                            "medical_checkup_past_1_year":data.get('you_had_medical_check_up_in_the_past_1_year'),
                            "diabetes":data.get('do_you_have_diabetes'),
                            "hypertension":data.get('do_you_have_hypertension'),
                            "smoke":data.get('do_you_smoke'),
                            "alcohol":data.get('do_you_consume_alcohol'),
                            "eye_examination":data.get('have_you_ever_had_eye_examination'),
                            "seeing_distant_objects":data.get('have_any_difficulty_in_seeing_distant_objects'),
                            "judging_distance_while_driving":data.get('any_difficulty_in_judging_distance_while_driving'),
                            "traffic_colors":data.get('you_able_to_identify_the_traffic_colors_easily'),
                            "seeing_while_night_driving":data.get('have_any_difficulty_in_seeing_while_night_driving'),
                            "wear_glasses_ever":data.get('have_you_been_advised_to_wear_glasses_ever'),
                            "wearing_glasses_currently":data.get('are_you_wearing_glasses_currently'),
                            "nearby_hospital":data.get('are_you_aware_of_any_nearby_hospital'),
                            "type_of_hospital_id":data.get('type_of_hospital') if data.get('type_of_hospital') != 0 else None,
                            "accident_while_driving_commercial_vehicle_before":data.get('accident_while_driving_commercial_vehicle_before') if data.get('accident_while_driving_commercial_vehicle_before') != 0 else None,
                            "accident_vehicle_in_last_twelve_months":data.get('accident_vehicle_in_last_twelve_months') if data.get('accident_vehicle_in_last_twelve_months') != 0 else None,
                            "first_aid_kit":data.get('you_have_proper_first_aid_kit_in_your_truck') if data.get('you_have_proper_first_aid_kit_in_your_truck') != 0 else None,
                            "you_happy_with_your_profession_id":data.get('you_happy_with_your_profession') if data.get('you_happy_with_your_profession') != 0 else None,
                            "if_you_are_happy_specify_in_what_way":data.get('if_you_are_happy_specify_in_what_way') if data.get('if_you_are_happy_specify_in_what_way') != '' else None,
                            "insulin_dependent_or_non_insulin_dependent_id":data.get('insulin_dependent_or_non_insulin_dependent') if data.get('insulin_dependent_or_non_insulin_dependent') != 0 else None,
                            "waist_circumference_id":data.get('waist_circumference') if data.get('waist_circumference') != 0 else None,
                            "physical_activity_id":data.get('physical_activity') if data.get('physical_activity') != 0 else None,
                            "family_history_of_diabetes_id":data.get('family_history_of_diabetes') if data.get('family_history_of_diabetes') != 0 else None,
                            "which_training_id":data.get('which_training') if data.get('which_training') != 0 else None,
                            "medication_hypertension":data.get('medication_hypertension') if data.get('medication_hypertension') != 0 else None,
                            "cough_for_more_than_two_weeks":data.get('cough_for_more_than_two_weeks') if data.get('cough_for_more_than_two_weeks') != 0 else None,
                            "night_sweats":data.get('night_sweats') if data.get('night_sweats') != 0 else None,
                            "fever_for_more_than_2_weeks":data.get('fever_for_more_than_2_weeks') if data.get('fever_for_more_than_2_weeks') != 0 else None,
                            "unexplained_weight_loss_or_loss_of_appetite":data.get('unexplained_weight_loss_or_loss_of_appetite') if data.get('unexplained_weight_loss_or_loss_of_appetite') != 0 else None,
                            "have_you_attended_awarness_training":data.get('have_you_attended_awarness_training') if data.get('have_you_attended_awarness_training') != 0 else None,
                            "dosage_of_insulin":data.get('dosage_of_insulin') if data.get('dosage_of_insulin') != 0 else None,
                            "duration_since_last_meal":data.get('duration_since_last_meal') if data.get('duration_since_last_meal') != 0 else None,
                            "when_was_it_diagnosed_number_of_years":data.get('when_was_it_diagnosed_number_of_years') if data.get('when_was_it_diagnosed_number_of_years') != 0 else None,
                            "when_was_it_diagnosed_years":data.get('when_was_it_diagnosed_years') if data.get('when_was_it_diagnosed_years') != 0 else None,
                            "app_updated_at" : data.get('app_updated_at'),
                            "latitude" : data.get('latitude') if data.get('latitude') != '' else None,
                            "longitude" : data.get('longitude') if data.get('longitude') != '' else None,    
                            })
            obj.employed_in_year.clear()
            obj.employed_in_year.add(*data.get('which_months_you_are_not_employed_in_a_year'))
            obj.save()

        objlist.append(obj)
        uuid_list.append(data.get('uuid'))
        if created:
            s_count += 1  

    try:
        last_daily_record = DailyRecordsCalculation.objects.filter(date=today_date, record="Screening", error=None).last()
        total_records = None
        if last_daily_record is None:
            daily = s_count
            created_count = daily 
        else:
            daily = last_daily_record.total_records
            created_count = daily + s_count

        if created and today_date :
            saved_count = s_count
            daily_records_report=DailyRecordsCalculation.objects.create(
                date=today_date,
                record="Screening",
                error = None,
                uuid = None,
                saved_records=saved_count,
                not_saved_records=0,
                total_records=created_count
            )
            daily_records_report.save()
    except Exception as e:
        daily = DailyRecordsCalculation.objects.filter(date=today_date,record="Screening", error=e.args[0]).count()
        not_saved_count = s_count
        created_count = daily + not_saved_count
        error_uuid = DailyRecordsCalculation.objects.filter(status=2)
        for receive in error_uuid:
            if receive.error != e.args[0] and receive.uuid not in uuid_list and receive.date == today_date:
                daily_records_report = DailyRecordsCalculation.objects.create(
                    date=today_date,
                    record="Screening", 
                    error=e.args[0],
                    uuid=uuid_list,
                    saved_records=0,
                    not_saved_records=not_saved_count,
                    total_records=created_count
                )
                daily_records_report.save()

        
    return objlist


def family_members_details(self):
    objlist =[]
    datas = self.get('family_members')
    create_post_log(self,datas)
    saved_count = 0
    not_saved_count = 0
    created_count = 0
    today_date =  datetime.now().date()
    created = False
    s_count = 0
    uuid_list = []

    for data in datas:
        if not Patient.objects.filter(uuid=data.get('patient_uuid')).exists():
            obj = {}
            obj['uuid'] = data.get('uuid')
            obj['patient_uuid'] = data.get('patient_uuid')
            obj['screening_uuid'] = data.get('screening_uuid')
        elif not Screening.objects.filter(uuid=data.get('screening_uuid')).exists():
            obj = {}
            obj['uuid'] = data.get('uuid')
        else:
            obj, created = FamilyMember.objects.update_or_create(
                uuid = data.get('uuid'),
                screening_uuid = data.get('screening_uuid'),
                patient_uuid = data.get('patient_uuid'),
                defaults= {
                            "app_created_at" : data.get('app_created_at'),
                            "partner_id" : data.get('partner_id'),
                            "vision_center_id" : data.get('vision_center_id'),
                            "name" : data.get('name') if data.get('name') != '' else None,
                            "sex" : data.get('sex') if data.get('sex') != 0 else None,
                            "age" : data.get('age') if data.get('age') != 0 else None,
                            "relationship_to_respondent_id" : data.get('relationship_to_respondent') if data.get('relationship_to_respondent') != 0 else None,
                            "educational_qualification_id" : data.get('educational_qualification') if data.get('educational_qualification') != 0 else None,
                            "occupation_id" : data.get('occupation') if data.get('occupation') != 0 else None,
                            "monthly_average_income_id" : data.get('monthly_average_income') if data.get('monthly_average_income') != 0 else None,
                            "app_updated_at" : data.get('app_updated_at'),
                            })
        objlist.append(obj)
        uuid_list.append(data.get('uuid'))
        if created:
            s_count += 1 

    try:
        last_daily_record = DailyRecordsCalculation.objects.filter(date=today_date, record="Family Members", error=None).last()
        total_records = None
        if last_daily_record is None:
            daily = s_count
            created_count = daily 
        else:
            daily = last_daily_record.total_records
            created_count = daily + s_count

        if created and today_date :
            saved_count = s_count
            daily_records_report=DailyRecordsCalculation.objects.create(
                date=today_date,
                record="Family Members",
                error = None,
                uuid = None,
                saved_records=saved_count,
                not_saved_records=0,
                total_records=created_count
            )
            daily_records_report.save()
    except Exception as e:
        daily = DailyRecordsCalculation.objects.filter(date=today_date,record="Family Members", error=e.args[0]).count()
        not_saved_count = s_count
        created_count = daily + not_saved_count
        error_uuid = DailyRecordsCalculation.objects.filter(status=2)
        for receive in error_uuid:
            if receive.error != e.args[0] and receive.uuid not in uuid_list and receive.date == today_date:
                daily_records_report = DailyRecordsCalculation.objects.create(
                    date=today_date,
                    record="Family Members", 
                    error=e.args[0],
                    uuid=uuid_list,
                    saved_records=0,
                    not_saved_records=not_saved_count,
                    total_records=created_count
                )
                daily_records_report.save()

    return objlist


def visual_acuity_details(self):
    objlist =[]
    datas = self.get('visual_acuity')
    create_post_log(self,datas)
    saved_count = 0
    not_saved_count = 0
    created_count = 0
    today_date =  datetime.now().date()
    created = False
    s_count = 0
    uuid_list = []

    for data in datas:
        if not Screening.objects.filter(uuid=data.get('screening_uuid')).exists():
            obj = {}
            obj['uuid'] = data.get('uuid')
            obj['screening_uuid'] = data.get('screening_uuid')
        else:
            obj, created = VisualAcuity.objects.update_or_create(
                screening_uuid = data.get('screening_uuid'),
                defaults= {
                            "app_created_at" : data.get('app_created_at'),
                            "uuid" : data.get('uuid'),
                            "partner_id" : data.get('partner_id'),
                            "vision_center_id" : data.get('vision_center_id'),
                            "unaided_distance_re_id" : data.get('un_aided_distance_re') if data.get('un_aided_distance_re') != 0 else None,
                            "unaided_distance_le_id" : data.get('un_aided_distance_le') if data.get('un_aided_distance_le') != 0 else None,
                            "unaided_near_re_id" : data.get('un_aided_near_re') if data.get('un_aided_near_re') != 0 else None,
                            "unaided_near_le_id" : data.get('un_aided_near_le') if data.get('un_aided_near_le') != 0 else None,
                            "aided_distance_re_id" : data.get('aided_distance_re') if data.get('aided_distance_re') != 0 else None,
                            "aided_distance_le_id" : data.get('aided_distance_le') if data.get('aided_distance_le') != 0 else None,
                            "aided_near_re_id" : data.get('aided_near_re') if data.get('aided_near_re') != 0 else None,
                            "aided_near_le_id" : data.get('aided_near_le') if data.get('aided_near_le') != 0 else None,
                            "pinhole_distance_re_id" : data.get('pinhole_distance_re') if data.get('pinhole_distance_re') != 0 else None,
                            "pinhole_distance_le_id" : data.get('pinhole_distance_le') if data.get('pinhole_distance_le') != 0 else None,
                            "pinhole_near_re_id" : data.get('pinhole_near_re') if data.get('pinhole_near_re') != 0 else None,
                            "pinhole_near_le_id" : data.get('pinhole_near_le') if data.get('pinhole_near_le') != 0 else None,
                            "color_re_id" : data.get('color_re') if data.get('color_re') != 0 else None,
                            "color_le_id" : data.get('color_le') if data.get('color_le') != 0 else None,
                            "treatment_for_refraction_id" : data.get('treatment_for_refraction'),
                            "do_you_want_to_refer" : data.get('want_to_refer') if data.get('want_to_refer') != 0 else None,
                            "refer_for_id" : data.get('refer_for') if data.get('refer_for') != 0 else None,
                            "refer_to_id" : data.get('referred_to') if data.get('referred_to') != 0 else None,
                            "app_updated_at" : data.get('app_updated_at'),
                            "latitude" : data.get('latitude') if data.get('latitude') != '' else None,
                            "longitude" : data.get('longitude') if data.get('longitude') != '' else None,    
                            })
        objlist.append(obj)
        uuid_list.append(data.get('uuid'))
        if created:
            s_count += 1 
    try:
        last_daily_record = DailyRecordsCalculation.objects.filter(date=today_date, record="Visual Acuity", error=None).last()
        total_records = None
        if last_daily_record is None:
            daily = s_count
            created_count = daily 
        else:
            daily = last_daily_record.total_records
            created_count = daily + s_count

        if created and today_date :
            saved_count = s_count
            daily_records_report=DailyRecordsCalculation.objects.create(
                date=today_date,
                record="Visual Acuity",
                error = None,
                uuid = None,
                saved_records=saved_count,
                not_saved_records=0,
                total_records=created_count
            )
            daily_records_report.save()
    except Exception as e:
        daily = DailyRecordsCalculation.objects.filter(date=today_date,record="Visual Acuity", error=e.args[0]).count()
        not_saved_count = s_count
        created_count = daily + not_saved_count
        error_uuid = DailyRecordsCalculation.objects.filter(status=2)
        for receive in error_uuid:
            if receive.error != e.args[0] and receive.uuid not in uuid_list and receive.date == today_date:
                daily_records_report = DailyRecordsCalculation.objects.create(
                    date=today_date,
                    record="Visual Acuity", 
                    error=e.args[0],
                    uuid=uuid_list,
                    saved_records=0,
                    not_saved_records=not_saved_count,
                    total_records=created_count
                )
                daily_records_report.save()
            

    return objlist

def glass_prescription_details(self):
    objlist =[]
    datas = self.get('glass_prescription')
    create_post_log(self,datas)
    saved_count = 0
    not_saved_count = 0
    created_count = 0
    today_date =  datetime.now().date()
    created = False
    s_count = 0
    uuid_list = []

    for data in datas:
        if not Screening.objects.filter(uuid=data.get('screening_uuid')).exists():
            obj = {}
            obj['uuid'] = data.get('uuid')
            obj['screening_uuid'] = data.get('screening_uuid')
        else:
            obj, created = GlassPrescription.objects.update_or_create(
                uuid = data.get('uuid'),
                screening_uuid = data.get('screening_uuid'),
                defaults= {
                            "app_created_at" : data.get('app_created_at'),
                            "partner_id" : data.get('partner_id'),
                            "vision_center_id" : data.get('vision_center_id'),
                            "sph_distance_re" : data.get('sph_distance_re') if data.get('sph_distance_re') != '' else None,
                            "sph_distance_le" : data.get('sph_distance_le') if data.get('sph_distance_le') != '' else None,
                            "cyl_distance_re" : data.get('cyl_distance_re') if data.get('cyl_distance_re') != '' else None,
                            "cyl_distance_le" : data.get('cyl_distance_le') if data.get('cyl_distance_le') != '' else None,
                            "axis_distance_re" : data.get('axis_distance_re') if data.get('axis_distance_re') != '' else None,
                            "axis_distance_le" : data.get('axis_distance_le') if data.get('axis_distance_le') != '' else None,
                            "va_distance_re_id" : data.get('va_distance_re') if data.get('va_distance_re') != 0 else None,
                            "va_distance_le_id" : data.get('va_distance_le') if data.get('va_distance_le') != 0 else None,
                            "sph_near_re" : data.get('sph_near_re') if data.get('sph_near_re') != '' else None,
                            "sph_near_le" : data.get('sph_near_le') if data.get('sph_near_le') != '' else None,
                            "cyl_near_re" : data.get('cyl_near_re') if data.get('cyl_near_re') != '' else None,
                            "cyl_near_le" : data.get('cyl_near_le') if data.get('cyl_near_le') != '' else None,
                            "axis_near_re" : data.get('axis_near_re') if data.get('axis_near_re') != '' else None,
                            "axis_near_le" : data.get('axis_near_le') if data.get('axis_near_le') != '' else None,
                            "va_near_re_id" : data.get('va_near_re') if data.get('va_near_re') != 0 else None,
                            "va_near_le_id" : data.get('va_near_le') if data.get('va_near_le') != 0 else None,
                            "spectacle_type_id" : data.get('spectacle_type')  if data.get('spectacle_type') != 0 else None,
                            "app_updated_at" : data.get('app_updated_at'),
                            "latitude" : data.get('latitude') if data.get('latitude') != '' else None,
                            "longitude" : data.get('longitude') if data.get('longitude') != '' else None,
                            })
        objlist.append(obj)
        uuid_list.append(data.get('uuid'))
        if created:
            s_count += 1 
    try:
        last_daily_record = DailyRecordsCalculation.objects.filter(date=today_date, record="Glass Prescription", error=None).last()
        total_records = None
        if last_daily_record is None:
            daily = s_count
            created_count = daily 
        else:
            daily = last_daily_record.total_records
            created_count = daily + s_count

        if created and today_date :
            saved_count = s_count
            daily_records_report=DailyRecordsCalculation.objects.create(
                date=today_date,
                record="Glass Prescription",
                error = None,
                uuid = None,
                saved_records=saved_count,
                not_saved_records=0,
                total_records=created_count
            )
            daily_records_report.save()
    except Exception as e:
        daily = DailyRecordsCalculation.objects.filter(date=today_date,record="Glass Prescription", error=e.args[0]).count()
        not_saved_count = s_count
        created_count = daily + not_saved_count
        error_uuid = DailyRecordsCalculation.objects.filter(status=2)
        for receive in error_uuid:
            if receive.error != e.args[0] and receive.uuid not in uuid_list and receive.date == today_date:
                daily_records_report = DailyRecordsCalculation.objects.create(
                    date=today_date,
                    record="Glass Prescription", 
                    error=e.args[0],
                    uuid=uuid_list,
                    saved_records=0,
                    not_saved_records=not_saved_count,
                    total_records=created_count
                )
                daily_records_report.save()

    return objlist


def spectacle_type_details(self):
    objlist =[]
    datas = self.get('spectacle_type')
    create_post_log(self,datas)
    saved_count = 0
    not_saved_count = 0
    created_count = 0
    today_date =  datetime.now().date()
    created = False
    s_count = 0
    uuid_list = []

    for data in datas:  
        if not GlassPrescription.objects.filter(uuid=data.get('glass_prescription_uuid')).exists():
            obj = {}
            obj['uuid'] = data.get('uuid')
            obj['glass_prescription_uuid'] = data.get('glass_prescription_uuid')
        else:
            st_obj = SpectacleType.objects.filter(uuid = data.get('uuid'))
            if st_obj.exists():
                otp_vc_camp= None
                otp_vc_camp_location= None
                location_state = st_obj.first().glass_collecting_location if hasattr(st_obj.first(), 'glass_collecting_location') else None
                if st_obj.first().get_pnt_details()[0].camp:
                    otp_vc_camp = st_obj.first().get_pnt_details()[0].camp
                    otp_vc_camp_location = st_obj.first().get_pnt_details()[0].camp.location
                else:
                    vc_camp_obj = VisionCenter.objects.filter(id=st_obj.first().get_pnt_details()[0].vision_center_id).first()
                    otp_vc_camp = vc_camp_obj.name 
                    otp_vc_camp_location = vc_camp_obj.address
                if st_obj.first().spectacle_status == 1 and st_obj.first().has_the_glass_collected == 2 and st_obj.first().spectacle_status != 2 and int(data.get('follow_up_status')) == 2:
                    send_sms(self, None, st_obj.first().get_pnt_details()[0].contact_no_1, st_obj.first().get_pnt_details()[0].unique_id, otp_vc_camp, otp_vc_camp_location,location_state, 3, st_obj.first().get_pnt_details()[0].language.id, st_obj.first().spectacle_status)
                if st_obj.first().spectacle_status in [1,2] and st_obj.first().spectacle_status !=3 and int(data.get('follow_up_status')) == 3:
                    send_sms(self, None, st_obj.first().get_pnt_details()[0].contact_no_1, st_obj.first().get_pnt_details()[0].unique_id, otp_vc_camp, otp_vc_camp_location,None, 6, st_obj.first().get_pnt_details()[0].language.id, st_obj.first().spectacle_status)
            obj, created = SpectacleType.objects.update_or_create(
                uuid = data.get('uuid'),
                defaults= {
                            "app_created_at" : data.get('app_created_at'),
                            "glass_prescription_uuid" : data.get('glass_prescription_uuid'),
                            "partner_id" : data.get('partner_id'),
                            "spectacle_name" : data.get('spectacle_name') if data.get('spectacle_name') != '' else None,
                            "spectacle_type_id" : data.get('spectacle_type') if data.get('spectacle_type') != 0 else None,
                            "has_the_glass_collected" : data.get('has_the_glass_collected') if data.get('has_the_glass_collected') != 0 else None,
                            "glass_collecting_location_id" : data.get('glass_collecting_location') if data.get('glass_collecting_location') != 0 else None,
                            "vision_center_id" : data.get('vision_center') if data.get('vision_center') != 0 else None,
                            "frame_code_id" : data.get('frame_code') if data.get('frame_code') != 0 else None,
                            "frame_size_id" : data.get('frame_size') if data.get('frame_size') != 0 else None,
                            "lens_type_id" : data.get('lens_type') if data.get('lens_type') != 0 else None,
                            "type_of_coating_id" : data.get('type_of_coating') if data.get('type_of_coating') != 0 else None,
                            "model_type_id" : data.get('model_type') if data.get('model_type') != 0 else None,
                            "r2c_eligible" : data.get('r2c_eligible') if data.get('r2c_eligible') != 0 else None,
                            "r2c_remark" : data.get('r2c_remark') if data.get('r2c_remark') != 0 else None,
                            "spectacle_status" : data.get('follow_up_status'),
                            "app_updated_at" : data.get('app_updated_at'),
                            })
            if created:
                if SpectacleType.objects.filter(uuid=obj.uuid).exists:
                    otp_vc_camp= None
                    otp_vc_camp_location= None
                    location_state = obj.glass_collecting_location if hasattr(obj, 'glass_collecting_location') else None
                    if obj.get_pnt_details()[0].camp:
                        otp_vc_camp = obj.get_pnt_details()[0].camp
                        otp_vc_camp_location = obj.get_pnt_details()[0].camp.location
                    else:
                        vc_camp_obj = VisionCenter.objects.filter(id=obj.get_pnt_details()[0].vision_center_id).first()
                        otp_vc_camp = vc_camp_obj.name 
                        otp_vc_camp_location = vc_camp_obj.address
                    if obj.spectacle_status == 3:
                        send_sms(self, None, obj.get_pnt_details()[0].contact_no_1, obj.get_pnt_details()[0].unique_id, otp_vc_camp, otp_vc_camp_location,None, 6, obj.get_pnt_details()[0].language.id, obj.spectacle_status)                    
                    if obj.spectacle_status == 1 and obj.has_the_glass_collected == 2:
                        send_sms(self, None, obj.get_pnt_details()[0].contact_no_1, obj.get_pnt_details()[0].unique_id, otp_vc_camp, otp_vc_camp_location,None, 4, obj.get_pnt_details()[0].language.id, obj.spectacle_status)
            
        objlist.append(obj)
        uuid_list.append(data.get('uuid'))
        if created:
            s_count += 1 
            
        
    try:
        last_daily_record = DailyRecordsCalculation.objects.filter(date=today_date, record="Spectacle Type", error=None).last()
        total_records = None
        if last_daily_record is None:
            daily = s_count
            created_count = daily 
        else:
            daily = last_daily_record.total_records
            created_count = daily + s_count

        if created and today_date :
            saved_count = s_count
            daily_records_report=DailyRecordsCalculation.objects.create(
                date=today_date,
                record="Spectacle Type",
                error = None,
                uuid = None,
                saved_records=saved_count,
                not_saved_records=0,
                total_records=created_count
            )
            daily_records_report.save()
    except Exception as e:
        daily = DailyRecordsCalculation.objects.filter(date=today_date,record="Spectacle Type", error=e.args[0]).count()
        not_saved_count = s_count
        created_count = daily + not_saved_count
        error_uuid = DailyRecordsCalculation.objects.filter(status=2)
        for receive in error_uuid:
            if receive.error != e.args[0] and receive.uuid not in uuid_list and receive.date == today_date:
                daily_records_report = DailyRecordsCalculation.objects.create(
                    date=today_date,
                    record="Spectacle Type", 
                    error=e.args[0],
                    uuid=uuid_list,
                    saved_records=0,
                    not_saved_records=not_saved_count,
                    total_records=created_count
                )
                daily_records_report.save()

    return objlist

def camp_details(self):
    objlist =[]
    datas = self.get('camp')
    create_post_log(self,datas)
    saved_count = 0
    not_saved_count = 0
    created_count = 0
    today_date =  datetime.now().date()
    camps_obj= Camp.objects.all().count()
    for data in datas:
        camp_code_list = Camp.objects.filter().values_list('code', flat=True)
        camp_code = sorted([int(i) for i in camp_code_list])[-1] + 1
        obj, created = Camp.objects.update_or_create(
            uuid = data.get('uuid'),
            defaults= {
                        "name" : data.get('name'),
                        "code" : camp_code,
                        "date" : data.get('date'),
                        "location" : data.get('location'),
                        "address" : data.get('address') if data.get('address') != "" else None,
                        "village" : data.get('village') if data.get('village') != "" else None,
                        "block" : data.get('block') if data.get('block') != "" else None,
                        "district_id" : data.get('district'),
                        "donor_id" : data.get('donor'),
                        "partner_id" : data.get('partner') if data.get('partner') != 0 else None,
                        "vision_center_id" : data.get('vision_center') if data.get('vision_center') != 0 else None,
                        "expected_glass_prescription" : data.get('expected_glass_prescription') if data.get('expected_glass_prescription') != "" else None,
                        "expected_refer_surgeries" : data.get('expected_refer_surgeries') if data.get('expected_refer_surgeries') != "" else None,
                        "expected_camp_OPD" : data.get('expected_camp_OPD') if data.get('expected_camp_OPD') != "" else None,
                        "coordinator_name" : data.get('coordinator_name') if data.get('coordinator_name') != "" else None,
                        "coordinator_mobile_no" : data.get('coordinator_mobile_no') if data.get('coordinator_mobile_no') != "" else None,
                        "exclusive_camp" : data.get('exclusive_camp'),
                        "delay_reason" : data.get('delay_reason') if data.get('delay_reason') != "" else None,
                        "start_time" : data.get('start_time') if data.get('start_time') != "" else None,
                        "end_time" : data.get('end_time') if data.get('end_time') != "" else None,
                        "created_by_id" : data.get('created_by'),
                        "modified_by_id" : data.get('modified_by') if data.get('modified_by') !=0 else data.get('created_by')
                        })
        objlist.append(obj)

        daily= DailyRecordsCalculation.objects.filter(date=today_date, record="Camp").count()       
        obj_server = obj.server_created_on.date()
        if created and obj_server == today_date :
            created_count = daily + 1
            saved_count += 1
            daily_records_report=DailyRecordsCalculation.objects.create(
                date=today_date,
                record="Camp",
                saved_records=saved_count,
                not_saved_records=0,
                total_records=created_count
            )
            daily_records_report.save()

    return objlist




def send_sms(request, number=None, mobile_no=None,camp=None,location=None,unique_id=None,state=None, value=None,language=None, spect_status=0):
    # Assuming you receive a POST request with JSON data
    from Raahi.settings import DATABASE_HOST, API_URL, API_KEY, SENDER_ID

    text=''
    if language == 1:
        if value == 1:  #otp
            text = "“Your One-Time Password (OTP) is " + str(number)+ ". By providing this information to the data entry personnel, you are granting consent for the collection of your personal information. This data will be used exclusively for the purpose of program quality improvement and assessing beneficiary satisfaction. Your signature on the consent form is mandatory and an integral part of this process”. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND."
            # otp_text = str(number)+" is your OTP. OTP is valid for 10 mins. Do not share this OTP with anyone for security reasons. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.",
            # text = otp_text[0] 
        if value == 2:    #registration
            # text = f"Thank you for participating in {#var#}{#var#} - Sightsavers National Truckers Programme. Your registration ID is {#var#}{unique_id}. We wish you a safe and happy journey."
            text = "Thank you for participating in {1} & {2}-Sightsavers National Truckers Programme. Your registration ID is {0}. We wish you a safe and happy journey. Sightsavers : : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 3:  #ready collect after 2 days
            text = "Thank you for participating in {1} & {2}-Sightsavers National Truckers Programme. Your registration ID is {0}. Your glass is ready now. Please collect the glass from the Location - {1} & {2} & {3} after 2 days from today. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, state, unique_id)
        if value == 4:    #pickup after 10 days(if select no in glass collected)
            text = "Thank you for participating in {1} & {2}-Sightsavers National Truckers Programme. Your registration ID is {0}. Please collect your glass after 10 days from this Location - {1} & {2}. Once glass is ready, you will receive SMS alert. We wish you a safe and happy journey. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 5: # Reminder
            text = "Thank you for participating in Sightsavers National Truckers Programme. Your registration ID is {0}. Your glass is ready and you have not yet collected it. Please collect it from the Location - {1} & {2} Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 6: #Delivered
            text = "Thank you for participating in {1} & {2}-Sightsavers National Truckers Programme. Your registration ID is {0}. Your spectacles have been delivered to you. We wish you a safe and happy journey. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
    if language == 2:
        if value == 1:
            text = "“आपका वन-टाइम पासवर्ड (ओटीपी) " + str(number)+ " है। डेटा एंट्री कर्मियों को यह जानकारी प्रदान करके, आप अपनी व्यक्तिगत जानकारी के संग्रह के लिए सहमति दे रहे हैं। इस डेटा का उपयोग विशेष रूप से कार्यक्रम की गुणवत्ता में सुधार और लाभार्थियों की संतुष्टि का आकलन करने के लिए किया जाएगा। सहमति प्रपत्र पर आपका हस्ताक्षर अनिवार्य है और इस प्रक्रिया का अभिन्न अंग है।” Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND."
        if value == 2:
            text = "{1} & {2} -साइट्सवर्स नेशनल ट्रकर्स प्रोग्राम में भाग लेने के लिए धन्यवाद। आपकी रजिस्ट्रेशन नंबर {0} है। हम आपकी सुखद एवं सुरक्षित यात्रा की कामना करते है । - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 3:  #ready collect after 2 days
            text = "साइट्सवर्स नेशनल ट्रकर्स प्रोग्राम में भाग लेने के लिए धन्यवाद। आपका रजिस्ट्रेशन नंबर {0} है। आपका चश्मा तैयार है। कृपया अपना चश्मा 2 दिनों के बाद - {1} & {2} से प्राप्त करें । Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, state, unique_id)
        if value == 4:
            text = "साइट्सवर्स नेशनल ट्रकर्स प्रोग्राम में भाग लेने के लिए धन्यवाद। आपका रजिस्ट्रेशन नंबर {0} है। कृपया {1} & {2} से 10 दिनों के बाद अपना चश्मा प्राप्त करें । हम आपकी सुखद एवं सुरक्षित यात्रा की कामना करते है। - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 5:
            text = "साइट्सवर्स नेशनल ट्रकर्स प्रोग्राम में भाग लेने के लिए धन्यवाद। आपका रजिस्ट्रेशन नंबर {0} है। आपका चश्मा तैयार है और आपने अभी तक इसे प्राप्त नहीं किया है। कृपया इसे {1} & {2} से प्राप्त करें - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 6:
            text = "{1} & {2} -साइट्सवर्स नेशनल ट्रकर्स प्रोग्राम में भाग लेने के लिए धन्यवाद। आपका रजिस्ट्रेशन नंबर {0} है। आपका चश्मा आपको प्राप्त हो चुका है । हम आपकी सुखद एवं सुरक्षित यात्रा की कामना करते है। - Sightsavers : : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
    if language == 3:
        if value == 1:
            text = "“ਤੁਹਾਡਾ ਵਨ-ਟਾਈਮ ਪਾਸਵਰਡ (OTP) " + str(number)+ " ਹੈ। ਡੇਟਾ ਐਂਟਰੀ ਕਰਨ ਵਾਲੇ ਕਰਮਚਾਰੀਆਂ ਨੂੰ ਇਹ ਜਾਣਕਾਰੀ ਦਿੰਦੇ ਹੋਏ, ਤੁਸੀਂ ਆਪਣੀ ਨਿੱਜੀ ਜਾਣਕਾਰੀ ਦੇ ਸੰਗ੍ਰਹਿ ਲਈ ਸਹਿਮਤੀ ਦੇ ਰਹੇ ਹੋ। ਇਹ ਡੇਟਾ ਵਿਸ਼ੇਸ਼ ਤੌਰ 'ਤੇ ਪ੍ਰੋਗਰਾਮ ਦੀ ਗੁਣਵੱਤਾ ਵਿੱਚ ਸੁਧਾਰ ਅਤੇ ਲਾਭਪਾਤਰੀਆਂ ਦੀ ਸੰਤੁਸ਼ਟੀ ਦਾ ਮੁਲਾਂਕਣ ਕਰਨ ਦੇ ਉਦੇਸ਼ ਲਈ ਵਰਤਿਆ ਜਾਵੇਗਾ। ਸਹਿਮਤੀ ਫਾਰਮ ਉਤੇ ਤੁਹਾਡੇ ਦਸਤਖਤ ਲਾਜ਼ਮੀ ਹਨ ਅਤੇ ਇਸ ਪ੍ਰਕਿਰਿਆ ਦਾ ਇੱਕ ਅਨਿੱਖੜਵਾਂ ਅੰਗ ਹੈ। Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND." 
        if value == 2:
            text = "{1} & {2} -ਸਾਈਟਸਾਵਰ ਕੌਮੀ ਟਰੱਕਰਜ਼ ਪ੍ਰੋਗਰਾਮ ਵਿਚ ਹਿੱਸਾ ਲੈਣ ਲਈ ਤੁਹਾਡਾ ਧੰਨਵਾਦ. ਤੁਹਾਡੀ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਆਈਡੀ {0} ਹੈ ਅਸੀਂ ਤੁਹਾਨੂੰ ਇੱਕ ਸੁਰੱਖਿਅਤ ਅਤੇ ਖੁਸ਼ਹਾਲ ਸਫ਼ਰ ਚਾਹੁੰਦੇ ਹਾਂ - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 3:
            text = "ਸਾਈਟਸਾਵਰ ਕੌਮੀ ਟਰੱਕਰਜ਼ ਪ੍ਰੋਗਰਾਮ ਵਿਚ ਹਿੱਸਾ ਲੈਣ ਲਈ ਤੁਹਾਡਾ ਧੰਨਵਾਦ. ਤੁਹਾਡੀ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਆਈਡੀ {0} ਹੈ ਤੁਹਾਡਾ ਗਲਾਸ ਹੁਣ ਤਿਆਰ ਹੈ. ਕਿਰਪਾ ਕਰਕੇ ਨਿਰਧਾਰਿਤ ਸਥਾਨ - {1} & {2} ਤੋਂ {3} ਤੋਂ ਬਾਅਦ ਗਲਾਸ ਲਿਆਓ – Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, state, unique_id)
        if value == 4:
            text = "ਪਿਆਰੇ ਲਾਭਪਾਤਰ, ਤੁਹਾਡੀ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਆਈਡੀ {0} ਹੈ .ਆਪਣੇ ਗਲਾਸ ਨੂੰ 10 ਦਿਨਾਂ ਬਾਅਦ {1} & {2}ਤੋਂ ਲਿਆਓ. - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 5:
            text = "ਸਾਈਟਸਾਵਰ ਕੌਮੀ ਟਰੱਕਰਜ਼ ਪ੍ਰੋਗਰਾਮ ਵਿੱਚ ਹਿੱਸਾ ਲੈਣ ਲਈ ਤੁਹਾਡਾ ਧੰਨਵਾਦ. ਤੁਹਾਡੀ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਆਈਡੀ {0} ਹੈ ਤੁਹਾਡਾ ਗਲਾਸ ਤਿਆਰ ਹੈ ਅਤੇ ਤੁਸੀਂ ਹਾਲੇ ਤੱਕ ਇਸਨੂੰ ਇਕੱਠਾ ਨਹੀਂ ਕੀਤਾ ਹੈ. ਕਿਰਪਾ ਕਰਕੇ ਇਸ ਸਥਾਨ ਤੋਂ ਭੇਜੋ - {1} & {2} - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 6:
            text = "{1} & {2} -ਸਾਈਟਸਾਵਰ ਕੌਮੀ ਟਰੱਕਰਜ਼ ਪ੍ਰੋਗਰਾਮ ਵਿੱਚ ਹਿੱਸਾ ਲੈਣ ਲਈ ਤੁਹਾਡਾ ਧੰਨਵਾਦ. ਤੁਹਾਡੀ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਆਈਡੀ {0} ਹੈ .ਤੁਹਾਡੇ ਐਨਕਾਂ ਤੁਹਾਨੂੰ ਸੌਂਪੀਆਂ ਗਈਆਂ ਹਨ ਅਸੀਂ ਤੁਹਾਨੂੰ ਇੱਕ ਸੁਰੱਖਿਅਤ ਅਤੇ ਖੁਸ਼ਹਾਲ ਸਫ਼ਰ ਚਾਹੁੰਦੇ ਹਾਂ - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
    if language == 4:
        if value == 1:
            text = "“Your One-Time Password (OTP) is " + str(number)+ ". By providing this information to the data entry personnel, you are granting consent for the collection of your personal information. This data will be used exclusively for the purpose of program quality improvement and assessing beneficiary satisfaction. Your signature on the consent form is mandatory and an integral part of this process”. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND."
        if value == 2:
            text = "ସାଇଟସେଭର୍ସ ର ଟ୍ରକ୍ସର୍ସ ଚକ୍ଷୁ ସ୍ଵାସ୍ଥ୍ୟ କାର୍ଯ୍ୟକ୍ରମ ଅନ୍ତର୍ଗତ {1} & {2} ରେ ଅଂଶ ଗ୍ରହଣ କରିଥିବାରୁ ଆପଣଙ୍କୁ ଧନ୍ୟବାଦ| ଆପଣଂକର ପଞିକରଣ ନମ୍ବର ହେଉଛି {0} | ଆମେ ଆପଣଙ୍କର ଶୁଭ ଏବଂ ସୁରକ୍ଷିତ ଯାତ୍ରା କାମନା କରୁଛୁ| - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 3:
            text = "ସାଇଟସେଭର୍ସ ର ଟ୍ରକ୍ସର୍ସ ଚକ୍ଷୁ ସ୍ଵାସ୍ଥ୍ୟ କାର୍ଯ୍ୟକ୍ରମ ଅନ୍ତର୍ଗତ ରେ ଅଂଶ ଗ୍ରହଣ କରିଥିବାରୁ ଆପଣଙ୍କୁ ଧନ୍ୟବାଦ| ଆପଣଂକର ପଞିକରଣ ନମ୍ବର ହେଉଛି {0} | ଆପଣଙ୍କର ଚଷମା ଏବେ ପ୍ରସ୍ତୁତ ହୋଇଯାଇଛି| ଦୟାକରି ତାକୁ {1} ଦିନ ପରେ {2} & {3} ସ୍ଥାନରୁ ସଂଗ୍ରହ କରିନିଅନ୍ତୁ| - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, state, unique_id)
        if value == 4: #pickup after 10 days(if select no in glass collected)
            text = "Thank you for participating in {1} & {2}-Sightsavers National Truckers Programme. Your registration ID is {0}. Please collect your glass after 10 days from this Location - {1} & {2}. Once glass is ready, you will receive SMS alert. We wish you a safe and happy journey. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 5:
            text = "ସାଇଟସେଭର୍ସ ର ଟ୍ରକ୍ସର୍ସ ଚକ୍ଷୁ ସ୍ଵାସ୍ଥ୍ୟ କାର୍ଯ୍ୟକ୍ରମ ଅନ୍ତର୍ଗତ ରେ ଅଂଶ ଗ୍ରହଣ କରିଥିବାରୁ ଆପଣଙ୍କୁ ଧନ୍ୟବାଦ| ଆପଣଂକର ପଞିକରଣ ନମ୍ବର ହେଉଛି {0} | ଆପଣଙ୍କର ଚଷମା ଏବେ ପ୍ରସ୍ତୁତ ହୋଇଯାଇଛି ଏବଂ ଆପଣ ଏବେ ଯାଏଁ ତାହା ସଂଗ୍ରହ କରିନାହାନ୍ତି| ଦୟାକରି ତାକୁ {1} & {2} ସ୍ଥାନରୁ ସଂଗ୍ରହ କରିନିଅନ୍ତୁ| - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 6: #Delivered
            text = "Thank you for participating in {1} & {2}-Sightsavers National Truckers Programme. Your registration ID is {0}. Your spectacles have been delivered to you. We wish you a safe and happy journey. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
    if language == 5:
        if value == 1:
            text = "“আপনার ওয়ান-টাইম পাসওয়ার্ড (OTP) হল " + str(number)+ " ৷ ডেটা এন্ট্রি কর্মীদের এই তথ্য প্রদান করে, আপনি আপনার ব্যক্তিগত তথ্য সংগ্রহের জন্য সম্মতি দিচ্ছেন। এই ডেটা শুধুমাত্র প্রোগ্রামের গুণমান উন্নয়ন এবং উপকৃত ব্যক্তির সন্তুষ্টি মূল্যায়নের উদ্দেশ্যে ব্যবহার করা হবে। সম্মতি ফর্মে আপনার স্বাক্ষর বাধ্যতামূলক এবং এই প্রক্রিয়ার একটি অবিচ্ছেদ্য অংশ”। Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND."
        if value == 2:
            text = "Thank you for participating in {1} & {2}-Sightsavers National Truckers Programme. Your registration ID is {0}. We wish you a safe and happy journey. Sightsavers : : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 3:
            text = "Thank you for participating in {1} & {2}-Sightsavers National Truckers Programme. Your registration ID is {0}. Your glass is ready now. Please collect the glass from the Location - {1} & {2} & {3} after 2 days from today. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, state, unique_id)
        if value == 4:
            text = "Thank you for participating in {1} & {2}-Sightsavers National Truckers Programme. Your registration ID is {0}. Please collect your glass after 10 days from this Location - {1} & {2}. Once glass is ready, you will receive SMS alert. We wish you a safe and happy journey. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 5:
            text = "Thank you for participating in Sightsavers National Truckers Programme. Your registration ID is {0}. Your glass is ready and you have not yet collected it. Please collect it from the Location - {1} & {2} Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 6:
            text = "Thank you for participating in {1} & {2}-Sightsavers National Truckers Programme. Your registration ID is {0}. Your spectacles have been delivered to you. We wish you a safe and happy journey. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
    if language == 6:
        if value == 1:
            text = "“Your One-Time Password (OTP) is " + str(number)+ ". By providing this information to the data entry personnel, you are granting consent for the collection of your personal information. This data will be used exclusively for the purpose of program quality improvement and assessing beneficiary satisfaction. Your signature on the consent form is mandatory and an integral part of this process”. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND."
        if value == 2:    #registration
            text = "Thank you for participating in {1} & {2}-Sightsavers National Truckers Programme. Your registration ID is {0}. We wish you a safe and happy journey. Sightsavers : : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 3:  #ready 
            text = "Thank you for participating in {1} & {2}-Sightsavers National Truckers Programme. Your registration ID is {0}. Your glass is ready now. Please collect the glass from the Location - {1} & {2} & {3} after 2 days from today. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, state, unique_id)
        if value == 4:    #pickup 
            text = "Thank you for participating in {1} & {2}-Sightsavers National Truckers Programme. Your registration ID is {0}. Please collect your glass after 10 days from this Location - {1} & {2}. Once glass is ready, you will receive SMS alert. We wish you a safe and happy journey. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 5: # Reminder
            text = "Thank you for participating in Sightsavers National Truckers Programme. Your registration ID is {0}. Your glass is ready and you have not yet collected it. Please collect it from the Location - {1} & {2} Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 6: #Delivered
            text = "Thank you for participating in {1} & {2}-Sightsavers National Truckers Programme. Your registration ID is {0}. Your spectacles have been delivered to you. We wish you a safe and happy journey. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
    
    if language == 7:
        if value == 1:
            text = "“നിങ്ങളുടെ ഒറ്റത്തവണ പാസ്‌വേഡ് (OTP) " + str(number)+ " ആണ്. ഡാറ്റാ എൻട്രി ഉദ്യോഗസ്ഥർക്ക് ഈ വിവരം നൽകുന്നതിലൂടെ, നിങ്ങളുടെ വ്യക്തിഗത വിവരങ്ങളുടെ ശേഖരണത്തിന് നിങ്ങൾ സമ്മതം നൽകുന്നു. ഈ ഡാറ്റ പ്രോഗ്രാമിന്റെ ഗുണനിലവാരം മെച്ചപ്പെടുത്തുന്നതിനും ഗുണഭോക്താവിന്റെ സംതൃപ്തി വിലയിരുത്തുന്നതിനും വേണ്ടി മാത്രമായി ഉപയോഗിക്കും. സമ്മത ഫോമിലെ നിങ്ങളുടെ ഒപ്പ് നിർബന്ധമാണ്, ഈ പ്രക്രിയ ഒരു അവിഭാജ്യ ഘടകമാണ്. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND."
        if value == 2:
            text = "{1} & {2} -Sightsavers ദേശീയ ട്രാക്കറുകൾ പ്രോഗ്രാം പങ്കെടുത്തതിന് നന്ദി. നിങ്ങളുടെ രജിസ്ട്രേഷൻ ID {0} ആണ്. സുരക്ഷിതവും സന്തുഷ്ടവുമായ ഒരു യാത്ര ഞങ്ങൾ ആശംസിക്കുന്നു. : : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 3:
            text = "Sightsavers ദേശീയ ട്രാക്കറുകൾ പ്രോഗ്രാം പങ്കെടുത്തതിന് നന്ദി. നിങ്ങളുടെ രജിസ്ട്രേഷൻ ID {0} ആണ്. നിങ്ങളുടെ ഗ്ലാസ് ഇപ്പോൾ തയ്യാർ. {1} ദിവസത്തിനു ശേഷം ഇന്നുമുതൽ ദിവസം മുതൽ {2} & {3} സ്ഥലത്ത് നിന്ന് ഗ്ലാസ് ശേഖരിക്കുക : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, state, unique_id)
        if value == 4:
            text = "Sightsavers നാഷണൽ ട്രക്ക്സ്മാർ പ്രോഗ്രാമിൽ പങ്കെടുത്തതിന് നന്ദി. നിങ്ങളുടെ രജിസ്ട്രേഷൻ ID {0} ആണ്. ഈ ലൊക്കേഷനിൽ നിന്ന് 10 ദിവസത്തിനുശേഷം നിങ്ങളുടെ ഗ്ലാസ് ശേഖരിക്കൂ - {2} & {3}. ഒരിക്കൽ ഗ്ലാസ് തയ്യാറാക്കിയാൽ നിങ്ങൾക്ക് SMS അലേർട്ട് ലഭിക്കും. സുരക്ഷിതവും സന്തുഷ്ടവുമായ ഒരു യാത്ര ഞങ്ങൾ ആശംസിക്കുന്നു. : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, state, unique_id)
        if value == 5:
            text = "{1} & {2} -Sightsavers ദേശീയ ട്രാക്കേർസ് പ്രോഗ്രാമിൽ പങ്കെടുത്തതിന് നന്ദി. നിങ്ങളുടെ രജിസ്ട്രേഷൻ ID {0} ആണ്. നിങ്ങളുടെ ഗ്ലാസ് തയ്യാർ, അത് ഇനിയും ശേഖരിക്കില്ല. ലൊക്കേഷനിൽ നിന്നും അത് ശേഖരിക്കുക - {1} & {2} & {3} : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, state, unique_id)
        if value == 6:
            text = "{1} & {2} -Sightsavers ദേശീയ ട്രാക്കറുകൾ പ്രോഗ്രാം പങ്കെടുത്തതിന് നന്ദി. നിങ്ങളുടെ രജിസ്ട്രേഷൻ ID {0} ആണ്. നിങ്ങളുടെ കണ്ണുകൾ നിങ്ങൾക്ക് നൽകിയിട്ടുണ്ട്. സുരക്ഷിതവും സന്തുഷ്ടവുമായ ഒരു യാത്ര ഞങ്ങൾ ആശംസിക്കുന്നു : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
    if language == 8:
        if value == 1:
            text = "“ನಿಮ್ಮ ಒನ್-ಟೈಮ್ ಪಾಸ್‌ವರ್ಡ್ (OTP) " + str(number)+ " ಆಗಿದೆ. ಡೇಟಾ ಎಂಟ್ರಿ ಸಿಬ್ಬಂದಿಗೆ ಈ ಮಾಹಿತಿಯನ್ನು ಒದಗಿಸುವ ಮೂಲಕ, ನಿಮ್ಮ ವೈಯಕ್ತಿಕ ಮಾಹಿತಿಯ ಸಂಗ್ರಹಣೆಗೆ ನೀವು ಸಮ್ಮತಿಯನ್ನು ನೀಡುತ್ತಿರುವಿರಿ. ಪ್ರೋಗ್ರಾಂ ಗುಣಮಟ್ಟ ಸುಧಾರಣೆ ಮತ್ತು ಫಲಾನುಭವಿಗಳ ತೃಪ್ತಿಯನ್ನು ನಿರ್ಣಯಿಸುವ ಉದ್ದೇಶಕ್ಕಾಗಿ ಈ ಡೇಟಾವನ್ನು ಪ್ರತ್ಯೇಕವಾಗಿ ಬಳಸಲಾಗುತ್ತದೆ. ಸಮ್ಮತಿ ನಮೂನೆಯಲ್ಲಿ ನಿಮ್ಮ ಸಹಿ ಕಡ್ಡಾಯವಾಗಿದೆ ಮತ್ತು ಈ ಪ್ರಕ್ರಿಯೆಯ ಅವಿಭಾಜ್ಯ ಅಂಗವಾಗಿದೆ”. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND."
        if value == 2:
            text = "{1} & {2} Sightsavers ನ್ಯಾಷನಲ್ ಟ್ರಕರ್ಸ್ ಕಾರ್ಯಕ್ರಮದಲ್ಲಿ ಭಾಗವಹಿಸಿದ್ದಕ್ಕಾಗಿ ಧನ್ಯವಾದಗಳು. ನಿಮ್ಮ ನೋಂದಣಿ ID {0} ಆಗಿದೆ. ಸುರಕ್ಷಿತ ಮತ್ತು ಸಂತೋಷದ ಪ್ರಯಾಣವನ್ನು ನಾವು ಬಯಸುತ್ತೇವೆ. - Sightsavers: ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 3:
            text = "ಆತ್ಮೀಯ ಫಲಾನುಭವಿ, ನಿಮ್ಮ ನೋಂದಣಿ ID {0} ಆಗಿದೆ. ನಿಮ್ಮ ಗಾಜು ಈಗ ಸಿದ್ಧವಾಗಿದೆ. ಇಂದಿನಿಂದ  {1} ದಿನಗಳ ನಂತರ - {2} & {3} ನಿಂದ ಗಾಜನ್ನು ಸಂಗ್ರಹಿಸಿ. - Sightsavers : : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, state, unique_id)
        if value == 4:
            text = "ಸೈಟವರ್ಸ್ ನ್ಯಾಷನಲ್ ಟ್ರಕರ್ಸ್ ಪ್ರೋಗ್ರಾಂನಲ್ಲಿ ಭಾಗವಹಿಸಿದ್ದಕ್ಕಾಗಿ ಧನ್ಯವಾದಗಳು. ನಿಮ್ಮ ನೋಂದಣಿ ID {0} ಆಗಿದೆ. ಈ ಸ್ಥಳದಿಂದ {1} & {2} , 10 ದಿನಗಳ ನಂತರ ನಿಮ್ಮ ಗ್ಲಾಸ್ ಅನ್ನು ಸಂಗ್ರಹಿಸಿ -. ಗಾಜಿನ ಸಿದ್ಧವಾದಾಗ, ನೀವು SMS ಎಚ್ಚರಿಕೆಯನ್ನು ಸ್ವೀಕರಿಸುತ್ತೀರಿ. ಸುರಕ್ಷಿತ ಮತ್ತು ಸಂತೋಷದ ಪ್ರಯಾಣವನ್ನು ನಾವು ಬಯಸುತ್ತೇವೆ. - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.-".format(camp, location, unique_id)
        if value == 5:
            text = "ಸೈಟ್ಸೇವರ್ಸ್ ರಾಷ್ಟ್ರೀಯ ಟ್ರಕರ್ಸ್ ಕಾರ್ಯಕ್ರಮದಲ್ಲಿ ಪಾಲ್ಗೊಂಡಿದ್ದಕ್ಕಾಗಿಧನ್ಯವಾದಗಳು.ನಿಮ್ಮ ನೋಂದಣಿ ID {0} ಆಗಿದೆ.ನಿಮ್ಮ ಗಾಜಿನ ಸಿದ್ಧವಾಗಿದೆ ಮತ್ತು ನೀವು ಅದನ್ನು ಇನ್ನೂ ಸಂಗ್ರಹಿಸಿಲ್ಲ.ದಯವಿಟ್ಟು ಅದನ್ನು ಸ್ಥಳದಿಂದ ಸಂಗ್ರಹಿಸಿ - {1} & {2} - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 6:
            text = "{1} & {2}Sightsavers ನ್ಯಾಷನಲ್ ಟ್ರಕರ್ಸ್ ಕಾರ್ಯಕ್ರಮದಲ್ಲಿ ಭಾಗವಹಿಸಿದ್ದಕ್ಕಾಗಿ ಧನ್ಯವಾದಗಳು. ನಿಮ್ಮ ನೋಂದಣಿ ID {0} .ನಿಮ್ಮ ಕನ್ನಡಕವನ್ನು ನಿಮಗೆ ವಿತರಿಸಲಾಗಿದೆ. ಸುರಕ್ಷಿತ ಮತ್ತು ಸಂತೋಷದ ಪ್ರಯಾಣವನ್ನು ನಾವು ಬಯಸುತ್ತೇವೆ - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
    if language == 9:
        if value == 1:
            text = "“మీ వన్-టైమ్ పాస్‌వర్డ్ (OTP) " + str(number)+ ". డేటా ఎంట్రీ సిబ్బందికి ఈ సమాచారాన్ని అందించడం ద్వారా, మీరు మీ వ్యక్తిగత సమాచార సేకరణకు సమ్మతిని మంజూరు చేస్తున్నారు. ప్రోగ్రామ్ నాణ్యత మెరుగుదల మరియు లబ్ధిదారుల సంతృప్తిని అంచనా వేయడం కోసం ఈ సమాచారం   ప్రత్యేకంగా ఉపయోగించబడుతుంది. సమ్మతి పత్రంపై మీ సంతకం తప్పనిసరి మరియు ఈ ప్రక్రియలో అంతర్భాగం” Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND."
        if value == 2:
            text = "{1} & {2} -Sightsavers నేషనల్ ట్రక్కర్స్ కార్యక్రమంలో పాల్గొన్నందుకు ధన్యవాదాలు. మీ నమోదు ID {0}. మీకు సురక్షితమైన మరియు సంతోషకరమైన ప్రయాణం కావాలి. - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 3:
            text = "Sightsavers నేషనల్ ట్రక్కర్స్ కార్యక్రమంలో పాల్గొన్నందుకు ధన్యవాదాలు. మీ నమోదు ID {0}. ఇప్పుడు మీ గాజు సిద్ధంగా ఉంది. దయచేసి నుండి 10 రోజుల తరువాత {1} & {2} రోజు నుండి గాజుని సేకరించండి - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, state, unique_id)
        if value == 4:
            text = "Sightsavers నేషనల్ ట్రక్కర్స్ కార్యక్రమంలో పాల్గొన్నందుకు ధన్యవాదాలు. మీ నమోదు ID {0}. ఈ స్థానం నుండి 2 రోజుల తరువాత మీ గ్లాసును తీసుకోండి - {1} & {2}. ఒకసారి గాజు సిద్ధంగా ఉంది, మీరు SMS హెచ్చరికను స్వీకరిస్తారు. మీకు సురక్షితమైన మరియు సంతోషకరమైన ప్రయాణం కావాలి. - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND..".format(camp, location, unique_id)
        if value == 5:
            text = "Sightsavers నేషనల్ ట్రక్కర్స్ కార్యక్రమంలో పాల్గొన్నందుకు ధన్యవాదాలు. మీ నమోదు ID {0}. మీ గ్లాస్ సిద్ధంగా ఉంది మరియు మీరు దాన్ని ఇంకా సేకరించలేదు. దయచేసి దీన్ని స్థానం నుండి సేకరించండి - {1} & {2} - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 6:
            text = "{1} & {2} -Sightsavers నేషనల్ ట్రక్కర్స్ కార్యక్రమంలో పాల్గొన్నందుకు ధన్యవాదాలు. మీ రిజిస్ట్రేషన్ ఐడి {0} గా ఉంది. మీ కళ్ళజోళ్ళు మీకు పంపించబడ్డాయి. మీకు సురక్షితమైన మరియు సంతోషకరమైన ప్రయాణం కావాలి - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
    if language == 10:
        if value == 1:
            text = "உங்களது ஒரு முறை கடவுச்சொல் (OTP) " + str(number)+ " ஆகும். தரவு உள்ளீடு செய்யும் நபரிடம் அதை வழங்குவதன் மூலம், உங்கள் தனிப்பட்ட தகவலைச் சேகரிக்கவும், ஆராய்ச்சி நோக்கங்களுக்காக அதைப் பயன்படுத்தவும் ஒப்புதல் அளிக்கிறீர்கள். சைட்சேவர்கள்: ராயல் காமன்வெல்த் சொசைட்டி ஃபார் தி பிளைண்ட். Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND."
        if value == 2:
            text = "{1} & {2} -Sightsavers தேசிய டிரக்கர்ஸ் திட்டத்தில் பங்கேற்றதற்கு நன்றி. உங்கள் பதிவு எண் {0} ஆகும். நாங்கள் உங்களுக்கு ஒரு பாதுகாப்பான மற்றும் மகிழ்ச்சியான பயணம் விரும்புகிறேன். : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 3:   # ready
            text = "Thank you for participating in {1} & {2}-Sightsavers National Truckers Programme. Your registration ID is {0}. Your glass is ready now. Please collect the glass from the Location - {1} & {2} & {3} after 2 days from today. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, state, unique_id)
        if value == 4:
            text = "Sightsavers தேசிய டிரக்கர்ஸ் திட்டத்தில் பங்கேற்றதற்கு நன்றி. உங்கள் பதிவு எண் {0} ஆகும். 10 நாட்களுக்குப் பின் {1} & {2} இடத்திலிருந்து உங்கள் கண்ணாடியை சேகரிக்கவும். கண்ணாடி தயாராக இருக்கும் போது, நீங்கள் ஒரு SMS அறிவிப்பை பெறுவீர்கள். நாங்கள் உங்களுக்கு ஒரு பாதுகாப்பான மற்றும் மகிழ்ச்சியான பயணம் விரும்புகிறேன். : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 5:
            text = "Sightsavers தேசிய டிரக்கர்ஸ் திட்டத்தில் பங்கேற்றதற்கு நன்றி. உங்கள் பதிவு எண் {0} ஆகும். உங்கள் கண்ணாடி தயாராக உள்ளது, நீங்கள் அதை இன்னும் சேகரிக்கவில்லை.  {1} & {2} இடத்திலிருந்து அதை சேகரிக்கவும். : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 6:
            text = "{1} & {2} -Sightsavers தேசிய டிரக்கர்ஸ் திட்டத்தில் பங்கேற்றதற்கு நன்றி. உங்கள் பதிவு எண் {0} ஆகும். உங்களுடைய கண்ணாடி உங்களுக்கு வழங்கப்பட்டுள்ளது. நாங்கள் உங்களுக்கு ஒரு பாதுகாப்பான மற்றும் மகிழ்ச்சியான பயணம் விரும்புகிறேன். : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
    if language == 11:
        if value == 1:
            text = "“Your One-Time Password (OTP) is " + str(number)+ ". By providing this information to the data entry personnel, you are granting consent for the collection of your personal information. This data will be used exclusively for the purpose of program quality improvement and assessing beneficiary satisfaction. Your signature on the consent form is mandatory and an integral part of this process”. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND."
        if value == 2:
            text = "{1} & {2} -Sightsavers National Truckers Program માં ભાગ લેવા બદલ આભાર. તમારી રજીસ્ટ્રેશન આઈડી એ {0} છે અમે તમને સલામત અને ખુશ પ્રવાસની ઇચ્છા રાખીએ છીએ. - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 3:
            text = "સાઇટવેર્સ નેશનલ ટ્રકર્સ પ્રોગ્રામમાં ભાગ લેવા બદલ આભાર. તમારી રજીસ્ટ્રેશન આઈડી એ {0} .છે તમારું કાચ હવે તૈયાર છે કૃપા કરીને સ્થાનમાંથી કાચ એકત્રિત કરો - {1} & {2} પછી {3} દિવસ પછી - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, state, unique_id)
        if value == 4:
            text = "સાઇટવેર્સ નેશનલ ટ્રકર્સ પ્રોગ્રામમાં ભાગ લેવા બદલ આભાર. તમારી રજીસ્ટ્રેશન આઈડી એ {0} છે આ સ્થાનથી 10 દિવસ પછી તમારા કાચને એકત્રિત કરો - {1} & {2}. અમે તમને સલામત અને ખુશ પ્રવાસની ઇચ્છા રાખીએ છીએ. - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND".format(camp, location, unique_id)
        if value == 5:
            text = "સાઇટવેર્સ નેશનલ ટ્રકર્સ પ્રોગ્રામમાં ભાગ લેવા બદલ આભાર. તમારી રજીસ્ટ્રેશન આઈડી એ {0}. છે તમારું ગ્લાસ તૈયાર છે અને તમે હજી તે એકત્રિત કરી નથી. કૃપા કરી તેને સ્થાનથી એકત્રિત કરો - {1} & {2} - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 6:
            text = "{1} & {2} -Sightsavers National Truckers Program માં ભાગ લેવા બદલ આભાર. તમારી રજીસ્ટ્રેશન આઈડી {0} છે .તમારા ચશ્માનો તમને વિતરિત કરવામાં આવ્યા છે. અમે તમને સલામત અને ખુશ પ્રવાસની ઇચ્છા રાખીએ છીએ. - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
    if language == 12:
        if value == 1:
            text = "“Your One-Time Password (OTP) is " + str(number)+ ". By providing this information to the data entry personnel, you are granting consent for the collection of your personal information. This data will be used exclusively for the purpose of program quality improvement and assessing beneficiary satisfaction. Your signature on the consent form is mandatory and an integral part of this process”. Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND."
        if value == 2:
            text = "{1} & {2} - Sightsavers राष्ट्रीय ट्रकवाहक कार्यक्रम मध्ये सहभागी झाल्याबद्दल धन्यवाद. आपला नोंदणी ID {0} आहे आम्ही आपल्याला सुरक्षित आणि आनंदी प्रवास ह : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 3:
            text = "साइटस्वारस नॅशनल ट्रककर्स प्रोग्रॅममध्ये सहभागी होण्याबद्दल धन्यवाद. आपला नोंदणी ID {0} आहे आपले काचेचे आता सज्ज आहे कृपया स्थानावरुन - {1} & {2} आजपासून {3} दिवसांनंतर काचेचा गोळा करा - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, state, unique_id)
        if value == 4:
            text = "साइटस्वारस नॅशनल ट्रककर्स प्रोग्रॅममध्ये सहभागी होण्याबद्दल धन्यवाद. आपला नोंदणी ID {0} आहे कृपया आपले स्थान 10 दिवसांनंतर संकलित करा - {1} & {2}. आम्ही आपल्याला सुरक्षित आणि आनंदी प्रवास ह - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
        if value == 5:
            text = "साइटस्वारस नॅशनल ट्रककर्स प्रोग्रॅममध्ये सहभागी होण्याबद्दल धन्यवाद. आपला नोंदणी ID {0} आहे आपले काच तयार आहे आणि आपण अद्याप ते संकलित केले नाही.​कृपया कडून गोळा करा - {1} & {2} - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND".format(camp, location, unique_id)
        if value == 6:
            text = "{1} & {2} - Sightsavers राष्ट्रीय ट्रकवाहक कार्यक्रम मध्ये सहभागी झाल्याबद्दल धन्यवाद. आपला नोंदणी ID {0} आहे .आपले नकाशे आपल्याला वितरित झाले आहेत आम्ही आपल्याला सुरक्षित आणि आनंदी प्रवास ह - Sightsavers : ROYAL COMMONWEALTH SOCIETY FOR THE BLIND.".format(camp, location, unique_id)
    # if request.method == 'POST':
    if value != 1:
        if not ReceivedSMS.objects.filter(mobile_no=mobile_no, languege_id=language, content=text).exists():
            sms_obj = ReceivedSMS.objects.create(
                mobile_no=mobile_no, 
                sms_status=1,
                languege_id=language, 
                content=text,
                )
            sms_obj.save()
    if text != None and mobile_no != None and value == 1:
        try:
            data = {
                        "Text" : text,
                        "Number" : "91"+str(mobile_no),
                        "SenderId" : SENDER_ID,
                        "DRNotifyUrl" : DATABASE_HOST,
                        "DRNotifyHttpMethod" : "POST",
                        "Message"  : "Accepted",
                        "Tool":"API"
                    } 

            # Send SMS using requests library
            response = requests.post(API_URL, json=data, headers={'Authorization': f'Basic {API_KEY}'})
            response_data = response.json()
            # Handle the response as needed
            if response.status_code == 200 and response_data.get("Message") == "Accepted":
                response_vlu ={"status": "success", "message": response_data.get("Message")}
            else:
                response_vlu ={"status": "error", "message": response_data.get("Message")}
        except Exception as e:
            logger.error(e.args[0])
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_stack = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(error_stack)
            response_vlu = {"status": "error", "message": str(e)}
        return JsonResponse(response_vlu)



import os
# from datetime import datetime
def create_post_log(request,data):
    from Raahi.settings import BASE_DIR
    from django.core.files.base import ContentFile, File
    today_date = datetime.now()
    year = today_date.strftime("%Y")
    dt = today_date.strftime("%d")
    m = today_date.strftime("%m")
    hour = today_date.strftime("%H")
    minute = today_date.strftime("%M")
    new_file_path = '%s/media/logSync/%s/%s/%s' % (BASE_DIR,year,m,dt)
    if not os.path.exists(new_file_path):
        os.makedirs(new_file_path)
    file_name = "SyncLog" + "-" + year + "-" + m + "-" + dt + ".txt"
    full_filename = os.path.join(BASE_DIR,new_file_path,file_name)
    with open(full_filename, 'a', encoding='utf8') as f:
        f.writelines("\n\n\n==================================================\n\n")
        f.writelines("\nLog Date & Time : "+ datetime.now().strftime("%m/%d/%Y, %H:%M:%S")+"hrs")
        # json.dump(data, f, ensure_ascii=False, indent=4)
        data_str = json.dumps(data, ensure_ascii=False, indent=4, default=str)
        f.writelines(data_str)
        f.close()

    return True


class WrongPushAPIView(APIView):
    permission_classes = ()
    def post(self, request):
        data = request.build_absolute_uri()
        response = {}
        data = request.data
        patient = Patient.objects.filter().order_by('server_modified_on')
        patient_serializers=PatientSerializers(patient, many=True)

        screening = Screening.objects.filter().order_by('server_modified_on')
        screening_dpl = screening.exclude(patient_uuid__in=patient.values_list('uuid', flat=True))
        screening_serializers=ScreeningSerializers(screening_dpl, many=True)

        family_member = FamilyMember.objects.filter().order_by('server_modified_on')
        family_member_dpl = family_member.exclude(screening_uuid__in=screening.values_list('uuid', flat=True),patient_uuid__in=patient.values_list('uuid', flat=True))
        family_member_serializers=FamilyMemberSerializers(family_member_dpl, many=True)

        visual_acuity = VisualAcuity.objects.filter().order_by('server_modified_on')
        visual_acuity_dpl=visual_acuity.exclude(screening_uuid__in=screening.values_list('uuid', flat=True))
        visual_acuity_serializers=VisualAcuitySerializers(visual_acuity_dpl, many=True)

        glass_prescription = GlassPrescription.objects.filter().order_by('server_modified_on')
        glass_prescription_dpl = glass_prescription.exclude(screening_uuid__in=screening.values_list('uuid', flat=True))
        glass_prescription_serializers=GlassPrescriptionSerializers(glass_prescription_dpl, many=True)

        spectacle_type = SpectacleType.objects.filter().order_by('server_modified_on')
        spectacle_type_dpl = spectacle_type.exclude(glass_prescription_uuid__in=glass_prescription.values_list('uuid', flat=True))
        spectacle_type_serializers=SpectacleTypeSerializers(spectacle_type_dpl, many=True)

        

        response['count'] = {"screening":screening_dpl.count(), "family_members":family_member_dpl.count(), "visual_acuity":visual_acuity_dpl.count(), "glass_prescription":glass_prescription_dpl.count(), "spectacle_type": spectacle_type_dpl.count()}
        response['screening'] = screening_serializers.data #3
        response['family_members'] = family_member_serializers.data #3
        response['visual_acuity'] = visual_acuity_serializers.data #4
        response['glass_prescription'] = glass_prescription_serializers.data #5
        response['spectacle_type'] = spectacle_type_serializers.data #5
        return Response(response)
