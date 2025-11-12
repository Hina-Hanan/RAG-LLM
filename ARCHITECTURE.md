# RAG Chatbot Architecture Overview

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Application                      │
│              (Web Browser, Postman, cURL, etc.)             │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST API
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    FastAPI Application                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  /chat Endpoint                                      │  │
│  │  - Accepts user questions                            │  │
│  │  - Returns JSON responses with answers & sources     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Memory Manager                                      │  │
│  │  - Conversation context retention                   │  │
│  │  - Session management                               │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐            ┌─────────▼──────────┐
│  LLM Manager   │            │ Vector Store Mgr   │
│                │            │                    │
│  ┌──────────┐  │            │  ┌──────────────┐  │
│  │ LangChain│  │            │  │ Document     │  │
│  │ Retrieval│◄─┼────────────┼─►│ Loader       │  │
│  │ Chain    │  │            │  │ (PDF/DOCX)   │  │
│  └────┬─────┘  │            │  └──────┬───────┘  │
│       │        │            │         │          │
│  ┌────▼─────┐  │            │  ┌──────▼───────┐  │
│  │ LLM API  │  │            │  │ FAISS Vector │  │
│  │ (OpenAI/ │  │            │  │ Store        │  │
│  │ Gemini/  │  │            │  │ - Embeddings │  │
│  │ HF)      │  │            │  │ - Similarity │  │
│  └──────────┘  │            │  │   Search     │  │
└────────────────┘            │  └──────────────┘  │
                              └────────────────────┘
```

## Component Details

### 1. FastAPI Application (`app.py`)
- **Purpose**: RESTful API server
- **Endpoints**:
  - `POST /chat`: Main chat endpoint for question answering
  - `GET /health`: Health check endpoint
  - `POST /chat/clear`: Clear conversation history
  - `GET /docs`: API documentation (Swagger UI)
- **Features**:
  - CORS middleware for cross-origin requests
  - Request/response validation using Pydantic
  - Error handling and HTTP status codes

### 2. LLM Manager (`llm_manager.py`)
- **Purpose**: Manages LLM integration and retrieval chain
- **Components**:
  - LLM initialization (OpenAI, Gemini, or Hugging Face)
  - LangChain `create_retrieval_chain` integration
  - Prompt template for RAG
  - Response processing and source extraction
- **Key Function**: Combines document retrieval with LLM generation

### 3. Vector Store Manager (`vector_store_manager.py`)
- **Purpose**: Document loading and FAISS vector store management
- **Components**:
  - `DocumentLoader`: Loads PDF and DOCX files
  - `VectorStore`: Manages FAISS index creation and retrieval
  - Text splitting for chunking documents
  - Embedding generation (provider-specific)
- **Features**:
  - Automatic vector store persistence
  - Top-K retrieval (default: 7 documents)
  - Source metadata tracking

### 4. Memory Manager (`memory_manager.py`)
- **Purpose**: Conversation context retention
- **Features**:
  - Session-based memory storage
  - Conversation history tracking
  - Context injection into queries
  - Memory clearing functionality

### 5. Configuration (`config.py`)
- **Purpose**: Centralized configuration management
- **Features**:
  - Environment variable loading
  - Settings validation
  - Provider-specific configuration

## Data Flow

### Query Processing Flow

1. **User Query** → FastAPI `/chat` endpoint
2. **Session Check** → Memory Manager retrieves conversation history
3. **Query Enhancement** → Context added to query (if memory enabled)
4. **Retrieval** → FAISS vector store searches for top-K similar documents
5. **Context Assembly** → Retrieved documents combined with query
6. **LLM Generation** → LangChain retrieval chain generates answer
7. **Response Processing** → Extract answer and source documents
8. **Memory Update** → Store conversation in memory
9. **JSON Response** → Return answer, sources, and session ID

### Document Indexing Flow

1. **Document Loading** → PDF/DOCX files loaded from `documents/` directory
2. **Text Splitting** → Documents split into chunks (1000 chars, 200 overlap)
3. **Embedding Generation** → Chunks converted to vectors using embeddings model
4. **FAISS Indexing** → Vectors stored in FAISS index
5. **Persistence** → Vector store saved to disk for reuse

## Technology Stack

- **Framework**: FastAPI (Python web framework)
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **LLM Framework**: LangChain
- **LLM Providers**: Google Gemini
- **Document Processing**: PyPDF, python-docx
- **Embeddings**: Provider-specific ( Gemini embeddings, Sentence Transformers)

## Security Considerations

- API keys stored in environment variables (`.env` file)
- `.env` file excluded from version control
- No hardcoded credentials
- CORS configuration for API access control

## Scalability Considerations

- Vector store can be rebuilt with new documents
- Session-based memory (can be migrated to Redis/database)
- Stateless API design (except memory)
- Efficient FAISS indexing for large document sets

## Future Enhancements

- Redis-based session management
- Database integration for conversation history
- Authentication and authorization
- Rate limiting
- Logging and monitoring
- Unit and integration tests
- Docker containerization
- Kubernetes deployment configuration

