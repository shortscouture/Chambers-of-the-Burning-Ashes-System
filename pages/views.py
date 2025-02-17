from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import CustomerForm, ColumbaryRecordForm, BeneficiaryForm, EmailVerificationForm, PaymentForm
from .models import Customer, ColumbaryRecord, Beneficiary, TwoFactorAuth,Customer, Payment, InquiryRecord, Payment, ChatQuery, ParishAdministrator

from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.db.models import Count, Sum
from django.db import transaction
from .models import Customer, ColumbaryRecord, Beneficiary
from .forms import CustomerForm, ColumbaryRecordForm, BeneficiaryForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pytesseract
from PIL import Image
import re
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
        pending_counts = Customer.objects.filter(status = "pending").count()

        # Available (vacant) columbaries
        vacant_columbaries = ColumbaryRecord.objects.filter(status="Vacant").count()
        
        occupied_columbaries = ColumbaryRecord.objects.filter(status="Occupied").count()
        
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
            'vacant_columbaries': vacant_columbaries,
            'occupied_columbaries': occupied_columbaries,
            'pending_counts' : pending_counts,
            'full_payment_count': full_payment_count,
            'installment_count': installment_count,
            "earnings_labels": earnings_labels,
            "earnings_data": earnings_data,
            'unissued_columbaries': unissued_columbaries
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
        context['beneficiary'] = Beneficiary.objects.filter(customer=customer).first()
        
        return context


class CustomerEditView(TemplateView):
    template_name = "pages/edit_customer.html"

    def get(self, request, *args, **kwargs):
        customer_id = self.kwargs.get('customer_id')  # Retrieve customer_id from URL
        customer = get_object_or_404(Customer, customer_id=customer_id)  # Use 'customer_id'

        # Fetch the first columbary record related to the customer
        columbary_record = ColumbaryRecord.objects.filter(customer=customer).first()
        
        # Fetch the first beneficiary related to the customer
        beneficiary = Beneficiary.objects.filter(customer=customer).first()

        # Initialize forms with the customer, columbary record, and beneficiary data
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

        # Fetch the first columbary record related to the customer
        columbary_record = ColumbaryRecord.objects.filter(customer=customer).first()
        
        # Fetch the first beneficiary related to the customer
        beneficiary = Beneficiary.objects.filter(customer=customer).first()

        # Initialize forms with the POST data and instance
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

def extract_text(image):
    """
    Extract text from image using pytesseract
    """
    preprocessed_img = preprocess_image(image)
    text = pytesseract.image_to_string(preprocessed_img)
    return text

def parse_text_to_dict(text):
    """
    Parse extracted text into a dictionary matching model fields
    """
    data = {
        # Customer fields
        'full_name': None,
        'permanent_address': None,
        'landline_number': None,
        'mobile_number': None,
        'email_address': None,
        
        # Beneficiary fields
        'first_beneficiary_name': None,
        'second_beneficiary_name': None,
        'third_beneficiary_name': None,
        
        # HolderOfPrivilege fields
        'holder_name': None,
        'holder_email': None,
        'holder_address': None,
        'holder_landline': None,
        'holder_mobile': None,
        
        # Payment fields
        'full_contribution': False,
        'six_month_installment': False,
        'official_receipt': None,
        
        # ColumbaryRecord fields
        'vault_id': None,
        'issuance_date': None,
        'expiration_date': None,
        'inurnment_date': None,
        'issuing_parish_priest': None,
        'urns_per_columbary': None,
    }
    
    # Pattern matching for all fields
    patterns = {
        # Customer patterns
        'full_name': r'Name:[\s]*([^\n]*)',
        'permanent_address': r'Address:[\s]*([^\n]*)',
        'landline_number': r'Landline:[\s]*(\d+)',
        'mobile_number': r'Mobile:[\s]*(\d{11})',
        'email_address': r'Email:[\s]*([^\s@]+@[^\s@]+\.[^\s@]+)',
        
        # Beneficiary patterns
        'first_beneficiary_name': r'First Beneficiary:[\s]*([^\n]*)',
        'second_beneficiary_name': r'Second Beneficiary:[\s]*([^\n]*)',
        'third_beneficiary_name': r'Third Beneficiary:[\s]*([^\n]*)',
        
        # HolderOfPrivilege patterns
        'holder_name': r'Holder Name:[\s]*([^\n]*)',
        'holder_email': r'Holder Email:[\s]*([^\s@]+@[^\s@]+\.[^\s@]+)',
        'holder_address': r'Holder Address:[\s]*([^\n]*)',
        'holder_landline': r'Holder Landline:[\s]*(\d+)',
        'holder_mobile': r'Holder Mobile:[\s]*(\d+)',
        
        # ColumbaryRecord patterns
        'vault_id': r'Vault ID:[\s]*([A-Za-z0-9-]+)',
        'issuance_date': r'Issuance Date:[\s]*(\d{2}/\d{2}/\d{4})',
        'expiration_date': r'Expiration Date:[\s]*(\d{2}/\d{2}/\d{4})',
        'inurnment_date': r'Inurnment Date:[\s]*(\d{2}/\d{2}/\d{4})',
        'issuing_parish_priest': r'Parish Priest:[\s]*([^\n]*)',
        'urns_per_columbary': r'Urns:[\s]*([1-4])',
    }
    
    # Extract payment information
    data['full_contribution'] = bool(re.search(r'Payment Type:[\s]*Full', text, re.IGNORECASE))
    data['six_month_installment'] = bool(re.search(r'Payment Type:[\s]*Installment', text, re.IGNORECASE))
    receipt_match = re.search(r'Receipt Number:[\s]*(\d+)', text)
    if receipt_match:
        data['official_receipt'] = int(receipt_match.group(1))
    
    # Extract all other fields using patterns
    for field, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            data[field] = match.group(1).strip()
            
            # Convert dates to proper format
            if 'date' in field and data[field]:
                try:
                    date_obj = datetime.strptime(data[field], '%d/%m/%Y')
                    data[field] = date_obj.date()
                except ValueError:
                    data[field] = None
    
    return data

