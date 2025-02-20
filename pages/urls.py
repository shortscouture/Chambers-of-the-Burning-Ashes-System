from django.urls import path
from . import views

from .views import get_crypt_status, MapView, HomePageView,AboutPageView, MainDashView,get_vault_data, ColumbaryRecordsView, CustomerHomeView, MemorialView, send_letter_of_intent, verify_otp, memorials_verification,accept_letter_of_intent, decline_letter_of_intent, RecordsDetailsView, CustomerEditView, SuccesView, ChatbotAPIView,CustomerDeleteView #dashboardView



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
    path("Success/", SuccesView.as_view(),name = "Success"),
    path('accept/<int:intent_id>/', accept_letter_of_intent, name='accept_letter_of_intent'),
    path('decline/<int:intent_id>/', decline_letter_of_intent, name='decline_letter_of_intent'),
    path('recordsdetails/<int:customer_id>/', RecordsDetailsView.as_view(), name='recordsdetails'),
    path('edit_customer/<int:customer_id>/', CustomerEditView.as_view(), name='edit_customer'),
    #path('dashboard/',dashboardView.dashboard, name='dashboard'), # out muna
    path('chatbot/', ChatbotAPIView.as_view(), name='chatbot'),
    path('get_crypt_status/<str:section>/', get_crypt_status, name='get_crypt_status'),
    path("Columbary_Map/    ", MapView.as_view(), name="Columbary_Map"),    
    path('columbaryrecords/', views.ColumbaryRecord, name='columbaryrecords'),  # Define this view for your records page
    path('addnewrecord/', views.addnewrecord, name='addnewrecord'),
    path('delete_customer/<int:customer_id>/', CustomerDeleteView.as_view(), name='delete_customer'),
    path('get_vault_data/<str:section_id>/', get_vault_data, name='get_vault_data'),
]
