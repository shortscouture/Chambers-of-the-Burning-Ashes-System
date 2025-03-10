from django.urls import path
from django.core.management.base import BaseCommand
from pages import views
from django.conf import settings  # Import settings
from django.conf.urls.static import static  # Import static
from .views import (
    HomePageView, AboutPageView, MainDashView, ColumbaryRecordsView,
    CustomerHomeView, MemorialView, send_letter_of_intent, verify_otp,
    memorials_verification, accept_letter_of_intent, decline_letter_of_intent,
    RecordsDetailsView, CustomerEditView, SuccesView, DashboardView, get_crypt_status, MapView, CustomerDeleteView,
    get_vault_data,contact,
    get_vault_data, upload_and_process
)

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("maindash/", MainDashView.as_view(), name="maindash"),
    path("columbaryrecords/", ColumbaryRecordsView.as_view(), name="columbaryrecords"),
    path("Customer_Home/", CustomerHomeView.as_view(), name="Customer_Home"),
    path("Memorials/", MemorialView.as_view(), name="Memorials"),
    path('memorials_verification/', memorials_verification, name='memorials_verification'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('send_letter_of_intent/', send_letter_of_intent, name='send_letter_of_intent'),
    path("Success/", SuccesView.as_view(), name="Success"),
    path('accept/<int:intent_id>/', accept_letter_of_intent, name='accept_letter_of_intent'),
    path('decline/<int:intent_id>/', decline_letter_of_intent, name='decline_letter_of_intent'),
    path('recordsdetails/<int:customer_id>/', RecordsDetailsView.as_view(), name='recordsdetails'),
    path('edit_customer/<int:customer_id>/', CustomerEditView.as_view(), name='edit_customer'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('get_crypt_status/<str:section>/', get_crypt_status, name='get_crypt_status'),
    path("Columbary_Map/", MapView.as_view(), name="Columbary_Map"),
    path('addnewrecord/', views.addnewrecord, name='addnewrecord'),
    path('delete_customer/<int:customer_id>/', CustomerDeleteView.as_view(), name='delete_customer'),
    path('get_vault_data/<str:section_id>/', get_vault_data, name='get_vault_data'),
    path('contact/', contact, name='contact'),
    path('upload_and_process/', views.upload_and_process, name='upload_and_process'),  
    path('addnewcustomer/', views.addnewcustomer, name='addnewcustomer'),

]

if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
