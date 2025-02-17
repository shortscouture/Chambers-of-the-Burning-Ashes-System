
from django import forms
from .models import Customer, ColumbaryRecord, Beneficiary


from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'first_name', 'middle_name', 'last_name', 'suffix', 
            'address_line_1', 'address_line_2', 'city', 'province_or_state', 'postal_code',
            'country', 'landline_number', 'mobile_number', 'email_address', 'status'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First Name',
                'required': True,
                'id': 'first_name',
                'class': 'form-control'
            }),
            'middle_name': forms.TextInput(attrs={
                'placeholder': 'Middle Name',
                'id': 'middle_name',
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last Name',
                'required': True,
                'id': 'last_name',
                'class': 'form-control'
            }),
            'suffix': forms.TextInput(attrs={
                'placeholder': 'Suffix (Optional)',
                'id': 'suffix',
                'class': 'form-control'
            }),
            'address_line_1': forms.TextInput(attrs={
                'placeholder': 'Address Line 1',
                'required': True,
                'class': 'form-control'
            }),
            'address_line_2': forms.TextInput(attrs={
                'placeholder': 'Address Line 2 (Optional)',
                'class': 'form-control'
            }),
            'city': forms.TextInput(attrs={
                'placeholder': 'City',
                'required': True,
                'class': 'form-control'
            }),
            'province_or_state': forms.TextInput(attrs={
                'placeholder': 'Province/State',
                'required': True,
                'class': 'form-control'
            }),
            'postal_code': forms.TextInput(attrs={
                'placeholder': 'Postal Code',
                'class': 'form-control'
            }),
            'country': forms.TextInput(attrs={
                'placeholder': 'Country',
                'required': True,
                'class': 'form-control'
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
            'status': forms.Select(attrs={
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
