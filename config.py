import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Provider Selection
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    
    # Embedding Provider Selection (defaults to "local" for free tier compatibility)
    # Options: "openai", "gemini", "local" (local uses sentence-transformers, free)
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "local")
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Google Gemini Configuration
    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    
    # Model Configuration
    model_name: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    
    # Local Embedding Model (for sentence-transformers)
    local_embedding_model: str = os.getenv("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Gemini Embedding Output Dimensionality (for gemini embeddings)
    # Options: 128, 256, 512, 768 (recommended), 1536, 2048, 3072
    # Default: 768 (recommended for RAG)
    gemini_embedding_dimensions: int = int(os.getenv("GEMINI_EMBEDDING_DIMENSIONS", "768"))
    
    # Vector Store Configuration
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "./vector_store")
    documents_path: str = os.getenv("DOCUMENTS_PATH", "./documents")
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # Retrieval Configuration
    top_k_results: int = int(os.getenv("TOP_K_RESULTS", "7"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        protected_namespaces = ('settings_',)


settings = Settings()

