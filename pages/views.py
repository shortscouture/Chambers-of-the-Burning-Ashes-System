from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import CustomerForm, ColumbaryRecordForm, BeneficiaryForm, EmailVerificationForm
from .models import Customer, ColumbaryRecord, Beneficiary, TwoFactorAuth,Customer, Payment, InquiryRecord, ParishAdministrator, ParishStaff, ChatQuery
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.db.models import Count, Sum
from .models import Customer, ColumbaryRecord, Beneficiary
from .forms import CustomerForm, ColumbaryRecordForm, BeneficiaryForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


import openai
import environ


class SuccesView(TemplateView):
    template_name = "success.html"

class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"


class MainDashView(TemplateView):
    template_name = "pages/maindash.html"


class CustomerHomeView(TemplateView):
    template_name = "pages/Customer_Home.html"


class ColumbaryRecordsView(TemplateView):
    template_name = "pages/columbaryrecords.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customers"] = Customer.objects.all()
        return context


class MemorialView(TemplateView):
    template_name = "pages/Memorials.html"

class dashboardView(TemplateView):
    template_name = "dashboard.html"
    
    def dashboard(request):
        # Customer Status Analytics
        customer_status_counts = Customer.objects.values('status').annotate(count=Count('status'))
        customer_status_labels = [entry['status'] for entry in customer_status_counts]
        customer_status_data = [entry['count'] for entry in customer_status_counts]

        # Columbary Records Analytics
        columbary_records = ColumbaryRecord.objects.all()
        columbary_status_counts = columbary_records.values('urns_per_columbary').annotate(count=Count('urns_per_columbary'))
        columbary_status_labels = [entry['urns_per_columbary'] for entry in columbary_status_counts]
        columbary_status_data = [entry['count'] for entry in columbary_status_counts]

        # Inquiry Record Analytics
        inquiry_counts = InquiryRecord.objects.count()
        
        #Customer Status
        pending_counts = Customer.objects.filter(status = "pending")

        # Available (vacant) columbaries
        vacant_columbaries = ColumbaryRecord.objects.filter(status="Vacant")
        
        occupied_columbaries = ColumbaryRecord.objects.filter(status="Occupied")
        
        #Unissued Columbaries
        unissued_columbaries = ColumbaryRecord.objects.filter(issuance_date__isnull=True, status = "Occupied").count()

        # Payment Mode Statistics
        full_payment_count = Payment.objects.filter(mode_of_payment="Full Payment").count()
        installment_count = Payment.objects.filter(mode_of_payment="6-Month Installment").count()
        earnings_by_date = (
        ColumbaryRecord.objects.filter(payment__isnull=False)
        .values("issuance_date")
        .annotate(total_earnings= Sum("payment__total_amount"))
        .order_by("issuance_date")
         )
        
        earnings_labels = [entry["issuance_date"].strftime("%Y-%m-%d") for entry in earnings_by_date]
        earnings_data = [float(entry["total_earnings"]) for entry in earnings_by_date]    


        context = {
            'customer_status_labels': customer_status_labels,
            'customer_status_data': customer_status_data,
            'columbary_status_labels': columbary_status_labels,
            'columbary_status_data': columbary_status_data,
            'inquiry_counts': inquiry_counts,
            'vacant_columbaries': vacant_columbaries.count(),
            'pending_counts' : pending_counts.count(),
            'full_payment_count': full_payment_count,
            'installment_count': installment_count,
            "earnings_labels": earnings_labels,
            "earnings_data": earnings_data,
            'unissued_columbaries': unissued_columbaries,
            'pending_customers': pending_counts,
            'available_columbaries': vacant_columbaries,
            'occupied_columbaries': occupied_columbaries,
            'occupied_columbaries_count': occupied_columbaries.count(),
        }

        return render(request, 'dashboard.html', context)

            
def send_letter_of_intent(request):
    if request.method == 'POST':

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
        accept_url = request.build_absolute_uri(f'/accept/{intent.customer_id}/')
        decline_url = request.build_absolute_uri(f'/decline/{intent.customer_id}/')
        email_body = f"""
Dear Rev. Bobby
    
I hope this message finds you well. I am writing to formally submit my letter of intent for Acquiring a Columbary find my details below:

Full Name: {full_name}
Permanent Address: {permanent_address}
Landline Number: {landline_number if landline_number else 'N/A'}
Mobile Number: {mobile_number}
Email Address: {email_address}

I would appreciate your time and attention to this matter. Please feel free to reach out to me if any further information or clarification is needed.

Thank you for considering my submission.

Best regards,

        Accept: {accept_url}
        Decline: {decline_url}
        """
        send_mail(
            'New Letter of Intent',
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
        )

        return render(request, 'Success.html', {'intent': intent})
    

def accept_letter_of_intent(request, intent_id):
    intent = get_object_or_404(Customer, customer_id=intent_id)
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
    intent = get_object_or_404(Customer, customer_id=intent_id)
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
        customer_id = self.kwargs.get('customer_id')
        
        customer = get_object_or_404(Customer, customer_id=customer_id)
        
        context['customer'] = customer
        context['columbary_records'] = ColumbaryRecord.objects.filter(customer=customer)
        context['beneficiary'] = Beneficiary.objects.filter(columbaryrecord__customer=customer).first()
        return context


class CustomerEditView(TemplateView):
    template_name = "pages/edit_customer.html"

    def get(self, request, *args, **kwargs):
        customer_id = self.kwargs.get('customer_id')  # Retrieve customer_id from URL
        customer = get_object_or_404(Customer, customer_id=customer_id)  # Use 'customer_id'
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
        customer_id = self.kwargs.get('customer_id')  # Retrieve customer_id from URL
        customer = get_object_or_404(Customer, customer_id=customer_id)  # Use 'customer_id'
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
        else:
            # Debugging: Print form errors
            print("Customer form errors:", customer_form.errors)
            print("Columbary record form errors:", columbary_record_form.errors)
            print("Beneficiary form errors:", beneficiary_form.errors)

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


@csrf_exempt
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
                created_at__gte=timezone.now() - timedelta(minutes=15)
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

#chatbot env
env = environ.Env(
    DEBUG=(bool, False) #default value for DEBUG = False
)

openai.api_key = env("OPEN_AI_API_KEY")
class ChatbotAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Chatbot API is running! Use POST to send messages."}, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        user_message = request.data.get('message')

        if not user_message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # Using GPT-3.5 models
                messages=[{"role": "user", "content": user_message}],
                max_tokens=150
            )
            bot_reply = response.choices[0].message.content.strip()  # Get the response from GPT-3.5
            #save to database
            ChatQuery.objects.create(user_message=user_message, bot_response=bot_reply)

            return Response({'response': bot_reply}, status=status.HTTP_200_OK)


        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
