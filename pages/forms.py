
from django import forms
from .models import Customer, ColumbaryRecord, Beneficiary

class CustomerForm(forms.ModelForm):
    street_address = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Street Address or P.O. Box',
        'class': 'form-control'
    }))
    barangay = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Barangay (Neighborhood or District)',
        'class': 'form-control'
    }))
    city = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'City or Municipality',
        'class': 'form-control'
    }))
    province = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Province',
        'class': 'form-control'
    }))

    class Meta:
        model = Customer
        fields = ['full_name', 'landline_number', 'mobile_number', 'email_address']

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Combine address fields and assign to permanent_address
        instance.permanent_address = f"{self.cleaned_data['street_address']}, {self.cleaned_data['barangay']}, {self.cleaned_data['city']}, {self.cleaned_data['province']}"
        
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
