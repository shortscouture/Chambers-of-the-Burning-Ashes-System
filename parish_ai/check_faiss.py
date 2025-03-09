from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from django.conf import settings
import environ
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent # always need lagyan tatlong parent kasi nasa base.py tayo


# Initialize env variablesparent
env = environ.Env(
    DEBUG=(bool, False) 
)

# Load environment variables
OPEN_AI_API_KEY = env("OPEN_AI_API_KEY")

# Load embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPEN_AI_API_KEY)

# Load FAISS index
index_path = os.path.join(os.path.dirname(__file__), "faiss_index")
try:
    vector_db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    print("FAISS index loaded successfully.")
except Exception as e:
    print(f"Error loading FAISS index: {e}")
    exit()

# Test a query
query = "test"  # Change this to any relevant query
docs = vector_db.similarity_search(query, k=3)

if docs:
    print("FAISS returned the following results:")
    for i, doc in enumerate(docs, 1):
        print(f"{i}. {doc.page_content}")
else:
    print("No relevant documents found in FAISS.")
