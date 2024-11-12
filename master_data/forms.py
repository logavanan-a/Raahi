from django import forms
from .models import *
from django.utils.translation import gettext_lazy as _
import re
from django import forms
from django.core.validators import RegexValidator

class ZoneForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'pattern':'[A-Za-z ]+','placeholder': 'Enter Zone Name '}),
        error_messages={'unique': _('This name already exists. Please enter a different name.')})
    # ssmis_id = forms.IntegerField(required=True,  initial=0, min_value=0)
    # code = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter Code '}),
    #     error_messages={'unique': _('This code already exists. Please enter a different code.')})
    

    class Meta:
        model = Zone
        fields = ['name']

    

class StateForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'pattern':'[A-Za-z ]+','placeholder': 'Enter State Name '}),
        error_messages={'unique': _('This name already exists. Please enter a different name.')})
    code = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter Code '}),
        error_messages={'unique': _('This code already exists. Please enter a different code.')})
    zone = forms.ModelChoiceField(queryset=Zone.objects.filter(status=2).order_by("name"),required = True,empty_label="Select Zone")
    
    def __init__(self, *args, **kwargs):
        super(StateForm, self).__init__(*args, **kwargs)
        self.fields['zone'].widget.attrs['class'] = 'form-select select2'
        
    class Meta:
        model = State
        fields = ['name', 'code', 'zone'] 
    
    # def clean(self):
    #     cleaned_data = self.cleaned_data
    #     if Zone.objects.filter(name=cleaned_data['name'], zone=self.zone).exists():
    #         raise forms.ValidationError("Name and Zone alreay exits.")
    #     # Always return cleaned_data
    #     return cleaned_data 


class DistrictForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'pattern':'[A-Za-z ]+','placeholder': 'Enter District Name '}),max_length=150)
    code = forms.CharField(required = False, widget=forms.TextInput(attrs={'pattern':'[A-Za-z0-9 \-\_\@\#\$ ]+', 'placeholder': 'Enter Code '}))
    zone = forms.ModelChoiceField(queryset=Zone.objects.filter(status=2).order_by("name"),required = True,empty_label="Select Zone")
    state = forms.ModelChoiceField(queryset=State.objects.filter(status=2).order_by("name"),required = True,empty_label="Select State")

    def __init__(self, *args, **kwargs):
        super(DistrictForm, self).__init__(*args, **kwargs)
        self.fields['zone'].widget.attrs['class'] = 'form-select select2'
        self.fields['state'].widget.attrs['class'] = 'form-select select2'
            # self.fields['state'].queryset = self.fields['state'].queryset.filter(zone_id=self.instance.state.zone.id)


        if self.instance.pk:
            if self.instance.state.zone:
                self.fields['state'].queryset = self.fields['state'].queryset.filter(zone_id=self.instance.state.zone.id)
            self.fields['zone'].initial = self.instance.state.zone
       


    class Meta:
        model=District
        fields=['name','code', 'zone', 'state']

        

    def clean_name(self):
        name = self.cleaned_data['name']
        return name.capitalize()

def validate_numeric(value):
    if not value.isdigit():
        raise forms.ValidationError('Please enter a valid numeric value in contact number.')


