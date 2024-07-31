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
CHAT_MODEL = "mistral-nemo"