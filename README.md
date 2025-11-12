# RAG Chatbot - Retrieval-Augmented Generation System

A production-ready RAG (Retrieval-Augmented Generation) chatbot built with FAISS vector database, LangChain, and FastAPI. This system enables accurate, context-aware question answering by retrieving relevant documents and generating responses using Large Language Models.

## 🏗️ Architecture Overview

```
┌─────────────────┐
│   FastAPI App   │
│   (/chat)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Manager    │
│  (LangChain)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Retrieval Chain │◄─────│  FAISS Vector    │
│ (LangChain)     │      │     Store        │
└────────┬────────┘      └──────────────────┘
         │                        ▲
         │                        │
         ▼                        │
┌─────────────────┐              │
│   Document      │──────────────┘
│   Loaders       │
│ (PDF, DOCX)     │
└─────────────────┘
```

### Components

1. **Document Loaders**: Load and process PDF and DOCX files
2. **FAISS Vector Store**: Efficient similarity search for document retrieval
3. **LLM Integration**: Supports OpenAI GPT and Google Gemini models
4. **LangChain Retrieval Chain**: Orchestrates RAG workflow
5. **FastAPI Endpoint**: RESTful API for chat interactions
6. **Memory Management**: Conversation context retention across interactions

## 🚀 Features

- ✅ **Multi-format Document Support**: PDF and DOCX files
- ✅ **FAISS Vector Database**: Fast similarity search
- ✅ **Multiple LLM Providers**: OpenAI, Google Gemini
- ✅ **Top-K Retrieval**: Configurable retrieval of top 7 (default) similar documents
- ✅ **Source Tracking**: Returns source document filenames with each response
- ✅ **Conversation Memory**: Maintains context across chat sessions
- ✅ **RESTful API**: Clean FastAPI endpoints with JSON responses
- ✅ **Secure Configuration**: Environment variable-based API key management

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- API key for your chosen LLM provider:
  - OpenAI API key (for GPT models)
  - Google API key (for Gemini models)

## 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ragllm
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   
   Create a `.env` file in the project root:
   ```env
   # LLM Provider Selection: "openai" or "gemini"
   LLM_PROVIDER=gemini
   
   # OpenAI Configuration (if using OpenAI)
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Google Gemini Configuration (if using Gemini)
   GOOGLE_API_KEY=your_google_api_key_here
   
   # Model Configuration
   MODEL_NAME=gemini-pro  # For OpenAI: gpt-3.5-turbo, gpt-4, etc.
   # For Gemini: gemini-2.5-flash
   
   # Vector Store Configuration
   VECTOR_STORE_PATH=./vector_store
   DOCUMENTS_PATH=./documents
   
   # API Configuration
   API_HOST=0.0.0.0
   API_PORT=8000
   
   # Retrieval Configuration
   TOP_K_RESULTS=7
   ```

5. **Add documents**:
   
   Place your PDF or DOCX files in the `documents/` directory:
   ```bash
   mkdir documents
   # Copy your PDF/DOCX files to documents/
   ```

## 🎯 Usage

### Starting the API Server

```bash
python app.py
```

Or using uvicorn directly:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

**🎨 Frontend Interface**: Visit `http://localhost:8000` in your browser to use the chat interface!

### API Endpoints

#### 1. Health Check
```bash
GET http://localhost:8000/health
```

#### 2. Chat Endpoint
```bash
POST http://localhost:8000/chat
Content-Type: application/json

{
  "question": "What is the main topic of the documents?",
  "session_id": "user123",
  "use_memory": true
}
```

**Response**:
```json
{
  "answer": "Based on the retrieved documents...",
  "sources": ["document1.pdf", "document2.pdf"],
  "session_id": "user123"
}
```

#### 3. Clear Conversation History
```bash
POST http://localhost:8000/chat/clear?session_id=user123
```

#### 4. Frontend Interface
- **Chat UI**: `http://localhost:8000` - Beautiful web interface for chatting
- **Swagger UI**: `http://localhost:8000/docs` - API documentation
- **ReDoc**: `http://localhost:8000/redoc` - Alternative API docs

