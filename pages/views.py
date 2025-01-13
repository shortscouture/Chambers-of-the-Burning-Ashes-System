from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.views.generic import ListView  # Import ListView
from .models import Customer, ColumbaryRecord
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

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

from django.shortcuts import render, redirect
from .models import Customer, ColumbaryRecord

@csrf_exempt
def register_customer(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            customer = Customer.objects.create(
                Full_Name=data['full_name'],
                Permanent_Address=data['address'],
                Landline_Number=data.get('landline', ''),
                Mobile_Number=data.get('mobile', ''),
                Email_Address=data.get('email', ''),
                # COLUMBARY_RECORDS_VaultID can be set later if needed
            )
            return JsonResponse({
                'status': 'success',
                'customer_id': customer.CustomerID,
                'message': 'Customer registered successfully'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return render(request, 'customer_form.html')