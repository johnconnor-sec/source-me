from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_text(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=30)
    return text_splitter.split_documents(documents)