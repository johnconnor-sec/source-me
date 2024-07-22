import streamlit as st
from streamlit_multipage import MultiPage
from streamlit_extras.switch_page_button import switch_page
import streamlit_shadcn_ui as ui


app = MultiPage()

def logo():
    st.image("media/JC-Profile-Update.png", width=100)

def create_main_page(header_title):
    st.header(header_title)
    
    # Add the project description using Markdown
    st.markdown("""
    ### Local RAG AI Assistant

    Welcome to the Local RAG AI Assistant, your powerful tool for document management and AI-powered interactions!

    #### 🌟 Key Features

    - **Document Processing**: Easily upload and process various document types (TXT, MD, PDF, CSV)
    - **Intelligent Search**: Find relevant information across your document collection
    - **AI-Powered Conversations**: Engage in meaningful dialogue based on your documents
    - **Local Database**: All your data stays secure on your local machine
    - **Customizable**: Built with Streamlit for easy modifications and extensions

    #### 💡 How It Works

    1. **Upload Documents**: Add your files to the assistant's knowledge base
    2. **Ask Questions**: Interact with the AI to get insights from your documents
    3. **Manage Your Data**: List, search, and remove documents as needed

    #### 🚀 Getting Started

    1. Use the sidebar to upload and manage your documents
    2. Start chatting with the AI in the main chat interface
    3. Explore the power of local, privacy-focused AI assistance!

    #### 🛠 Technical Details

    - Built with Python, Streamlit, and LangChain
    - Uses Ollama for embeddings and chat completions
    - Stores data in a local PostgreSQL database

    Dive in and experience the future of document interaction and AI assistance!
    """)

def main():
    logo()
    create_main_page("source.me")
        

if __name__ == "__main__":
    main()
