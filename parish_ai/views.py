from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
from rest_framework.views import APIView
from langchain.chat_models import ChatOpenAI
from langchain.chains import SQLDatabaseChain
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.sql_database import SQLDatabase
from langchain.graphs import StateGraph
from pydantic import BaseModel

# Initialize SQLAlchemy Database
from sqlalchemy import create_engine
engine = create_engine(settings.DATABASE_URL)
db = SQLDatabase(engine)

class ChatbotAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "Chatbot API is running! Use POST to send messages."}, status=200)

    def post(self, request, *args, **kwargs):
        user_query = request.data.get("message", "").strip()
        if not user_query:
            return JsonResponse({"error": "No query provided"}, status=400)

        # Load chat history from session
        past_conversations = request.session.get("chat_history", [])
        chatbot = self.create_chatbot_workflow()
        
        result = chatbot.invoke({
            "user_query": user_query,
            "past_conversations": past_conversations
        })

        # Update session history
        past_conversations.append({"query": user_query, "response": result.final_response})
        request.session["chat_history"] = past_conversations[-5:]

        # Save chat history in DB
        self.save_chat_history(user_query, result.final_response)

        return JsonResponse({"query": user_query, "response": result.final_response})

    def sql_agent(self, state):
        """Executes SQL query using LangChain SQLDatabaseChain."""
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        sql_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
        sql_result = sql_chain.run(state.user_query)
        state.sql_result = sql_result
        return state

    def rag_retriever(self, state):
        """Retrieves relevant documents using FAISS vector search."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT answer FROM parish_knowledge")
            docs = [row[0] for row in cursor.fetchall()]
        
        vectorstore = FAISS.from_texts(docs, OpenAIEmbeddings())
        retriever = vectorstore.as_retriever()
        results = retriever.get_relevant_documents(state.user_query)
        
        state.rag_result = results[0].page_content if results else "No relevant data found."
        return state

    def generate_response(self, state):
        """Generates a chatbot response using OpenAI and context."""
        system_prompt = (
            "You are a chatbot for church visitors, specializing in columbarium policies.\n"
            "Rules:\n"
            "- Use database answers when available.\n"
            "- Do NOT answer baptism, funeral, or wedding-related queries.\n"
            "- Be professional and concise.\n"
        )

        messages = [{"role": "system", "content": system_prompt}]
        
        for convo in state.past_conversations:
            messages.append({"role": "user", "content": convo["query"]})
            messages.append({"role": "assistant", "content": convo["response"]})

        if state.sql_result:
            messages.append({"role": "assistant", "content": f"Database answer: {state.sql_result}"})

        if state.rag_result:
            messages.append({"role": "assistant", "content": f"Knowledge Base: {state.rag_result}"})

        messages.append({"role": "user", "content": state.user_query})

        response = ChatOpenAI(model="gpt-4").predict_messages(messages)
        state.final_response = response.content
        return state

    def create_chatbot_workflow(self):
        """Creates a structured LangGraph workflow for SQL + RAG chatbot responses."""
        class ChatState(BaseModel):
            user_query: str
            sql_result: str = ""
            rag_result: str = ""
            past_conversations: list = []
            final_response: str = ""

        workflow = StateGraph(ChatState)
        workflow.add_node("SQL Query", self.sql_agent)
        workflow.add_node("RAG Retrieval", self.rag_retriever)
        workflow.add_node("AI Response", self.generate_response)

        workflow.set_entry_point("SQL Query")
        workflow.add_edge("SQL Query", "RAG Retrieval")
        workflow.add_edge("RAG Retrieval", "AI Response")

        return workflow.compile()

    def save_chat_history(self, user_query, bot_response):
        """Logs chat history into pages_chatquery."""
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO pages_chatquery (user_message, bot_response, created_at) VALUES (%s, %s, NOW(6));",
                [user_query, bot_response]
            )

