import os
import json
from dotenv import load_dotenv
from langgraph.graph import END, MessageGraph
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import HumanMessage
from langgraph.graph import Graph
from langchain.vectorstores import FAISS
from sqlalchemy.orm import Session
from django.conf import settings
from .database import SessionLocal
import environ
from pathlib import Path
from sqlalchemy.sql import text



BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent # always need lagyan tatlong parent kasi nasa base.py tayo


# Initialize env variablesparent
env = environ.Env(
    DEBUG=(bool, False) 
)

# Load environment variables
OPEN_AI_API_KEY = env("OPEN_AI_API_KEY")



llm = ChatOpenAI(model="gpt-4", temperature=0.5, openai_api_key=OPEN_AI_API_KEY)
embeddings = OpenAIEmbeddings(openai_api_key=OPEN_AI_API_KEY)


index_path = os.path.join(os.path.dirname(__file__), "faiss_index")

print(f"🟢 Checking FAISS index path: {index_path}")
print(f"🟢 Files in directory: {os.listdir(index_path) if os.path.exists(index_path) else 'Not Found'}")

try:
    if os.path.exists(index_path):
        vector_db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        if vector_db is None:
            print("❌ FAISS failed to load. vector_db is None.")
        else:
            print("✅ FAISS loaded successfully!")
    else:
        print("⚠️ FAISS index not found. Running generate_faiss.py...")
        from parish_ai.generate_faiss import generate_faiss_index
        generate_faiss_index()
        
        if os.path.exists(index_path):
            vector_db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
            print("✅ FAISS successfully regenerated and loaded!")
        else:
            print("❌ FAISS index generation failed. vector_db is None.")
            vector_db = None
except Exception as e:
    print(f"❌ FAISS loading error: {e}")
    vector_db = None

# Create LangGraph Workflow
workflow = Graph()

def retrieve_context(state):
    query = state.get("query")
    if not query:
        print("❌ Missing 'query' in state.")
        return {"answer": "Error: No query provided.", "source": "None"}
    
    retrieved_docs = vector_db.similarity_search_with_score(query, k=5)
    documents = []
    
    for doc_tuple in retrieved_docs:
        if isinstance(doc_tuple, tuple) and len(doc_tuple) == 2:
            document, score = doc_tuple
        elif isinstance(doc_tuple, tuple) and len(doc_tuple) > 2:
            document, score = doc_tuple[:2]  # Adjust for extra values
        else:
            print("❌ Unexpected FAISS return format:", doc_tuple)
            continue
        
        documents.append(document.page_content)

    context = "\n".join(documents) if documents else "No relevant documents found."

    return {"query": query, "context": context}

def check_relevance(state: dict):
    print(f"🟢 Received state: {state}")

    # Ensure 'query' exists
    user_query = state.get("query")
    if not user_query:
        print("❌ Error: 'query' not found in state.")
        return {"answer": "Error: No query provided.", "source": "None"}

    print(f"🔍 Checking relevance for: {user_query}")
    context = state.get("context", "")

    # Structured prompt to avoid ambiguous responses
    relevance_prompt = f"""
    Given the following context:
    {context}

    Determine if the user's query relates to parish information.
    Reply strictly in JSON format:
    {{"relevant": true}} 
    or 
    {{"relevant": false}}

    User query: {user_query}
    """

    # Call LLM and parse JSON response
    response = llm.invoke([HumanMessage(content=relevance_prompt)]).content.strip()
    print(f"🔍 LLM relevance response: {response}")

    try:
        relevance_json = json.loads(response)
        is_relevant = relevance_json.get("relevant", False)
    except json.JSONDecodeError:
        print("❌ LLM response was not in JSON format:", response)
        is_relevant = False

    if is_relevant:
        return {"relevant": True, "query": user_query, "context": context}
    
    return {"relevant": False}

def convert_to_sql(state: dict):
    user_query = state["query"]
    sql_prompt = f"Convert this user question into a valid MySQL query that searches the parish_knowledge table: {user_query}"
    
    sql_query = llm.invoke([HumanMessage(content=sql_prompt)]).content
    
    print("DEBUG: Generated SQL query ->", sql_query)
    return {"sql_query": sql_query, "attempts": 1}

def execute_sql(state):
    query_data = state.get("query")
    
    if not isinstance(query_data, dict) or "query" not in query_data:
        return {"sql_result": None, "error": "Invalid query format."}

    query = query_data["query"]  # Extract SQL query

    if not isinstance(query, str):
        return {"sql_result": None, "error": "Query must be a string."}

    query = query.lower().strip()

    if not query.startswith("select"):  # Ensure only SELECT queries
        return {"sql_result": None, "error": "Invalid SQL query. Only SELECT queries are allowed."}

    try:
        result = db.session.execute(text(query)).fetchall()
        return {"sql_result": result}  # Ensure key exists
    except Exception as e:
        return {"sql_result": None, "error": f"SQL Execution Error: {str(e)}"}

def handle_sql_retries(state: dict):
    print("DEBUG: Received state ->", state)
    if state["attempts"] >= 5:
        return {"sql_result": None,  # Ensure key exists
                "response": {"answer": "I'm unable to find relevant information. Please contact the parish for more details.",
                             "source": "None"}}

    new_sql = convert_to_sql({"query": state["query"]})
    
    return {"sql_query": new_sql["sql_query"], 
            "attempts": state["attempts"] + 1,
            "sql_result": None}  # Ensure key is always present
    
def generate_response(state: dict):
    sql_result = state.get("sql_result")  # Use .get() to avoid KeyError

    if sql_result:  # Only process if sql_result is valid
        response_prompt = f"Format this database result in a polite and informative response: {sql_result}"
        human_response = llm.invoke([HumanMessage(content=response_prompt)]).content
        return {"response": {"answer": human_response, "source": "parish_knowledge database"}}

    return {"response": {"answer": "I'm unable to find relevant information. Please contact the parish for more details.", "source": "None"}}

# Define Nodes
workflow.add_node("retrieve_context", retrieve_context)
workflow.add_node("check_relevance", check_relevance)
workflow.add_node("convert_to_sql", convert_to_sql)
workflow.add_node("execute_sql", execute_sql)
workflow.add_node("handle_sql_retries", handle_sql_retries)
workflow.add_node("generate_response", generate_response)

# Define Edges
workflow.set_entry_point("retrieve_context")
workflow.add_edge("retrieve_context", "check_relevance")
workflow.add_conditional_edges(
    "check_relevance",
    lambda state: "convert_to_sql" if state["relevant"] else "generate_response"
)
workflow.add_edge("convert_to_sql", "execute_sql")
workflow.add_conditional_edges(
    "execute_sql",
    lambda state: "generate_response" if state["sql_result"] else "handle_sql_retries"
)
workflow.add_edge("handle_sql_retries", "execute_sql")
workflow.add_edge("generate_response", END)

# Compile Workflow
chatbot = workflow.compile()


