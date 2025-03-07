from django.http import JsonResponse
from django.views import View
from sqlalchemy.orm import sessionmaker
from .models import ParishKnowledge, ChatQuery  # Import ORM models
from .database import engine  # Ensure you have an SQLAlchemy engine setup

# Create a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class ChatbotAPIView(View):
    def get_answer(self, question_text):
        """Retrieve an answer from the parish_knowledge table."""
        session = SessionLocal()
        result = session.query(ParishKnowledge).filter_by(question=question_text).first()
        session.close()
        return result.answer if result else "Sorry, I don't have an answer for that."

    def store_chat_query(self, user_query):
        """Store user queries in the chat_query table."""
        session = SessionLocal()
        new_query = ChatQuery(chat_query=user_query)
        session.add(new_query)
        session.commit()
        session.close()

    def post(self, request):
        """Handle chatbot interactions via POST requests."""
        data = request.POST
        user_query = data.get("query")

        # Store user query
        self.store_chat_query(user_query)

        # Get AI response
        answer = self.get_answer(user_query)

        return JsonResponse({"question": user_query, "answer": answer})
