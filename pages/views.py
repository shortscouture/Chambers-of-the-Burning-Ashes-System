from django.views.generic import TemplateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404,  HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
from .forms import CustomerForm, ColumbaryRecordForm, BeneficiaryForm, EmailVerificationForm, PaymentForm, HolderOfPrivilegeForm, DocumentUploadForm
from .models import Customer, ColumbaryRecord, Beneficiary, TwoFactorAuth,Customer, Payment, ChatQuery, ParishAdministrator, HolderOfPrivilege
from django.forms import modelformset_factory
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.db import transaction, connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pytesseract
from PIL import Image
import re
import numpy as np
import cv2
import openai
from django.db import transaction
import json
import environ
from django.db.models.functions import TruncMonth
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.db.models import Q
from .models import ColumbaryRecord
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
import json


logger = logging.getLogger(__name__)


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

        # Get search query & selected filters
        search_query = self.request.GET.get("search", "").strip()
        selected_filters = self.request.GET.getlist("filter")  # Multiple selections

        # Fetch all records
        columbary_records = ColumbaryRecord.objects.select_related("customer").all()

        # Apply search filter
        if search_query:
            columbary_records = columbary_records.filter(
                Q(vault_id__icontains=search_query) | 
                Q(customer__first_name__icontains=search_query) | 
                Q(customer__last_name__icontains=search_query)
            )

        records_data = []
        for record in columbary_records:
            customer = getattr(record, "customer", None)  # Avoid NoneType errors

            has_beneficiary = (
                customer and customer.beneficiaries.filter(first_beneficiary_name__isnull=False).exists()
            )

            has_payment = (
                customer and customer.payments.filter(
                    mode_of_payment__isnull=False
                ).filter(
                    Q(mode_of_payment="Full Payment", Full_payment_receipt_1__isnull=False, Full_payment_amount_1__isnull=False) |
                    Q(mode_of_payment="6-Month Installment", 
                      six_month_receipt_1__isnull=False, six_month_amount_1__isnull=False, 
                      six_month_receipt_2__isnull=False, six_month_amount_2__isnull=False, 
                      six_month_receipt_3__isnull=False, six_month_amount_3__isnull=False, 
                      six_month_receipt_4__isnull=False, six_month_amount_4__isnull=False, 
                      six_month_receipt_5__isnull=False, six_month_amount_5__isnull=False, 
                      six_month_receipt_6__isnull=False, six_month_amount_6__isnull=False)
                ).exists()
            )

            has_holder_of_privilege = (
                customer and customer.privileges.filter(issuance_date__isnull=False).exists()
            )

            record_entry = {
                "vault_id": record.vault_id,
                "customer_name": customer.full_name() if customer else "No Customer",
                "has_beneficiary": has_beneficiary,
                "has_payment": has_payment,
                "has_holder_of_privilege": has_holder_of_privilege,
                "customer_id": customer.customer_id if customer else None,
            }

            records_data.append(record_entry)

        # Apply filter logic
        if selected_filters:
            if len(selected_filters) == 3:
                # Show only fully completed records if all three filters are selected
                records_data = [
                    record for record in records_data
                    if record["has_beneficiary"] and record["has_payment"] and record["has_holder_of_privilege"]
                ]
            else:
                # Show records that match at least one selected filter
                records_data = [
                    record for record in records_data
                    if (
                        ("beneficiary" in selected_filters and record["has_beneficiary"]) or
                        ("payment" in selected_filters and record["has_payment"]) or
                        ("holder" in selected_filters and record["has_holder_of_privilege"])
                    )
                ]

        # Apply pagination (10 records per page)
        page = self.request.GET.get("page", 1)
        paginator = Paginator(records_data, 10)  # Show 10 per page
        paginated_records = paginator.get_page(page)

        # Add to context
        context["records_data"] = paginated_records
        context["search_query"] = search_query  # Keep search input filled
        context["selected_filters"] = selected_filters  # Keep selected filters
        return context





