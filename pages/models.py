from django.db import models

# Create your models here.
class ColumbaryRecord(models.Model):
    VaultID = models.CharField(max_length=16, primary_key=True)  # Corresponds to the VARCHAR(16) primary key

    def __str__(self):
        return self.VaultID


class Customer(models.Model):
    CustomerID = models.AutoField(primary_key=True)  # Auto-increment integer primary key
    Full_Name = models.CharField(max_length=45, null=False)
    Permanent_Address = models.CharField(max_length=255, null=False)
    Landline_Number = models.CharField(max_length=7, null=True, blank=True)  # Changed to CharField for flexibility
    Mobile_Number = models.CharField(max_length=11, null=True, blank=True)  # Changed to CharField for flexibility
    Email_Address = models.EmailField(max_length=45, null=True, blank=True)
    
    # Foreign key to ColumbaryRecord
    COLUMBARY_RECORDS_VaultID = models.ForeignKey(
        ColumbaryRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="COLUMBARY_RECORDS_VaultID"
    )

    def __str__(self):
        return self.Full_Name