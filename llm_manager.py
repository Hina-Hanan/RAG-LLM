"""
LLM Integration with LangChain

This module handles LLM API integration using LangChain's create_retrieval_chain
for RAG-based question answering.
"""

from typing import Optional, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable

from config import settings


class LLMManager:
    """Manages LLM initialization and retrieval chain creation."""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.retrieval_chain: Optional[Runnable] = None
    
    def _initialize_llm(self) -> BaseChatModel:
        """Initialize LLM based on provider settings."""
        provider = settings.llm_provider.lower()
        
        if provider == "openai":
            try:
                from langchain_openai import ChatOpenAI
            except ImportError:
                raise ImportError(
                    "langchain-openai is required for OpenAI provider. "
                    "Install it with: pip install langchain-openai"
                )
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set in environment variables")
            return ChatOpenAI(
                model=settings.model_name,
                api_key=settings.openai_api_key,
                temperature=0.7
            )
        
        elif provider == "gemini":
            if not settings.google_api_key:
                raise ValueError("GOOGLE_API_KEY not set in environment variables")
            return ChatGoogleGenerativeAI(
                model=settings.model_name if settings.model_name != "gpt-3.5-turbo" else "gemini-pro",
                google_api_key=settings.google_api_key,
                temperature=0.7,
                convert_system_message_to_human=True  # Required for Gemini - it doesn't support SystemMessage
            )
        
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}. Supported providers: 'openai', 'gemini'")
    
    def create_retrieval_chain(self, retriever):
        """
        Create a retrieval chain using LangChain's create_retrieval_chain.
        
        Args:
            retriever: LangChain retriever instance
            
        Returns:
            Retrieval chain runnable
        """
        # Import chains - LangChain 1.0+ compatibility
        # In LangChain 1.0+, chains moved to langchain-classic package
        try:
            # Try langchain-classic first (LangChain 1.0+)
            from langchain_classic.chains import create_retrieval_chain
            from langchain_classic.chains.combine_documents import create_stuff_documents_chain
        except ImportError:
            # Fallback to langchain.chains (older versions)
            try:
                from langchain.chains import create_retrieval_chain
                from langchain.chains.combine_documents import create_stuff_documents_chain
            except ImportError:
                # Last resort: try langchain.chains.retrieval
                from langchain.chains.retrieval import create_retrieval_chain
                from langchain.chains.combine_documents import create_stuff_documents_chain
        
        # Create prompt template for RAG
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant that answers questions based on the provided context.
            
Use the following pieces of retrieved context to answer the question. If you don't know the answer based on the context, 
say that you don't know. Don't make up information.

Context: {context}"""),
            ("human", "{input}")
        ])
        
        # Create document chain
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        
        # Create retrieval chain
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        self.retrieval_chain = retrieval_chain
        return retrieval_chain
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the retrieval chain with a question.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with 'answer' and 'context' keys
        """
        if self.retrieval_chain is None:
            raise ValueError("Retrieval chain not initialized. Create it first.")
        
        response = self.retrieval_chain.invoke({"input": question})
        return response
    
    def get_source_documents(self, response: Dict[str, Any]) -> list:
        """
        Extract source document filenames from response.
        
        Args:
            response: Response from retrieval chain
            
        Returns:
            List of unique source filenames
        """
        source_files = set()
        if "context" in response:
            documents = response.get("context", [])
            if isinstance(documents, list):
                for doc in documents:
                    if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                        source_files.add(doc.metadata['source'])
        return list(source_files)

