from django.urls import path
from .views import chatbotAPIView

urlpatterns = [
    path('chatbot/', chatbotAPIView.as_view(), name='chatbot'),
]