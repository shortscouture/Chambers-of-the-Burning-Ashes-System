from django.views.generic import TemplateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
from .forms import CustomerForm, ColumbaryRecordForm, BeneficiaryForm, EmailVerificationForm, PaymentForm, HolderOfPrivilegeForm
from .models import Customer, ColumbaryRecord, Beneficiary, TwoFactorAuth,Customer, Payment, HolderOfPrivilege
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
from django.views.generic.base import TemplateView
import json
import environ
from django.db.models.functions import TruncMonth
import logging
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from .models import ColumbaryRecord
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
import boto3
from django.db.models import Sum, F, Value, DecimalField
from django.db.models.functions import Coalesce

env = environ.Env()
textract_client = boto3.client("textract", region_name="us-east-1")

logger = logging.getLogger(__name__)
AWS_S3_BUCKET_NAME = env("AWS_S3_BUCKET_NAME")
AWS_REGION = env("AWS_REGION")
s3_client = boto3.client("s3")

try:
    print(f"Testing AWS S3 connection to bucket: {AWS_S3_BUCKET_NAME}")
    response = s3_client.list_objects_v2(Bucket=AWS_S3_BUCKET_NAME, MaxKeys=1)
    print(f"S3 connection successful. Found {response.get('KeyCount', 0)} objects")
except Exception as e:
    print(f"AWS S3 connection error: {str(e)}")
    logger.error(f"AWS S3 connection error: {e}")


class SuccesView(TemplateView):
    template_name = "success.html"

class MapView(TemplateView):
    template_name = "Columbary_Map.html"

class HomePageView(TemplateView):
    template_name = "pages/home.html"



class AboutPageView(TemplateView):
    template_name = "pages/about.html"


    
class MainDashView(TemplateView):
    template_name = "pages/maindash.html"


class CustomerHomeView(TemplateView):
    template_name = "pages/Customer_Home.html"



from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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

        try:
            paginated_records = paginator.page(page)
        except PageNotAnInteger:
            paginated_records = paginator.page(1)  # Show first page if invalid
        except EmptyPage:
            paginated_records = paginator.page(paginator.num_pages)  # Show last page if out of range

        # Add to context
        context["records_data"] = paginated_records
        context["search_query"] = search_query  # Keep search input filled
        context["selected_filters"] = selected_filters  # Keep selected filters
        context["is_paginated"] = paginator.num_pages > 1  # Flag for pagination
        return context








