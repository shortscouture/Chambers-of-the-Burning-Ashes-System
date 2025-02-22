from django.urls import path
from .views import chatbotAPIView, chatbot_view

urlpatterns = [
    path('chatbot/api', chatbotAPIView.as_view(), name='chatbot_api'),
    path("chatbot/", chatbot_view, name="chatbot")
]