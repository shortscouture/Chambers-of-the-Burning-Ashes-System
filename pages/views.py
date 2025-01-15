from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView  # Import ListView
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomerForm, ColumbaryRecordForm, BeneficiaryForm
from .models import Customer, ColumbaryRecord, Beneficiary
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

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
            return redirect('pages/Success.html')  # Replace with the actual success page or view name
    else:
        form = CustomerForm()

    return render(request, 'pages/Customer_Home.html', {'form': form})

class RecordsDetailsView(TemplateView):
    template_name = "pages/recordsdetails.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer_id = self.kwargs.get('customer_id')  # Get the customer_id from the URL
        customer = Customer.objects.get(customer_id=customer_id)  # Fetch the customer
        context['customer'] = customer
        context['columbary_records'] = ColumbaryRecord.objects.filter(customer=customer)  # Fetch related columbary records
        # Fetch beneficiary details
        context['beneficiary'] = Beneficiary.objects.filter(columbaryrecord__customer=customer).first()
        return context
    
class CustomerEditView(TemplateView):
    template_name = "pages/edit_customer.html"

    def get(self, request, *args, **kwargs):
        customer_id = self.kwargs.get('customer_id')
        customer = get_object_or_404(Customer, customer_id=customer_id)
        
        # Get related columbary record and beneficiary (if available)
        columbary_record = ColumbaryRecord.objects.filter(customer=customer).first()
        beneficiary = Beneficiary.objects.filter(columbaryrecord__customer=customer).first()

        customer_form = CustomerForm(instance=customer)
        columbary_record_form = ColumbaryRecordForm(instance=columbary_record) if columbary_record else ColumbaryRecordForm()
        beneficiary_form = BeneficiaryForm(instance=beneficiary) if beneficiary else BeneficiaryForm()

        return self.render_to_response({
            'customer_form': customer_form,
            'columbary_record_form': columbary_record_form,
            'beneficiary_form': beneficiary_form,
            'customer': customer
        })

    def post(self, request, *args, **kwargs):
        customer_id = self.kwargs.get('customer_id')
        customer = get_object_or_404(Customer, customer_id=customer_id)
        
        # Get related columbary record and beneficiary (if available)
        columbary_record = ColumbaryRecord.objects.filter(customer=customer).first()
        beneficiary = Beneficiary.objects.filter(columbaryrecord__customer=customer).first()

        customer_form = CustomerForm(request.POST, instance=customer)
        columbary_record_form = ColumbaryRecordForm(request.POST, instance=columbary_record) if columbary_record else ColumbaryRecordForm(request.POST)
        beneficiary_form = BeneficiaryForm(request.POST, instance=beneficiary) if beneficiary else BeneficiaryForm(request.POST)

        if customer_form.is_valid() and columbary_record_form.is_valid() and beneficiary_form.is_valid():
            customer_form.save()
            columbary_record_form.save()
            beneficiary_form.save()
            return HttpResponseRedirect(reverse_lazy('recordsdetails', kwargs={'customer_id': customer_id}))

        return self.render_to_response({
            'customer_form': customer_form,
            'columbary_record_form': columbary_record_form,
            'beneficiary_form': beneficiary_form,
            'customer': customer
        })
