from django.db import models
from django.contrib.auth.models import User
import random
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone



class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=45, unique=True)
    password = models.CharField(max_length=25)

    def __str__(self):
        return self.username


class ParishAdministrator(models.Model):
    admin_id = models.AutoField(primary_key=True)
    account = models.OneToOneField(Account, on_delete=models.CASCADE)

    def __str__(self):
        return f"Admin {self.admin_id}"


class ParishStaff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    account = models.OneToOneField(Account, on_delete=models.CASCADE)

    def __str__(self):
        return f"Staff {self.staff_id}"


from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    
    # Name Fields
    first_name = models.CharField(max_length=50, default="Unknown")
    middle_name = models.CharField(max_length=50, blank=True, null=True)  
    last_name = models.CharField(max_length=50, default="Unknown")
    suffix = models.CharField(max_length=10, blank=True, null=True)  # Optional

    # Address Fields
    country = models.CharField(max_length=100, default="Philippines")
    address_line_1 = models.CharField(max_length=255, default="Unknown Address")
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)  # Optional
    city = models.CharField(max_length=100, default="Unknown City")
    province_or_state = models.CharField(max_length=100, default="Unknown Province")
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    # Contact Fields
    landline_number = models.CharField(max_length=15, blank=True, null=True)
    mobile_number = models.CharField(max_length=11, blank=True, null=True)
    email_address = models.EmailField(max_length=45, blank=True, null=True)

    # Status
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='pending'
    )

    def __str__(self):
        return f"{self.first_name} {self.middle_name or ''} {self.last_name}"
    
    def full_name(self):
        return f"{self.first_name} {self.middle_name or ''} {self.last_name} {self.suffix or ''}".strip()
    
    def full_address(self):
        address_parts = [
            self.address_line_1,
            self.address_line_2 if self.address_line_2 else None,  # Only include if exists
            self.city,
            self.province_or_state,
            self.postal_code if self.postal_code else None,  # Only include if exists
            self.country
        ]
        return ", ".join(filter(None, address_parts))  # Join and remove None values

    def __str__(self):
        return self.full_address()



class InquiryRecord(models.Model):
    letter_of_intent_id = models.AutoField(primary_key=True)
    columbary_vault = models.ForeignKey('ColumbaryRecord', on_delete=models.SET_NULL, null=True, blank=True)
    parish_administrator = models.ForeignKey(ParishAdministrator, on_delete=models.SET_NULL, null=True, blank=True)
    parish_staff = models.ForeignKey(ParishStaff, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Inquiry {self.letter_of_intent_id}"


class HolderOfPrivilege(models.Model):
    holder_of_privilege_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=45)
    email_address = models.EmailField(max_length=45, blank=True, null=True)
    address = models.CharField(max_length=45, blank=True, null=True)
    landline_number = models.IntegerField(blank=True, null=True)
    mobile_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.full_name


class Beneficiary(models.Model):
    beneficiary_id = models.AutoField(primary_key=True)
    first_beneficiary_name = models.CharField(max_length=255)
    second_beneficiary_name = models.CharField(max_length=45, blank=True, null=True)
    third_beneficiary_name = models.CharField(max_length=45, blank=True, null=True)
    
    # Add ForeignKey relationship
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="beneficiaries")

    def __str__(self):
        return self.first_beneficiary_name




class Payment(models.Model):
    PAYMENT_MODES = [
        ("Full Payment", "Full Payment"),
        ("6-Month Installment", "6-Month Installment"),
    ]
    
    payment_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='payments', 
        default=1  # Replace 1 with the ID of an existing customer
    )
    mode_of_payment = models.CharField(max_length=20, choices=PAYMENT_MODES, default="Full Payment")

    # Seven receipt fields
    Full_payment_receipt_1 = models.IntegerField(blank=True, null=True)
    six_month_receipt_1 = models.IntegerField(blank=True, null=True)
    six_month_receipt_2 = models.IntegerField(blank=True, null=True)
    six_month_receipt_3 = models.IntegerField(blank=True, null=True)
    six_month_receipt_4 = models.IntegerField(blank=True, null=True)
    six_month_receipt_5 = models.IntegerField(blank=True, null=True)
    six_month_receipt_6 = models.IntegerField(blank=True, null=True)
    
    Full_payment_amount_1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) 
    six_month_amount_1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    six_month_amount_2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    six_month_amount_3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    six_month_amount_4 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    six_month_amount_5 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    six_month_amount_6 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) 
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        if self.mode_of_payment == "Full Payment":
            full_payment_value = 220000  # Adjust based on actual pricing
            self.Full_payment_amount_1 = full_payment_value
            self.total_amount = full_payment_value  # Assign total amount

            # Clear unused fields
            self.six_month_receipt_1 = self.six_month_receipt_2 = self.six_month_receipt_3 = self.six_month_receipt_4 = self.six_month_receipt_5 = self.six_month_receipt_6 = None
            self.six_month_amount_1 = self.six_month_amount_2 = self.six_month_amount_3 = self.six_month_amount_4 = self.six_month_amount_5 = self.six_month_amount_6 = None
        
        elif self.mode_of_payment == "6-Month Installment":
            installment_value = 60000 / 6  # Divide total amount into 6 payments
            self.six_month_amount_1 = self.six_month_amount_2 = self.six_month_amount_3 = self.six_month_amount_4 = self.six_month_amount_5 = self.six_month_amount_6 = installment_value

            # Sum all non-null amounts
            self.total_amount = sum(filter(None, [self.six_month_amount_1, self.six_month_amount_2, self.six_month_amount_3, self.six_month_amount_4, self.six_month_amount_5, self.six_month_amount_6]))

        super().save(*args, **kwargs)


