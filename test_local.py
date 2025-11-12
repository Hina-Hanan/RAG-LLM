#!/usr/bin/env python
"""
Local testing script for RAG Chatbot.
Tests embeddings, vector store, and LLM initialization.
"""

import os
import sys

def test_imports():
    """Test if all required packages are installed."""
    print("=" * 60)
    print("Testing Imports")
    print("=" * 60)
    
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("langchain", "LangChain"),
        ("langchain_google_genai", "LangChain Google GenAI"),
        ("faiss", "FAISS"),
        ("pypdf", "PyPDF"),
        ("docx", "python-docx"),
    ]
    
    missing = []
    for module_name, display_name in required_packages:
        try:
            __import__(module_name)
            print(f"[OK] {display_name}")
        except ImportError:
            print(f"[FAIL] {display_name} - MISSING")
            missing.append(display_name)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("\n[OK] All required packages installed!")
    return True

def test_env_variables():
    """Test if environment variables are set."""
    print("\n" + "=" * 60)
    print("Testing Environment Variables")
    print("=" * 60)
    
    from config import settings
    
    print(f"LLM_PROVIDER: {settings.llm_provider}")
    print(f"EMBEDDING_PROVIDER: {settings.embedding_provider}")
    print(f"MODEL_NAME: {settings.model_name}")
    
    if settings.llm_provider == "gemini":
        if settings.google_api_key:
            print("[OK] GOOGLE_API_KEY is set")
        else:
            print("[FAIL] GOOGLE_API_KEY is NOT set")
            return False
    
    if settings.embedding_provider == "gemini":
        if settings.google_api_key:
            print("[OK] GOOGLE_API_KEY is set (needed for Gemini embeddings)")
        else:
            print("[FAIL] GOOGLE_API_KEY is NOT set (needed for Gemini embeddings)")
            return False
    
    if settings.embedding_provider == "local":
        try:
            import sentence_transformers
            print("[OK] sentence-transformers is installed (for local embeddings)")
        except ImportError:
            print("[FAIL] sentence-transformers is NOT installed")
            print("  Install with: pip install sentence-transformers")
            return False
    
    print("\n[OK] Environment variables configured!")
    return True

def test_embeddings():
    """Test embedding generation."""
    print("\n" + "=" * 60)
    print("Testing Embeddings")
    print("=" * 60)
    
    try:
        from vector_store_manager import VectorStore
        
        print("Initializing embeddings...")
        vector_store = VectorStore()
        
        print("Testing embedding generation...")
        test_text = "This is a test sentence for embedding."
        embedding = vector_store.embeddings.embed_query(test_text)
        
        print(f"[OK] Embedding generated successfully!")
        print(f"  Dimensions: {len(embedding)}")
        print(f"  Provider: {vector_store.embeddings.__class__.__name__}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error testing embeddings: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_documents():
    """Test document loading."""
    print("\n" + "=" * 60)
    print("Testing Document Loading")
    print("=" * 60)
    
    try:
        from vector_store_manager import DocumentLoader
        from config import settings
        
        loader = DocumentLoader()
        documents = loader.load_documents(settings.documents_path)
        
        if not documents:
            print(f"[WARNING] No documents found in {settings.documents_path}")
            print("  Add PDF or DOCX files to test document loading")
            return False
        
        print(f"[OK] Loaded {len(documents)} document(s)")
        for i, doc in enumerate(documents, 1):
            print(f"  Document {i}: {len(doc.page_content)} characters")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error loading documents: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vector_store():
    """Test vector store initialization."""
    print("\n" + "=" * 60)
    print("Testing Vector Store")
    print("=" * 60)
    
    try:
        from vector_store_manager import initialize_vector_store
        
        print("Initializing vector store...")
        vector_store = initialize_vector_store(force_rebuild=False)
        
        if vector_store.vector_store is None:
            print("[WARNING] Vector store is None (may need to build)")
            return False
        
        print("[OK] Vector store initialized successfully!")
        
        # Test retrieval
        print("\nTesting retrieval...")
        retriever = vector_store.get_retriever(top_k=3)
        results = retriever.get_relevant_documents("test query")
        
        print(f"[OK] Retrieval works! Retrieved {len(results)} documents")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error testing vector store: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm():
    """Test LLM initialization."""
    print("\n" + "=" * 60)
    print("Testing LLM")
    print("=" * 60)
    
    try:
        from llm_manager import LLMManager
        
        print("Initializing LLM manager...")
        llm_manager = LLMManager()
        
        print("[OK] LLM manager initialized successfully!")
        print(f"  Provider: {llm_manager.llm.__class__.__name__}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error testing LLM: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_chain():
    """Test the full RAG chain."""
    print("\n" + "=" * 60)
    print("Testing Full RAG Chain")
    print("=" * 60)
    
    try:
        from vector_store_manager import initialize_vector_store
        from llm_manager import LLMManager
        
        print("Initializing vector store...")
        vector_store = initialize_vector_store(force_rebuild=False)
        
        print("Initializing LLM...")
        llm_manager = LLMManager()
        
        print("Creating retrieval chain...")
        retriever = vector_store.get_retriever(top_k=3)
        llm_manager.create_retrieval_chain(retriever)
        
        print("Testing query...")
        test_query = "What is this document about?"
        response = llm_manager.query(test_query)
        
        print(f"[OK] Query successful!")
        answer = response.get("answer", "No answer")
        print(f"\nResponse preview: {answer[:200]}...")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error testing full chain: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("RAG Chatbot - Local Testing")
    print("=" * 60)
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    if not results[-1][1]:
        print("\n[FAIL] Please install missing packages first!")
        sys.exit(1)
    
    # Test 2: Environment variables
    results.append(("Environment Variables", test_env_variables()))
    if not results[-1][1]:
        print("\n[FAIL] Please configure environment variables in .env file!")
        sys.exit(1)
    
    # Test 3: Embeddings
    results.append(("Embeddings", test_embeddings()))
    
    # Test 4: Documents
    results.append(("Documents", test_documents()))
    
    # Test 5: Vector Store
    if results[-1][1]:  # Only test if documents exist
        results.append(("Vector Store", test_vector_store()))
    
    # Test 6: LLM
    results.append(("LLM", test_llm()))
    
    # Test 7: Full Chain
    if results[-2][1] and results[-1][1]:  # Only if vector store and LLM work
        results.append(("Full RAG Chain", test_full_chain()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYou can now run the app with:")
        print("  python app.py")
        print("\nThen visit: http://localhost:8000")
    else:
        print("\n" + "=" * 60)
        print("[WARNING] SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease fix the issues above before running the app.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