def upload_document(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = request.FILES['document']
            
            try:
                # Extract and parse text
                extracted_text = extract_text(image)
                data = parse_text_to_dict(extracted_text)
                
                # Create Customer
                customer = Customer.objects.create(
                    full_name=data['full_name'],
                    permanent_address=data['permanent_address'],
                    landline_number=data['landline_number'],
                    mobile_number=data['mobile_number'],
                    email_address=data['email_address']
                )
                
                # Create Beneficiary
                beneficiary = None
                if data['first_beneficiary_name']:
                    beneficiary = Beneficiary.objects.create(
                        first_beneficiary_name=data['first_beneficiary_name'],
                        second_beneficiary_name=data['second_beneficiary_name'],
                        third_beneficiary_name=data['third_beneficiary_name']
                    )
                
                # Create HolderOfPrivilege
                holder = None
                if data['holder_name']:
                    holder = HolderOfPrivilege.objects.create(
                        full_name=data['holder_name'],
                        email_address=data['holder_email'],
                        address=data['holder_address'],
                        landline_number=data['holder_landline'],
                        mobile_number=data['holder_mobile']
                    )
                
                # Create Payment
                payment = None
                if data['full_contribution'] or data['six_month_installment']:
                    payment = Payment.objects.create(
                        full_contribution=data['full_contribution'],
                        six_month_installment=data['six_month_installment'],
                        official_receipt=data['official_receipt']
                    )
                
                # Create ColumbaryRecord
                if data['vault_id']:
                    columbary = ColumbaryRecord.objects.create(
                        vault_id=data['vault_id'],
                        issuance_date=data['issuance_date'],
                        expiration_date=data['expiration_date'],
                        inurnment_date=data['inurnment_date'],
                        issuing_parish_priest=data['issuing_parish_priest'],
                        urns_per_columbary=data['urns_per_columbary'],
                        customer=customer,
                        beneficiary=beneficiary,
                        payment=payment,
                        holder_of_privilege=holder
                    )
                
                messages.success(request, 'Document processed successfully!')
                return redirect('success_url')
                
            except Exception as e:
                messages.error(request, f'Error processing document: {str(e)}')
                return redirect('upload_document')
    else:
        form = DocumentUploadForm()
    
    return render(request, 'ocr_app/upload.html', {'form': form})
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CustomerForm
from .models import Customer

# views.py
from django.shortcuts import render, redirect
from .forms import CustomerForm, ColumbaryRecordForm, BeneficiaryForm

def addnewrecord(request):
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        record_form = ColumbaryRecordForm(request.POST)
        beneficiary_form = BeneficiaryForm(request.POST)
        payment_form = PaymentForm(request.POST)  # Add payment form
        
        # Check if all forms are valid
        if all([customer_form.is_valid(), record_form.is_valid(), beneficiary_form.is_valid(), payment_form.is_valid()]):
            # Save the customer record
            customer = customer_form.save()

            # Save the Columbary record
            record = record_form.save(commit=False)
            record.customer = customer  # Associate the customer with the record
            record.save()

            # Save the beneficiary record
            beneficiary_form.save()

            # Handle payment data based on the payment mode
            payment = payment_form.save(commit=False)
            payment.customer = customer  # Associate the customer with the payment
            if payment.mode_of_payment == 'Full Payment':
                payment.save()  # Save full payment
            elif payment.mode_of_payment == '6-Month Installment':
                # If installment, save each installment receipt
                for i in range(1, 7):  # 6 months
                    receipt_field = f'six_month_receipt_{i}'
                    amount_field = f'six_month_amount_{i}'
                    receipt = payment_form.cleaned_data.get(receipt_field)
                    amount = payment_form.cleaned_data.get(amount_field)
                    if receipt and amount:
                        Payment.objects.create(
                            customer=customer,
                            mode_of_payment='6-Month Installment',
                            receipt_number=receipt,
                            amount=amount,
                            installment_month=i
                        )

            # Redirect after successful record and payment save
            return redirect('columbaryrecords')
    else:
        customer_form = CustomerForm()
        record_form = ColumbaryRecordForm()
        beneficiary_form = BeneficiaryForm()
        payment_form = PaymentForm()  # Initialize payment form

    return render(request, 'pages/addnewrecord.html', {
        'customer_form': customer_form,
        'record_form': record_form,
        'beneficiary_form': beneficiary_form,
        'payment_form': payment_form  # Pass the payment form to the template
    })
