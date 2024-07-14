import os
import ast
import psycopg2
import psycopg2.extras
from psycopg2 import sql
import ollama
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Tuple
from tqdm import tqdm
from colorama import Fore, init
import traceback
import emoji

# Initialize colorama
init(autoreset=True)

# Database configuration
DB_PARAMS = {
    "dbname": "langchain",
    "user": "langchain",
    "password": "langchain",
    "host": "localhost",
    "port": "6024"
}

# Embedding configuration
EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_SIZE = 768  # Adjust based on the model's output

# Chat model configuration
CHAT_MODEL = "llama3"

def connect_db():
    try:
        return psycopg2.connect(**DB_PARAMS)
    except psycopg2.Error as e:
        print(f"Unable to connect to the database: {e}")
        return None

def initialize_db():
    conn = connect_db()
    if not conn:
        print("Failed to connect to the database.")
        return
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    metadata JSONB,
                    embedding vector({EMBEDDING_SIZE})
                )
            """)
        conn.commit()
        print("Database initialized successfully.")
    except psycopg2.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def update_db_schema():
    conn = connect_db()
    if not conn:
        print("Failed to connect to the database.")
        return
    try:
        with conn.cursor() as cur:
            # Drop the existing table
            cur.execute("DROP TABLE IF EXISTS documents")
            
            # Recreate the table with the new embedding size
            cur.execute(f"""
                CREATE TABLE documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    metadata JSONB,
                    embedding vector({EMBEDDING_SIZE})
                )
            """)
        conn.commit()
        print("Database schema updated successfully.")
    except psycopg2.Error as e:
        print(f"Error updating database schema: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_embedding(text: str or List[str]) -> List[float] or List[List[float]]:
    try:
        if isinstance(text, str):
            response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)
            return response['embedding']
        elif isinstance(text, list):
            response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)
            return [item['embedding'] for item in response['embeddings']]
        else:
            raise ValueError("Input must be a string or a list of strings")
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return [] if isinstance(text, str) else [[] for _ in text]

def store_document(content: str, metadata: dict):
    conn = connect_db()
    if not conn:
        return
    try:
        embedding = get_embedding(content)
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("INSERT INTO documents (content, metadata, embedding) VALUES (%s, %s, %s)"),
                (content, psycopg2.extras.Json(metadata), embedding)
            )
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error storing document: {e}")
        conn.rollback()
    finally:
        conn.close()

def retrieve_similar_documents(query: str, limit: int = 5) -> List[Tuple[str, float]]:
    conn = connect_db()
    if not conn:
        return []
    try:
        query_embedding = get_embedding(query)
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("""
                    SELECT content, 1 - (embedding <=> %s) AS similarity
                    FROM documents
                    ORDER BY similarity DESC
                    LIMIT %s
                """),
                (query_embedding, limit)
            )
            return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error retrieving similar documents: {e}")
        return []
    finally:
        conn.close()

def process_document(file_path: str):
    print(f"Debug: Starting to process document: {file_path}")
    
    file_path = file_path.strip().strip("\"'")
    file_path = os.path.expanduser(os.path.expandvars(file_path))
    file_path = file_path.replace("\\", "")
    
    print(f"Debug: Processed file path: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File does not exist at path: {file_path}")
        return
    
    try:
        print(f"Debug: Attempting to determine file type and load document")
        _, file_extension = os.path.splitext(file_path)
        print(f"Debug: File extension: {file_extension}")
        
        if file_extension.lower() == '.md':
            print("Debug: Loading markdown file")
            loader = UnstructuredMarkdownLoader(file_path)
        elif file_extension.lower() == '.pdf':
            print("Debug: Loading PDF file")
            loader = PyPDFLoader(file_path)
        else:
            print("Debug: Loading text file")
            loader = TextLoader(file_path, encoding='utf-8')
        
        print("Debug: About to load documents")
        documents = loader.load()
        print(f"Debug: Successfully loaded file: {file_path}")
        print(f"Debug: Number of documents: {len(documents)}")
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        
        print(f"Debug: Split content into {len(chunks)} chunks")
        
        successful_chunks = 0
        for i, chunk in enumerate(chunks):
            try:
                store_document(chunk.page_content, {"source": file_path, "chunk_index": i})
                successful_chunks += 1
            except Exception as e:
                print(f"Error storing chunk {i}: {e}")
        
        print(f"Processed file: {file_path}. Successfully stored {successful_chunks} out of {len(chunks)} chunks.")
        print(emoji.emojize(":star:"))
    except Exception as e:
        print(f"Error processing file: {e}")
        print(f"Debug: Exception type: {type(e)}")
        print(f"Stack trace: {traceback.format_exc()}")

def forget_document(file_path: str):
    conn = connect_db()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("DELETE FROM documents WHERE metadata->>'source' = %s"),
                (file_path,)
            )
        conn.commit()
        print(colorize_output(f"Document '{file_path}' has been removed from the database.", "yellow"))
    except psycopg2.Error as e:
        print(f"Error removing document: {e}")
        conn.rollback()
    finally:
        conn.close()

def list_documents():
    conn = connect_db()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("SELECT DISTINCT metadata->>'source' FROM documents")
            )
            documents = [doc[0] for doc in cur.fetchall()]
        return documents
        print(colorize_output("Stored documents:", "yellow"))
        for doc in documents:
            print(colorize_output(f"- {doc[0]}", "white"))
    except psycopg2.Error as e:
        print(f"Error listing documents: {e}")
        return []
    finally:
        conn.close()

def create_queries(prompt):
    query_message = "Generate a list of search queries to find relevant context for the following prompt. Return only a Python list of strings."
    query_convo = [
        {"role": "system", "content": query_message},
        {"role": "user", "content": "What's the capital of France?"},
        {"role": "assistant", "content": "['capital of France', 'French cities', 'Paris facts']"},
        {"role": "user", "content": prompt}
    ]
    
    response = ollama.chat(model=CHAT_MODEL, messages=query_convo)
    print("Generating queries...")
    print(response['message']['content'])
    
    try:
        return ast.literal_eval(response['message']['content'])
    except:
        return [prompt]

def retrieve_similar_documents(query: str or List[str], limit: int = 5) -> List[Tuple[str, float]]:
    conn = connect_db()
    if not conn:
        return []
    try:
        query_embedding = get_embedding(query)
        if not query_embedding:
            return []
        
        if isinstance(query_embedding[0], list):
            # If we got multiple embeddings, use the first one
            query_embedding = query_embedding[0]
        
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("""
                    SELECT content, 1 - (embedding <=> %s::vector) AS similarity
                    FROM documents
                    ORDER BY similarity DESC
                    LIMIT %s
                """),
                (query_embedding, limit)
            )
            return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error retrieving similar documents: {e}")
        return []
    finally:
        conn.close()

def classify_embedding(query: str, context: str) -> str:
    classify_message = "Determine if the given context is directly related to the query. Respond with only 'yes' or 'no'."
    classify_convo = [
        {"role": "system", "content": classify_message},
        {"role": "user", "content": f"Query: {query}\nContext: {context}"}
    ]
    
    response = ollama.chat(model=CHAT_MODEL, messages=classify_convo)
    return response['message']['content'].strip().lower()

def recall(prompt: str) -> List[dict]:
    queries = create_queries(prompt)
    embeddings = []
    for query in queries:
        similar_docs = retrieve_similar_documents(query)
        embeddings.extend(similar_docs)
    
    relevant_embeddings = [
        embedding for embedding in embeddings
        if classify_embedding(prompt, embedding[0]) == "yes"
    ]
    
    context = [{"role": "system", "content": f"Relevant context (similarity {sim:.2f}):\n{content}"} for content, sim in relevant_embeddings]
    print(f"Added {len(context)} relevant contexts.")
    return context

def search_documents(query: str):
    similar_docs = retrieve_similar_documents(query)
    print(colorize_output("\nRelevant documents:", "yellow"))
    for doc, similarity in similar_docs:
        print(colorize_output(f"Similarity: {similarity:.2f}", "white"))
        print(doc[:200] + "..." if len(doc) > 200 else doc)
        print()

def colorize_output(text, color):
    color_map = {
        "green": Fore.LIGHTGREEN_EX,
        "yellow": Fore.YELLOW,
        "white": Fore.WHITE
    }
    return f"{color_map[color]}{text}"

def stream_response(prompt: str, context: List[dict]):
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant. If provided with context, use it to answer questions accurately. If no context is provided, answer to the best of your ability based on your training."},
    ] + context + [
        {"role": "user", "content": prompt}
    ]
    
    print(colorize_output("Assistant: ", "yellow"), end="", flush=True)
    response = ""
    for chunk in ollama.chat(model=CHAT_MODEL, messages=messages, stream=True):
        content = chunk['message']['content']
        response += content
        print(colorize_output(content, "green"), end="", flush=True)
    
    print("\n")
    return response

def main():
    initialize_db()
    # Call this function before processing any documents
    update_db_schema()
    
    print(colorize_output("Welcome to the Local RAG AI Agent!", "yellow"))
    print(colorize_output("Commands:", "yellow"))
    print(colorize_output("- 'exit' to quit", "white"))
    print(colorize_output("- 'process' to add a document", "white"))
    print(colorize_output("- 'forget' to remove a document", "white"))
    print(colorize_output("- 'list' to show all stored documents", "white"))
    print(colorize_output("- 'search' to find relevant documents", "white"))
    print(colorize_output("- Or simply ask a question", "white"))
    
    while True:
        user_input = input(colorize_output("You: ", "white"))
        
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'process':
            file_path = input(colorize_output("Enter the path to the document: ", "white"))
            process_document(file_path)
        elif user_input.lower() == 'forget':
            file_path = input(colorize_output("Enter the path of the document to forget: ", "white"))
            forget_document(file_path)
        elif user_input.lower() == 'list':
            list_documents()
        elif user_input.lower() == 'search':
            query = input(colorize_output("Enter your search query: ", "white"))
            search_documents(query)
        else:
            context = recall(user_input)
            response = stream_response(user_input, context)

if __name__ == "__main__":
    main()