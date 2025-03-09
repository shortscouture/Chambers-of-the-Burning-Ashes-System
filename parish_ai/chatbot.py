import os
from dotenv import load_dotenv
from langgraph.graph import END, MessageGraph
from langchain_openai import OpenAIEmbeddings
from langchain.schema import HumanMessage
from langgraph.graph import Graph
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from sqlalchemy.orm import Session
from django.conf import settings
from .database import SessionLocal
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent # always need lagyan tatlong parent kasi nasa base.py tayo


# Initialize env variablesparent
env = environ.Env(
    DEBUG=(bool, False) 
)

# Load environment variables
OPEN_AI_API_KEY = env("OPEN_AI_API_KEY")



llm = ChatOpenAI(model="gpt-4", temperature=0.5, openai_api_key=OPEN_AI_API_KEY)
embeddings = OpenAIEmbeddings(openai_api_key=OPEN_AI_API_KEY)


index_path = "faiss_index"
if not os.path.exists(index_path):
    from .generate_faiss import generate_faiss_index
    generate_faiss_index()
vector_db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)

# Create LangGraph Workflow
workflow = Graph()

def retrieve_context(state: dict):
    user_query = state["query"]
    docs = vector_db.similarity_search(user_query, k=3)
    context = "\n".join([doc.page_content for doc in docs])
    return {"query": user_query, "context": context}

def check_relevance(state: dict):
    user_query = state["query"]
    context = state["context"]
    relevance_prompt = f"Given the following context:\n{context}\nDoes this question relate to parish information? Respond with 'yes' or 'no': {user_query}"
    
    response = llm.invoke([HumanMessage(content=relevance_prompt)]).content.lower()
    
    if "yes" in response:
        return {"relevant": True, "query": user_query, "context": context}
    return {"relevant": False}

def convert_to_sql(state: dict):
    user_query = state["query"]
    sql_prompt = f"Convert this user question into a valid MySQL query that searches the parish_knowledge table: {user_query}"
    
    sql_query = llm.invoke([HumanMessage(content=sql_prompt)]).content
    return {"sql_query": sql_query, "attempts": 1}

def execute_sql(state: dict):
    session = SessionLocal()
    sql_query = state["sql_query"]
    
    try:
        result = session.execute(sql_query).fetchone()
        session.close()
        if result:
            return {"sql_result": result[0]}
        return {"sql_result": None}
    except:
        return {"sql_result": None}

def handle_sql_retries(state: dict):
    if state["attempts"] >= 5:
        return {"response": {"answer": "I'm unable to find relevant information. Please contact the parish for more details.", "source": "None"}}
    
    new_sql = convert_to_sql({"query": state["query"]})
    return {"sql_query": new_sql["sql_query"], "attempts": state["attempts"] + 1}

def generate_response(state: dict):
    if state["sql_result"]:
        response_prompt = f"Format this database result in a polite and informative response: {state['sql_result']}"
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


