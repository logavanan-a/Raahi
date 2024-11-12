from django.db import models
from master_data.models import *
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta

# Create your models here.
YES_NO_CHOICE = (
        (1, 'YES'),
        (2, 'NO'),
        )

REPLY_CHOICE = (
        (1, 'YES'),
        (2, 'NO'),
        (3, 'NA'),
        )
class Product(BaseContent):
    name = models.CharField(max_length=150)

    class Meta:
        verbose_name_plural = "Product"

    def __str__(self):
        return self.name

class Camp(BaseContent):
    uuid = models.CharField(max_length=150, unique=True, db_index=True, null= True,blank=True)
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=150)
    date = models.DateField() 
    ssmis_id = models.PositiveIntegerField(default=0,null=True, blank=True)
    location = models.CharField(max_length=150)
    address = models.CharField(max_length=150,null= True,blank=True)
    village = models.CharField(max_length=150,null= True,blank=True)
    block = models.CharField(max_length=150,null= True,blank=True)
    district = models.ForeignKey(District, on_delete=models.DO_NOTHING)
    expected_glass_prescription = models.CharField(max_length=150,null= True,blank=True)
    expected_refer_surgeries = models.CharField(max_length=150,null= True,blank=True)
    expected_camp_OPD = models.CharField(max_length=150,null= True,blank=True)
    donor = models.ForeignKey(Donor, on_delete=models.DO_NOTHING)
    vision_center = models.ForeignKey(VisionCenter, on_delete=models.DO_NOTHING,null= True,blank=True)
    coordinator_name =  models.CharField(max_length=150,null= True,blank=True)
    coordinator_mobile_no = models.CharField(max_length=10,null= True,blank=True)
    exclusive_camp = models.IntegerField(choices=YES_NO_CHOICE, default=1)
    partner = models.ForeignKey(Partner, on_delete=models.DO_NOTHING,null= True,blank=True)
    delay_reason = models.TextField(null=True,blank=True)
    start_time = models.TimeField(null=True,blank=True)
    end_time = models.TimeField(null=True,blank=True)
    
    class Meta:
        verbose_name_plural = "Camp"

    def __str__(self):
        return self.name    

    
    def get_start_end_date(self):
        try:
            patients = Patient.objects.filter(status=2,camp_id=self.id).order_by('server_created_on')
            if patients.exists():
                start_date = patients.first().server_created_on
                end_date = patients.last().server_created_on
                return start_date, end_date
            else:
                return None, None
        except ObjectDoesNotExist:
            return None, None

    def get_camp(self):
        try:
            camp = OrderRequest.objects.filter(camp_id=self.id).first()
        except ObjectDoesNotExist:
            camp = None
        return camp


    def get_approved_status(self):
        from dateutil.relativedelta import relativedelta
        current_date = datetime.now().date()
        syn_date = current_date + relativedelta(months=1)
        start_date = current_date.strftime('%Y-%m-06')
        end_date = syn_date.strftime('%Y-%m-05')
        
        no_of_patients_created = Patient.objects.filter(camp_id=self.id, app_created_at__range=(start_date, end_date))
        no_of_patients_to_be_verfied = no_of_patients_created.filter(server_created_on__gt=end_date, status=3)
        try:
            approved_status = no_of_patients_created.order_by('approved_on').first() 
        except:
            approved_status = None
        return approved_status

    def get_unsync_patient(self):
        current_date = datetime.now().date()        
        start_date = datetime(current_date.year, current_date.month, 1).date()
        next_month_start = datetime(current_date.year, current_date.month, 1) + timedelta(days=32)
        end_date = (next_month_start - timedelta(days=next_month_start.day)).date()
        try:
            product = Patient.objects.filter(camp_id=self.id)
        except ObjectDoesNotExist:
            product = None
        return product

    def get_syn_count(self):
        from dateutil.relativedelta import relativedelta
        current_date = datetime.now().date()
        syn_date = current_date + relativedelta(months=1)
        start_date = current_date.strftime('%Y-%m-06')
        end_date = syn_date.strftime('%Y-%m-05')
        
        no_of_patients_created = Patient.objects.filter(camp_id=self.id, app_created_at__range=(start_date, end_date))
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



