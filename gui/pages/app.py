import streamlit as st
import os
from pages.assistant import (
    process_document, forget_document, list_documents, 
    search_documents, stream_response, recall, DB_PARAMS, EMBEDDING_SIZE
)

st.set_page_config(page_title="Local RAG AI Assistant", layout="wide")

st.title("Local RAG AI Assistant")

# Sidebar for document management
st.sidebar.header("Document Management")

# File upload
uploaded_file = st.sidebar.file_uploader("Upload a document", type=["txt", "md", "pdf"])
if uploaded_file is not None:
    if st.sidebar.button("Process Document"):
        with st.spinner("Processing document..."):
            # Save the file temporarily
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            # Process the document
            process_document(uploaded_file.name)
            # Remove the temporary file
            os.remove(uploaded_file.name)
        st.sidebar.success(f"Document {uploaded_file.name} processed successfully!")

# Document deletion
doc_to_delete = st.sidebar.text_input("Enter the name of the document to forget:")
if st.sidebar.button("Forget Document"):
    with st.spinner("Forgetting document..."):
        forget_document(doc_to_delete)
    st.sidebar.success(f"Document {doc_to_delete} has been removed from the database.")

# List documents
if st.sidebar.button("List Documents"):
    docs = list_documents()
    st.sidebar.write("Stored documents:")
    for doc in docs:
        st.sidebar.write(f"- {doc}")

# Document search
search_query = st.sidebar.text_input("Enter your search query:")
if st.sidebar.button("Search Documents"):
    results = search_documents(search_query)
    st.sidebar.write("Search results:")
    for doc, similarity in results:
        st.sidebar.write(f"Similarity: {similarity:.2f}")
        st.sidebar.write(doc[:200] + "..." if len(doc) > 200 else doc)
        st.sidebar.write("---")

# Main chat interface
st.header("Chat with your documents")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is your question?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate a response
    with st.spinner("Thinking..."):
        context = recall(prompt)
        response = stream_response(prompt, context)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
