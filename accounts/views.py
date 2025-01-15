from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from .forms import SignUpForm

class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"
    
#update view i love djangox everything's so much easier
def signupView(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') #adjust to login url as well
    else:
        form = SignUpForm()
        
    return render(request, 'registration/signup.html', {'form': form})
        