class OrderRequest(BaseContent):
    STATUS_CHOICES = (
        (1,'Pending'),     
        (2,'Submited for Approval'),
        (3,'Approved'),
        (4,'Rejected'),
        (5,'Shipped'),
        (6,'Received'),
    )
    vision_center = models.ForeignKey(VisionCenter, on_delete=models.DO_NOTHING, null=True,blank=True)
    order_for = models.IntegerField(choices=((1,'Vision Center'),(2,'Camp')), null=True,blank=True)
    order_status = models.IntegerField(choices=STATUS_CHOICES, null=True,blank=True)
    approved_by =  models.ForeignKey(User, on_delete=models.DO_NOTHING,null= True,blank=True)
    approved_on = models.DateField(null=True,blank=True)
    camp = models.ForeignKey(Camp, on_delete=models.DO_NOTHING, null=True,blank=True)
    shippment_address = models.IntegerField(choices=((1,'Partner'),(2,'Camp'),(3,'Other'),(4,'Vision Center')),null=True,blank=True)
    other_address = models.TextField(null=True,blank=True)
    remark = models.TextField(null=True,blank=True)
    # custom_made = models.CharField(max_length=150, blank=True, null=True)
    donor = models.ForeignKey(Donor, on_delete=models.DO_NOTHING,null=True,blank=True)
    district = models.ForeignKey(District, on_delete=models.DO_NOTHING,null=True,blank=True)
    invoice_date = models.DateField(blank=True, null=True)
    invoice_no = models.CharField(max_length=150, blank=True, null=True)
    invoice_value = models.CharField(max_length=150, blank=True, null=True)
    courier_name = models.CharField(max_length=150, blank=True, null=True)
    awb_no = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Order Request"
    
    def __str__(self):
        return self.created_by.username   

    
    def get_product(self):
        try:
            product=OrderRequestDetails.objects.filter(order_request_id=self.id).first()
        except ObjectDoesNotExist:
            product = None
        return product

    def get_frame(self):
        try:
            frame=OrderRequestDetails.objects.filter(order_request_id=self.id).first()
        except ObjectDoesNotExist:
            frame = None
        return frame

    def get_address(self):
        try:
            partner_address=UserPartnerLinkage.objects.get(user_id=self.created_by.id).partner
        except ObjectDoesNotExist:
            partner_address = None
        return partner_address
    
class OrderRequestDetails(BaseContent):
    order_request =  models.ForeignKey(OrderRequest, on_delete=models.DO_NOTHING, null = True, blank = True)
    product =  models.ForeignKey(Product, on_delete=models.DO_NOTHING, null = True, blank = True )
    quantity = models.PositiveIntegerField(default = 0,blank=True,null=True)
    rrv = models.IntegerField( default = 0,blank=True,null=True)   # Ready Reader Spectacles Value
    frame_type = models.IntegerField(choices=((1,'R2CCM015'),(2,'R2CCM021')),null=True,blank=True)
    
    class Meta:
        verbose_name_plural = "Order Request Details"
        
    def __str__(self):
        return self.product.name    

class OrderDeliveryDetails(BaseContent):
    order_request = models.ForeignKey(OrderRequest, on_delete=models.DO_NOTHING)
    product =  models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    rrv = models.IntegerField(blank=True,null=True)   # Ready Reader Spectacles Value
    received_quantity = models.PositiveIntegerField(blank=True,null=True)
    damaged_quantity = models.PositiveIntegerField(blank=True,null=True)
    frame_type = models.IntegerField(choices=((1,'R2CCM015'),(2,'R2CCM021')),null=True,blank=True)

    class Meta:
        verbose_name_plural = "Order Delivery Details"

    def __str__(self):
        return self.product.name    

 
GENDER_CHOICE = (
        (1, 'Male'),
        (2, 'Female'),
        (3, 'Third gender')
        )
DATAFREEZE_CHOICE = (
        (1, 'Synced'),
        (2, 'Not Synced'),
        )
