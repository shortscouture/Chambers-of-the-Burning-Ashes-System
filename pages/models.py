from django.db import models
import random
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime, timedelta


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


class Customer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    full_name = models.CharField(max_length=45)
    permanent_address = models.TextField(255)
    landline_number = models.CharField(max_length=15, blank=True)
    mobile_number = models.CharField(max_length=11)
    email_address = models.EmailField(45)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


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

    def __str__(self):
        return self.first_beneficiary_name


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    full_contribution = models.BooleanField()
    six_month_installment = models.BooleanField()
    official_receipt = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Payment {self.payment_id}"


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

    def __str__(self):
        return f"Vault {self.vault_id}"

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