import os
import psycopg2
import psycopg2.extras
from psycopg2 import sql
import ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from typing import List, Tuple
from tqdm import tqdm
from colorama import Fore, init

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
EMBEDDING_SIZE = 500  # Adjust based on the model's output

# Chat model configuration
CHAT_MODEL = "gemma2"

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
            cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            if cur.fetchone() is None:
                print("Creating 'vector' extension...")
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            print("Checking if 'documents' table exists...")
            cur.execute("SELECT to_regclass('public.documents')")
            if cur.fetchone()[0] is None:
                print("Creating 'documents' table...")
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS documents (
                        id SERIAL PRIMARY KEY,
                        content TEXT,
                        metadata JSONB,
                        embedding vector({EMBEDDING_SIZE})
                    )
                """)
            else:
                print("'documents' table already exists.")
        conn.commit()
        print("Database initialized successfully.")
    except psycopg2.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def get_embedding(text: str) -> List[float]:
    response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)
    return response['embedding']

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
    print(f"Attempting to process file: {file_path}")
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File does not exist at path: {file_path}")
        return
    
    # Check if it's a file (not a directory)
    if not os.path.isfile(file_path):
        print(f"Error: Path exists but is not a file: {file_path}")
        return
    
    # Check read permissions
    if not os.access(file_path, os.R_OK):
        print(f"Error: No read permissions for file: {file_path}")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        print(f"Successfully read file: {file_path}")
        print(f"File content length: {len(content)} characters")
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(content)
        
        print(f"Split content into {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            store_document(chunk, {"source": file_path, "chunk_index": i})
        
        print(f"Successfully processed and stored all chunks for file: {file_path}")
    
    except IOError as e:
        print(f"IOError while reading file: {e}")
    except Exception as e:
        print(f"Unexpected error while processing file: {e}")

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
            documents = cur.fetchall()
        print(colorize_output("Stored documents:", "yellow"))
        for doc in documents:
            print(colorize_output(f"- {doc[0]}", "white"))
    except psycopg2.Error as e:
        print(f"Error listing documents: {e}")
    finally:
        conn.close()

def colorize_output(text, color):
    color_map = {
        "green": Fore.LIGHTGREEN_EX,
        "yellow": Fore.YELLOW,
        "white": Fore.WHITE
    }
    return f"{color_map[color]}{text}"

def stream_response(prompt: str, context: List[Tuple[str, float]]):
    context_str = "\n".join([f"Context (similarity {sim:.2f}): {content}" for content, sim in context])
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant with access to relevant context. Use the provided context to answer questions accurately."},
        {"role": "system", "content": f"Relevant context:\n{context_str}"},
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
    
    print(colorize_output("Welcome to the Local RAG AI Agent!", "yellow"))
    print(colorize_output("Commands:", "yellow"))
    print(colorize_output("- 'exit' to quit", "white"))
    print(colorize_output("- 'process' to add a document", "white"))
    print(colorize_output("- 'forget' to remove a document", "white"))
    print(colorize_output("- 'list' to show all stored documents", "white"))
    print(colorize_output("- Or simply ask a question", "white"))
    
    while True:
        user_input = input(colorize_output("You: ", "white"))
        
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'process':
            file_path = input(colorize_output("Enter the path to the document: ", "white"))
            if os.path.exists(file_path):
                process_document(file_path)
                print(colorize_output("Document processed and stored.", "yellow"))
            else:
                print(colorize_output("File not found.", "yellow"))
        elif user_input.lower() == 'forget':
            file_path = input(colorize_output("Enter the path of the document to forget: ", "white"))
            forget_document(file_path)
        elif user_input.lower() == 'list':
            list_documents()
        else:
            similar_docs = retrieve_similar_documents(user_input)
            response = stream_response(user_input, similar_docs)

if __name__ == "__main__":
    main()