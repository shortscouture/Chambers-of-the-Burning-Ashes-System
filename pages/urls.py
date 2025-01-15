from django.urls import path

from .views import HomePageView, AboutPageView, maindashview, columbaryrecordsview, customerhomeview, memorialview,send_letter_of_intent, accept_letter_of_intent, decline_letter_of_intent
urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("maindash/", maindashview.as_view(), name="maindash"),
    path("columbaryrecords/", columbaryrecordsview.as_view(), name="columbaryrecords"),
    path("Customer_Home/", customerhomeview.as_view(), name="Customer_Home"),
    path("Memorials/", memorialview.as_view(), name="Memorials"),
    path('accept/<int:intent_id>/', send_letter_of_intent, name='accept_letter_of_intent'),
    path('accept/<int:intent_id>/', accept_letter_of_intent, name='accept_letter_of_intent'),
    path('decline/<int:intent_id>/', decline_letter_of_intent, name='decline_letter_of_intent'),
]
