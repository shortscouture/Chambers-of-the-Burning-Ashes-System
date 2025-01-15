from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView  # Import ListView
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomerForm
from django.core.mail import send_mail
from django.conf import settings


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

class memorialview(TemplateView):
    template_name = "pages/Memorials.html"


def send_letter_of_intent(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        permanent_address = request.POST['permanent_address']
        landline_number = request.POST.get('landline_number', '')
        mobile_number = request.POST['mobile_number']
        email_address = request.POST['email_address']

        # Save the form data with a pending status
        intent = CustomerForm.objects.create(
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

        return redirect('pages/Success.html')  # Redirect after submission

    return render(request, 'pages/Customer_Home.html')

def accept_letter_of_intent(request, intent_id):
    intent = get_object_or_404(CustomerForm, id=intent_id)
    intent.status = 'approved'
    intent.save()
    return render(request, 'pages/accept_success.html')

def decline_letter_of_intent(request, intent_id):
    intent = get_object_or_404(CustomerForm, id=intent_id)
    intent.status = 'declined'
    intent.save()
    return render(request, 'pages/decline_success.html')
