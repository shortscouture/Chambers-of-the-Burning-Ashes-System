
from django import forms
from .models import Customer, ColumbaryRecord, Beneficiary


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['full_name', 'permanent_address', 'landline_number', 'mobile_number', 'email_address']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Full Name',
                'required': True,
                'id': 'fn',
                'class': 'form-control'
            }),
            'permanent_address': forms.Textarea(attrs={
                'placeholder': 'Permanent Address',
                'required': True,
                'class': 'form-control',
                'rows': 3
            }),
            'landline_number': forms.TextInput(attrs={
                'placeholder': 'Landline Number',
                'type': 'tel',
                'class': 'form-control'
            }),
            'mobile_number': forms.TextInput(attrs={
                'placeholder': 'Mobile Number',
                'required': True,
                'type': 'tel',
                'class': 'form-control'
            }),
            'email_address': forms.EmailInput(attrs={
                'placeholder': 'Email Address',
                'required': True,
                'class': 'form-control'
            }),
        }

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
        widgets = {
            'issuance_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'inurnment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }

class BeneficiaryForm(forms.ModelForm):
    class Meta:
        model = Beneficiary
        fields = ['first_beneficiary_name', 'second_beneficiary_name', 'third_beneficiary_name']
        widgets = {
            'first_beneficiary_name': forms.TextInput(attrs={'placeholder': 'First Beneficiary', 'class': 'form-control'}),
            'second_beneficiary_name': forms.TextInput(attrs={'placeholder': 'Second Beneficiary', 'class': 'form-control'}),
            'third_beneficiary_name': forms.TextInput(attrs={'placeholder': 'Third Beneficiary', 'class': 'form-control'})
        }
