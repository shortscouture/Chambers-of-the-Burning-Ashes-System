from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from captcha.fields import CaptchaField

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'username')
        
class SignUpForm(UserCreationForm):
    c = CaptchaField()
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2') #new and confirm password for password 1 and 2