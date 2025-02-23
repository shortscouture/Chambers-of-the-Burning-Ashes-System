from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404,  HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from datetime import datetime, timedelta
from .forms import CustomerForm, ColumbaryRecordForm, BeneficiaryForm, EmailVerificationForm, PaymentForm, HolderOfPrivilegeForm
from .models import Customer, ColumbaryRecord, Beneficiary, TwoFactorAuth,Customer, Payment, Payment, ChatQuery, ParishAdministrator, HolderOfPrivilege
from django.views.generic import TemplateView, DeleteView
from django.forms import modelformset_factory
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.db.models import Count, Sum
from .models import Customer, ColumbaryRecord, Beneficiary, Payment
from .forms import CustomerForm, ColumbaryRecordForm, BeneficiaryForm, PaymentForm, DocumentUploadForm
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pytesseract
from PIL import Image
import re
import openai
from django.db import transaction
import json
import environ
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from .models import Customer, Payment
from datetime import datetime



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


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch necessary data
        customer_status_counts = Customer.objects.values('status').annotate(count=Count('status'))
        #inquiry_counts = InquiryRecord.objects.count()
        pending_counts = Customer.objects.filter(status="pending").count()
        vacant_columbaries = ColumbaryRecord.objects.filter(status="Vacant")
        occupied_columbaries = ColumbaryRecord.objects.filter(status="Occupied")
        unissued_columbaries = ColumbaryRecord.objects.filter(issuance_date__isnull=True, customer__isnull=False).count()
        full_payment_count = Payment.objects.filter(mode_of_payment="Full Payment").count()
        installment_count = Payment.objects.filter(mode_of_payment="6-Month Installment").count()
        unissued_columbary_records = ColumbaryRecord.objects.filter(issuance_date__isnull=True, customer__isnull=False)
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        earnings_by_date = (
            ColumbaryRecord.objects.filter(payment__isnull=False)
            .values("issuance_date")
            .annotate(total_earnings=Sum("payment__total_amount"))
            .order_by("issuance_date")
        )

        # Convert data to JSON for Chart.js
        payment_labels = ["Full Payment", "Installment"]
        payment_data = [full_payment_count, installment_count]

        # Convert strings to datetime objects (if provided)
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Filter earnings based on the selected date range
        earnings_queryset = Payment.objects.filter(
            transaction_date__gte=start_date if start_date else "1900-01-01",
            transaction_date__lte=end_date if end_date else "2100-01-01"
        ).annotate(month=TruncMonth("transaction_date"))  # ✅ Apply filter BEFORE aggregation

        earnings_by_month = (
            earnings_queryset
            .values("month")
            .annotate(total_earnings=Sum("total_amount"))
            .order_by("month")
        )

        # Convert data for Chart.js
        earnings_labels = [
            entry["month"].strftime("%b %Y") for entry in earnings_by_month if entry["month"] is not None
        ]
        earnings_data = [float(entry["total_earnings"]) for entry in earnings_by_month]

        # Debugging: Print earnings data
        print("Earnings Labels:", earnings_labels)
        print("Earnings Data:", earnings_data)

        # Add data to context
        context.update({
            'customer_status_counts': customer_status_counts,
            #'inquiry_counts': inquiry_counts,
            'pending_counts': Customer.objects.filter(status="pending").count(),
            'pending_customers': Customer.objects.filter(status="pending"),
            'unissued_columbaries': ColumbaryRecord.objects.filter(issuance_date__isnull=True, customer__isnull=False).count(),
            'vacant_columbaries': ColumbaryRecord.objects.filter(status="Vacant"),
            'vacant_columbaries_count': ColumbaryRecord.objects.filter(status="Vacant").count(),  # Returns an int
            'occupied_columbaries': ColumbaryRecord.objects.filter(status="Occupied"),
            'occupied_columbaries_count': ColumbaryRecord.objects.filter(status="Occupied").count(),
            'unissued_columbary_records' : unissued_columbary_records,
            "payment_labels": mark_safe(json.dumps(payment_labels)),
            "payment_data": mark_safe(json.dumps(payment_data)),
            "earnings_labels": mark_safe(json.dumps(earnings_labels)),  # Labels (months)
            "earnings_data": mark_safe(json.dumps(earnings_data)),  # Earnings
            "start_date": start_date.strftime("%Y-%m-%d") if start_date else "",
            "end_date": end_date.strftime("%Y-%m-%d") if end_date else "",

        })

        return context

