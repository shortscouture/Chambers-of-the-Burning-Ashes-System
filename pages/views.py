from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"

@login_required
def home_view(request):
    return render(request, 'home.html')
