from django.shortcuts import render
import openai
import environ
from .models import ChatQuery
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

env = environ.Env(
    DEBUG=(bool, False) #default value for DEBUG = False
)


openai.api_key = env("OPEN_AI_API_KEY")


class ChatbotAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Chatbot API is running! Use POST to send messages."}, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        user_message = request.data.get('message')

        if not user_message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # Using GPT-3.5 models
                messages=[{"role": "user", "content": user_message}],
                max_tokens=150
            )
            bot_reply = response.choices[0].message.content.strip()  # Get the response from GPT-3.5
            #save to database
            ChatQuery.objects.create(user_message=user_message, bot_response=bot_reply)

            return Response({'response': bot_reply}, status=status.HTTP_200_OK)


        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        