class MemorialView(TemplateView):
    template_name = "pages/Memorials.html"


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch necessary data
        customer_status_counts = Customer.objects.values('status').annotate(count=Count('status'))
        pending_counts = Customer.objects.filter(status="pending").count()
        vacant_columbaries_count = ColumbaryRecord.objects.filter(status="Vacant").count()
        occupied_columbaries_count = ColumbaryRecord.objects.filter(status="Occupied").count()
        full_payment_count = Payment.objects.filter(mode_of_payment="Full Payment").count()
        installment_count = Payment.objects.filter(mode_of_payment="6-Month Installment").count()

        # Ensure correct referencing of issuance date in HolderOfPrivilege
        unissued_columbaries = ColumbaryRecord.objects.filter(
            holder_of_privilege__issuance_date__isnull=True, 
            customer__isnull=False
        ).count()

        # Retrieve all unissued Columbary records
        unissued_columbary_records = ColumbaryRecord.objects.filter(
            holder_of_privilege__issuance_date__isnull=True, 
            customer__isnull=False
        )

        # Calculate earnings per issuance date
        earnings_by_date = (
            ColumbaryRecord.objects.filter(payment__isnull=False, holder_of_privilege__issuance_date__isnull=False)
            .values("holder_of_privilege__issuance_date")
            .annotate(total_earnings=Sum("payment__total_amount"))
            .order_by("holder_of_privilege__issuance_date")
        )

        # Get earnings per month
        earnings_by_month = (
            ColumbaryRecord.objects.filter(payment__isnull=False, holder_of_privilege__issuance_date__isnull=False)
            .annotate(month=TruncMonth("holder_of_privilege__issuance_date"))
            .values("month")
            .annotate(total_earnings=Sum("payment__total_amount"))
            .order_by("month")
        )

        # Convert data for Chart.js
        earnings_labels = [
            entry["month"].strftime("%b %Y") for entry in earnings_by_month if entry["month"] is not None
        ]
        earnings_data = [float(entry["total_earnings"]) if entry["total_earnings"] else 0 for entry in earnings_by_month]

        # Convert payment method data
        payment_labels = ["Full Payment", "Installment"]
        payment_data = [full_payment_count, installment_count]

        # Add data to context
        context.update({
            'customer_status_counts': customer_status_counts,
            'pending_counts': pending_counts,
            'pending_customers': Customer.objects.filter(status="pending"),
            'unissued_columbaries': unissued_columbaries,
            'vacant_columbaries_count': vacant_columbaries_count,
            'occupied_columbaries_count': occupied_columbaries_count,
            'unissued_columbary_records': unissued_columbary_records,  
            "payment_labels": mark_safe(json.dumps(payment_labels)),
            "payment_data": mark_safe(json.dumps(payment_data)),
            "earnings_labels": mark_safe(json.dumps(earnings_labels)),  
            "earnings_data": mark_safe(json.dumps(earnings_data)),  
        })

        return context

            
