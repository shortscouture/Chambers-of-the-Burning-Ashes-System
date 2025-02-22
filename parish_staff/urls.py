from django.urls import path
from .views import ChatbotAPIView

urlpatterns = [
    path('parish_staff/', ChatbotAPIView.as_view(), name='chatbot'),
]