from typing import List, Tuple
from psycopg2 import sql
from database.connection import connect_db
from embedding.embed import get_embedding
from utils.output import colorize_output
from sentence_transformers import CrossEncoder

def rerank_documents(query: str, documents: List[Tuple[str, float]], top_k: int = 3) -> List[Tuple[str, float]]:
    cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    pairs = [(query, doc[0]) for doc in documents]
    scores = cross_encoder.predict(pairs)
    reranked = list(zip([doc[0] for doc in documents], scores))
    return sorted(reranked, key=lambda x: x[1], reverse=True)[:top_k]

def retrieve_similar_documents(query: str, limit: int = 10) -> List[Tuple[str, float]]:
    conn = connect_db()
    if not conn:
        return []
    try:
        query_embedding = get_embedding(query)
        if not query_embedding:
            return []
        
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
            initial_results = cur.fetchall()
        
        # Rerank the results
        reranked_results = rerank_documents(query, initial_results, top_k=3)
        
        return reranked_results
    except Exception as e:
        print(f"Error retrieving similar documents: {e}")
        return []
    finally:
        conn.close()

def search_documents(query: str):
    similar_docs = retrieve_similar_documents(query)
    print(colorize_output("\nRelevant documents:", "yellow"))
    for doc, similarity in similar_docs:
        print(colorize_output(f"Similarity: {similarity:.2f}", "white"))
        print(doc[:200] + "..." if len(doc) > 200 else doc)
        print()
    return similar_docs  # Return the results for further processing