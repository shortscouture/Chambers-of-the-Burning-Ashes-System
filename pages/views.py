from django.views.generic import TemplateView
from django.shortcuts import render

class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"

    
class maindashview(TemplateView):
    template_name = "pages/maindash.html"
    
class customerhomeview(TemplateView):
    template_name ='pages/Customer_Home.html'

class columbaryrecordsview(TemplateView):
    template_name = "pages/columbaryrecords.html"
    
class indexview(TemplateView):
    template_name = "pages/index.html"
