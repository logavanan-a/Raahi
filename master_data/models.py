from django.db import models
from django.contrib.auth.models import User, Group
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from ckeditor.fields import RichTextField
# Create your models here.


class BaseContent(models.Model):
    ACTIVE_CHOICES = ((1, 'Inactive'), (2, 'Active'), (3, 'Pending'),(4,'Approved'),
        (5,'Rejected'))
    status = models.PositiveIntegerField(
        choices=ACTIVE_CHOICES, default=2, db_index=True)
    server_created_on = models.DateTimeField(auto_now_add=True)
    server_modified_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='created%(app_label)s_%(class)s_related', null=True, blank=True,)
    modified_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='modified%(app_label)s_%(class)s_related', null=True, blank=True,)
    sync_status = models.PositiveIntegerField(default=2)


    class Meta:
        abstract = True

class MasterLookup(BaseContent):
    name = models.CharField(max_length=150, blank=False,
                            null=False)
    parent = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Zone(BaseContent):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=150, unique=True,  null=True, blank=True)
    ssmis_id = models.PositiveIntegerField(default=0,null=True, blank=True)
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Zone"

class State(BaseContent):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=150, unique=True, null=True, blank=True)
    zone = models.ForeignKey(Zone, on_delete=models.DO_NOTHING, null=True, blank=True)
    ssmis_id = models.PositiveIntegerField(default=0,null=True, blank=True)

    class Meta:
        verbose_name_plural = "State"
        unique_together = ['name', 'zone']

    def __str__(self):
        return self.name
    
    def get_district_value(self):
        try:
            districts = District.objects.get(state_id=self.id)
        except:
            districts = None
        return districts
    
class District(BaseContent):
    name = models.CharField(max_length=150,unique=True)
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING)
    code = models.CharField(max_length=150,null=True, blank=True)
    ssmis_id = models.PositiveIntegerField(default=0,null=True, blank=True)

    class Meta:
        verbose_name_plural = "District"

    def __str__(self):
        return self.name

class Partner(BaseContent):
    OTP_CHOICE = (
        (1, 'Not Required'),
        (2, 'Required'),
        )
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=150, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    contact_no = models.CharField(max_length=10)
    email_id = models.EmailField(max_length=150)
    otp_verification = models.IntegerField(choices=OTP_CHOICE, default=2)
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING, null=True, blank=True)
    ssmis_id = models.PositiveIntegerField(default=0,null=True, blank=True)
    latitude = models.CharField(max_length=150,null=True, blank=True)
    longitude = models.CharField(max_length=150,null=True, blank=True)

    class Meta:
        verbose_name_plural = "Partner"

    def __str__(self):
        return self.name

class Role(BaseContent):
    ROLE_CHOICES = (
        (0,'Web'),
        (1,'App'),
        (2,'Both')
    )
    name = models.CharField(max_length=150)
    role_type = models.IntegerField(
        choices=ROLE_CHOICES)
    role_slug = models.SlugField(max_length=100, null=True, blank=True)
    class Meta:
        verbose_name_plural = "Role"

    def __str__(self):
        return self.name

class UserProfile(BaseContent):
    user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING)
    role = models.ForeignKey(
        Role, on_delete=models.DO_NOTHING) 
    class Meta:
        verbose_name_plural = "User Profile"

    def __str__(self):
        return self.user.username

    def get_vision_center_value(self):
        try:
            vision_centers = UserVisionCenterLinkage.objects.get(user_id=self.user.id, status=2).vision_center
        except:
            vision_centers = None
        return vision_centers

    def get_partner_value(self):
        try:
            parent = UserPartnerLinkage.objects.get(user_id=self.user.id, status=2)
        except:
            parent = None
        return parent
    
    def get_partner_patient(self):
        from sims.models import Patient 
        from master_data.models import Donor 

        current_date = datetime.now().date()
        start_date = current_date - timedelta(days=5)
        end_date = current_date 
        try:
            product = Patient.objects.filter(partner_id=self.id, camp__isnull=True, server_created_on__gte=start_date, server_created_on__lte=end_date).count()
        except ObjectDoesNotExist:
            product = 0
        return product

class Donor(BaseContent):
    name = models.CharField(max_length=150)
    mobile_number = models.CharField(max_length=10)
    email_id = models.EmailField(max_length=150)
    code = models.SlugField(max_length=150, null=True, blank=True)
    ssmis_id = models.PositiveIntegerField(default=0,null=True, blank=True)

    class Meta:
        verbose_name_plural = "Donor"

    def __str__(self):
        return self.name        
    

VC_CHOICES = (
        (1,'Mobile vc'),
        (2,'Static vc')
        ) 
