from django.urls import path

from .views import HomePageView, AboutPageView, maindashview, columbaryrecordsview, customerhomeview, memorialview, send_letter_of_intent, verify_otp, memorials_verification
urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("maindash/", maindashview.as_view(), name="maindash"),
    path("columbaryrecords/", columbaryrecordsview.as_view(), name="columbaryrecords"),
    path("Customer_Home/", customerhomeview.as_view(), name="Customer_Home"),
    path("Memorials/", memorialview.as_view(), name="Memorials"),
    path('memorials_verification/', memorials_verification, name='memorials_verification'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('send_letter_of_intent/', send_letter_of_intent, name='send_letter_of_intent'),
]
