from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .chatbot import chatbot

class ChatbotAPIView(APIView):
    def post(self, request):
        user_query = request.data.get("query", "")

        if not user_query:
            return Response({"error": "Query cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        result = chatbot.invoke({"query": user_query})

        # Extract "answer" directly instead of nesting it inside "response"
        bot_response = result.get("response", {})
        return Response({"response": bot_response.get("answer", "No response from bot")}, status=status.HTTP_200_OK)