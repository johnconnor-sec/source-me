import psycopg2
from psycopg2 import sql
from config import DB_PARAMS, EMBEDDING_SIZE
import time

def wait_for_db(max_retries=5, delay=5):
    retries = 0
    while retries < max_retries:
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            conn.close()
            print("Successfully connected to the database.")
            return True
        except psycopg2.OperationalError:
            retries += 1
            print(f"Database not ready. Retrying in {delay} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(delay)
    print("Failed to connect to the database after maximum retries.")
    return False

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
                
            print("Checking if 'feedback' table exists...")
            cur.execute("SELECT to_regclass('public.feedback')")
            if cur.fetchone()[0] is None:
                print("Creating 'feedback' table...")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS feedback (
                        id SERIAL PRIMARY KEY,
                        query TEXT,
                        document_id INTEGER REFERENCES documents(id),
                        is_relevant BOOLEAN,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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