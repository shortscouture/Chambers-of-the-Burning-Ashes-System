from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView  # Import ListView
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .forms import CustomerForm, ColumbaryRecordForm, BeneficiaryForm, EmailVerificationForm
from .models import Customer, ColumbaryRecord, Beneficiary, TwoFactorAuth, Account
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

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
            return redirect('success')  # Redirect to success view
    else:
        form = CustomerForm()

    return render(request, 'pages/Customer_Home.html', {'form': form})

        full_name = request.POST['full_name']
        permanent_address = request.POST['permanent_address']
        landline_number = request.POST.get('landline_number', '')
        mobile_number = request.POST['mobile_number']
        email_address = request.POST['email_address']

        # Save the form data with a pending status
        intent = Customer.objects.create(
            full_name=full_name,
            permanent_address=permanent_address,
            landline_number=landline_number,
            mobile_number=mobile_number,
            email_address=email_address,
        )

        # Send email to admin
        accept_url = request.build_absolute_uri(f'/accept/{intent.id}/')
        decline_url = request.build_absolute_uri(f'/decline/{intent.id}/')
        email_body = f"""
        A new letter of intent has been submitted:
        Full Name: {full_name}
        Address: {permanent_address}

        Accept: {accept_url}
        Decline: {decline_url}
        """
        send_mail(
            'New Letter of Intent',
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
        )

        return redirect('Customer_Home.html')  # Redirect after submission

    return render(request, 'pages/Customer_Home.html')

def accept_letter_of_intent(request, intent_id):
    intent = get_object_or_404(Customer, id=intent_id)
    intent.status = 'approved'
    intent.save()
    
    send_mail(
        subject="Your Letter of Intent has been Accepted",
        message=(
            f"Dear {intent.full_name},\n\n"
            "We are pleased to inform you that your letter of intent has been accepted.\n\n"
            "Best regards,\nThe Team"
        ),
        from_email='stalphonsusmakati@gmail.com',
        recipient_list=[intent.email_address],
        fail_silently=False,
    )

    return render(request, 'pages/accept_success.html', {'intent': intent})


def decline_letter_of_intent(request, intent_id):
    intent = get_object_or_404(Customer, id=intent_id)
    intent.status = 'declined'
    intent.delete()
        
    send_mail(
        subject="Your Letter of Intent has been Declined",
        message=(
            f"Dear {intent.full_name},\n\n"
            "We regret to inform you that your letter of intent has been declined.\n\n"
            "Best regards,\nThe Team"
        ),
        from_email='stalphonsusmakati@gmail.com',
        recipient_list=[intent.email_address],
        fail_silently=False,
    )



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
  def memorials_verification(request):
    form = EmailVerificationForm()
    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                customer = Customer.objects.get(email_address=email)
                
                tfa = TwoFactorAuth.objects.create(email=email)
                otp = tfa.generate_otp()
                if tfa.send_otp_email(customer):
                    request.session['verification_email'] = email
                    messages.success(request, "Verification code sent to your email.")
                    return redirect('verify_otp')
                else:
                    messages.error(request, "Failed to send verification code. Please try again.")
            except Customer.DoesNotExist:
                messages.error(request, f"No records found for the email address: {email}")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "The form is not valid. Please check the input.")
    return render(request, 'pages/Memorials.html', {'form': form})


  def verify_otp(request):
    if 'verification_email' not in request.session:
        return redirect('Memorials')
            
    if request.method == 'POST':
        submitted_otp = request.POST.get('otp')
        email = request.session['verification_email']
        
        try:
            customer = Customer.objects.get(email_address=email)
            tfa = TwoFactorAuth.objects.get(
                email=email,
                is_verified=False,
                created_at__gte=timezone.now() - timedelta(minutes=15)  # Correctly use timezone.now()
            )
    
            if tfa.verify_otp(submitted_otp):
                records = ColumbaryRecord.objects.filter(customer=customer)
                for record in records:
                    record.send_record_email()
                    
                messages.success(request, "Verification successful! Your records have been sent to your email.")
                del request.session['verification_email']
                return redirect('Customer_Home')
            else:
                messages.error(request, "Invalid or expired verification code.")
        except (Customer.DoesNotExist, TwoFactorAuth.DoesNotExist):
            messages.error(request, "Something went wrong. Please try again.")
            return redirect('Memorials')
        
    return render(request, 'pages/verify_otp.html')

  def success(request):
    return render(request, 'pages/success.html')