class PartnerForm(forms.ModelForm):
    OTP_CHOICES = (
        (1, 'Not Required'),
        (2, 'Required'),
    )
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter Name '}),max_length=150, strip=True)
    code = forms.CharField(required=True, widget=forms.TextInput(attrs={'pattern':'[A-Za-z0-9 \-\_\@\#\$ ]+','placeholder': 'Enter Code '}))
    contact_no = forms.CharField(
            max_length=10,min_length=10,label='Contact no',widget=forms.TextInput(attrs={'placeholder': 'Enter Contact No'}),validators=[validate_numeric],error_messages={'invalid': 'Please enter a valid Mobile Number.'})    
    email_id = forms.EmailField(max_length=244,widget=forms.TextInput(attrs={'placeholder': 'Enter Email id'}), error_messages={'invalid': 'Please enter a valid email address.'})
    state = forms.ModelChoiceField(queryset=State.objects.filter(status=2).order_by("name"),required = True,empty_label="Select State")
    otp_verification = forms.ChoiceField(choices=OTP_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-select'}), initial=2)
    address = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Enter address','rows':5}),required = False)

    def __init__(self, *args, **kwargs):
        super(PartnerForm, self).__init__(*args, **kwargs)
        self.fields['state'].widget.attrs['class'] = 'form-select select2'
        self.fields['address'].widget.attrs['class'] = 'form-control'


    def clean_mobile_number(self):
        contact_no = self.cleaned_data['contact_no']
        if not str(contact_no).isdigit():
            raise forms.ValidationError("Mobile number should only contain numbers.")
        return contact_no

    class Meta:
        model=Partner
        fields=['name','code','contact_no','email_id','state','otp_verification','address']


class VisioncenterForm(forms.ModelForm):
    VC_CHOICES = (
        (1,'Mobile vc'),
        (2,'Static vc')
        ) 
    VC_CHOICES = list(VC_CHOICES)
    VC_CHOICES.insert(0, ("", "Select Vision Center Type"))

    partner = forms.ModelChoiceField(queryset=Partner.objects.filter(status=2).order_by("name"),empty_label="Select Partner")
    donor = forms.ModelChoiceField(queryset=Donor.objects.filter(status=2).order_by("name"),empty_label="Select Donor")
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'pattern':'[A-Za-z0-9 \-\_\@\#\$]+','placeholder': 'Enter Name '}),max_length=150,strip=True)
    vc_type = forms.ChoiceField(choices=VC_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-select'}))
    contact_no = forms.CharField(
            max_length=10,min_length=10,label='Contact no',widget=forms.TextInput(attrs={'placeholder': 'Enter Contact No'}),validators=[validate_numeric],error_messages={'invalid': 'Please enter a valid Mobile Number.'})
    address = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Enter address','rows':5}),required = False)

    def __init__(self, *args, **kwargs):
        super(VisioncenterForm, self).__init__(*args, **kwargs)
        self.fields['partner'].widget.attrs['class'] = 'form-select select2'
        self.fields['donor'].widget.attrs['class'] = 'form-select select2'
        self.fields['vc_type'].widget.attrs['class'] = 'form-select select2'
        self.fields['address'].widget.attrs['class'] = 'form-control'
        self.fields['partner'].label_from_instance = self.label_from_instance

        if self.instance.pk:
            dpl = DonorPartnerLinkage.objects.filter(status=2, partner_id=self.instance.partner.id).values_list('donor_id', flat=True)
            donor_obj = Donor.objects.filter(id__in=dpl)
            self.fields['donor'].queryset = donor_obj
            self.fields['donor'].initial = self.instance.donor

    def label_from_instance(self, obj):
        # Customize how each option is displayed in the dropdown
        return f'{obj.name} - ({obj.state})'  

    class Meta:
        model = VisionCenter
        fields = ['partner', 'donor', 'name', 'contact_no','address', 'vc_type']
    

class DonorForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter Name '}),max_length=150,strip=True)
    mobile_number = forms.CharField(
            max_length=10,min_length=10,label='Contact no',widget=forms.TextInput(attrs={'placeholder': 'Enter Contact No'}),validators=[validate_numeric],error_messages={'invalid': 'Please enter a valid Mobile Number.'})
    email_id = forms.EmailField(max_length=244,widget=forms.TextInput(attrs={'placeholder': 'Enter Email id'}),error_messages={'invalid': 'Please enter a valid email address.'})

    class Meta:
        model=Donor
        fields= ['name','mobile_number','email_id']


class UserprofileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['user', 'role']


class VendorForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'pattern':'[A-Za-z0-9 \-\_\@\#\$ ]+','placeholder': 'Enter Name '}),max_length=150)
    contact_no = forms.CharField(
            max_length=10,min_length=10,label='Contact no',widget=forms.TextInput(attrs={'placeholder': 'Enter Contact No'}),validators=[validate_numeric],error_messages={'invalid': 'Please enter a valid Mobile Number.'})
    email_id = forms.EmailField(max_length=244,widget=forms.TextInput(attrs={'placeholder': 'Enter Email id'}),error_messages={'invalid': 'Please enter a valid email address.'})
    alternative_email_id_1 = forms.EmailField(max_length=244,widget=forms.TextInput(attrs={'placeholder': 'Enter Alternative Email id 1'}),required = False, error_messages={'invalid': 'Please enter a valid alternative email id 1.'})
    alternative_email_id_2 = forms.EmailField(max_length=244,widget=forms.TextInput(attrs={'placeholder': 'Enter Alternative Email id 2'}),required = False, error_messages={'invalid': 'Please enter a valid alternative email id 2.'})
    alternative_email_id_3 = forms.EmailField(max_length=244,widget=forms.TextInput(attrs={'placeholder': 'Enter Alternative Email id 3'}),required = False, error_messages={'invalid': 'Please enter a valid alternative email id 3.'})
    alternative_email_id_4 = forms.EmailField(max_length=244,widget=forms.TextInput(attrs={'placeholder': 'Enter Alternative Email id 4'}),required = False, error_messages={'invalid': 'Please enter a valid alternative email id 4.'})
    zone = forms.ModelChoiceField(queryset=Zone.objects.filter(status=2).order_by("name"),required = True,empty_label="Select Zone")
    state = forms.ModelChoiceField(queryset=State.objects.filter(status=2).order_by("name"),required = True,empty_label="Select State")
    district = forms.ModelChoiceField(queryset=District.objects.filter(status=2).order_by("name"),empty_label="Select District")
    address = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Enter address','rows':5}),required = False)

    def __init__(self, *args, **kwargs):
        super(VendorForm, self).__init__(*args, **kwargs)
        self.fields['zone'].widget.attrs['class'] = 'form-select select2'
        self.fields['state'].widget.attrs['class'] = 'form-select select2'
        self.fields['district'].widget.attrs['class'] = 'form-select select2'
        self.fields['address'].widget.attrs['class'] = 'form-control'

        if self.instance.pk:
            if self.instance.district.state.zone:
                self.fields['state'].queryset = self.fields['state'].queryset.filter(zone_id=self.instance.district.state.zone.id)
            if self.instance.district.state:
                self.fields['district'].queryset = self.fields['district'].queryset.filter(state_id=self.instance.district.state.id)
            self.fields['state'].initial = self.instance.district.state
            self.fields['zone'].initial = self.instance.district.state.zone

    class Meta:
        model=Vendor
        fields=['name','contact_no','email_id','alternative_email_id_1','alternative_email_id_2','alternative_email_id_3','alternative_email_id_4','zone', 'state','district','address',]