def accept_letter_of_intent(request, intent_id):
    """ Update customer status to 'approved' when accepted. """
    customer = get_object_or_404(Customer, customer_id=intent_id)
    customer.status = "approved"
    customer.save()
    
    return JsonResponse({"status": "success", "message": "Accepted", "new_status": "approved"})

def decline_letter_of_intent(request, intent_id):
    """ Update customer status to 'declined' when declined. """
    customer = get_object_or_404(Customer, customer_id=intent_id)
    customer.status = "declined"
    customer.save()
    
    return JsonResponse({"status": "success", "message": "Declined", "new_status": "declined"})
            
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
                model="gpt-3.5-turbo",  # Using GPT-3.5 model
                messages=[{"role": "user", "content": user_message}],
                max_tokens=150
            )
            bot_reply = response.choices[0].message.content.strip()  # Get the response from GPT-3.5
            return Response({'response': bot_reply}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

      
def preprocess_image(image):
    """
    Preprocess the image to improve OCR accuracy
    """
    img = Image.open(image).convert('L')
    img = img.point(lambda x: 0 if x < 128 else 255)
    return img

@csrf_exempt 
def process_ocr(request):
    if request.method == 'POST' and request.FILES.get('document'):
        try:
            # Extract text from the uploaded image
            image = request.FILES['document']
            extracted_text = extract_text(image)
            
            # Parse the extracted text into a dictionary
            data = parse_text_to_dict(extracted_text)
            
            return JsonResponse({'success': True, 'data': data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def extract_text(image):
    """
    Extract text from image using pytesseract
    """
    img = Image.open(image).convert('L')  # Convert to grayscale
    text = pytesseract.image_to_string(img)
    return text

def parse_text_to_dict(text):
    """
    Parse extracted text into a dictionary matching model fields.
    """
    data = {
        # Customer fields
        'first_name': None,
        'middle_name': None,
        'last_name': None,
        'suffix': None,
        'country': 'Philippines',  # Default value
        'address_line_1': None,
        'address_line_2': None,
        'city': None,
        'province_or_state': None,
        'postal_code': None,
        'landline_number': None,
        'mobile_number': None,
        'email_address': None,
        
        # Beneficiary fields
        'first_beneficiary_name': None,
        'second_beneficiary_name': None,
        'third_beneficiary_name': None,
        
        # ColumbaryRecord fields
        'vault_id': None,
        'inurnment_date': None,
        'urns_per_columbary': None,
    }

    # Example patterns (adjust based on your document structure)
    patterns = {
        # Customer patterns
        'full_name': r'Full name:[\s]*([^\n]*)',
        'permanent_address': r'Permanent Address:[\s]*([^\n]*)',
        'mobile_number': r'Mobile Number:[\s]*([^\n]*)',
        'email_address': r'Email Address:[\s]*([^\n]*)',
        
        # Beneficiary patterns
        'first_beneficiary_name': r'FIRST PRIORITY[\s]*Full name:[\s]*([^\n]*)',
        'second_beneficiary_name': r'SECOND PRIORITY[\s]*Full name:[\s]*([^\n]*)',
        'third_beneficiary_name': r'THIRD PRIORITY[\s]*Full name:[\s]*([^\n]*)',
        
        # ColumbaryRecord patterns
        'vault_id': r'Vault ID:[\s]*([^\n]*)',
        'inurnment_date': r'Inurnment Date:[\s]*([^\n]*)',
        'urns_per_columbary': r'Urns Per Columbary:[\s]*([^\n]*)',
    }

    # Extract all fields using patterns
    for field, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            data[field] = match.group(1).strip()

    # Split full name into first, middle, and last names
    if data.get('full_name'):
        name_parts = data['full_name'].split()
        if len(name_parts) >= 1:
            data['first_name'] = name_parts[0]
        if len(name_parts) >= 2:
            data['last_name'] = name_parts[-1]
        if len(name_parts) > 2:
            data['middle_name'] = ' '.join(name_parts[1:-1])

    return data


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