class Patient(BaseContent):
    uuid = models.CharField(max_length=150, unique=True, db_index=True)
    unique_id = models.CharField(max_length=150, null=True,blank=True, unique=True, db_index=True)
    patient_id = models.CharField(max_length=150, null=True,blank=True)
    partner_id = models.IntegerField(default=0)
    vision_center_id = models.IntegerField(default=0)
    name = models.CharField(max_length=150)
    donor = models.ForeignKey(Donor, on_delete=models.DO_NOTHING, null=True,blank=True)
    district = models.ForeignKey(District, on_delete=models.DO_NOTHING)
    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING, null=True,blank=True)
    user = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True,blank=True)
    camp = models.ForeignKey(Camp, on_delete=models.DO_NOTHING, null=True,blank=True)
    age = models.PositiveIntegerField(blank=True,null=True)
    qr_code = models.CharField(max_length=150, null=True,blank=True)
    gender = models.IntegerField(choices=GENDER_CHOICE, blank=True, null=True)
    contact_no_1 = models.CharField(max_length=150, null=True, blank=True)
    contact_no_2 = models.CharField(max_length=150, null=True, blank=True)
    permanent_address = models.TextField(null=True,blank=True)
    aadhaar_pan_no = models.CharField(max_length=150, null=True, blank=True)
    drivers_license_no = models.CharField(max_length=150, null=True, blank=True)
    renewal_date = models.DateField(null=True,blank=True)
    type_of_job = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="type_of_job", null=True,blank=True)
    time_since_driving = models.CharField(max_length=150, null=True, blank=True)
    type_of_vehicle = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="type_of_vehicle", null=True,blank=True)
    type_of_route = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="type_of_route", null=True,blank=True)
    monthly_income = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="monthly_income", null=True,blank=True)
    life_insurance_policy = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    vehicle_insurance_policy = models.IntegerField(choices=YES_NO_CHOICE , blank=True, null=True)
    health_insurance_policy = models.IntegerField(choices=YES_NO_CHOICE , blank=True, null=True)
    how_do_you_know_about_camp = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="how_do_you_know_about_camp", null=True,blank=True)
    educational_qualification = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="educational_qualification", null=True,blank=True)
    no_of_months_employed_in_a_year = models.CharField(max_length=150, null=True, blank=True)
    residence_type = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="residence_type", null=True,blank=True)
    feedback = models.CharField(max_length=150, null=True,blank=True)
    app_created_at = models.DateTimeField(null=True, blank=True)
    app_updated_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.PositiveIntegerField(default=2)
    approved_by =  models.ForeignKey(User, on_delete=models.DO_NOTHING,null= True,blank=True)
    approved_on = models.DateField(null=True,blank=True)
    remarks = models.TextField(null=True,blank=True)
    data_freeze_status = models.IntegerField(choices=DATAFREEZE_CHOICE, default=2,null=True, blank=True)
    latitude = models.CharField(max_length=150,null=True, blank=True)
    longitude = models.CharField(max_length=150,null=True, blank=True)
    
    def __str__(self):
        return self.name    
    
    def get_spectacles_type(self):
        try:
            spectacles = SpectacleType.objects.filter(id=self.id).first().name
        except:
            spectacles = None
        return spectacles


    def get_vision_center(self):
        try:
            vision_centers = UserVisionCenterLinkage.objects.select_related('user','vision_center').filter(user_id=self.user.user.id).first().vision_center
        except:
            vision_centers = None
        return vision_centers
    

    def get_glass_questions(self):
        try:
            questions=TellicallingQuestionsAndAnswers.objects.filter(patient_id=self.id).order_by('-server_created_on').first()
        except ObjectDoesNotExist:
            questions = None
        return questions


    def get_catract_questions(self):
        try:
            questions=CataractQuestions.objects.filter(patient_id=self.id).order_by('-server_created_on').first()
        except ObjectDoesNotExist:
            questions = None
        return questions
    

