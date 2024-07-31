import os
from database.connection import initialize_db, update_db_schema
from database.operations import store_document, forget_document, list_documents
from document_processing.loader import process_document, process_directory
from retrieval.similarity import search_documents
from chat.ollama_chat import recall, stream_response
from utils.output import colorize_output

def main():
    initialize_db()
    update_db_schema()
    
    print(colorize_output("Welcome to the Local RAG AI Agent!", "yellow"))
    print(colorize_output("Commands:", "yellow"))
    print(colorize_output("- 'exit' to quit", "white"))
    print(colorize_output("- 'process' to add a document", "white"))
    print(colorize_output("- 'process_dir' to add all documents in a directory", "white"))
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
        elif user_input.lower() == 'process_dir':
            dir_path = input(colorize_output("Enter the path to the directory: ", "white"))
            process_directory(dir_path)
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