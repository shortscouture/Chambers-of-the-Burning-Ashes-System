from django.urls import path

from .views import HomePageView, AboutPageView, maindashview, columbaryrecordsview, customerhomeview
urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("maindash/", maindashview.as_view(), name="maindash"),
    path("columbaryrecords/", columbaryrecordsview.as_view(), name="columbaryrecords"),
    path("Customer_Home/", customerhomeview.as_view(), name="Customer_Home"),
]