class VisionCenter(BaseContent):
    partner = models.ForeignKey(Partner, on_delete=models.DO_NOTHING)
    donor = models.ForeignKey(Donor, on_delete=models.DO_NOTHING, null=True, blank=True)
    name = models.CharField(max_length=150)
    address = models.TextField(max_length=1024,null=True, blank=True)
    contact_no = models.CharField(max_length=10)
    ssmis_id = models.PositiveIntegerField(default=0,null=True, blank=True)
    vc_type = models.IntegerField(choices=VC_CHOICES,null=True, blank=True )
    latitude = models.CharField(max_length=150,null=True, blank=True)
    longitude = models.CharField(max_length=150,null=True, blank=True)

    class Meta:
        verbose_name_plural = "Vision Center"

    def __str__(self):
        return self.name
    
    def get_vision_center_patient(self):
        from sims.models import Patient 
        from master_data.models import Donor 

        current_date = datetime.now().date()
        start_date = current_date - timedelta(days=5)
        end_date = current_date 
        try:
            product = Patient.objects.filter(vision_center_id=self.id, camp__isnull=True, server_created_on__gte=start_date, server_created_on__lte=end_date).count()
        except ObjectDoesNotExist:
            product = 0
        return product

    def get_approved_vc_status(self):
        from dateutil.relativedelta import relativedelta
        from sims.models import  Patient
        from master_data.models import Donor 
        current_date = datetime.now().date()
        syn_date = current_date + relativedelta(months=1)
        start_date = current_date.strftime('%Y-%m-06')
        end_date = syn_date.strftime('%Y-%m-05')
        
        no_of_patients_created = Patient.objects.filter(vision_center_id=self.id, camp__isnull=True, app_created_at__range=(start_date, end_date))
        no_of_patients_to_be_verfied = no_of_patients_created.filter(server_created_on__gt=end_date, status=3)
        try:
            approved_status = no_of_patients_created.order_by('approved_on').first() 
        except:
            approved_status = None
        return approved_status
    
    def get_syn_vc_count(self):
        from sims.models import  Patient, Screening,FamilyMember,VisualAcuity,GlassPrescription, SpectacleType
        from master_data.models import Donor 
        from dateutil.relativedelta import relativedelta
        current_date = datetime.now().date()
        syn_date = current_date + relativedelta(months=1)
        start_date = current_date.strftime('%Y-%m-06')
        end_date = syn_date.strftime('%Y-%m-05')

        no_of_patients_created = Patient.objects.filter(vision_center_id=self.id, camp__isnull=True,app_created_at__range=(start_date, end_date))
        no_of_patients_to_be_verfied = no_of_patients_created.filter(server_created_on__gt=end_date, status=3)

        # Screening Count
        no_of_screening_created= Screening.objects.filter(patient_uuid__in=no_of_patients_created.values_list('uuid'),app_created_at__range=(start_date, end_date))
        no_of_screening_to_be_verfied = no_of_screening_created.filter(server_created_on__gt=end_date, status=3)

        # Family Member Count
        no_of_family_member_created = FamilyMember.objects.filter(screening_uuid__in=no_of_screening_created.values_list('uuid'),app_created_at__range=(start_date, end_date))
        no_of_family_member_to_be_verfied = no_of_family_member_created.filter(server_created_on__gt=start_date, status=3)

        # Visual Acuity Count
        no_of_visual_acuity_created = VisualAcuity.objects.filter(screening_uuid__in=no_of_screening_created.values_list('uuid'),app_created_at__range=(start_date, end_date))
        no_of_visual_acuity_to_be_verfied = no_of_visual_acuity_created.filter(server_created_on__gt=start_date, status=3)

        # Glass Prescription Count
        no_of_glass_prescription_created = GlassPrescription.objects.filter(screening_uuid__in=no_of_screening_created.values_list('uuid'),app_created_at__range=(start_date, end_date))
        no_of_glass_prescription_to_be_verfied = no_of_glass_prescription_created.filter(server_created_on__gt=start_date, status=3)

        # Spectacle Type Count
        no_of_spectacle_type_created = SpectacleType.objects.filter(glass_prescription_uuid__in=no_of_glass_prescription_created.values_list('uuid'), app_created_at__range=(start_date, end_date))
        no_of_spectacle_type_to_be_verfied = no_of_spectacle_type_created.filter(server_created_on__gt=start_date, status=3)

        total_patient_count = no_of_patients_created.count()
        syn_patient_count = no_of_patients_to_be_verfied.count()
        total_screening_count = no_of_screening_created.count()
        syn_screening_count = no_of_screening_to_be_verfied.count()
        total_family_member_count = no_of_family_member_created.count()
        syn_family_member_count = no_of_family_member_to_be_verfied.count()
        total_visual_acuity_count = no_of_visual_acuity_created.count()
        syn_visual_acuity_count = no_of_visual_acuity_to_be_verfied.count()
        total_glass_prescription_count = no_of_glass_prescription_created.count()
        syn_glass_prescription_count = no_of_glass_prescription_to_be_verfied.count()
        total_spectacle_type_count = no_of_spectacle_type_created.count()
        syn_spectacle_type_count = no_of_spectacle_type_to_be_verfied.count()
        return total_patient_count, syn_patient_count, total_screening_count, syn_screening_count, total_family_member_count, syn_family_member_count,total_visual_acuity_count,syn_visual_acuity_count,total_glass_prescription_count,syn_glass_prescription_count,total_spectacle_type_count,syn_spectacle_type_count



