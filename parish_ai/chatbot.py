import os
import json
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import HumanMessage
from langgraph.graph import Graph, END
from langchain.vectorstores import FAISS
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
import environ
from pathlib import Path

# Initialize environment variables
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
env = environ.Env(DEBUG=(bool, False))
OPEN_AI_API_KEY = env("OPEN_AI_API_KEY")

# Initialize LLM and embeddings
llm = ChatOpenAI(model="gpt-4", temperature=0.5, openai_api_key=OPEN_AI_API_KEY)
embeddings = OpenAIEmbeddings(openai_api_key=OPEN_AI_API_KEY)

# Load FAISS index
index_path = os.path.join(os.path.dirname(__file__), "faiss_index")
print(f"🟢 Checking FAISS index path: {index_path}")
print(f"🟢 Files in directory: {os.listdir(index_path) if os.path.exists(index_path) else 'Not Found'}")

vector_db = None
try:
    if os.path.exists(index_path):
        vector_db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        if vector_db is None:
            print("❌ FAISS failed to load. vector_db is None.")
        else:
            print("✅ FAISS loaded successfully!")
    else:
        print("⚠️ FAISS index not found. Running generate_faiss.py...")
        from .generate_faiss import generate_faiss_index
        generate_faiss_index()
        if os.path.exists(index_path):
            vector_db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
            print("✅ FAISS successfully regenerated and loaded!")
        else:
            print("❌ FAISS index generation failed. vector_db is None.")
except Exception as e:
    print(f"❌ FAISS loading error: {e}")

# Database initialization
from .database import SessionLocal
db = SessionLocal()

# LangGraph Workflow
workflow = Graph()

def classify_intent(query):
    intent_prompt = f"Classify the intent of the following query: '{query}'. Respond with only the intent label (e.g., 'farewell', 'information', 'greeting')."
    intent = llm.invoke([HumanMessage(content=intent_prompt)]).content.strip().lower()
    print(f"DEBUG: Intent for '{query}' is '{intent}'")
    return intent

def retrieve_context(state):
    query = state.get("query")
    if not query:
        return {"answer": "Error: No query provided.", "source": "None"}

    if vector_db:
        retrieved_docs_with_scores = vector_db.similarity_search_with_score(query, k=1)
        if retrieved_docs_with_scores:
            document, score = retrieved_docs_with_scores[0]
            print(f"DEBUG: FAISS score for '{query}' is {score}")
            if score > 0.7:
                context = document.page_content
                print(f"DEBUG: FAISS context: {context}")
                return {"query": query, "context": context}
            else:
                return {"query": query, "context": ""}
        else:
            return {"query": query, "context": ""}
    else:
        return {"query": query, "context": "FAISS Index Not Loaded"}


def retrieve_context(state):
    query = state.get("query")
    if not query:
        return {"answer": "Error: No query provided.", "source": "None"}

    if vector_db:
        retrieved_docs_with_scores = vector_db.similarity_search_with_score(query, k=1)
        if retrieved_docs_with_scores:
            document, score = retrieved_docs_with_scores[0]
            print(f"DEBUG: FAISS score for '{query}' is {score}")
            print(f"DEBUG: FAISS document: {document.page_content}") #added print statement
            context = document.page_content
            print(f"DEBUG: FAISS context: {context}")
            return {"query": query, "context": context}
        else:
            return {"query": query, "context": ""}
    else:
        return {"query": query, "context": "FAISS Index Not Loaded"}

def check_relevance(state: dict):
    query = state.get("query")
    context = state.get("context", "")
    if not context:
        print("Debug: context was empty")
        return {"relevant": False, "query": query, "context": ""}

    relevance_prompt = f"""
    Given the following context: {context}
    Determine if the user's query relates to parish information.
    Reply strictly in JSON format: {{"relevant": true}} or {{"relevant": false}}
    User query: {query}
    Make sure you only get the answer from the parish_knowledge table when replying.
    Don't take the user questions literally. Instead, focus on the intent behind the question. Find the most relevant question if possible.
    """
    try:
        response = llm.invoke([HumanMessage(content=relevance_prompt)]).content.strip()
        relevance_json = json.loads(response)
        is_relevant = relevance_json.get("relevant", False)
        print(f"Debug: relevance was: {is_relevant}")
        return {"relevant": is_relevant, "query": query, "context": context}
    except Exception as e:
        print(f"Error checking relevance: {e}")
        return {"relevant": False, "query": query, "context": context}