class Screening(BaseContent):
    uuid = models.CharField(max_length=150, unique=True, db_index=True)
    patient_uuid = models.CharField(max_length=150, db_index=True)
    partner_id = models.IntegerField(default=0)
    vision_center_id = models.IntegerField(default=0)
    code_description = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="code_description",null=True, blank=True)
    blood_pressure = models.CharField(max_length=150, null=True, blank=True)
    blood_sugar = models.CharField(max_length=150, null=True, blank=True)
    weight = models.CharField(max_length=150, null=True, blank=True)
    height = models.CharField(max_length=150, null=True, blank=True)
    family_details = models.TextField(null=True,blank=True)
    total_family_members = models.CharField(max_length=150, null=True, blank=True)
    salary_calculated = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="salary_calculated", blank=True, null=True)
    owner_holding_amount = models.CharField(max_length=150, null=True, blank=True)
    employed_in_year = models.ManyToManyField(MasterLookup, blank=True)
    non_working_months = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="non_working_months", blank=True, null=True)
    alter_employment = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    learn_alter_livelihood_skill = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    family_support_financially = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    medical_checkup_past_1_year = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    diabetes = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    hypertension = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    smoke = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    alcohol = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    eye_examination = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    seeing_distant_objects = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    judging_distance_while_driving = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    traffic_colors = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    seeing_while_night_driving = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    wear_glasses_ever = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    wearing_glasses_currently = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    nearby_hospital = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    type_of_hospital = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="type_of_hospital", blank=True, null=True)
    accident_while_driving_commercial_vehicle_before = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    accident_vehicle_in_last_twelve_months = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    first_aid_kit = models.IntegerField(choices=REPLY_CHOICE, blank=True, null=True)
    you_happy_with_your_profession = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="profession", blank=True, null=True)
    if_you_are_happy_specify_in_what_way = models.CharField(max_length=150, null=True, blank=True)
    insulin_dependent_or_non_insulin_dependent = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="insulin_dependent_or_non_insulin_dependent", blank=True, null=True)
    waist_circumference = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="waist_circumference", blank=True, null=True)
    physical_activity = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="physical_activity", blank=True, null=True)
    family_history_of_diabetes = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="family_history_of_diabetes", blank=True, null=True)
    which_training = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="which_training", blank=True, null=True)
    medication_hypertension = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    cough_for_more_than_two_weeks = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    night_sweats = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    fever_for_more_than_2_weeks = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    unexplained_weight_loss_or_loss_of_appetite = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    have_you_attended_awarness_training = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    dosage_of_insulin = models.IntegerField(blank=True, null=True)
    duration_since_last_meal = models.FloatField(blank=True, null=True)
    when_was_it_diagnosed_number_of_years = models.IntegerField(blank=True, null=True)
    when_was_it_diagnosed_years = models.IntegerField(blank=True, null=True)
    app_created_at = models.DateTimeField(null=True, blank=True)
    app_updated_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.PositiveIntegerField(default=2)
    data_freeze_status = models.IntegerField(choices=DATAFREEZE_CHOICE, default=2,null=True, blank=True)
    latitude = models.CharField(max_length=150,null=True, blank=True)
    longitude = models.CharField(max_length=150,null=True, blank=True)

    def get_ps_details(self):
        try:
            pnt = Patient.objects.filter(uuid=self.patient_uuid).first()
        except:
            pnt = None
        return pnt
    
    

class FamilyMember(BaseContent):
    uuid = models.CharField(max_length=150, unique=True, db_index=True)
    screening_uuid = models.CharField(max_length=150, db_index=True)
    patient_uuid = models.CharField(max_length=150, db_index=True)
    partner_id = models.IntegerField(default=0, blank=True, null=True)
    vision_center_id = models.IntegerField(default=0, blank=True, null=True)
    name = models.CharField(max_length=150, blank=True, null=True)
    sex = models.IntegerField(choices=GENDER_CHOICE, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True,null=True)
    relationship_to_respondent = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="relationship_to_respondent", blank=True, null=True)
    educational_qualification = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="family_educational_qualification", blank=True, null=True)
    occupation = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="occupation", blank=True, null=True)
    monthly_average_income = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="monthly_average_income", blank=True, null=True)
    model_type = models.CharField(max_length=150, blank=True, null=True)
    patient_id = models.CharField(max_length=150, blank=True, null=True)
    app_created_at = models.DateTimeField(null=True, blank=True)
    app_updated_at = models.DateTimeField(null=True, blank=True)
    data_freeze_status = models.IntegerField(choices=DATAFREEZE_CHOICE, default=2,null=True, blank=True)
    sync_status = models.PositiveIntegerField(default=2)

    class Meta:
        verbose_name_plural = "Family Members"
    
    
    
    def get_psf_details(self):
        try:
            scr = Screening.objects.filter(uuid=self.screening_uuid)
            pnt = Patient.objects.filter(uuid__in=scr.values_list('patient_uuid')).first()
        except:
            pnt = None
        return pnt



