from sqlalchemy.orm import Session
from sqlalchemy import text
from parish_ai.database import SessionLocal
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import os
import environ
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    try:
        rows = session.execute(text("SELECT question, answer FROM parish_knowledge")).fetchall()
    except Exception as e:
        logging.error(f"Error fetching data from parish_knowledge: {e}")
        session.close()
        return
    session.close()

    if not rows:
        logging.warning("No data found in parish_knowledge table. Skipping FAISS index generation.")
        return

    documents = [f"Q: {row[0]}\nA: {row[1]}" for row in rows]

    # Example of document chunking (if necessary)
    # If the answer is too long, you might want to split it.
    # This is just a placeholder, you'll need to adapt it to your specific needs.
    # chunked_documents = []
    # for doc in documents:
    #     if len(doc) > 500: # Example chunk length
    #         chunks = [doc[i:i + 500] for i in range(0, len(doc), 500)]
    #         chunked_documents.extend(chunks)
    #     else:
    #         chunked_documents.append(doc)

    try:
        vector_db = FAISS.from_texts(documents, embeddings)
        vector_db.save_local(index_path)
        logging.info(f"FAISS index successfully generated at {index_path}.")
    except Exception as e:
        logging.error(f"Error generating FAISS index: {e}")
        return

    logging.info(f"Fetched {len(rows)} rows from parish_knowledge.")

if __name__ == "__main__":
    generate_faiss_index()