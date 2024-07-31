import os
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader, PyPDFLoader, DirectoryLoader
from document_processing.splitter import split_text
from database.operations import store_document
import traceback
import emoji

def get_loader_for_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == '.md':
        return UnstructuredMarkdownLoader(file_path)
    elif file_extension.lower() == '.pdf':
        return PyPDFLoader(file_path)
    else:
        return TextLoader(file_path, encoding='utf-8')

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
        
        chunks = split_text(documents)
        
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
        
def process_directory(directory_path: str):
    print(f"Debug: Starting to process directory: {directory_path}")
    directory_path = os.path.expanduser(os.path.expandvars(directory_path))
    if not os.path.exists(directory_path):
        print(f"Error: Directory does not exist at path: {directory_path}")
        return
    
    try:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if file.lower().endswith('.md'):
                        loader = UnstructuredMarkdownLoader(file_path)
                    else:
                        # Skip non-markdown files
                        print(f"Skipping non-markdown file: {file_path}")
                        continue
                    
                    documents = loader.load()
                    
                    chunks = split_text(documents)
                    
                    for i, chunk in enumerate(chunks):
                        try:
                            store_document(chunk.page_content, {"source": file_path, "chunk_index": i})
                        except Exception as e:
                            print(f"Error storing chunk {i} from {file_path}: {e}")
                    
                    print(f"Processed file: {file_path}")
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
        
        print(f"Finished processing directory: {directory_path}")
        print(emoji.emojize(":star:"))
    except Exception as e:
        print(f"Error processing directory: {e}")
        print(f"Debug: Exception type: {type(e)}")
        print(f"Stack trace: {traceback.format_exc()}")