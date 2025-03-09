from sqlalchemy.orm import Session
from sqlalchemy import text
from django.conf import settings
from .database import SessionLocal
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import os
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent # always need lagyan tatlong parent kasi nasa base.py tayo


# Initialize env variablesparent
env = environ.Env(
    DEBUG=(bool, False) 
)

# Load environment variables
OPEN_AI_API_KEY = env("OPEN_AI_API_KEY")

# Initialize embeddings
embeddings = OpenAIEmbeddings(openai_api_key=settings.OPEN_AI_API_KEY)

def generate_faiss_index():
    session = SessionLocal()
    rows = session.execute(text("SELECT question, answer FROM parish_knowledge")).fetchall()
    session.close()

    if not rows:
        print("No data found in parish_knowledge table.")
        return

    documents = [f"Q: {row[0]}\nA: {row[1]}" for row in rows]
    vector_db = FAISS.from_texts(documents, embeddings, allow_dangerous_deserialization=True)
    
    index_path = "faiss_index"
    if not os.path.exists(index_path):
        os.makedirs(index_path)
    
    vector_db.save_local(index_path)
    print("FAISS index successfully generated.")

if __name__ == "__main__":
    generate_faiss_index()
