import os
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    CSVLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader
)
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# File type to loader mapping
LOADER_MAPPING = {
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
    ".docx": Docx2txtLoader,
    ".csv": CSVLoader,
    ".html": UnstructuredHTMLLoader,
    ".md": UnstructuredMarkdownLoader
}

def get_documents_from_directory(directory_path: str) -> List[Dict[str, Any]]:
    """
    Load all documents from a directory
    """
    documents = []
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension in LOADER_MAPPING:
                loader_class = LOADER_MAPPING[file_extension]
                loader = loader_class(file_path)
                try:
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"Error loading {file_path}: {str(e)}")
    
    return documents

def create_embeddings_from_documents(
    documents: List[Dict[str, Any]],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    embedding_model_name: str = "mxbai-embed-large:latest",
    base_url: str = "http://host.docker.internal:11434"
) -> FAISS:
    """
    Create embeddings from documents using Ollama
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    # Split documents into chunks
    texts = text_splitter.split_documents(documents)
    
    # Create embeddings using Ollama
    embeddings = OllamaEmbeddings(
        model=embedding_model_name,
        base_url=base_url
    )
    
    # Create and return vector store
    return FAISS.from_documents(texts, embeddings)

def save_embeddings(vector_store: FAISS, directory: str, collection_name: str) -> None:
    """
    Save embeddings to disk
    """
    save_path = os.path.join(directory, collection_name)
    vector_store.save_local(save_path)

def load_embeddings(
    directory: str,
    collection_name: str,
    embedding_model_name: str = "mxbai-embed-large:latest",
    base_url: str = "http://host.docker.internal:11434"
) -> Optional[FAISS]:
    """
    Load embeddings from disk
    """
    load_path = os.path.join(directory, collection_name)
    
    if not os.path.exists(load_path):
        return None
    
    embeddings = OllamaEmbeddings(
        model=embedding_model_name,
        base_url=base_url
    )
    return FAISS.load_local(load_path, embeddings)
