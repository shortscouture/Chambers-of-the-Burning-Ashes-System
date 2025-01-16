from django.urls import path


from .views import HomePageView, AboutPageView, maindashview, columbaryrecordsview, customerhomeview, memorialview, send_letter_of_intent, verify_otp, memorials_verification,accept_letter_of_intent, decline_letter_of_intent, RecordsDetailsView, CustomerEditView


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

    path('accept/<int:intent_id>/', accept_letter_of_intent, name='accept_letter_of_intent'),
    path('decline/<int:intent_id>/', decline_letter_of_intent, name='decline_letter_of_intent'),

    path('recordsdetails/<int:customer_id>/', RecordsDetailsView.as_view(), name='recordsdetails'),
    path('edit_customer/<int:customer_id>/', CustomerEditView.as_view(), name='edit_customer'),


]
