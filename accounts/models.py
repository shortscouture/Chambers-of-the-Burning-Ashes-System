from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
     # Add your custom fields here
     # account in web app
    username = models.CharField(max_length=16, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    

    def __str__(self):
        return self.username #can greet people in methods by calling this
    