class VisualAcuity(BaseContent):
    uuid = models.CharField(max_length=150, unique=True, db_index=True)
    screening_uuid = models.CharField(max_length=150, db_index=True)
    partner_id = models.IntegerField(default=0)
    vision_center_id = models.IntegerField(default=0)
    aided_near_re = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="aided_near_re", blank=True, null=True)
    aided_near_le = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="aided_near_le", blank=True, null=True)
    aided_distance_re = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="aided_distance_re", blank=True, null=True)
    aided_distance_le = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="aided_distance_le", blank=True, null=True)
    pinhole_distance_re = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="pinhole_distance_re", blank=True, null=True)
    pinhole_distance_le = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="pinhole_distance_le", blank=True, null=True)
    pinhole_near_re = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="pinhole_near_re", blank=True, null=True)
    pinhole_near_le = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="pinhole_near_le", blank=True, null=True)
    color_re = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="color_re", blank=True, null=True)
    color_le = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="color_le", blank=True, null=True)
    unaided_distance_re = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="unaided_distance_re", blank=True, null=True)
    unaided_distance_le = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="unaided_distance_le", blank=True, null=True)
    unaided_near_re = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="unaided_near_re", blank=True, null=True)
    unaided_near_le = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="unaided_near_le", blank=True, null=True)
    treatment_for_refraction = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="treatment_for_refraction", blank=True, null=True)
    do_you_want_to_refer = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    refer_for = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="refer_for", blank=True, null=True)
    refer_to = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="refer_to", blank=True, null=True)
    app_created_at = models.DateTimeField(null=True, blank=True)
    app_updated_at = models.DateTimeField(null=True, blank=True)
    data_freeze_status = models.IntegerField(choices=DATAFREEZE_CHOICE, default=2,null=True, blank=True)
    sync_status = models.PositiveIntegerField(default=2)
    latitude = models.CharField(max_length=150,null=True, blank=True)
    longitude = models.CharField(max_length=150,null=True, blank=True)
    
    def get_psv_details(self):
        try:
            scr = Screening.objects.filter(uuid=self.screening_uuid)
            pnt = Patient.objects.filter(uuid__in=scr.values_list('patient_uuid')).first()
        except:
            pnt = None
        return pnt


class GlassPrescription(BaseContent):
    uuid = models.CharField(max_length=150, unique=True, db_index=True)
    partner_id = models.IntegerField(default=0)
    vision_center_id = models.IntegerField(default=0)
    screening_uuid = models.CharField(max_length=150, db_index=True)
    sph_distance_re = models.CharField(max_length=150, null=True, blank=True)
    sph_distance_le = models.CharField(max_length=150, null=True, blank=True)
    cyl_distance_re = models.CharField(max_length=150, null=True, blank=True)
    cyl_distance_le = models.CharField(max_length=150, null=True, blank=True)
    axis_distance_re = models.CharField(max_length=150, null=True, blank=True)
    axis_distance_le = models.CharField(max_length=150, null=True, blank=True)
    va_distance_re = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="va_distance_re", blank=True, null=True)
    va_distance_le = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="va_distance_le", blank=True, null=True)
    sph_near_re = models.CharField(max_length=150, null=True, blank=True)
    sph_near_le = models.CharField(max_length=150, null=True, blank=True)
    cyl_near_re = models.CharField(max_length=150, null=True, blank=True)
    cyl_near_le = models.CharField(max_length=150, null=True, blank=True)
    axis_near_re = models.CharField(max_length=150, null=True, blank=True)
    axis_near_le = models.CharField(max_length=150, null=True, blank=True)
    va_near_re = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="va_near_re", blank=True, null=True)
    va_near_le = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="va_near_le", blank=True, null=True)
    spectacle_type = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="glass_spectacle_type", blank=True, null=True)
    app_created_at = models.DateTimeField(null=True, blank=True)
    app_updated_at = models.DateTimeField(null=True, blank=True)
    data_freeze_status = models.IntegerField(choices=DATAFREEZE_CHOICE, default=2,null=True, blank=True)
    sync_status = models.PositiveIntegerField(default=2)
    latitude = models.CharField(max_length=150,null=True, blank=True)
    longitude = models.CharField(max_length=150,null=True, blank=True)
    
    def get_psg_details(self):
        try:
            scr = Screening.objects.filter(uuid=self.screening_uuid)
            pnt = Patient.objects.filter(uuid__in=scr.values_list('patient_uuid')).first()
        except:
            pnt = None
        return pnt

