from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from pages.models import ChatQuery #pages folder query views

from allauth.account.models import EmailAddress


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'phone_number', 'address')
    search_fields = ('Username', 'Email', 'Phone Number', 'Address')
    ordering = ('username',)

    # Customizing the fieldsets to include the phone number and address
    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': ('phone_number', 'address'),
        }),
    )

    # If you want to customize the add form as well in the flat page
    add_fieldsets = UserAdmin.add_fieldsets + ( 
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )



admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ChatQuery)
#print("Unregistering EmailAddress from admin.")
#unshows the email address tab.
admin.site.unregister(EmailAddress)