### Example Usage with cURL

```bash
# Ask a question
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key findings in the documents?",
    "session_id": "test_session",
    "use_memory": true
  }'

# Clear conversation history
curl -X POST "http://localhost:8000/chat/clear?session_id=test_session"
```

### Example Usage with Python

```python
import requests

# Chat endpoint
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "question": "What is discussed in the documents?",
        "session_id": "my_session",
        "use_memory": True
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
```

## 📁 Project Structure

```
ragllm/
├── app.py                      # FastAPI application and endpoints
├── config.py                   # Configuration and settings
├── vector_store_manager.py     # FAISS vector store management
├── llm_manager.py              # LLM integration and retrieval chain
├── memory_manager.py           # Conversation memory management
├── static/                     # Frontend files
│   └── index.html             # Chat interface
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .gitignore                  # Git ignore file
├── documents/                  # Place PDF/DOCX files here
├── vector_store/               # FAISS vector store (auto-generated)
├── render.yaml                 # Render deployment config
├── Procfile                    # Process file for deployment
├── DEPLOY.md                   # Deployment guide
└── README.md                   # This file
```

## 🔐 Security Notes

- **Never commit your `.env` file** to version control
- API keys are loaded from environment variables
- The `.gitignore` file excludes sensitive files
- Use different API keys for development and production

## ⚙️ Configuration Options

### LLM Provider Selection

Set `LLM_PROVIDER` in your `.env` file:
- `openai` - Use OpenAI GPT models
- `gemini` - Use Google Gemini models

### Model Selection

- **OpenAI**: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo-preview`
- **Gemini**: `gemini-pro`, `gemini-pro-vision`

### Retrieval Configuration

- `TOP_K_RESULTS`: Number of similar documents to retrieve (default: 7)
- `VECTOR_STORE_PATH`: Path to store FAISS index
- `DOCUMENTS_PATH`: Path to document files

## 🧪 Testing

### Test the API

1. Start the server:
   ```bash
   python app.py
   ```

2. Test health endpoint:
   ```bash
   curl http://localhost:8000/health
   ```

3. Test chat endpoint:
   ```bash
   curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"question": "Hello, what can you tell me?"}'
   ```

## 🐛 Troubleshooting

### Common Issues

1. **"No documents found" error**:
   - Ensure PDF/DOCX files are in the `documents/` directory
   - Check file permissions

2. **"API key not set" error**:
   - Verify your `.env` file exists and contains the correct API key
   - Check that the API key variable name matches your LLM provider

3. **"Vector store not found" error**:
   - The vector store is created automatically on first run
   - Ensure write permissions in the project directory

4. **Import errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+)

## 📝 Development Notes

### Rebuilding Vector Store

To rebuild the vector store (e.g., after adding new documents):

1. Delete the `vector_store/` directory
2. Restart the application - it will rebuild automatically

Or modify `app.py` to call `initialize_vector_store(force_rebuild=True)`

### Adding New Document Types

To support additional document types, modify `vector_store_manager.py`:
- Add new loader imports from `langchain_community.document_loaders`
- Add file extension handling in `DocumentLoader.load_documents()`

## 📚 Dependencies

- **FastAPI**: Modern web framework for building APIs
- **LangChain**: Framework for LLM applications
- **FAISS**: Vector similarity search library
- **OpenAI/Gemini**: LLM providers
- **PyPDF**: PDF document loading
- **python-docx**: DOCX document loading

## 📄 License

This project is provided as-is for assessment purposes.

## 🤝 Contributing

This is an assessment project. For production use, consider:
- Adding authentication/authorization
- Implementing proper session management (Redis/database)
- Adding rate limiting
- Implementing logging and monitoring
- Adding unit tests
- Optimizing vector store performance for large document sets

## 📧 Support

For issues or questions, please refer to the project documentation or contact the development team.

---

**Built with ❤️ using FastAPI, LangChain, and FAISS**

