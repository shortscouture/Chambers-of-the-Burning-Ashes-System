import os
from django.core.management.base import BaseCommand
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from django.conf import settings
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent # always need lagyan tatlong parent kasi nasa base.py tayo


# Initialize env variablesparent
env = environ.Env(
    DEBUG=(bool, False) #default value for DEBUG = False
)

# Load environment variables
OPEN_AI_API_KEY = env("OPEN_AI_API_KEY")

class Command(BaseCommand):
    help = "Generate FAISS index for chatbot RAG"

    def handle(self, *args, **kwargs):
        openai_api_key = settings.OPEN_AI_API_KEY
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        
        # Example: List of documents to index
        documents = [
            "Parish mass schedule information.",
            "How to contact the parish office?",
            "Details about parish events and activities."
        ]

        # Create FAISS index
        vector_db = FAISS.from_texts(documents, embeddings)
        index_path = "faiss_index"
        
        if not os.path.exists(index_path):
            os.makedirs(index_path)

        vector_db.save_local(index_path)
        self.stdout.write(self.style.SUCCESS("FAISS index generated successfully."))
