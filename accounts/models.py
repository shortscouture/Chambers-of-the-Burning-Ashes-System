from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
     # Add your custom fields here
     # account in web app
     
    ROLE_CHOICES = (     
        ('parish_staff', 'Parish Staff'),
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    username = models.CharField(max_length=16, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return self.username #can greet people in methods by calling this
    
