from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.views.generic import ListView  # Import ListView
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomerForm
from .models import Customer


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customers"] = Customer.objects.all()  # Fetch all customers from the database
        return context

class memorialview(TemplateView):
    template_name = "pages/Memorials.html"


def send_letter_of_intent(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('successfull.html')  # Replace with the actual success page or view name
    else:
        form = CustomerForm()

    return render(request, '500.html', {'form': form})