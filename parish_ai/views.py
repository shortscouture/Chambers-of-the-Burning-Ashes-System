from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .chatbot import chatbot

class ChatbotAPIView(APIView):
    def post(self, request):
        user_query = request.data.get("query", "")

        if not user_query:
            return Response({"error": "Query cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        # Run the chatbot workflow
        result = chatbot.invoke({"query": user_query})

        return Response(result["response"], status=status.HTTP_200_OK)