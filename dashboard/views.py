from django.shortcuts import render
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .models import Customer, ColumbaryRecord, Payment, InquiryRecord, ParishAdministrator, ParishStaff

def dashboard(request):
    # Customer Status Analytics
    customer_status_counts = Customer.objects.values('status').annotate(count=Count('status'))
    
    # Columbary Record Analytics
    columbary_records = ColumbaryRecord.objects.all()
    columbary_status_counts = columbary_records.values('urns_per_columbary').annotate(count=Count('urns_per_columbary'))
    
    # Payment Analytics
    payment_counts = Payment.objects.aggregate(
        full_contribution=Count('full_contribution', filter=Q(full_contribution=True)),
        six_month_installment=Count('six_month_installment', filter=Q(six_month_installment=True))
    )
    
    # Inquiry Record Analytics
    inquiry_counts = InquiryRecord.objects.count()
    
    # Parish Staff and Admin Counts
    parish_admin_count = ParishAdministrator.objects.count()
    parish_staff_count = ParishStaff.objects.count()
    
    context = {
        'customer_status_counts': list(customer_status_counts),
        'columbary_status_counts': list(columbary_status_counts),
        'payment_counts': payment_counts,
        'inquiry_counts': inquiry_counts,
        'parish_admin_count': parish_admin_count,
        'parish_staff_count': parish_staff_count,
    }
    
    return render(request, 'dashboard/dashboard.html', context)