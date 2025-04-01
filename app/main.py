import os
import tempfile
import shutil
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader, 
    TextLoader, 
    Docx2txtLoader, 
    CSVLoader
)
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model configuration
OLLAMA_API_BASE_URL = os.environ.get("OLLAMA_API_BASE_URL", "http://host.docker.internal:11434")
embeddings_model_name = "mxbai-embed-large:latest"
embeddings = OllamaEmbeddings(
    model=embeddings_model_name,
    base_url=OLLAMA_API_BASE_URL
)
llm_model_name = "phi4"  # Default LLM model
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
DATA_DIR = "/data"
EMBEDDINGS_DIR = "/embeddings"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    query: str
    collection_name: str
    model_name: Optional[str] = "phi4"  # Default model with option to override

class Response(BaseModel):
    response: str
    source_documents: Optional[List[Dict[str, Any]]] = None

@app.get("/")
def read_root():
    return {"message": "Charcha RAG API is running"}

@app.post("/upload_documents")
async def upload_documents(
    files: List[UploadFile] = File(...),
    collection_name: str = Form(...)
):
    try:
        # Create collection directory if it doesn't exist
        collection_dir = os.path.join(DATA_DIR, collection_name)
        os.makedirs(collection_dir, exist_ok=True)
        
        documents = []
        
        for file in files:
            # Save the file to the collection directory
            file_path = os.path.join(collection_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Load the document based on file type
            if file.filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file.filename.endswith(".txt"):
                loader = TextLoader(file_path)
            elif file.filename.endswith(".docx"):
                loader = Docx2txtLoader(file_path)
            elif file.filename.endswith(".csv"):
                loader = CSVLoader(file_path)
            else:
                # Skip unsupported file types
                continue
            
            documents.extend(loader.load())
        
        # Split the documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        texts = text_splitter.split_documents(documents)
        
        # Create the embeddings and save to disk
        db = FAISS.from_documents(texts, embeddings)
        db.save_local(os.path.join(EMBEDDINGS_DIR, collection_name))
        
        return {
            "message": f"Successfully processed {len(files)} documents",
            "collection_name": collection_name,
            "document_count": len(texts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=Response)
async def query_documents(request: QueryRequest):
    try:
        # Load the vector store
        db_path = os.path.join(EMBEDDINGS_DIR, request.collection_name)
        if not os.path.exists(db_path):
            raise HTTPException(status_code=404, detail=f"Collection '{request.collection_name}' not found")
        
        # Use Ollama embeddings for loading the vector store
        ollama_embeddings = OllamaEmbeddings(
            model=embeddings_model_name,
            base_url=OLLAMA_API_BASE_URL
        )
        db = FAISS.load_local(db_path, ollama_embeddings)
        
        # Initialize the LLM with the requested model
        llm = Ollama(model=request.model_name, base_url=OLLAMA_API_BASE_URL)
        
        # Create the retrieval QA chain
        retriever = db.as_retriever(search_kwargs={"k": 5})
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
        )
        
        # Execute the query
        result = qa_chain.invoke(request.query)
        
        # Format source documents for the response
        source_docs = []
        for doc in result["source_documents"]:
            source_docs.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        
        return {
            "response": result["result"],
            "source_documents": source_docs
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections")
async def list_collections():
    try:
        collections = [
            d for d in os.listdir(EMBEDDINGS_DIR) 
            if os.path.isdir(os.path.join(EMBEDDINGS_DIR, d))
        ]
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    try:
        # Delete the embeddings
        embeddings_path = os.path.join(EMBEDDINGS_DIR, collection_name)
        if os.path.exists(embeddings_path):
            shutil.rmtree(embeddings_path)
        
        # Delete the data files
        data_path = os.path.join(DATA_DIR, collection_name)
        if os.path.exists(data_path):
            shutil.rmtree(data_path)
        
        return {"message": f"Collection '{collection_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_available_models():
    """List available models from Ollama"""
    try:
        import requests
        response = requests.get(f"{OLLAMA_API_BASE_URL}/api/tags")
        
        if response.status_code != 200:
            return {"models": ["phi4", "gemma3:12b", "mxbai-embed-large:latest"]}  # Fallback
            
        models = [model["name"] for model in response.json().get("models", [])]
        return {"models": models}
    except Exception as e:
        # If we can't connect, return the models we expect to be there
        return {"models": ["phi4", "gemma3:12b", "mxbai-embed-large:latest"]}

@app.get("/embedding-model")
async def get_embedding_model():
    """Return the current embedding model"""
    return {"model": embeddings_model_name}
