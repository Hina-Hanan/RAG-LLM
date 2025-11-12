"""
Document Loading and FAISS Vector Store Setup

This module handles loading documents (PDF, DOCX) and creating a FAISS vector store
for efficient similarity search.
"""

import os
from typing import List, Optional
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document
from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer

from config import settings


class LocalEmbeddings(Embeddings):
    """Local embeddings using sentence-transformers (free, no API calls)."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"Loading local embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print(f"Local embedding model loaded successfully!")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        embedding = self.model.encode([text], show_progress_bar=False)
        return embedding[0].tolist()


class DocumentLoader:
    """Handles loading and processing documents from various formats."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def load_documents(self, directory_path: str) -> List[Document]:
        """
        Load all documents from the specified directory.
        
        Args:
            directory_path: Path to directory containing PDF and DOCX files
            
        Returns:
            List of Document objects
        """
        documents = []
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"Directory {directory_path} does not exist. Creating it...")
            directory.mkdir(parents=True, exist_ok=True)
            return documents
        
        # Load PDF files
        pdf_files = list(directory.glob("*.pdf"))
        for pdf_file in pdf_files:
            try:
                print(f"Loading PDF: {pdf_file}")
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()
                # Add metadata with filename
                for doc in docs:
                    doc.metadata['source'] = pdf_file.name
                    doc.metadata['file_path'] = str(pdf_file)
                documents.extend(docs)
            except Exception as e:
                print(f"Error loading {pdf_file}: {e}")
        
        # Load DOCX files
        docx_files = list(directory.glob("*.docx"))
        for docx_file in docx_files:
            try:
                print(f"Loading DOCX: {docx_file}")
                loader = Docx2txtLoader(str(docx_file))
                docs = loader.load()
                # Add metadata with filename
                for doc in docs:
                    doc.metadata['source'] = docx_file.name
                    doc.metadata['file_path'] = str(docx_file)
                documents.extend(docs)
            except Exception as e:
                print(f"Error loading {docx_file}: {e}")
        
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks."""
        return self.text_splitter.split_documents(documents)


class VectorStore:
    """Manages FAISS vector store creation and retrieval."""
    
    def __init__(self):
        self.embeddings = self._get_embeddings()
        self.vector_store: Optional[FAISS] = None
    
    def _get_embeddings(self):
        """Initialize embeddings based on embedding provider setting."""
        provider = settings.embedding_provider.lower()
        
        if provider == "local":
            # Use local embeddings (free, no API calls) - recommended for free tier
            print("Using local embeddings (sentence-transformers) - free, no API calls")
            return LocalEmbeddings(model_name=settings.local_embedding_model)
        
        elif provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set in environment variables")
            return OpenAIEmbeddings(api_key=settings.openai_api_key)
        
        elif provider == "gemini":
            if not settings.google_api_key:
                raise ValueError("GOOGLE_API_KEY not set in environment variables")
            print("Warning: Gemini embeddings may have quota limits on free tier.")
            print("Consider using 'local' embeddings instead (set EMBEDDING_PROVIDER=local)")
            return GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=settings.google_api_key
            )
        
        else:
            raise ValueError(
                f"Unsupported embedding provider: {provider}. "
                f"Supported providers: 'local', 'openai', 'gemini'"
            )
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """
        Create a FAISS vector store from documents.
        
        Args:
            documents: List of Document objects to index
            
        Returns:
            FAISS vector store
        """
        print(f"Creating vector store from {len(documents)} document chunks...")
        
        # Use LangChain's built-in FAISS creation (works with all embedding types)
        vector_store = FAISS.from_documents(documents, self.embeddings)
        
        self.vector_store = vector_store
        return vector_store
    
    def save_vector_store(self, path: str):
        """Save vector store to disk."""
        if self.vector_store is None:
            raise ValueError("No vector store to save. Create one first.")
        
        os.makedirs(path, exist_ok=True)
        self.vector_store.save_local(path)
        print(f"Vector store saved to {path}")
    
    def load_vector_store(self, path: str) -> FAISS:
        """Load vector store from disk."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Vector store not found at {path}")
        
        # Try loading with allow_dangerous_deserialization first (newer versions)
        # Fall back to without it if that parameter is not supported
        try:
            self.vector_store = FAISS.load_local(
                path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        except TypeError:
            # Older version of FAISS doesn't support allow_dangerous_deserialization
            try:
                self.vector_store = FAISS.load_local(path, self.embeddings)
            except Exception as e:
                # If both fail, try with a different approach
                import pickle
                import faiss
                # Load the FAISS index and documents separately
                with open(os.path.join(path, "index.pkl"), "rb") as f:
                    store = pickle.load(f)
                self.vector_store = store
        
        print(f"Vector store loaded from {path}")
        return self.vector_store
    
    def get_retriever(self, top_k: int = None):
        """Get a retriever from the vector store."""
        if self.vector_store is None:
            raise ValueError("No vector store available. Create or load one first.")
        
        top_k = top_k or settings.top_k_results
        return self.vector_store.as_retriever(search_kwargs={"k": top_k})


def initialize_vector_store(force_rebuild: bool = False) -> VectorStore:
    """
    Initialize or load the vector store.
    
    Args:
        force_rebuild: If True, rebuild the vector store even if it exists
        
    Returns:
        VectorStore instance
    """
    vector_store_manager = VectorStore()
    store_path = settings.vector_store_path
    
    if not force_rebuild and os.path.exists(store_path):
        try:
            print(f"Loading existing vector store from {store_path}...")
            vector_store_manager.load_vector_store(store_path)
            return vector_store_manager
        except Exception as e:
            print(f"Error loading vector store: {e}. Rebuilding...")
    
    # Build new vector store
    print("Building new vector store...")
    loader = DocumentLoader()
    documents = loader.load_documents(settings.documents_path)
    
    if not documents:
        raise ValueError(
            f"No documents found in {settings.documents_path}. "
            "Please add PDF or DOCX files to this directory."
        )
    
    split_docs = loader.split_documents(documents)
    vector_store_manager.create_vector_store(split_docs)
    vector_store_manager.save_vector_store(store_path)
    
    return vector_store_manager