class MemorialView(TemplateView):
    template_name = "pages/Memorials.html"


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        request = self.request

        # Fetch necessary data
        customer_status_counts = Customer.objects.values('status').annotate(count=Count('status'))
        pending_counts = Customer.objects.filter(status="pending").count()
        vacant_columbaries_count = ColumbaryRecord.objects.filter(status="Vacant").count()
        occupied_columbaries_count = ColumbaryRecord.objects.filter(status="Occupied").count()
        full_payment_count = Payment.objects.filter(mode_of_payment="Full Payment").count()
        installment_count = Payment.objects.filter(mode_of_payment="6-Month Installment").count()
        
        customer = None
        if request.user.is_authenticated:
            customer = Customer.objects.filter(email_address=request.user.email).first()

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
            .annotate(total_earnings=Sum("payment__Full_payment_amount_1") + 
                    Sum("payment__six_month_amount_1") +
                    Sum("payment__six_month_amount_2") +
                    Sum("payment__six_month_amount_3") +
                    Sum("payment__six_month_amount_4") +
                    Sum("payment__six_month_amount_5") +
                    Sum("payment__six_month_amount_6"))
            .order_by("holder_of_privilege__issuance_date")
        )

        # Get filter parameters from the request
        request = self.request
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            start_date = None
            end_date = None

        # Always include **unissued** columbaries (no filtering on them)
        unissued_columbaries = ColumbaryRecord.objects.filter(
            holder_of_privilege__issuance_date__isnull=True, 
            customer__isnull=False
        )

        # Always include **pending** customers
        pending_customers = Customer.objects.filter(status="pending")

        # Fetch all columbaries without filtering first
        all_columbaries = ColumbaryRecord.objects.all()

        # Apply filtering **only to columbaries with issuance dates**  
        if start_date and end_date:
            filtered_columbaries = all_columbaries.filter(holder_of_privilege__issuance_date__range=[start_date, end_date])
        else:
            filtered_columbaries = all_columbaries  # No filter if no date selected

        # Separate vacant and occupied columbaries
        vacant_columbaries = filtered_columbaries.filter(status="Vacant")
        occupied_columbaries = filtered_columbaries.filter(status="Occupied")
        
        context["occupied_columbaries"] = [
            {
                "vault_id": record.vault_id,
                "inurnment_date": record.inurnment_date,
                "expiration_date": record.expiration_date,  # Add calculated expiration date
            }
            for record in occupied_columbaries
        ]

        # Count filtered columbaries
        vacant_columbaries_count = vacant_columbaries.count()
        occupied_columbaries_count = occupied_columbaries.count()

        # Get Payments & Apply Date Filter
        payments = Payment.objects.all()
        if start_date and end_date:
            payments = payments.filter(created_at__date__range=[start_date, end_date])

        # Earnings per month based on filtered payments
        earnings_by_month = (
            payments.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total_earnings=Sum("total_amount"))
            .order_by("month")
        )
        
        # Fetch Payment Records
        full_payment_records = Payment.objects.filter(mode_of_payment="Full Payment")
        # Retrieve installment payments and calculate total paid
        installment_payments = Payment.objects.filter(mode_of_payment="6-Month Installment").annotate(
            total_installment_paid=Coalesce(
                Sum(F("six_month_amount_1"), output_field=DecimalField()) +
                Sum(F("six_month_amount_2"), output_field=DecimalField()) +
                Sum(F("six_month_amount_3"), output_field=DecimalField()) +
                Sum(F("six_month_amount_4"), output_field=DecimalField()) +
                Sum(F("six_month_amount_5"), output_field=DecimalField()) +
                Sum(F("six_month_amount_6"), output_field=DecimalField()), 
                Value(0, output_field=DecimalField())  # Default to 0 if no payments
            )
        )

        # Count Payments
        full_payment_count = payments.filter(mode_of_payment="Full Payment").count()

        # Define completed and unpaid installment counts
        completed_installment_count = installment_payments.filter(total_installment_paid=F("total_amount")).count()
        unpaid_installment_count = installment_payments.exclude(total_installment_paid=F("total_amount")).count()

        # Convert data for Chart.js
        earnings_labels = [entry["month"].strftime("%b %Y") if entry["month"] else "Unknown" for entry in earnings_by_month]
        earnings_data = [float(entry["total_earnings"]) if entry["total_earnings"] else 0 for entry in earnings_by_month]

        payment_labels = ["Full Payment", "Completed Installment", "Unpaid Installment"]
        payment_data = [full_payment_count, completed_installment_count, unpaid_installment_count]

        # Update context with ALL columbaries (ensures they are always passed)
        context.update({
            "vacant_columbaries": vacant_columbaries,  # ✅ Fix: Always pass available columbaries
            "occupied_columbaries": occupied_columbaries,  # ✅ Fix: Always pass occupied columbaries
            "vacant_columbaries_count": vacant_columbaries_count,
            "occupied_columbaries_count": occupied_columbaries_count,
            "unissued_columbaries": unissued_columbaries.count(),
            "pending_counts": pending_customers.count(),
            "unissued_columbary_records": unissued_columbaries,
            "pending_customers": pending_customers,
            "earnings_labels": mark_safe(json.dumps(earnings_labels)),
            "earnings_data": mark_safe(json.dumps(earnings_data)),
            "start_date": start_date.strftime("%Y-%m-%d") if start_date else "",
            "end_date": end_date.strftime("%Y-%m-%d") if end_date else "",
            "full_payment_records": full_payment_records,
            "payment_labels": mark_safe(json.dumps(payment_labels)),
            "payment_data": mark_safe(json.dumps(payment_data)),
            "completed_installment_records": installment_payments.filter(total_installment_paid=F("total_amount")),
            "unpaid_installment_records": installment_payments.exclude(total_installment_paid=F("total_amount")),
            "customer": customer if customer else "No associated customer",
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

    return redirect('success.html')


from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from .models import Customer, ColumbaryRecord, HolderOfPrivilege, Beneficiary, Payment, CustomerFile
from .forms import CustomerFileForm

class RecordsDetailsView(TemplateView):
    template_name = "pages/recordsdetails.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer_id = self.kwargs.get("customer_id")

        customer = get_object_or_404(Customer, customer_id=customer_id)
        
        context["customer"] = customer
        context["columbary_records"] = ColumbaryRecord.objects.filter(customer=customer)
        context["holderofprivilege"] = HolderOfPrivilege.objects.filter(customer=customer)
        context["beneficiaries"] = Beneficiary.objects.filter(customer=customer)
        context["payments"] = Payment.objects.filter(customer=customer)
        context["files"] = CustomerFile.objects.filter(customer=customer)
        context["file_form"] = CustomerFileForm()

        return context

    def post(self, request, *args, **kwargs):
        customer_id = self.kwargs.get("customer_id")
        customer = get_object_or_404(Customer, customer_id=customer_id)

        file_form = CustomerFileForm(request.POST, request.FILES)
        if file_form.is_valid():
            file_instance = file_form.save(commit=False)
            file_instance.customer = customer
            file_instance.save()
            return redirect("recordsdetails", customer_id=customer.customer_id)

        return self.get(request, *args, **kwargs)



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
def upload_to_s3_and_extract_text(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=env("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=env("AWS_SECRET_ACCESS_KEY"),
        )
        bucket_name = env("AWS_S3_BUCKET_NAME")
        file_name = uploaded_file.name
        
        
        s3_client.upload_fileobj(uploaded_file, bucket_name, file_name)
        
        
        textract_client = boto3.client(
            "textract",
            aws_access_key_id=env("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=env("AWS_SECRET_ACCESS_KEY"),
        )
        response = textract_client.detect_document_text(
            Document={"S3Object": {"Bucket": bucket_name, "Name": file_name}}
        )
        
        
        extracted_text = "".join([block["Text"] for block in response.get("Blocks", []) if block["BlockType"] == "LINE"])
        
        return JsonResponse({"text": extracted_text})
    
    return render(request, "upload.html")

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

    return render(request, 'pages/Memorials.html')

def success(request):
    return render(request, 'pages/success.html')

@csrf_exempt
def upload_and_process(request):
    if request.method == "POST" and request.FILES.get("document"):
        uploaded_file = request.FILES["document"]
        s3_client = boto3.client("s3")
        bucket_name = env("AWS_S3_BUCKET_NAME")
        file_key = f"uploads/{uploaded_file.name}"
        
        s3_client.upload_fileobj(uploaded_file, bucket_name, file_key)
        
        textract_client = boto3.client("textract")
        response = textract_client.analyze_document(
            Document={"S3Object": {"Bucket": bucket_name, "Name": file_key}},
            FeatureTypes=["FORMS", "TABLES"]  # Add TABLES feature type
        )

        extracted_data = {}
        
        # Process key-value pairs (forms)
        for block in response.get("Blocks", []):
            if block["BlockType"] == "KEY_VALUE_SET" and "KEY" in block.get("EntityTypes", []):
                key_text = ""
                value_text = ""
                for rel in block.get("Relationships", []):
                    if rel["Type"] == "CHILD":
                        key_text = " ".join([w["Text"] for w in response["Blocks"] if w["Id"] in rel["Ids"]])
                    if rel["Type"] == "VALUE":
                        for value_block in response["Blocks"]:
                            if value_block["Id"] in rel["Ids"]:
                                for value_rel in value_block.get("Relationships", []):
                                    if value_rel["Type"] == "CHILD":
                                        value_text = " ".join([w["Text"] for w in response["Blocks"] if w["Id"] in value_rel["Ids"]])
                if key_text and value_text:
                    extracted_data[key_text] = value_text
        

        beneficiaries = extract_beneficiaries_from_tables(response.get("Blocks", []))
        if beneficiaries:
            extracted_data["BENEFICIARIES"] = beneficiaries
        
        return JsonResponse({"success": True, "data": extracted_data})

    return JsonResponse({"success": False, "error": "Invalid request"})

def extract_beneficiaries_from_tables(blocks):
    """Extract beneficiaries from tables in the document."""

    tables = [block for block in blocks if block["BlockType"] == "TABLE"]
    

    beneficiaries_table = None
    for table in tables:

        table_bbox = table["Geometry"]["BoundingBox"]
        nearby_texts = [
            block for block in blocks 
            if block["BlockType"] == "LINE" 
            and is_nearby(block["Geometry"]["BoundingBox"], table_bbox)
            and "BENEFICIARIES" in block.get("Text", "").upper()
        ]
        
        if nearby_texts:
            beneficiaries_table = table
            break
    
    if not beneficiaries_table:
        return None
    

    table_cells = {}
    for block in blocks:
        if (block["BlockType"] == "CELL" and 
            "Relationships" in block and
            any(rel["Type"] == "CHILD_OF" and beneficiaries_table["Id"] in rel["Ids"] 
                for rel in block.get("Relationships", []))):
            
            row_index = block.get("RowIndex", 0)
            col_index = block.get("ColumnIndex", 0)
            
            if row_index not in table_cells:
                table_cells[row_index] = {}
            

            cell_text = ""
            for rel in block.get("Relationships", []):
                if rel["Type"] == "CHILD":
                    words = [b for b in blocks if b["Id"] in rel["Ids"] and b["BlockType"] == "WORD"]
                    cell_text = " ".join(word["Text"] for word in words)
            
            table_cells[row_index][col_index] = cell_text
    

    beneficiary_names = []
    for row_index in sorted(table_cells.keys()):
        if row_index > 1 and 1 in table_cells[row_index]: 
            beneficiary_names.append(table_cells[row_index][1])
    
    return beneficiary_names

def is_nearby(bbox1, bbox2):
    """Check if two bounding boxes are near each other."""

    vertical_distance = min(
        abs(bbox1["Top"] - bbox2["Top"]),
        abs(bbox1["Top"] + bbox1["Height"] - bbox2["Top"]),
        abs(bbox1["Top"] - bbox2["Top"] - bbox2["Height"])
    )
    

    return vertical_distance < 0.1

def parse_text_to_dict(text):
    """
    Parse extracted text into a structured dictionary.
    """
    if not text:
        logger.error("OCR extracted text is empty.")
        return {"error": "No text extracted"}
    
    data = {
        "first_name": None,
        "middle_name": None,
        "last_name": None,
        "suffix": None,
        "country": "Philippines",
        "address_line_1": None,
        "address_line_2": None,
        "city": None,
        "province_or_state": None,
        "postal_code": None,
        "landline_number": None,
        "mobile_number": None,
        "email_address": None,
        "first_beneficiary_name": None,
        "second_beneficiary_name": None,
        "third_beneficiary_name": None,
        "vault_id": None,
        "inurnment_date": None,
        "urns_per_columbary": None
    }
    
    
    full_name_match = re.search(r"Full\s*name:\s*([^\n]*)", text, re.IGNORECASE)
    if full_name_match:
        full_name = full_name_match.group(1).strip()
        name_parts = full_name.split()
        if len(name_parts) >= 2:
            data["first_name"] = name_parts[0]
            data["last_name"] = name_parts[-1]
            if len(name_parts) > 2:
                if name_parts[-1].upper() in ["SR", "JR", "II", "III", "IV"]:
                    data["suffix"] = name_parts[-1]
                    data["last_name"] = name_parts[-2]
                    if len(name_parts) > 3:
                        data["middle_name"] = " ".join(name_parts[1:-2])
                else:
                    data["middle_name"] = " ".join(name_parts[1:-1])
    
    
    address_match = re.search(r"Address:\s*([^\n]*)", text, re.IGNORECASE)
    if address_match:
        address = address_match.group(1).strip()
        
        
        postal_code_match = re.search(r"(\d{4,})", address)
        if postal_code_match:
            data["postal_code"] = postal_code_match.group(1)
        
        address_parts = address.split(',')
        if len(address_parts) >= 1:
            data["address_line_1"] = address_parts[0].strip()
        if len(address_parts) >= 2:
            data["city"] = address_parts[-2].strip()
        if len(address_parts) >= 3:
            data["province_or_state"] = address_parts[-1].strip()
    
    
    landline_match = re.search(r"Landline\s*Number:?\s*([0-9()\s\-+]*)", text, re.IGNORECASE)
    if landline_match:
        data["landline_number"] = landline_match.group(1).strip()
    
    mobile_match = re.search(r"Mobile\s*Number:?\s*([0-9()\s\-+]*)", text, re.IGNORECASE)
    if mobile_match:
        data["mobile_number"] = mobile_match.group(1).strip()
    
    
    email_match = re.search(r"Email\s*Address:?\s*([^\s\n]*@[^\s\n]*)", text, re.IGNORECASE)
    if email_match:
        data["email_address"] = email_match.group(1).strip()
    
    
    beneficiary_match = re.search(r"Beneficiary\s*Name:?\s*([^\n]*)", text, re.IGNORECASE)
    if beneficiary_match:
        data["first_beneficiary_name"] = beneficiary_match.group(1).strip()
    
    
    vault_match = re.search(r"Vault\s*ID:?\s*([^\n\s]*)", text, re.IGNORECASE)
    if vault_match:
        data["vault_id"] = vault_match.group(1).strip()
    
    # Extract inurnment date if present
    date_match = re.search(r"Inurnment\s*Date:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text, re.IGNORECASE)
    if date_match:
        data["inurnment_date"] = date_match.group(1).strip()
    
    return data



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
        columbary_form = ColumbaryRecordForm(request.POST, instance=vault)  # ✅ Load existing vault record

        if customer_form.is_valid() and columbary_form.is_valid():
            customer = customer_form.save()

            
            payment = None
            if payment_form.is_valid():
                payment = payment_form.save(commit=False)
                payment.customer = customer
                payment.save()

            
            holder = None
            if holder_form.is_valid():
                holder = holder_form.save(commit=False)
                holder.customer = customer
                holder.save()

            
            beneficiary = None
            if beneficiary_form.is_valid():
                beneficiary = beneficiary_form.save(commit=False)
                beneficiary.customer = customer
                beneficiary.save()

            if vault:
                
                vault.customer = customer
                vault.payment = payment if payment else None
                vault.holder_of_privilege = holder if holder else None
                vault.beneficiary = beneficiary if beneficiary else None

                
                vault.inurnment_date = columbary_form.cleaned_data.get("inurnment_date")
                vault.urns_per_columbary = columbary_form.cleaned_data.get("urns_per_columbary")
                vault.status = 'Occupied'
                
                vault.save()

            return redirect('columbaryrecords')  

    else:
        customer_form = CustomerForm()
        payment_form = PaymentForm()
        holder_form = HolderOfPrivilegeForm()
        beneficiary_form = BeneficiaryForm()
        columbary_form = ColumbaryRecordForm(instance=vault)  

    return render(request, 'pages/addcustomer.html', {
        'customer_form': customer_form,
        'payment_form': payment_form,
        'holder_form': holder_form,
        'beneficiary_form': beneficiary_form,
        'columbary_form': columbary_form,  
        'vault_id': vault_id
    })

@csrf_exempt  # Only use if CSRF token isn't included in the form
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        subject = f"New Contact Form Submission from {name}"
        body = f"Name: {name}\nEmail: {email}\nMessage:\n{message}"

        email_message = EmailMessage(subject, body, 'stalphonsusmakati@gmail.com', ['jamesnaldo376@gmail.com'])
        email_message.send()

        return JsonResponse({'success': True, 'message': 'Email sent successfully'})

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)



