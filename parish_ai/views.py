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

        # Extract "answer" directly and clean up quotes
        bot_response = result.get("response", {}).get("answer", "No response from bot")
        clean_response = bot_response.strip("'\"")  # Remove unnecessary quotes

        return Response({"response": clean_response}, status=status.HTTP_200_OK)