def send_letter_of_intent(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        mobile_number = request.POST['mobile_number']
        email_address = request.POST['email_address']
        section = request.POST['section']
        level = request.POST['level']

        # Ensure selected vault is vacant
        try:
            vault = ColumbaryRecord.objects.get(section=section, level=level, status="Vacant")
        except ColumbaryRecord.DoesNotExist:
            return JsonResponse({"error": "Selected vault is already occupied or does not exist!"}, status=400)

        # Save the customer record with a pending status
        customer = Customer.objects.create(
            first_name=first_name,
            last_name=last_name,
            mobile_number=mobile_number,
            email_address=email_address,
            status="pending"
        )

        # Assign the selected ColumbaryRecord to this customer but keep it Vacant until approval
        vault.customer = customer  
        vault.save()  

        # Generate accept & decline URLs dynamically
        accept_url = request.build_absolute_uri(reverse('accept_letter_of_intent', args=[customer.customer_id]))
        decline_url = request.build_absolute_uri(reverse('decline_letter_of_intent', args=[customer.customer_id]))

        email_body = f"""
Dear Rev. Bobby,

A new Letter of Intent has been submitted:

First Name: {first_name}
Last Name: {last_name}
Mobile Number: {mobile_number}
Email Address: {email_address}
Requested Vault: Section {section}, Level {level}

[✅ Accept]({accept_url})
[❌ Decline]({decline_url})

Please review this request.

Best regards,
St. Alphonsus Parish
        """

        send_mail(
            'New Letter of Intent',
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )

        return render(request, 'success.html')

    return JsonResponse({"error": "Invalid request method"}, status=405)

    

def accept_letter_of_intent(request, intent_id):
    intent = get_object_or_404(Customer, customer_id=intent_id)
    intent.status = "approved"
    intent.save()

    # Find the ColumbaryRecord assigned to this customer (set during Letter of Intent submission)
    columbary = ColumbaryRecord.objects.filter(customer=intent, status="Vacant").first()

    if columbary:
        columbary.status = "Occupied"  # Change status to Occupied
        columbary.save()
    else:
        return HttpResponse("No available columbary assigned for this customer.", status=400)

    # Send acceptance email
    send_mail(
        subject="Your Letter of Intent has been Accepted",
        message=f"Dear {intent.first_name} {intent.last_name},\n\n"
                f"We are pleased to inform you that your letter of intent has been accepted.\n"
                f"You have been assigned to Columbary: {columbary.section}-{columbary.level}.\n\n"
                "Best regards,\nSt. Alphonsus Parish",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[intent.email_address],
        fail_silently=False,
    )

    return render(request, 'success.html', {'intent': intent, 'columbary': columbary})




def decline_letter_of_intent(request, intent_id):
    intent = get_object_or_404(Customer, customer_id=intent_id)
    intent.status = 'declined'
    intent.save()  # Keep the record instead of deleting it

    # Send rejection email
    send_mail(
        subject="Your Letter of Intent has been Declined",
        message=f"Dear {intent.first_name} {intent.last_name},\n\n"
                "We regret to inform you that your letter of intent has been declined.\n\n"
                "Best regards,\n St. Alphonsus Parish",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[intent.email_address],
        fail_silently=False,
    )

    return redirect('some_rejection_page')


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
        customer = self.get_object()

        # Unlink ColumbaryRecord (keep the vault ID, but remove associations)
        columbary_records = ColumbaryRecord.objects.filter(customer=customer)
        for record in columbary_records:
            record.customer = None
            record.payment = None
            record.holder_of_privilege = None
            record.beneficiary = None
            record.status = 'Vacant'  # Mark as Vacant if necessary
            record.save()

        # Delete all related records
        Payment.objects.filter(customer=customer).delete()
        HolderOfPrivilege.objects.filter(customer=customer).delete()
        Beneficiary.objects.filter(customer=customer).delete()

        # Delete the customer
        customer.delete()

        messages.success(request, "Customer and related records deleted successfully, but Vault ID remains intact.")
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

      
def preprocess_image(image):
    """
    Enhanced image preprocessing specifically for form documents
    """
    # Converting PIL Image to cv2 format
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    denoised = cv2.fastNlMeansDenoising(binary)
    
    contrast = cv2.convertScaleAbs(denoised, alpha=1.5, beta=0)
    
    return Image.fromarray(contrast)

def extract_name_components(full_name):
    """
    Extract first, middle, and last name from full name string
    """
    parts = full_name.strip().split()
    
    # Handle special cases like "Jr", "Sr", "III"
    suffix = ""
    if parts[-1].lower() in ['jr', 'sr', 'ii', 'iii', 'iv']:
        suffix = parts.pop()
    
    if len(parts) >= 3:
        first_name = parts[0]
        last_name = parts[-1]
        middle_name = ' '.join(parts[1:-1])
    elif len(parts) == 2:
        first_name = parts[0]
        last_name = parts[1]
        middle_name = ''
    else:
        first_name = parts[0] if parts else ''
        middle_name = ''
        last_name = ''
    
    return {
        'first_name': first_name,
        'middle_name': middle_name,
        'last_name': last_name,
        'suffix': suffix
    }

def parse_text_to_form_data(text):
    """
    Enhanced parsing function specifically matched to your form structure
    """
    data = {
        'first_name': '',
        'middle_name': '',
        'last_name': '',
        'suffix': '',
        'country': 'Philippines',
        'address_line_1': '',
        'address_line_2': '',
        'city': '',
        'province_or_state': '',
        'postal_code': '',
        'landline_number': '',
        'mobile_number': '',
        'email_address': '',
        'first_beneficiary_name': '',
        'second_beneficiary_name': '',
        'third_beneficiary_name': '',
        'vault_id': '',
        'inurnment_date': None,
        'urns_per_columbary': '1'
    }

    # Define detailed patterns for each field
    patterns = {
        'full_name': r'Full\s*name:?\s*([^\n]*)',
        'permanent_address': r'Permanent\s*Address:?\s*([^\n]*)',
        'current_address': r'Current\s*Address:?\s*([^\n]*)',
        'email': r'Email\s*Address:?\s*([^\n]*)',
        'landline': r'Landline\s*Number:?\s*([^\n]*)',
        'mobile': r'Mobile\s*Number:?\s*([^\n]*)',
        'first_priority': r'FIRST\s*PRIORITY\s*Full\s*name:?\s*([^\n]*)',
        'second_priority': r'SECOND\s*PRIORITY\s*Full\s*name:?\s*([^\n]*)',
        'third_priority': r'THIRD\s*PRIORITY\s*Full\s*name:?\s*([^\n]*)',
    }

    # Extract and process main name
    main_name_match = re.search(patterns['full_name'], text, re.IGNORECASE)
    if main_name_match:
        name_components = extract_name_components(main_name_match.group(1))
        data.update(name_components)

    # Process address
    address_match = re.search(patterns['permanent_address'], text, re.IGNORECASE)
    if address_match:
        address = address_match.group(1).strip()
        # Split address into components
        address_parts = address.split(',')
        data['address_line_1'] = address_parts[0].strip()
        if len(address_parts) > 1:
            data['address_line_2'] = address_parts[1].strip()
        if len(address_parts) > 2:
            data['city'] = address_parts[2].strip()
        if len(address_parts) > 3:
            data['province_or_state'] = address_parts[3].strip()

    # Extract email
    email_match = re.search(patterns['email'], text, re.IGNORECASE)
    if email_match:
        data['email_address'] = email_match.group(1).strip().lower()

    # Extract phone numbers
    landline_match = re.search(patterns['landline'], text, re.IGNORECASE)
    if landline_match:
        data['landline_number'] = ''.join(filter(str.isdigit, landline_match.group(1)))

    mobile_match = re.search(patterns['mobile'], text, re.IGNORECASE)
    if mobile_match:
        mobile = mobile_match.group(1)
        # Handle multiple mobile numbers
        numbers = mobile.split('or')
        data['mobile_number'] = ''.join(filter(str.isdigit, numbers[0]))

    # Process beneficiaries
    for priority in ['first_priority', 'second_priority', 'third_priority']:
        match = re.search(patterns[priority], text, re.IGNORECASE)
        if match:
            beneficiary_name = match.group(1).strip()
            if priority == 'first_priority':
                data['first_beneficiary_name'] = beneficiary_name
            elif priority == 'second_priority':
                data['second_beneficiary_name'] = beneficiary_name
            elif priority == 'third_priority':
                data['third_beneficiary_name'] = beneficiary_name

    return data

@csrf_exempt
def process_ocr(request):
    if request.method == 'POST' and request.FILES.get('document'):
        try:
            image = request.FILES['document']
            extracted_text = extract_text_openai(image)

            return JsonResponse({'success': True, 'extracted_text': extracted_text})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def extract_text_openai(image):
    """
    Extract text using OpenAI's OCR API.
    """
    response = openai.images.create_variation(
        image=image.read(),
        model="gpt-4-vision-preview"
    )
    return response.data['text']  # Extract text from response

def extract_text(image):
    """
    Extract text from image using pytesseract
    """
    img = Image.open(image).convert('L')  # Convert to grayscale
    text = pytesseract.image_to_string(img)
    return text

def parse_extracted_text(text):
    """
    Parse extracted text into structured form fields.
    Modify this function to fit your document structure.
    """
    structured_data = {
        "first_name": "",
        "middle_name": "",
        "last_name": "",
        "suffix": "",
        "country": "Philippines",
        "address_line_1": "",
        "address_line_2": "",
        "city": "",
        "province_or_state": "",
        "postal_code": "",
        "landline_number": "",
        "mobile_number": "",
        "email_address": "",
        "first_beneficiary_name": "",
        "second_beneficiary_name": "",
        "third_beneficiary_name": "",
        "vault_id": "",
        "inurnment_date": "",
        "urns_per_columbary": ""
    }

    lines = text.split("\n")
    for line in lines:
        if "First Name" in line:
            structured_data["first_name"] = line.split(":")[1].strip()
        elif "Middle Name" in line:
            structured_data["middle_name"] = line.split(":")[1].strip()
        elif "Last Name" in line:
            structured_data["last_name"] = line.split(":")[1].strip()
        elif "Suffix" in line:
            structured_data["suffix"] = line.split(":")[1].strip()
        elif "City" in line:
            structured_data["city"] = line.split(":")[1].strip()
        elif "Province" in line:
            structured_data["province_or_state"] = line.split(":")[1].strip()
        elif "Postal Code" in line:
            structured_data["postal_code"] = line.split(":")[1].strip()
        elif "Landline" in line:
            structured_data["landline_number"] = line.split(":")[1].strip()
        elif "Mobile" in line:
            structured_data["mobile_number"] = line.split(":")[1].strip()
        elif "Email" in line:
            structured_data["email_address"] = line.split(":")[1].strip()
        elif "Vault ID" in line:
            structured_data["vault_id"] = line.split(":")[1].strip()
        elif "Inurnment Date" in line:
            structured_data["inurnment_date"] = line.split(":")[1].strip()

    return structured_data

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

#chatbot env
env = environ.Env(
    DEBUG=(bool, False) #default value for DEBUG = False
)
        
openai.api_key = env("OPEN_AI_API_KEY")
class ChatbotAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Chatbot API is running! Use POST to send messages."}, status=status.HTTP_200_OK)
    
    def get_relevant_info(self, query):
        """
        Retrieves relevant data from the database using full-text search.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT content FROM parish_knowledge "
                "WHERE MATCH(content) AGAINST (%s IN NATURAL LANGUAGE MODE) "
                "LIMIT 3;", [query]
            )
            results = cursor.fetchall()
        if results:
            return " ".join([row[0] for row in results]) if results else ""
        return "I'm not sure about that. Please check with the parish office or refer to the official guidelines."
        
    def post(self, request, *args, **kwargs):
        database_data  = get_data_from_db()
        ai_response = self.query_openai(database_data)
        user_query = request.data.get("message", "")
        context_data = self.get_relevant_info(self.query_openai)
        logger.info(f"User query: {user_query}")
        
        messages = [
            {"role": "system", "content": "You are a knowledgeable assistant helping parish staff."},
            {"role": "assistant", "content": f"Relevant Data from Database: {database_data}"},
            {"role": "user", "content": f"{user_query}"},  # Include user query in OpenAI request
        ]
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
           )

        return JsonResponse({
            "query": user_query,  
            "context": context_data,  
            "ai_insights": ai_response,
            "response": response.choices[0].message.content  
        })
   # def chatbot_view(request):
       # """Handle AJAX request and return chatbot response."""
       # db_data = get_data_from_db()
        #ai_response = query_openai(db_data)
      #  return JsonResponse({"response": ai_response})
    
    def query_openai(self, data):
        try:
            formatted_data = json.dumps(data, indent=2)
        except (TypeError, ValueError) as e:
            return f"Error formatting data: {str(e)}"

        prompt = (
            "You are an AI assistant analyzing parish data. "
            "Here is the structured database information:\n\n"
            f"{formatted_data}\n\n"
            "Please provide insights, trends, and any important observations."
        )

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an AI assistant."},
                    {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content


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

#def get_data_from_db():
#    data = Customer.objects.all().values()  # Fetch all fields
#    return list(data)
def get_data_from_db():
    """Fetch relevant data from the database, excluding the 'customer' table."""
    from django.db import connection

    data = {}

    try:
        with connection.cursor() as cursor:
            # List of tables to query (EXCLUDE 'customer' TABLE)
            tables = ["parish_knowledge", "parish_staff", "pages_account", "pages_customer", "pages_beneficiary"]  # Add only safe tables

            for table in tables:
                try:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 10;")
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    data[table] = [dict(zip(columns, row)) for row in rows]
                except Exception as e:
                    print(f"Skipping {table}: {e}")  # Avoid crashing on missing tables

    except Exception as e:
        print(f"Database error: {e}")

    return data  # Returns a dictionary of database contents

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

def get_vault_data(request, section_id):
    vaults = ColumbaryRecord.objects.filter(section=section_id)
    levels = {vault.level: vault.status == "Occupied" for vault in vaults}
    
    response_data = {'levels': levels}
    print(json.dumps(response_data, indent=4))  # Debugging output
    
    return JsonResponse(response_data)


def addnewcustomer(request):
    vault_id = request.GET.get('vault_id')
    vault = None

    if vault_id:
        vault = get_object_or_404(ColumbaryRecord, vault_id=vault_id, customer__isnull=True)

    if request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        payment_form = PaymentForm(request.POST)
        holder_form = HolderOfPrivilegeForm(request.POST)
        beneficiary_form = BeneficiaryForm(request.POST)

        if customer_form.is_valid():
            customer = customer_form.save()
            
            # Save payment only if valid
            payment = None
            if payment_form.is_valid():
                payment = payment_form.save(commit=False)
                payment.customer = customer
                payment.save()
            
            # Save holder of privilege only if valid
            holder = None
            if holder_form.is_valid():
                holder = holder_form.save(commit=False)
                holder.customer = customer
                holder.save()
            
            # Save beneficiary only if valid
            beneficiary = None
            if beneficiary_form.is_valid():
                beneficiary = beneficiary_form.save(commit=False)
                beneficiary.customer = customer
                beneficiary.save()

            if vault:
                # Link the new customer and associated records to the existing vault
                vault.customer = customer
                vault.payment = payment if payment else None
                vault.holder_of_privilege = holder if holder else None
                vault.beneficiary = beneficiary if beneficiary else None
                vault.save()
            else:
                # Create a new ColumbaryRecord
                columbary_record = ColumbaryRecord(
                    vault_id=vault_id,
                    customer=customer,
                    payment=payment if payment else None,
                    holder_of_privilege=holder if holder else None,
                    beneficiary=beneficiary if beneficiary else None,
                    status='Occupied'
                )
                columbary_record.save()

            return redirect('success')  # Redirect to success page

    else:
        customer_form = CustomerForm()
        payment_form = PaymentForm()
        holder_form = HolderOfPrivilegeForm()
        beneficiary_form = BeneficiaryForm()

    return render(request, 'pages/addcustomer.html', {
        'customer_form': customer_form,
        'payment_form': payment_form,
        'holder_form': holder_form,
        'beneficiary_form': beneficiary_form,
        'vault_id': vault_id
    })


