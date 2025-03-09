from sqlalchemy.orm import Session
from django.conf import settings
from .database import SessionLocal
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import os

# Initialize embeddings
embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

def generate_faiss_index():
    session = SessionLocal()
    rows = session.execute("SELECT question, answer FROM parish_knowledge").fetchall()
    session.close()

    if not rows:
        print("No data found in parish_knowledge table.")
        return

    documents = [f"Q: {row[0]}\nA: {row[1]}" for row in rows]
    vector_db = FAISS.from_texts(documents, embeddings)
    
    index_path = "faiss_index"
    if not os.path.exists(index_path):
        os.makedirs(index_path)
    
    vector_db.save_local(index_path)
    print("FAISS index successfully generated.")

if __name__ == "__main__":
    generate_faiss_index()
