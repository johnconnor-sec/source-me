import ast
import ollama
from typing import List, Tuple
from config import CHAT_MODEL
from retrieval.similarity import retrieve_similar_documents
from utils.output import colorize_output

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
'''
def summarize_documents(documents: List[Tuple[str, float]]) -> str:
    summarize_message = "Summarize the following documents into a concise paragraph, preserving the key information:"
    doc_content = "\n\n".join([f"Document {i+1}:\n{doc[0]}" for i, doc in enumerate(documents)])
    
    summarize_convo = [
        {"role": "system", "content": summarize_message},
        {"role": "user", "content": doc_content}
    ]
    
    response = ollama.chat(model=CHAT_MODEL, messages=summarize_convo)
    return response['message']['content']
'''
def recall(prompt: str) -> List[dict]:
    queries = create_queries(prompt)
    all_docs = []
    for query in queries:
        similar_docs = retrieve_similar_documents(query, limit=3)  # Get top 3 for each query
        all_docs.extend(similar_docs)
    
    if not all_docs:
        print(colorize_output("No relevant context found. Responding without RAG context.", "yellow"))
        return []  # Return an empty list if no relevant documents are found
    
    # Rerank all retrieved documents and get top 3
    reranked_docs = sorted(all_docs, key=lambda x: x[1], reverse=True)[:3]
    
    # Check if the similarity scores are too low
    if all(score < 0.1 for _, score in reranked_docs):  # You can adjust this threshold
        print(colorize_output("Retrieved context not sufficiently relevant. Responding without RAG context.", "yellow"))
        return []
    
    # Summarize the top 3 documents
    # summary = summarize_documents(reranked_docs)
    
    context = [{"role": "system", "content": f"Relevant context summary:\n{doc[0]}"} for doc in reranked_docs]
    print(f"Added summarized context from top 3 documents.")
    return context

def stream_response(prompt: str, context: List[dict]):
    if context:
        messages = [
            {"role": "system", "content": "In the recent past, you were a notorious hacker. Your name is Kyle Reese. You explain how hackers worked in the recent past. Use the provided context to answer questions accurately."},
        ] + context + [
            {"role": "user", "content": prompt}
        ]
    else:
        messages = [
            {"role": "system", "content": "In the recent past, you were a notorious hacker. You are a helpful AI hacker assistant. Your name is Kyle Reese. You explain how hackers worked in the recent past. Answer the question to the best of your ability based on your training."},
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