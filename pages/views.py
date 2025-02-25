from django.views.generic import TemplateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404,  HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, EmailMessage
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

#chatbot env
env = environ.Env(
    DEBUG=(bool, False) #default value for DEBUG = False
)
        
openai.api_key = env("OPEN_AI_API_KEY")
logger = logging.getLogger(__name__)
class ChatbotAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Chatbot API is running! Use POST to send messages."}, status=200)

    
    def post(self, request, *args, **kwargs):
        user_query = request.data.get("message", "").strip()
        if not user_query:
            return JsonResponse({"error": "No query provided"}, status=400)

        db_answer = self.get_answer_from_parish_knowledge(user_query)

        ai_response = self.query_openai(user_query, db_answer)
        
        # Save the chat history into pages_chatquery
        self.save_chat_history(user_query, ai_response)


        return JsonResponse({
            "query": user_query,
            "response": ai_response,
        })


    def get_answer_from_parish_knowledge(self, query):
        """Uses FULLTEXT search to find the best matching answer in parish_knowledge."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT answer, MATCH(question) AGAINST (%s IN NATURAL LANGUAGE MODE) AS relevance 
                FROM parish_knowledge 
                WHERE MATCH(question) AGAINST (%s IN NATURAL LANGUAGE MODE) 
                ORDER BY relevance DESC LIMIT 1;
                """, [query, query])
            result = cursor.fetchone()
            return result[0] if result else None


    def get_all_knowledge(self):
        """Retrieves all questions and answers from parish_knowledge for AI context."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT question, answer FROM parish_knowledge;")
            rows = cursor.fetchall()
        return [{"question": q, "answer": a} for q, a in rows]



    def query_openai(self, user_query, db_answer=None, past_conversations=None):
        """Uses OpenAI while incorporating database knowledge."""
        try:
            # Construct the AI prompt to guide behavior
            system_prompt = (
                "You are a helpful chatbot for church visitors. "
                "If there is relevant information from the church database, use it, "
                "Only answer questions about the columbarium, and if they answer things such as baptism or wedding, or funeral services, direct them to the contact information, it's found in the parish_questions database"
                "but if the user gives you specific instructions on how to respond, follow them."
                "direct them to the church's contact information."
            )

            # Prepare messages with context  
            messages = [{"role": "system", "content": system_prompt}]

            if past_conversations:
                for convo in past_conversations:
                    messages.append({"role": "user", "content": convo["query"]})
                    messages.append({"role": "assistant", "content": convo["response"]})

            if db_answer:
                messages.append({"role": "assistant", "content": f"Database says: {db_answer}"})

                messages.append({"role": "user", "content": user_query})

                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7
                )

                if response and response.choices:
                    return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")

        return "I'm not sure how to answer that. Please contact the St. Alphonsus Mary de Liguori Parish for further assistance."


    def save_unanswered_query(self, query):
        """Logs unanswered queries to pages_chatquery."""
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO pages_chatquery (query, created_at) VALUES (%s, NOW());", [query])

    
    def get_related_parish_knowledge(self, query):
        """Finds questions in parish_knowledge that contain keywords from the user's query."""
        search_query = f"%{query}%"
        with connection.cursor() as cursor:
            cursor.execute("SELECT question, answer FROM parish_knowledge WHERE question LIKE %s LIMIT 5;", [search_query])
            return cursor.fetchall()  # Returns a list of (question, answer) tuples

    def get_past_conversations(self, limit=5):
        """Retrieve the last few conversations from pages_chatquery for context"""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_message, bot_response FROM pages_chatquery ORDER BY created_at DESC LIMIT %s;",
                [limit]
            )
            past_chats = cursor.fetchall()

        return [{"query": chat[0], "response": chat[1]} for chat in past_chats]
    
    def save_chat_history(self, user_query, bot_response):
        """Logs chat messages to pages_chatquery."""
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO pages_chatquery (user_message, bot_response, created_at) VALUES (%s, %s, NOW(6));",
                [user_query, bot_response]
            )



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

@csrf_exempt  # Only use if CSRF token isn't included in the form
def send_email(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        subject = f"New Contact Form Submission from {name}"
        body = f"Name: {name}\nEmail: {email}\nMessage:\n{message}"

        email_message = EmailMessage(subject, body, 'jamesnaldo376@gmail.com', ['recipient_email@gmail.com'])
        email_message.send()

        return JsonResponse({'success': True, 'message': 'Email sent successfully'})

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
