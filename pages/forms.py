
from django import forms
from .models import Customer, ColumbaryRecord, Beneficiary

from django import forms
from .models import Customer

from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    # Name Fields
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'First Name',
        'class': 'form-control'
    }))
    middle_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Middle Name (Optional)',
        'class': 'form-control'
    }))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Last Name',
        'class': 'form-control'
    }))
    suffix = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Suffix (e.g., Jr., Sr., III)',
        'class': 'form-control'
    }))

    # Address Fields
    country = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Country',
        'class': 'form-control'
    }))
    address_line_1 = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Address Line 1',
        'class': 'form-control'
    }))
    address_line_2 = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Address Line 2 (Optional)',
        'class': 'form-control'
    }))
    city = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'City',
        'class': 'form-control'
    }))
    province_or_state = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Province/State',
        'class': 'form-control'
    }))
    postal_code = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Postal Code',
        'class': 'form-control'
    }))

    class Meta:
        model = Customer
        fields = [
            'first_name', 'middle_name', 'last_name', 'suffix',
            'country', 'address_line_1', 'address_line_2', 'city', 
            'province_or_state', 'postal_code',
            'landline_number', 'mobile_number', 'email_address', 'status'
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()
        return instance




class EmailVerificationForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address',
            'required': True
        })
    )


class ColumbaryRecordForm(forms.ModelForm):
    class Meta:
        model = ColumbaryRecord
        fields = ['vault_id', 'issuance_date', 'expiration_date', 'inurnment_date', 'issuing_parish_priest', 'urns_per_columbary']

class BeneficiaryForm(forms.ModelForm):
    class Meta:
        model = Beneficiary
        fields = ['first_beneficiary_name', 'second_beneficiary_name', 'third_beneficiary_name']
        
        widgets = {
            'first_beneficiary_name': forms.TextInput(attrs={'placeholder': 'First Beneficiary', 'class': 'form-control'}),
            'second_beneficiary_name': forms.TextInput(attrs={'placeholder': 'Second Beneficiary', 'class': 'form-control'}),
            'third_beneficiary_name': forms.TextInput(attrs={'placeholder': 'Third Beneficiary', 'class': 'form-control'})
        }


class DocumentUploadForm(forms.Form):
    document = forms.ImageField(
        label='Upload Document',
        help_text='Upload a clear image of the handwritten form'
    )