class SpectacleType(BaseContent):
    SPECTACLE_CHOICE = (
        (1, 'Pending'),
        (2, 'Ready'),
        (3, 'Delivered'),
        )
    uuid = models.CharField(max_length=150, unique=True, db_index=True)
    glass_prescription_uuid = models.CharField(max_length=150, db_index=True)
    partner_id = models.IntegerField(default=0)
    spectacle_name = models.CharField(max_length=150, blank=True, null=True)
    spectacle_type = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="spectacle_type", blank=True, null=True)
    has_the_glass_collected = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    glass_collecting_location = models.ForeignKey(State, on_delete=models.DO_NOTHING, blank=True, null=True)
    vision_center = models.ForeignKey(VisionCenter, on_delete=models.DO_NOTHING, blank=True, null=True)
    frame_code = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="frame_code", blank=True, null=True)
    frame_size = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="frame_size", blank=True, null=True)
    lens_type = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="lens_type", blank=True, null=True)
    type_of_coating = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="type_of_coating", blank=True, null=True)
    model_type = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="near_model_type", blank=True, null=True)
    spectacle_status = models.IntegerField(default=1, choices=SPECTACLE_CHOICE, blank=True, null=True)
    order_id = models.IntegerField(default=0)
    r2c_eligible = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    r2c_remark = models.CharField(max_length=150,blank=True, null=True)
    data_freeze_status = models.IntegerField(choices=DATAFREEZE_CHOICE, default=2,null=True, blank=True)
    app_created_at = models.DateTimeField(null=True, blank=True)
    app_updated_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.PositiveIntegerField(default=2)

    def get_pnt_details(self):
        glass = GlassPrescription.objects.filter(uuid=self.glass_prescription_uuid)
        try:
            glass_pre = glass.first()
        except:
            glass_pre = None
        try:
            screening = Screening.objects.filter(uuid__in=glass.values_list('screening_uuid'))
            patients = Patient.objects.filter(uuid__in=screening.values_list('patient_uuid')).first()
        except:
            screening = None
            patients = None
        return patients, glass_pre
    
    def get_partner_shippment_address(self):
        glass_pre = GlassPrescription.objects.filter(uuid=self.glass_prescription_uuid).first()
        screening = Screening.objects.get(uuid=glass_pre.screening_uuid)
        patients = Patient.objects.get(uuid=screening.patient_uuid,status=2)
        try:
            vision_id=UserVisionCenterLinkage.objects.get(user_id=patients.user.user.id,status=2).vision_center.id
            parner_address = VisionCenter.objects.get(id=vision_id)
        except:
            parner_address = None
        
        try:
            parner_details = UserPartnerLinkage.objects.get(user_id=patients.user.user.id)
        except:
            parner_details = None
        return parner_address, parner_details
    




CALL_DISPOSITION_CHOICE =(
        (1, 'Complaint'),
        (2, 'Retry'),
        (3, 'Successful'),
        (4, 'UnSuccessful'),
        (5, 'Spectacle out of stock')
    )


class TellicallingQuestionsAndAnswers(BaseContent):
    RATE_CHOICE = (
        (1, 'Excellent'),
        (2, 'Good'),
        (3, 'Not so good'),
        (4, 'Average'),
        (5, 'Bad')
    )
   
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING)
    receive_your_spectacles =  models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    receiver_spectacles_reason = models.CharField(max_length=255, blank=True, null=True)

    # After how many days of screening you received spectacles and where 
    ahmd_spectacles_received = models.CharField(max_length=150, null=True, blank=True) 
    currently_using_spectacles = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)

    # Are you satisfied with the quality of spectacle provided 
    satisfied_with_spectacle = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)

    # Is there any impact on their driving after wearing glasses (Yes/No)
    impact_on_their_driving_after_wearing = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    
    # Any problems raised before after receiving spectacles or in centre. 
    any_problems_raised = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    satisfied_with_our_service =  models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    any_charges_while_collecting = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)

    # How much would you rate our services (Beale out of 1-5) or How was our services (Excellent, Good, Not so good, Bad)
    rate_our_services = models.IntegerField(choices=RATE_CHOICE, blank=True, null=True)
    ad = models.TextField(blank=True, null=True)
    disposition_name = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="disposition_name", blank=True, null=True)
    call_disposition_group = models.IntegerField(choices=CALL_DISPOSITION_CHOICE, null=True, blank=True) 
    comments = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="comments", blank=True, null=True)
    agent_comments = models.TextField(null=True, blank=True) 


