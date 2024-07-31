from typing import List, Union
import ollama
from config import EMBEDDING_MODEL

def get_embedding(text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
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