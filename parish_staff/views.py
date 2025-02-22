from django.shortcuts import render
import openai
import environ
from .models import ChatLog
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions


env = environ.Env(
    DEBUG=(bool, False) #default value for DEBUG = False
)


openai.api_key = env("OPEN_AI_API_KEY")

class isParishStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.CustomUser.is_authenticated and request.CustomUser.role == "parish_staff"

class chatbotAPIView(APIView):
    
    permission_classes = [isParishStaff]
    
    def get(self, request, *args, **kwargs):
        return Response({"message": "Chatbot API is running! Use POST to send messages."}, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        user_message = request.data.get('message')

        if not user_message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        return self.process_message(user_message)
    
    def process_message(self, request, user_message):
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  
                messages=[{"role": "user", "content": user_message}],
                max_tokens=150
            )
            bot_reply = response.choices[0].message.content.strip()  
            #save to database
            ChatLog.objects.create(
                user=request.CustomUser, #saves user if logged in 
                message=user_message, 
                bot_response=bot_reply)

            return Response({'response': bot_reply}, status=status.HTTP_200_OK)


        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def parish_chatbot_history(self, request):
        if not request.CustomUser.is_authenticated:
            return Response({'error': 'Authentication REQUIRED.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        chats = ChatLog.objects.filter(user=request.CustomUser).order_by("-timestamp")[:10]
        
        chat_history = [
            {"message": chat.message, "response": chat.response, "timestamp": chat.timestamp}
            for chat in chats
        ]
        
        return Response({"history": chat_history}, status=status.HTTP_200_OK)