class ColumbaryRecord(models.Model):
    vault_id = models.CharField(primary_key=True, max_length=7)
    issuance_date = models.DateField(null=True)
    expiration_date = models.DateField(null=True)
    inurnment_date = models.DateField(blank=True, null=True)
    issuing_parish_priest = models.CharField(max_length=45, blank=True, null=True)
    urns_per_columbary = models.CharField(max_length=1, null=True, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')])
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    parish_staff = models.ForeignKey(ParishStaff, on_delete=models.SET_NULL, null=True, blank=True)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    holder_of_privilege = models.ForeignKey(HolderOfPrivilege, on_delete=models.SET_NULL, null=True, blank=True)
    
    STATUS_CHOICES = [('Vacant', 'Vacant'), ('Occupied', 'Occupied')]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Vacant')
    

    def update_status(self):
        fields_to_check = [
            self.issuance_date, self.expiration_date, self.inurnment_date,
            self.issuing_parish_priest, self.urns_per_columbary,
            self.customer, self.parish_staff, self.beneficiary, self.payment, self.holder_of_privilege
        ]
        if any(fields_to_check):  
            self.status = "Occupied"  # If any field has a value, status is Occupied
        elif not any(fields_to_check) and self.status == "Occupied":
            self.status = "Vacant"

    def save(self, *args, **kwargs):
        self.update_status()  # Ensure status is updated before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Vault {self.vault_id} - {self.status}"
    
    def get_record_data(self):
        """Get formatted record data"""
        data = {
            'vault_info': {
                'vault_id': self.vault_id,
                'issuance_date': self.issuance_date,
                'expiration_date': self.expiration_date,
                'inurnment_date': self.inurnment_date,
                'urns_per_columbary': self.urns_per_columbary,
                'issuing_parish_priest': self.issuing_parish_priest,
            }
        }
        
        if self.customer:
            data['customer_info'] = {
                'full_name': self.customer.full_name,
                'address': self.customer.permanent_address,
                'mobile': self.customer.mobile_number,
                'email': self.customer.email_address,
            }
        
        if self.beneficiary:
            data['beneficiary_info'] = {
                'first_beneficiary': self.beneficiary.first_beneficiary_name,
                'second_beneficiary': self.beneficiary.second_beneficiary_name,
                'third_beneficiary': self.beneficiary.third_beneficiary_name,
            }
        
        if self.payment:
            data['payment_info'] = {
                'full_contribution': self.payment.full_contribution,
                'six_month_installment': self.payment.six_month_installment,
                'official_receipt': self.payment.official_receipt,
            }
            
        return data

    def send_record_email(self):
        """Send record details to customer's email"""
        if not self.customer or not self.customer.email_address:
            return False

        data = self.get_record_data()
        
        message = f"Dear {self.customer.full_name},\n\nHere are your columbary record details:\n\n"
        
        # Add vault information
        message += f"""
VAULT INFORMATION
----------------
Vault ID: {data['vault_info']['vault_id']}
Issuance Date: {data['vault_info']['issuance_date']}
Expiration Date: {data['vault_info']['expiration_date']}
Inurnment Date: {data['vault_info']['inurnment_date']}
Urns Per Columbary: {data['vault_info']['urns_per_columbary']}
Issuing Parish Priest: {data['vault_info']['issuing_parish_priest']}

"""
        # Add beneficiary information if available
        if 'beneficiary_info' in data:
            message += f"""
BENEFICIARY INFORMATION
----------------------
First Beneficiary: {data['beneficiary_info']['first_beneficiary']}
Second Beneficiary: {data['beneficiary_info']['second_beneficiary']}
Third Beneficiary: {data['beneficiary_info']['third_beneficiary']}

"""
        # Add payment information if available
        if 'payment_info' in data:
            message += f"""
PAYMENT INFORMATION
------------------
Full Contribution: {'Yes' if data['payment_info']['full_contribution'] else 'No'}
Six Month Installment: {'Yes' if data['payment_info']['six_month_installment'] else 'No'}
Official Receipt Number: {data['payment_info']['official_receipt']}
"""

        message += "\n\nBest regards,\nParish Administration"

        subject = 'Your Columbary Record Details'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [self.customer.email_address]
        
        return send_mail(subject, message, from_email, recipient_list)

class TwoFactorAuth(models.Model):
    email = models.EmailField(max_length=45)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()
        return self.otp

    def send_otp_email(self, customer):
        if not customer.email_address:
            return False
            
        subject = 'Columbary System - Verification Code'
        message = f'''
        Dear {customer.full_name},
        
        Your verification code is: {self.otp}
        
        This code will expire in 15 minutes.
        
        Best regards,
        Parish Administration
        '''
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [customer.email_address]
        
        try:
            send_mail(subject, message, from_email, recipient_list)
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False

    def verify_otp(self, submitted_otp):
        if self.otp == submitted_otp and not self.is_verified:
            if self.created_at + timedelta(minutes=15) > timezone.now():
                self.is_verified = True
                self.save()
                return True
        return False

#chatbot
class ChatQuery(models.Model):
    user_message = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query at {self.created_at}"