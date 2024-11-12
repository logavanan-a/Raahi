# import imp
from rest_framework import serializers
from django.contrib.auth import authenticate,login,logout
from rest_framework.validators import UniqueValidator
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from master_data.models import *
from sims.models import *
from reports.models import ReportMeta,MprIndicator,TruckerMprData


class StateSerializers(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

class DistrictSerializers(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'

class UserProfileSerializers(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    user_name = serializers.CharField(source='user.username')
    user_id = serializers.CharField(source='user.id')
    email = serializers.CharField(source='user.email')
    role_name = serializers.CharField(source='role.name')
    role_id = serializers.CharField(source='role.id')

    class Meta:
        model = UserProfile
        exclude = ['user', 'role']
    
    vision_center_id = serializers.SerializerMethodField()
    partner_id = serializers.SerializerMethodField()
    otp_verification = serializers.SerializerMethodField()

    def get_otp_verification(self, obj):
        if obj.get_vision_center_value():
            return obj.get_vision_center_value().partner.otp_verification 
        elif obj.get_partner_value():
            return obj.get_partner_value().partner.otp_verification 
        else:
            return 0

    def get_vision_center_id(self, obj):
        if obj.get_vision_center_value():
            return obj.get_vision_center_value().id 
        else:
            return 0
        
    def get_partner_id(self, obj):
        if obj.get_vision_center_value():
            return obj.get_vision_center_value().partner.id 
        elif obj.get_partner_value():
            return obj.get_partner_value().partner.id
        else:
            return 0 

class OtpVerificationDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model = OtpVerificationDetails
        fields = '__all__'

class LanguageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'

class PartnerSerializers(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'


class DonorSerializers(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = '__all__'

class VisionCenterSerializers(serializers.ModelSerializer):
    class Meta:
        model = VisionCenter
        fields = '__all__'

class MasterLookupSerializers(serializers.ModelSerializer):
    class Meta:
        model = MasterLookup
        fields = '__all__'

class CampSerializers(serializers.ModelSerializer):
    class Meta:
        model = Camp
        fields = '__all__'

class PatientSerializers(serializers.ModelSerializer):
    app_created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False)
    app_updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False)
    
    class Meta:
        model = Patient
        fields = '__all__'


class ScreeningSerializers(serializers.ModelSerializer):
    app_created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False)
    app_updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False)
    
    class Meta:
        model = Screening
        fields = '__all__'


class FamilyMemberSerializers(serializers.ModelSerializer):
    app_created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False)
    app_updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False)
    
    class Meta:
        model = FamilyMember
        fields = '__all__'

class FamilyMemberOtherSerializers(serializers.ModelSerializer):
    app_created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False)
    app_updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False)
    sex = serializers.CharField(source='get_sex_display', required=False)
    relationship_to_respondent = serializers.CharField(source='relationship_to_respondent.name', required=False)
    educational_qualification = serializers.CharField(source='educational_qualification.name', required=False)
    occupation = serializers.CharField(source='occupation.name', required=False)
    monthly_average_income = serializers.CharField(source='monthly_average_income.name', required=False)
    class Meta:
        model = FamilyMember
        fields = '__all__'


class VisualAcuitySerializers(serializers.ModelSerializer):
    app_created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False)
    app_updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False)
    
    class Meta:
        model = VisualAcuity
        fields = '__all__'


class GlassPrescriptionSerializers(serializers.ModelSerializer):
    app_created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False)
    app_updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False)
    
    class Meta:
        model = GlassPrescription
        fields = '__all__'


class SpectacleTypeSerializers(serializers.ModelSerializer):
    app_created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False)
    app_updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False)
    follow_up_status = serializers.IntegerField(source='spectacle_status')

    class Meta:
        model = SpectacleType
        # fields = '__all__'
        exclude = ['spectacle_status']

class TruckerMprDataSerializers(serializers.ModelSerializer):
    class Meta:
        model = TruckerMprData
        fields = '__all__'


class QrCodeGenerationSerializers(serializers.ModelSerializer):
    class Meta:
        model = QrCodeGeneration
        fields = '__all__'
        
class DonorPartnerLinkageSerializers(serializers.ModelSerializer):
    class Meta:
        model = DonorPartnerLinkage
        fields = '__all__'

class TruckerMprOne(serializers.ModelSerializer):
    metric_id = serializers.CharField(source='mpr_indicator.ssmis_id')

    class Meta:
        model = TruckerMprData
        exclude = ['mpr_indicator', 'partner_name', 'vision_center_name', 'donor_name','priority',
                   'male_target','female_target','total_target','current_month_achievement_male',
                   'current_month_achievement_female','current_month_achievement_total',
                   'two_column_value', 'three_column_value','four_column_value','till_date_achievement',
                   'server_created_on','server_modified_on','sync_status','status','id', 'created_by', 'modified_by',
                   ]

class TruckerMprTwo(serializers.ModelSerializer):
    metric_id = serializers.CharField(source='mpr_indicator.ssmis_id')
    class Meta:
        model = TruckerMprData
        exclude = ['mpr_indicator','partner_name', 'vision_center_name', 'donor_name','priority',
                   'male_target','female_target','total_target','current_month_achievement_male',
                   'current_month_achievement_female','current_month_achievement_total','till_date_achievement',
                    'three_column_value','four_column_value',
                   'server_created_on','server_modified_on','sync_status','status','id', 'created_by', 'modified_by'
                    ]


class TruckerMprThree(serializers.ModelSerializer):
    metric_id = serializers.CharField(source='mpr_indicator.ssmis_id')
    class Meta:
        model = TruckerMprData
        exclude = ['mpr_indicator','partner_name', 'vision_center_name', 'donor_name','priority',
                   'male_target','female_target','total_target','current_month_achievement_male',
                   'current_month_achievement_female','current_month_achievement_total',
                   'server_created_on','server_modified_on','sync_status','status','id', 'created_by', 'modified_by'
                   ]






