from django import forms
from .models import Customer, ColumbaryRecord, Beneficiary, Payment, HolderOfPrivilege

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
            'address_line_1', 'address_line_2', 'city', 'province_or_state', 'postal_code',
            'country', 'landline_number', 'mobile_number', 'email_address'
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
        }



class EmailVerificationForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address',
            'required': True
        })
    )

class HolderOfPrivilegeForm(forms.ModelForm):
    class Meta:
        model = HolderOfPrivilege
        fields = ['issuance_date', 'expiration_date', 'issuing_parish_priest']
        widgets = {
            'issuance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'issuing_parish_priest': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ColumbaryRecordForm(forms.ModelForm):
    class Meta:
        model = ColumbaryRecord
        fields = [
            'vault_id', 'inurnment_date', 'urns_per_columbary']
        widgets = {
            'vault_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vault ID'}),
            'inurnment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'urns_per_columbary': forms.Select(attrs={'class': 'form-control'}),
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

class PaymentForm(forms.ModelForm):
    # Payment Mode (Full Payment or Installments)
    MODE_OF_PAYMENT_CHOICES = [
        ('', 'Select Payment Mode'),
        ('Full Payment', 'Full Payment'),
        ('6-Month Installment', '6-Month Installment'),
    ]
    
    mode_of_payment = forms.ChoiceField(
        choices=MODE_OF_PAYMENT_CHOICES, 
        required=True,
        widget=forms.Select(attrs={'onchange': 'togglePaymentFields()', 'class': 'form-control'})
    )

    # Full Payment fields
    Full_payment_receipt_1 = forms.CharField(
        label="Full Payment Receipt #1", 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Receipt #1 (Optional)', 'class': 'form-control'})
    )
    Full_payment_amount_1 = forms.DecimalField(
        label="Full Payment Amount", 
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Amount', 'class': 'form-control'})
    )

    # 6-Month Installment fields
    six_month_receipt_1 = forms.CharField(
        label="Receipt #1", 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Receipt #1 (Optional)', 'class': 'form-control'})
    )
    six_month_amount_1 = forms.DecimalField(
        label="Amount", 
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Amount', 'class': 'form-control'})
    )
    six_month_receipt_2 = forms.CharField(
        label="Receipt #2", 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Receipt #2 (Optional)', 'class': 'form-control'})
    )
    six_month_amount_2 = forms.DecimalField(
        label="Amount", 
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Amount', 'class': 'form-control'})
    )
    six_month_receipt_3 = forms.CharField(
        label="Receipt #3", 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Receipt #3 (Optional)', 'class': 'form-control'})
    )
    six_month_amount_3 = forms.DecimalField(
        label="Amount", 
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Amount', 'class': 'form-control'})
    )
    six_month_receipt_4 = forms.CharField(
        label="Receipt #4", 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Receipt #4 (Optional)', 'class': 'form-control'})
    )
    six_month_amount_4 = forms.DecimalField(
        label="Amount", 
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Amount', 'class': 'form-control'})
    )
    six_month_receipt_5 = forms.CharField(
        label="Receipt #5", 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Receipt #5 (Optional)', 'class': 'form-control'})
    )
    six_month_amount_5 = forms.DecimalField(
        label="Amount", 
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Amount', 'class': 'form-control'})
    )
    six_month_receipt_6 = forms.CharField(
        label="Receipt #6", 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Receipt #6 (Optional)', 'class': 'form-control'})
    )
    six_month_amount_6 = forms.DecimalField(
        label="Amount", 
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Amount', 'class': 'form-control'})
    )

    class Meta:
        model = Payment
        fields = [
            'mode_of_payment', 
            'Full_payment_receipt_1', 'Full_payment_amount_1', 
            'six_month_receipt_1', 'six_month_amount_1',
            'six_month_receipt_2', 'six_month_amount_2',
            'six_month_receipt_3', 'six_month_amount_3',
            'six_month_receipt_4', 'six_month_amount_4',
            'six_month_receipt_5', 'six_month_amount_5',
            'six_month_receipt_6', 'six_month_amount_6'
        ]
        widgets = {
            'mode_of_payment': forms.Select(attrs={'class': 'form-control'}),
            'Full_payment_receipt_1': forms.TextInput(attrs={'placeholder': 'Receipt #1 (Optional)', 'class': 'form-control'}),
            'Full_payment_amount_1': forms.NumberInput(attrs={'placeholder': 'Amount', 'class': 'form-control'}),
            'six_month_receipt_1': forms.TextInput(attrs={'placeholder': 'Receipt #1 (Optional)', 'class': 'form-control'}),
            'six_month_amount_1': forms.NumberInput(attrs={'placeholder': 'Amount', 'class': 'form-control'}),
            'six_month_receipt_2': forms.TextInput(attrs={'placeholder': 'Receipt #2 (Optional)', 'class': 'form-control'}),
            'six_month_amount_2': forms.NumberInput(attrs={'placeholder': 'Amount', 'class': 'form-control'}),
            'six_month_receipt_3': forms.TextInput(attrs={'placeholder': 'Receipt #3 (Optional)', 'class': 'form-control'}),
            'six_month_amount_3': forms.NumberInput(attrs={'placeholder': 'Amount', 'class': 'form-control'}),
            'six_month_receipt_4': forms.TextInput(attrs={'placeholder': 'Receipt #4 (Optional)', 'class': 'form-control'}),
            'six_month_amount_4': forms.NumberInput(attrs={'placeholder': 'Amount', 'class': 'form-control'}),
            'six_month_receipt_5': forms.TextInput(attrs={'placeholder': 'Receipt #5 (Optional)', 'class': 'form-control'}),
            'six_month_amount_5': forms.NumberInput(attrs={'placeholder': 'Amount', 'class': 'form-control'}),
            'six_month_receipt_6': forms.TextInput(attrs={'placeholder': 'Receipt #6 (Optional)', 'class': 'form-control'}),
            'six_month_amount_6': forms.NumberInput(attrs={'placeholder': 'Amount', 'class': 'form-control'})
        }

        def clean(self):
            cleaned_data = super().clean()

            # Convert empty string to None for receipt fields
            receipt_fields = ['Full_payment_receipt_1', 'six_month_receipt_1', 'six_month_receipt_2', 
                            'six_month_receipt_3', 'six_month_receipt_4', 'six_month_receipt_5', 'six_month_receipt_6']
            
            for field in receipt_fields:
                if cleaned_data.get(field) == '':
                    cleaned_data[field] = None
            
            return cleaned_data