def convert_to_sql(state: dict):
    user_query = state["query"]
    context = state.get("context", "")

    if context:
        sql_prompt = f"""
        Given the following question and answer pair: '{context}', generate a SQL query to retrieve the 'answer' from the 'parish_knowledge' table.
        The table has columns 'question' and 'answer'.
        Generate a sql query that would return the answer from the context.
        """
    else:
        sql_prompt = f"""
        Given the user question: '{user_query}', generate a SQL query to retrieve the 'answer' from the 'parish_knowledge' table.
        The table has columns 'question' and 'answer'.
        Find the 'answer' that best corresponds to the meaning of the user's question, even if the exact wording is different.
        Perform some level of fuzzy matching or semantic similarity to find the most relevant question in the database.
        Do not take the user questions literally. Instead, focus on the intent behind the question. Find the most relevant question if possible.
        
        Examples:
        User Question: 'Mass schedule?'
        SQL Query: SELECT answer FROM parish_knowledge WHERE question LIKE '%mass times%';

        User Question: 'Tell me about the columbary.'
        SQL Query: SELECT answer FROM parish_knowledge WHERE question LIKE '%columbary%';

        User Question: '{user_query}'
        SQL Query:
        If you cannot find a similar match, check the database and give them the parish contact information which is also located inside the parish_knowledge table.
        """
    sql_query = llm.invoke([HumanMessage(content=sql_prompt)]).content
    print("DEBUG: Generated SQL query ->", sql_query)
    return {"sql_query": sql_query, "attempts": 1, "query": state["query"]}

def execute_sql(state):
    query = state.get("sql_query")
    if not query:
        return {"sql_result": None, "error": "No SQL query provided.", "query": state.get("query")}

    query = query.lower().strip()
    if not query.startswith("select"):
        return {"sql_result": None, "error": "Invalid SQL query. Only SELECT queries are allowed.", "query": state.get("query")}

    try:
        result = db.execute(text(query)).fetchall()
        print(f"DEBUG: SQL query result: {result}") #added print statement
        return {"sql_result": result, "query": state.get("query")}
    except Exception as e:
        return {"sql_result": None, "error": f"SQL Execution Error: {str(e)}", "query": state.get("query")}

def handle_sql_retries(state: dict):
    print("DEBUG: Received state ->", state)
    if state["attempts"] >= 5:
        return {"sql_result": None,
                "response": {"answer": "I'm unable to find relevant information. Please contact the parish for more details.",
                             "source": "None"},
                "query": state.get("query")}

    new_sql = convert_to_sql({"query": state["query"]})
    return {"sql_query": new_sql["sql_query"],
            "attempts": state["attempts"] + 1,
            "sql_result": None,
            "query": state.get("query")}

def generate_response(state: dict):
    sql_result = state.get("sql_result")
    context = state.get("context", "")

    if sql_result:
        response_prompt = f"Format this database result in a polite and informative response: {sql_result}. Use this context to add more information: {context}. Do not include any salutations or closing remarks."
        human_response = llm.invoke([HumanMessage(content=response_prompt)]).content
        return {"response": {"answer": human_response, "source": "parish_knowledge database and FAISS"}}
    elif context:
        response_prompt = f"""
        Given the following context, which is a question and answer pair: '{context}'
        Extract and return only the answer from the context.
        """
        human_response = llm.invoke([HumanMessage(content=response_prompt)]).content
        return {"response": {"answer": human_response, "source": "FAISS"}}
    else:
        return {"response": {"answer": "I'm unable to find relevant information. Please contact the parish for more details.", "source": "None"}}
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
    lambda state: "generate_response" if state.get("sql_result") else "handle_sql_retries" if state.get("sql_result") is None and state.get("sql_query") is not None else "generate_response"
)
workflow.add_edge("handle_sql_retries", "execute_sql")
workflow.add_edge("generate_response", END)

# Compile Workflow
chatbot = workflow.compile()