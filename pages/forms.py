from django import forms
from .models import Customer


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
