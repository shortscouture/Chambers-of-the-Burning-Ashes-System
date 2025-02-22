from django.urls import path
from .views import chatbotAPIView

urlpatterns = [
    path('parish_staff/', chatbotAPIView.as_view(), name='chatbot'),
]