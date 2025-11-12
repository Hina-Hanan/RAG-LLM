# Quick Start Guide

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] API key for your chosen LLM provider (OpenAI, Gemini, or Hugging Face)
- [ ] PDF or DOCX documents to index

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file:
```bash
# Windows
copy env.example .env

# Linux/Mac
cp env.example .env
```

Edit `.env` and add your API key:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-api-key-here
MODEL_NAME=gpt-3.5-turbo
```

### 3. Add Documents

Place your PDF or DOCX files in the `documents/` directory:
```bash
mkdir documents
# Copy your PDF/DOCX files to documents/
```

Or download sample documents:
```bash
python setup_documents.py
```

### 4. Run the Application

Option 1: Using the quick start script:
```bash
python run.py
```

Option 2: Directly with Python:
```bash
python app.py
```

Option 3: Using uvicorn:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Test the API

Open your browser and go to:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

Or test with cURL:
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?", "session_id": "test"}'
```

## Common Issues

### Issue: "No documents found"
**Solution**: Add PDF or DOCX files to the `documents/` directory

### Issue: "API key not set"
**Solution**: Check your `.env` file and ensure the API key is correct

### Issue: Import errors
**Solution**: Run `pip install -r requirements.txt` again

### Issue: Port already in use
**Solution**: Change `API_PORT` in `.env` or stop the process using port 8000

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Explore the API documentation at http://localhost:8000/docs

