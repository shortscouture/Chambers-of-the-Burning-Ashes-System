from sqlalchemy.orm import Session
from sqlalchemy import text
from django.conf import settings
from parish_ai.database import SessionLocal
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import os
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # Adjust if needed

# Initialize environment variables
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, ".env"))  # Ensure the .env file is loaded

OPEN_AI_API_KEY = env("OPEN_AI_API_KEY")

index_path = os.path.join(BASE_DIR, "parish_ai", "faiss_index")

# Ensure FAISS directory exists
if not os.path.exists(index_path):
    os.makedirs(index_path)

# Initialize embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPEN_AI_API_KEY)

def generate_faiss_index():
    session = SessionLocal()
    rows = session.execute(text("SELECT question, answer FROM parish_knowledge")).fetchall()
    session.close()

    if not rows:
        print("⚠️ No data found in parish_knowledge table. Skipping FAISS index generation.")
        return

    documents = [f"Q: {row[0]}\nA: {row[1]}" for row in rows]
    vector_db = FAISS.from_texts(documents, embeddings)
    vector_db.save_local(index_path)

    print(f"✅ FAISS index successfully generated at {index_path}.")
    rows = session.execute(text("SELECT question, answer FROM parish_knowledge")).fetchall()
    print(f"Fetched {len(rows)} rows from parish_knowledge.")

if __name__ == "__main__":
    generate_faiss_index()