class CataractQuestions(BaseContent):
    TREATMENT_CHOICE = (
        (1,'Free'),
        (2,'Subsidized'),
        (3,'Paid')
    )
    PAID_CHOICES = (
        (1,'Own Pocket'),
        (2,'Insurences'),
        (3,'Govt.Health Cards')
    )
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING,blank=True, null=True)
    referred_to_hospital_for_cataract = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    reason_for_cataract_no = models.CharField(max_length=255, blank=True, null=True)
    visited_hospital = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    reason_for_visited_hospital_no = models.CharField(max_length=255, blank=True, null=True)
    hospital_recomand_cataract_surgery  = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    reason_for_hospital_recomand_cataract_surgery_no  = models.CharField(max_length=255, blank=True, null=True)
    undergo_surgery  = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    reason_for_undergo_surgery_no  = models.CharField(max_length=255, blank=True, null=True)
    place_cataract_surgery = models.CharField(max_length=255, blank=True, null=True)
    date_cataract_surgery = models.DateField(blank=True, null=True)
    reason_for_notgone_cataract_surgery = models.CharField(max_length=255, blank=True, null=True)
    treatment_free = models.IntegerField(choices=TREATMENT_CHOICE, blank=True, null=True)
    how_it_paid = models.IntegerField(choices=PAID_CHOICES, blank=True, null=True)
    improvement_vision = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    helpful_for_driving = models.IntegerField(choices=YES_NO_CHOICE, blank=True, null=True)
    beneficiary_feed_back = models.CharField(max_length=255, blank=True, null=True)
    ad = models.TextField(blank=True, null=True)
    disposition_name = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="cataract_disposition", blank=True, null=True)
    call_disposition_group = models.IntegerField(choices=CALL_DISPOSITION_CHOICE, null=True, blank=True) 
    comments = models.ForeignKey(MasterLookup, on_delete=models.DO_NOTHING, related_name="cataract_comments", blank=True, null=True)
    agent_comments = models.TextField(null=True, blank=True) 

class DataFreeze(BaseContent):
    hospital_name = models.ForeignKey(Partner, on_delete=models.DO_NOTHING, null=True,blank=True)
    vision_center = models.ForeignKey(VisionCenter, on_delete=models.DO_NOTHING, null=True,blank=True)
    camp = models.ForeignKey(Camp, on_delete=models.DO_NOTHING, null=True,blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True) 
    no_of_patients_syn = models.IntegerField(default=0)
    no_of_patients_not_syn = models.IntegerField(default=0)
    not_syn_patients_ids = models.TextField(blank=True, null=True)
    no_of_screening_syn = models.IntegerField(default=0)
    no_of_screening_not_syn = models.IntegerField(default=0)
    not_syn_screening_ids = models.TextField(blank=True, null=True)
    no_of_family_member_syn = models.IntegerField(default=0)
    no_of_family_member_not_syn = models.IntegerField(default=0)
    not_syn_family_member_ids = models.TextField(blank=True, null=True)
    no_of_visual_acuity_syn = models.IntegerField(default=0)
    no_of_visual_acuity_not_syn = models.IntegerField(default=0)
    not_syn_visual_acuity_ids = models.TextField(blank=True, null=True)
    no_of_glass_prescription_syn = models.IntegerField(default=0)
    no_of_glass_prescription_not_syn = models.IntegerField(default=0)
    not_syn_glass_prescription_ids = models.TextField(blank=True, null=True)
    no_of_spectacle_type_syn = models.IntegerField(default=0)
    no_of_spectacle_type_not_syn = models.IntegerField(default=0)
    not_syn_spectacle_type_ids = models.TextField(blank=True, null=True)
    approved_by =  models.ForeignKey(User, on_delete=models.DO_NOTHING,null= True,blank=True)
    approved_on = models.DateField(null=True,blank=True)
    remarks = models.TextField(null=True,blank=True) 





class QrCodeGeneration(BaseContent):
    unique_id = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True,blank=True)
    prefix = models.CharField(max_length=255, blank=True, null=True)
    range_from = models.PositiveIntegerField(blank=True, null=True)
    range_to = models.PositiveIntegerField(blank=True, null=True)


    class Meta:
        verbose_name_plural = "QR Code Generation"





class ReceivedSMS(BaseContent):
    mobile_no = models.CharField(max_length=12)
    languege = models.ForeignKey(Language, on_delete=models.DO_NOTHING, null=True,blank=True)
    content = models.TextField()
    sms_status = models.IntegerField(default=0, blank=True,null=True)
    no_of_times_attempt = models.IntegerField(default=0, blank=True,null=True)
    last_attempt_on = models.DateTimeField(blank=True,null=True)
    error_info = models.TextField(blank=True,null=True)

    class Meta:
        verbose_name_plural = "Received SMS"

