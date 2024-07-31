import psycopg2
from psycopg2 import sql
import psycopg2.extras
from database.connection import connect_db
from embedding.embed import get_embedding
from utils.output import colorize_output

def is_file_in_database(file_path: str) -> bool:
    conn = connect_db()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT EXISTS(SELECT 1 FROM documents WHERE metadata->>'source' = %s)",
                (file_path,)
            )
            return cur.fetchone()[0]
    except psycopg2.Error as e:
        print(f"Error checking if file exists in database: {e}")
        return False
    finally:
        conn.close()
        
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
        
def store_feedback(query: str, document_id: int, is_relevant: bool):
    conn = connect_db()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO feedback (query, document_id, is_relevant) VALUES (%s, %s, %s)",
                (query, document_id, is_relevant)
            )
        conn.commit()
        print("Feedback stored successfully.")
    except psycopg2.Error as e:
        print(f"Error storing feedback: {e}")
        conn.rollback()
    finally:
        conn.close()
        
