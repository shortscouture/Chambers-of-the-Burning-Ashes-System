from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import CustomerForm, ColumbaryRecordForm, BeneficiaryForm, EmailVerificationForm, PaymentForm, HolderOfPrivilegeForm
from .models import Customer, ColumbaryRecord, Beneficiary, TwoFactorAuth,Customer, Payment, Payment, ChatQuery, ParishAdministrator, HolderOfPrivilege

from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from .models import Customer, ColumbaryRecord, Beneficiary, Payment
from .forms import CustomerForm, ColumbaryRecordForm, BeneficiaryForm, PaymentForm
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import openai
import environ
import json


class SuccesView(TemplateView):
    template_name = "success.html"

class MapView(TemplateView):
    template_name = "Columbary_Map.html"

class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"

class MapView(TemplateView):
    template_name= "Columbary_Map.html"
    
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
        context['holderofprivilege'] = HolderOfPrivilege.objects.filter(customer=customer)
        context['beneficiaries'] = Beneficiary.objects.filter(customer=customer)
        context['payments'] = Payment.objects.filter(customer=customer)
        
        return context




from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DeleteView
from django.forms import modelformset_factory
from django.contrib import messages
from .models import Customer, ColumbaryRecord, Beneficiary, Payment
from .forms import CustomerForm, ColumbaryRecordForm, BeneficiaryForm

class CustomerEditView(TemplateView):
    template_name = "pages/edit_customer.html"

    def get(self, request, *args, **kwargs):
        customer_id = self.kwargs.get('customer_id')
        customer = get_object_or_404(Customer, customer_id=customer_id)

        # Get existing records
        columbary_record = ColumbaryRecord.objects.filter(customer=customer).first()
        holder_of_privilege = HolderOfPrivilege.objects.filter(customer=customer).first()
        beneficiary = Beneficiary.objects.filter(customer=customer).first()
        payment = Payment.objects.filter(customer=customer).first()

        # Initialize forms
        customer_form = CustomerForm(instance=customer)
        columbary_record_form = ColumbaryRecordForm(instance=columbary_record) if columbary_record else ColumbaryRecordForm()
        holder_of_privilege_form = HolderOfPrivilegeForm(instance=holder_of_privilege) if holder_of_privilege else HolderOfPrivilegeForm()
        beneficiary_form = BeneficiaryForm(instance=beneficiary) if beneficiary else BeneficiaryForm()
        payment_form = PaymentForm(instance=payment) if payment else PaymentForm()

        return self.render_to_response({
            'customer_form': customer_form,
            'columbary_record_form': columbary_record_form,
            'holder_of_privilege_form': holder_of_privilege_form,
            'beneficiary_form': beneficiary_form,
            'payment_form': payment_form,
            'customer': customer
        })

    def post(self, request, *args, **kwargs):
        customer_id = self.kwargs.get('customer_id')
        customer = get_object_or_404(Customer, customer_id=customer_id)

        # Get existing records
        columbary_record = ColumbaryRecord.objects.filter(customer=customer).first()
        holder_of_privilege = HolderOfPrivilege.objects.filter(customer=customer).first()
        beneficiary = Beneficiary.objects.filter(customer=customer).first()
        payment = Payment.objects.filter(customer=customer).first()

        # Process forms
        customer_form = CustomerForm(request.POST, instance=customer)
        columbary_record_form = ColumbaryRecordForm(request.POST, instance=columbary_record) if columbary_record else ColumbaryRecordForm(request.POST)
        holder_of_privilege_form = HolderOfPrivilegeForm(request.POST, instance=holder_of_privilege) if holder_of_privilege else HolderOfPrivilegeForm(request.POST)
        beneficiary_form = BeneficiaryForm(request.POST, instance=beneficiary) if beneficiary else BeneficiaryForm(request.POST)
        payment_form = PaymentForm(request.POST, instance=payment) if payment else PaymentForm(request.POST)

        if (
            customer_form.is_valid() and 
            columbary_record_form.is_valid() and 
            holder_of_privilege_form.is_valid() and 
            beneficiary_form.is_valid() and 
            payment_form.is_valid()
        ):
            # Save Customer
            customer = customer_form.save()

            # Save Columbary Record
            columbary_record_obj = columbary_record_form.save(commit=False)
            columbary_record_obj.customer = customer
            columbary_record_obj.save()

            # Save Holder of Privilege
            holder_of_privilege_obj = holder_of_privilege_form.save(commit=False)
            holder_of_privilege_obj.customer = customer
            holder_of_privilege_obj.save()

            # Save Beneficiary
            beneficiary_obj = beneficiary_form.save(commit=False)
            beneficiary_obj.customer = customer
            beneficiary_obj.save()

            # Save Payment
            payment_obj = payment_form.save(commit=False)
            payment_obj.customer = customer
            payment_obj.save()

            messages.success(request, "Customer and related records updated successfully.")
            return redirect('recordsdetails', customer_id=customer.customer_id)
        else:
            messages.error(request, "There was an error updating the records. Please check the form data.")

        return self.render_to_response({
            'customer_form': customer_form,
            'columbary_record_form': columbary_record_form,
            'holder_of_privilege_form': holder_of_privilege_form,
            'beneficiary_form': beneficiary_form,
            'payment_form': payment_form,
            'customer': customer
        })



