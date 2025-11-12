"""
FastAPI Application - Chat API Endpoint

This module implements the FastAPI application with the /chat endpoint
for RAG-based question answering.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from contextlib import asynccontextmanager
import uvicorn
import os

from config import settings
from vector_store_manager import initialize_vector_store
from llm_manager import LLMManager
from memory_manager import get_memory, clear_memory


# Global variables for vector store and LLM manager
vector_store_manager = None
llm_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global vector_store_manager, llm_manager
    
    # Startup
    try:
        print("Initializing vector store...")
        vector_store_manager = initialize_vector_store()
        
        print("Initializing LLM manager...")
        llm_manager = LLMManager()
        
        print("Creating retrieval chain...")
        retriever = vector_store_manager.get_retriever(top_k=settings.top_k_results)
        llm_manager.create_retrieval_chain(retriever)
        
        print("RAG Chatbot API is ready!")
    except Exception as e:
        print(f"Error during startup: {e}")
        raise
    
    yield
    
    # Shutdown (if needed)
    pass


# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Retrieval-Augmented Generation Chatbot using FAISS and LangChain",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Request/Response Models
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"
    use_memory: Optional[bool] = True


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    session_id: str


class HealthResponse(BaseModel):
    status: str
    message: str


@app.get("/")
async def root():
    """Root endpoint - serve frontend."""
    static_file = os.path.join(static_dir, "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return HealthResponse(
        status="healthy",
        message="RAG Chatbot API is running. Use /chat endpoint to ask questions."
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    if vector_store_manager is None or llm_manager is None:
        return HealthResponse(
            status="unhealthy",
            message="Vector store or LLM manager not initialized"
        )
    
    return HealthResponse(
        status="healthy",
        message="All systems operational"
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for RAG-based question answering.
    
    Args:
        request: ChatRequest with question and optional session_id
        
    Returns:
        ChatResponse with answer and source documents
    """
    if llm_manager is None or vector_store_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Service not initialized. Please wait for startup to complete."
        )
    
    try:
        # Get conversation memory if enabled
        memory = get_memory(request.session_id) if request.use_memory else None
        
        # Add conversation context to question if memory is enabled
        question = request.question
        if memory and memory.get_history_dict():
            context = memory.get_context_string()
            if context:
                # Enhance question with context (optional - can be adjusted)
                question = f"Previous conversation:\n{context}\n\nCurrent question: {request.question}"
        
        # Query the retrieval chain
        response = llm_manager.query(question)
        
        # Extract answer
        answer = response.get("answer", "I couldn't generate an answer.")
        
        # Extract source documents
        sources = llm_manager.get_source_documents(response)
        
        # Update memory
        if memory:
            memory.add_message("user", request.question)
            memory.add_message("assistant", answer)
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            session_id=request.session_id
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@app.post("/chat/clear")
async def clear_chat(session_id: str = "default"):
    """Clear conversation history for a session."""
    clear_memory(session_id)
    return {"message": f"Conversation history cleared for session: {session_id}"}


@app.get("/docs")
async def get_documentation():
    """Get API documentation."""
    return {
        "endpoints": {
            "/": "Root endpoint - health check",
            "/health": "Health check endpoint",
            "/chat": {
                "method": "POST",
                "description": "Chat endpoint for RAG-based question answering",
                "request_body": {
                    "question": "string (required) - User's question",
                    "session_id": "string (optional) - Session ID for conversation memory",
                    "use_memory": "boolean (optional) - Enable conversation memory"
                },
                "response": {
                    "answer": "string - Chatbot's answer",
                    "sources": "list[string] - Source document filenames",
                    "session_id": "string - Session ID used"
                }
            },
            "/chat/clear": {
                "method": "POST",
                "description": "Clear conversation history",
                "query_params": {
                    "session_id": "string (optional) - Session ID to clear"
                }
            }
        },
        "example_request": {
            "question": "What is the main topic of the documents?",
            "session_id": "user123",
            "use_memory": True
        },
        "example_response": {
            "answer": "Based on the documents...",
            "sources": ["document1.pdf", "document2.pdf"],
            "session_id": "user123"
        }
    }


def main():
    """Run the FastAPI application."""
    uvicorn.run(
        "app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )


if __name__ == "__main__":
    main()

