from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.views.generic import ListView  # Import ListView
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomerForm

class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"

    
class maindashview(TemplateView):
    template_name = "pages/maindash.html"

class customerhomeview(TemplateView):
    template_name = "pages/Customer_Home.html"

class columbaryrecordsview(TemplateView):
    template_name = "pages/columbaryrecords.html"

class memorialview(TemplateView):
    template_name = "pages/Memorials.html"


def send_letter_of_intent(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pages/Success.html')  # Replace with the actual success page or view name
    else:
        form = CustomerForm()

    return render(request, 'pages/Customer_Home.html', {'form': form})