class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = "pages/delete_customer.html"
    success_url = reverse_lazy('columbaryrecords')

    def get_object(self, queryset=None):
        customer_id = self.kwargs.get('customer_id')
        return get_object_or_404(Customer, customer_id=customer_id)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, "Customer and all related records deleted successfully.")
        return redirect(self.success_url)




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
            return Response({'response': bot_reply}, status=status.HTTP_200_OK)


        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

def get_crypt_status(request, section):
    # Get all vaults belonging to the given section
    vaults = ColumbaryRecord.objects.filter(section=section)
    
    occupied_count = vaults.filter(status="Occupied").count()
    total_count = vaults.count()
    
    # Determine color based on occupancy
    if occupied_count == 0:
        color = "green"   # All vacant
    elif occupied_count < total_count:
        color = "yellow"  # Partially occupied
    else:
        color = "red"     # All occupied

    # Return JSON response with the color
    return JsonResponse({"section": section, "color": color})

def get_section_details(request, section_id):
    columbaries = ColumbaryRecord.objects.filter(section=section_id).values("level", "vault_id", "status")
    return JsonResponse({"section": section_id, "columbaries": list(columbaries)})

def get_data_from_db():
    data = Customer.objects.all().values()  # Fetch all fields
    return list(data)

def query_openai(data):
    """Send database data to OpenAI and get a response."""
    formatted_data = json.dumps(data, indent=2)
    prompt = f"Here is the database data: {formatted_data}\nAnalyze it and provide insights."

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are an AI assistant."},
                {"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

    def chatbot_view(request):
        """Handle AJAX request and return chatbot response."""
        db_data = get_data_from_db()
        ai_response = query_openai(db_data)
        return JsonResponse({"response": ai_response})


def addnewrecord(request):
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        payment_form = PaymentForm(request.POST)
        columbary_form = ColumbaryRecordForm(request.POST)
        holder_form = HolderOfPrivilegeForm(request.POST)
        beneficiary_form = BeneficiaryForm(request.POST)

        if all([customer_form.is_valid(), payment_form.is_valid(), columbary_form.is_valid(), holder_form.is_valid(), beneficiary_form.is_valid()]):
            # Save customer first
            customer = customer_form.save()

            # Save payment linked to customer
            payment = payment_form.save(commit=False)
            payment.customer = customer
            payment.save()

            # Save columbary record linked to customer and payment
            columbary_record = columbary_form.save(commit=False)
            columbary_record.customer = customer
            columbary_record.payment = payment
            columbary_record.save()

            # Save holder of privilege linked to customer
            holder = holder_form.save(commit=False)
            holder.customer = customer
            holder.save()

            # Save beneficiary linked to customer
            beneficiary = beneficiary_form.save(commit=False)
            beneficiary.customer = customer
            beneficiary.save()

            return redirect('columbaryrecords')  # Redirect to a success page

    else:
        customer_form = CustomerForm()
        payment_form = PaymentForm()
        columbary_form = ColumbaryRecordForm()
        holder_form = HolderOfPrivilegeForm()
        beneficiary_form = BeneficiaryForm()

    return render(request, 'pages/addnewrecord.html', {
        'customer_form': customer_form,
        'payment_form': payment_form,
        'columbary_form': columbary_form,
        'holder_form': holder_form,
        'beneficiary_form': beneficiary_form
    })
