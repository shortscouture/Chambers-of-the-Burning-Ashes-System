from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.views.generic import ListView  # Import ListView
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomerForm, EmailVerificationForm
from .models import Customer, ColumbaryRecord, TwoFactorAuth, Account
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

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