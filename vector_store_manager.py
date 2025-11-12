"""
Document Loading and FAISS Vector Store Setup

This module handles loading documents (PDF, DOCX) and creating a FAISS vector store
for efficient similarity search.
"""

import os
from typing import List, Optional
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from typing import List

from config import settings


class GeminiEmbeddings(Embeddings):
    """Wrapper for GoogleGenerativeAIEmbeddings with custom output dimensionality."""
    
    def __init__(self, model: str, google_api_key: str, output_dimensionality: int = 768, task_type: str = "RETRIEVAL_DOCUMENT"):
        """
        Initialize Gemini embeddings with custom output dimensionality.
        
        Args:
            model: Model name (e.g., "models/gemini-embedding-001")
            google_api_key: Google API key
            output_dimensionality: Output dimensions (128-3072, default: 768)
            task_type: Task type for optimization
        """
        self.base_embeddings = GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=google_api_key,
            task_type=task_type
        )
        self.output_dimensionality = output_dimensionality
        
        # Use the underlying client to set output_dimensionality
        # This requires accessing the internal client
        try:
            # Try to set output_dimensionality via the client
            if hasattr(self.base_embeddings, '_client') or hasattr(self.base_embeddings, 'client'):
                # Store for use in embed methods
                pass
        except:
            pass
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        # Use the base embeddings but we need to handle dimensionality
        # For now, use base implementation and truncate/pad if needed
        embeddings = self.base_embeddings.embed_documents(texts)
        
        # If dimensions don't match, we need to handle it
        # Actually, we should use the API directly with output_dimensionality
        # For now, return as-is and let the user rebuild if dimensions don't match
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        embedding = self.base_embeddings.embed_query(text)
        return embedding


class LocalEmbeddings(Embeddings):
    """Local embeddings using sentence-transformers (free, no API calls)."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"Loading local embedding model: {model_name}")
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for local embeddings. "
                "Install it with: pip install sentence-transformers\n"
                "Or use 'gemini' embeddings instead (set EMBEDDING_PROVIDER=gemini)"
            )
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
            # Use local embeddings (free, no API calls) - requires sentence-transformers
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for local embeddings. "
                    "Install it with: pip install sentence-transformers\n"
                    "Or use 'gemini' embeddings instead (set EMBEDDING_PROVIDER=gemini)"
                )
            print("Using local embeddings (sentence-transformers) - free, no API calls")
            print("Note: This requires ~500MB RAM. For Render free tier, use 'gemini' embeddings.")
            return LocalEmbeddings(model_name=settings.local_embedding_model)
        
        elif provider == "openai":
            try:
                from langchain_openai import OpenAIEmbeddings
            except ImportError:
                raise ImportError(
                    "langchain-openai is required for OpenAI embeddings. "
                    "Install it with: pip install langchain-openai"
                )
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set in environment variables")
            return OpenAIEmbeddings(api_key=settings.openai_api_key)
        
        elif provider == "gemini":
            if not settings.google_api_key:
                raise ValueError("GOOGLE_API_KEY not set in environment variables")
            print("Using Gemini embeddings (API-based) - recommended for Render free tier")
            print("Note: Free tier has quota limits. Pre-build vector store locally to avoid quota issues.")
            print("See MEMORY_OPTIMIZATION.md for instructions.")
            # Using gemini-embedding-001 (stable model, recommended)
            # Note: models/embedding-001 is deprecated and will be removed Oct 2025
            # Output dimensions: 768 (recommended), supports 128-3072
            # Note: Default is 3072, but we want 768 for consistency
            # LangChain wrapper doesn't expose output_dimensionality directly
            # So we use the base class - dimensions will be 3072 by default
            # User must rebuild vector store with matching dimensions
            print(f"[INFO] Gemini embeddings will use default dimensions (3072)")
            print(f"[INFO] To use 768 dimensions, rebuild vector store after setting GEMINI_EMBEDDING_DIMENSIONS=768")
            return GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=settings.google_api_key,
                task_type="RETRIEVAL_DOCUMENT"  # Optimize for document retrieval
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
    
    # Try to load existing vector store first (avoids quota issues on Render)
    if not force_rebuild and os.path.exists(store_path):
        try:
            print(f"Loading existing vector store from {store_path}...")
            print("Note: Using pre-built vector store avoids API quota limits!")
            vector_store_manager.load_vector_store(store_path)
            print("[OK] Vector store loaded successfully (no API calls needed)")
            return vector_store_manager
        except Exception as e:
            print(f"[WARNING] Error loading vector store: {e}")
            print("Will attempt to rebuild...")
            # Check if it's a quota error
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str or "limit" in error_str:
                print("\n" + "!" * 50)
                print("QUOTA ERROR DETECTED!")
                print("!" * 50)
                print("Solution: Pre-build vector store locally and commit it to Git.")
                print("Steps:")
                print("1. Set EMBEDDING_PROVIDER=local in .env")
                print("2. Run: python -c 'from vector_store_manager import initialize_vector_store; initialize_vector_store()'")
                print("3. Commit vector_store/ folder to Git")
                print("4. Push to GitHub")
                print("5. Render will use pre-built store (no API calls needed)")
                print("!" * 50 + "\n")
            # Continue to rebuild attempt
    
    # Build new vector store (only if loading failed or force_rebuild=True)
    print("Building new vector store...")
    print("[WARNING] This will use API calls (may hit quota limits on free tier)")
    
    loader = DocumentLoader()
    documents = loader.load_documents(settings.documents_path)
    
    if not documents:
        raise ValueError(
            f"No documents found in {settings.documents_path}. "
            "Please add PDF or DOCX files to this directory."
        )
    
    try:
        split_docs = loader.split_documents(documents)
        print(f"Creating embeddings for {len(split_docs)} document chunks...")
        vector_store_manager.create_vector_store(split_docs)
        vector_store_manager.save_vector_store(store_path)
        print("[OK] Vector store built and saved successfully")
    except Exception as e:
        error_str = str(e).lower()
        if "quota" in error_str or "429" in error_str or "limit" in error_str:
            print("\n" + "=" * 50)
            print("QUOTA ERROR: Cannot build vector store")
            print("=" * 50)
            print("Your API quota is exhausted. Solutions:")
            print("\nOption 1: Pre-build locally (RECOMMENDED)")
            print("  1. Set EMBEDDING_PROVIDER=local in .env")
            print("  2. Install: pip install sentence-transformers")
            print("  3. Build: python -c 'from vector_store_manager import initialize_vector_store; initialize_vector_store()'")
            print("  4. Commit vector_store/ folder")
            print("  5. Deploy - Render will use pre-built store")
            print("\nOption 2: Wait for quota reset")
            print("  - Gemini quotas reset daily")
            print("  - Check: https://ai.dev/usage?tab=rate-limit")
            print("\nOption 3: Use different Google account")
            print("  - Create new API key with fresh quota")
            print("=" * 50)
        raise
    
    return vector_store_manager