class TeleCalling(BaseContent):
    feedback = models.CharField(max_length=1500)
    feedback_by = models.CharField(max_length=150)
    feedback_date = models.DateField()

    class Meta:
        verbose_name_plural = "Tele Calling"

    def __str__(self):
        return self.feedback




class Vendor(BaseContent):
    name = models.CharField(max_length=150)
    address = models.TextField(null=True, blank=True)
    contact_no = models.CharField(max_length=10)
    email_id = models.EmailField(max_length=150)
    alternative_email_id_1 = models.EmailField(max_length=150,null=True, blank=True)
    alternative_email_id_2 = models.EmailField(max_length=150,null=True, blank=True)
    alternative_email_id_3 = models.EmailField(max_length=150,null=True, blank=True)
    alternative_email_id_4 = models.EmailField(max_length=150,null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.DO_NOTHING)
    ssmis_id = models.PositiveIntegerField(default=0,null=True, blank=True)

    class Meta:
        verbose_name_plural = "Vendor"

    def __str__(self):
        return self.name



class UserPartnerLinkage(BaseContent):
    partner = models.ForeignKey(Partner, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name_plural = "User Partner Linkage"

    

   
class UserVendorLinkage(BaseContent):
    vendor = models.ForeignKey(Vendor, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name_plural = "User Vendor Linkage"

class PartnerVendorLinkage(BaseContent):
    partner = models.ForeignKey(Partner, on_delete=models.DO_NOTHING)
    vendor = models.ForeignKey(Vendor, on_delete=models.DO_NOTHING)
    deactivated_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Partner Vendor Linkage"

class UserVisionCenterLinkage(BaseContent):
    vision_center = models.ForeignKey(VisionCenter, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name_plural = "User VisionCenter Linkage"

class UserDonorLinkage(BaseContent):
    donor = models.ForeignKey(Donor, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name_plural = "User Donor Linkage"

class DonorPartnerLinkage(BaseContent):
    donor = models.ForeignKey(Donor, on_delete=models.DO_NOTHING, null=True, blank=True)
    partner = models.ForeignKey(Partner, on_delete=models.DO_NOTHING)
    district = models.ForeignKey(District, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name_plural = "Donor Partner Linkage"

class ApplicationUserStateLinkage(BaseContent):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    state = models.ManyToManyField(State)


class Config(BaseContent):
    code = models.CharField(max_length=150)
    value = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Config"

    def __str__(self):
        return self.code

class Language(BaseContent):
    name = models.CharField(max_length=150)
    code = models.IntegerField()

    class Meta:
        verbose_name_plural = "Language"

    def __str__(self):
        return self.name

class OtpVerificationDetails(BaseContent):
    SEND_CHOICE = (
        (1, 'Send'),
        (2, 'Not Send'),
        )
    user = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING)
    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING)
    mobile_no = models.CharField(max_length=150)
    otp_value = models.CharField(max_length=150)
    no_of_verified = models.PositiveIntegerField(null=True, blank=True)
    otp_status = models.IntegerField(choices=SEND_CHOICE, default=2)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_verified_at = models.DateTimeField(null=True, blank=True)

# class EmailStatus(BaseContent):
#     SEND_CHOICE = (
#         (1, 'Send'),
#         (2, 'Not Send'),
#         )
#     mobile_no = models.CharField(max_length=150)
#     sms_text = models.TextField()
#     sms_status = models.IntegerField(choices=SEND_CHOICE)
#     error_msg = models.CharField(max_length=150)




class DailyRecordsCalculation(BaseContent):
    date = models.DateField(auto_now_add=True)
    record = models.CharField(max_length=1500)
    error = models.CharField(max_length=1500,null=True, blank=True)
    uuid = models.CharField(max_length=150, null=True, blank=True)
    saved_records = models.PositiveIntegerField(default=0)
    not_saved_records = models.PositiveIntegerField(default=0)
    total_records = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = "Daily Records Calculation"

INTERFACE_CHOICE = ((1,'Db'),(2,"Web"),(3,"App"))
class VersionUpdate(BaseContent):
    version_code = models.IntegerField(default=0)
    version_name = models.CharField(max_length=100, blank=True, null=True)
    force_update = models.BooleanField(default=False)
    interface  = models.PositiveIntegerField(choices=INTERFACE_CHOICE,default=3)
    releasenotes  = RichTextField(blank=True,null=True)
    release_date  = models.DateField(blank=True,null=True)

    def __str__(self):
        return str(self.version_code)
    

class CronJobSummaryLog(BaseContent):
    log_key = models.CharField(max_length=500, unique=True)
    last_successful_update = models.DateTimeField(blank=True, null=True)
    most_recent_update = models.DateTimeField(blank=True, null=True)
    most_recent_update_status = models.CharField(
        max_length=2500, blank=True, null=True)
    most_recent_update_time_taken_millis = models.CharField(max_length=500,blank=True, null=True)
    error = models.CharField(max_length=2500, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Cron Job SummaryLog"

    def __str__(self):
        return self.log_key
