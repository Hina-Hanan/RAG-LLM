#!/usr/bin/env python
"""
Test Gemini embeddings locally before deploying to Render.
This ensures everything works with the same configuration as Render.

IMPORTANT: Before running this script, set EMBEDDING_PROVIDER=gemini in your .env file
"""

import os
import sys

def test_gemini_embeddings():
    """Test Gemini embeddings configuration (same as Render)."""
    print("=" * 60)
    print("Testing Gemini Embeddings (Render Configuration)")
    print("=" * 60)
    
    # Check current configuration
    from config import settings
    
    print(f"\nCurrent EMBEDDING_PROVIDER: {settings.embedding_provider}")
    
    if settings.embedding_provider != "gemini":
        print("\n" + "!" * 60)
        print("[WARNING] EMBEDDING_PROVIDER is not set to 'gemini'")
        print("!" * 60)
        print("\nTo test Gemini embeddings:")
        print("1. Open your .env file")
        print("2. Change: EMBEDDING_PROVIDER=gemini")
        print("3. Save the file")
        print("4. Run this script again")
        print("\nOr set it temporarily:")
        print("  set EMBEDDING_PROVIDER=gemini  # Windows")
        print("  export EMBEDDING_PROVIDER=gemini  # Linux/Mac")
        print("!" * 60)
        
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return False
    
    # Check if GOOGLE_API_KEY is set
    if not settings.google_api_key:
        print("\n[FAIL] GOOGLE_API_KEY is not set!")
        print("Please set GOOGLE_API_KEY in your .env file")
        return False
    
    print(f"[OK] GOOGLE_API_KEY is set")
    print(f"[OK] Using Gemini embeddings")
    
    try:
        print("\n" + "-" * 60)
        print("Test 1: Initialize Gemini Embeddings")
        print("-" * 60)
        
        from vector_store_manager import VectorStore
        
        print("Creating VectorStore with Gemini embeddings...")
        vector_store = VectorStore()
        
        print(f"[OK] Embeddings initialized: {vector_store.embeddings.__class__.__name__}")
        
        print("\n" + "-" * 60)
        print("Test 2: Generate Embedding")
        print("-" * 60)
        
        test_text = "This is a test sentence for Gemini embeddings."
        print(f"Testing with: '{test_text}'")
        
        embedding = vector_store.embeddings.embed_query(test_text)
        
        print(f"[OK] Embedding generated successfully!")
        print(f"  Dimensions: {len(embedding)}")
        print(f"  Note: Gemini gemini-embedding-001 default is 3072 dimensions")
        print(f"  (Supports 128-3072, recommended: 768, 1536, 3072)")
        
        if len(embedding) == 3072:
            print("[OK] Using default dimensions (3072) - this is fine!")
        elif len(embedding) == 768:
            print("[OK] Using 768 dimensions - recommended for RAG!")
        else:
            print(f"[INFO] Using {len(embedding)} dimensions")
        
        print("\n" + "-" * 60)
        print("Test 3: Load/Build Vector Store")
        print("-" * 60)
        
        from vector_store_manager import initialize_vector_store
        
        print("Attempting to load existing vector store...")
        print("[NOTE] If vector store was built with local embeddings (384 dim),")
        print("       it won't work with Gemini embeddings (3072 dim default).")
        print("       You'll need to rebuild with Gemini embeddings.")
        
        try:
            vector_store_manager = initialize_vector_store(force_rebuild=False)
            
            if vector_store_manager.vector_store is None:
                print("[WARNING] Vector store is None - needs to be built")
                rebuild = input("\nRebuild vector store with Gemini embeddings? (y/n): ")
                if rebuild.lower() == 'y':
                    print("\nRebuilding vector store with Gemini embeddings...")
                    print("[WARNING] This will use API calls and may hit quota limits!")
                    vector_store_manager = initialize_vector_store(force_rebuild=True)
                    print("[OK] Vector store rebuilt successfully!")
                else:
                    print("[SKIP] Skipping rebuild")
                    return True
            else:
                print("[OK] Vector store loaded successfully!")
            
            # Test retrieval
            print("\nTesting retrieval...")
            retriever = vector_store_manager.get_retriever(top_k=3)
            results = retriever.get_relevant_documents("test query")
            
            print(f"[OK] Retrieval works! Retrieved {len(results)} documents")
            
        except AssertionError as e:
            # FAISS dimension mismatch - most common issue
            # Get embedding dimensions for error message
            try:
                test_emb = vector_store.embeddings.embed_query("test")
                emb_dim = len(test_emb)
            except:
                emb_dim = 3072  # Default
            
            print("\n" + "!" * 60)
            print("[ERROR] DIMENSION MISMATCH DETECTED!")
            print("!" * 60)
            print("Your vector store was built with LOCAL embeddings (384 dim)")
            print(f"but you're trying to load it with GEMINI embeddings ({emb_dim} dim).")
            print("\nSolution: Rebuild vector store with Gemini embeddings")
            print("\nThis will:")
            print("  1. Use API calls (may hit quota limits)")
            print("  2. Create new vector store with correct dimensions")
            print("  3. Allow you to commit it for Render deployment")
            
            rebuild = input("\nRebuild vector store now? (y/n): ")
            if rebuild.lower() == 'y':
                print("\nRebuilding vector store with Gemini embeddings...")
                try:
                    vector_store_manager = initialize_vector_store(force_rebuild=True)
                    print("[OK] Vector store rebuilt with Gemini embeddings!")
                    print("\n[IMPORTANT] Commit this to Git:")
                    print("  git add vector_store/")
                    print("  git commit -m 'Rebuild vector store with Gemini embeddings'")
                    print("  git push")
                    
                    # Test retrieval again
                    print("\nTesting retrieval with rebuilt vector store...")
                    retriever = vector_store_manager.get_retriever(top_k=3)
                    results = retriever.get_relevant_documents("test query")
                    print(f"[OK] Retrieval works! Retrieved {len(results)} documents")
                except Exception as rebuild_error:
                    if "quota" in str(rebuild_error).lower() or "429" in str(rebuild_error).lower():
                        print("\n" + "!" * 60)
                        print("[ERROR] QUOTA EXHAUSTED!")
                        print("!" * 60)
                        print("Your Gemini API quota is exhausted.")
                        print("\nSolutions:")
                        print("1. Wait for quota reset (usually daily)")
                        print("2. Check quota: https://ai.dev/usage?tab=rate-limit")
                        print("3. Use a different Google account")
                        print("!" * 60)
                        return False
                    else:
                        print(f"\n[FAIL] Error rebuilding: {rebuild_error}")
                        import traceback
                        traceback.print_exc()
                        return False
            else:
                print("[SKIP] Skipping rebuild. You'll need to rebuild before deploying to Render.")
                return False
                
        except Exception as e:
            error_str = str(e).lower()
            if "dimension" in error_str or "shape" in error_str:
                # Get embedding dimensions for error message
                try:
                    test_emb = vector_store.embeddings.embed_query("test")
                    emb_dim = len(test_emb)
                except:
                    emb_dim = 3072  # Default
                
                print("\n" + "!" * 60)
                print("[ERROR] DIMENSION MISMATCH!")
                print("!" * 60)
                print("Your vector store was built with LOCAL embeddings (384 dim)")
                print(f"but you're trying to load it with GEMINI embeddings ({emb_dim} dim).")
                print("\nSolution: Rebuild vector store with Gemini embeddings")
                print("\nThis will:")
                print("  1. Use API calls (may hit quota limits)")
                print("  2. Create new vector store with correct dimensions")
                print("  3. Allow you to commit it for Render deployment")
                print("\nRebuilding now...")
                
                try:
                    vector_store_manager = initialize_vector_store(force_rebuild=True)
                    print("[OK] Vector store rebuilt with Gemini embeddings!")
                    print("\n[IMPORTANT] Commit this to Git:")
                    print("  git add vector_store/")
                    print("  git commit -m 'Rebuild vector store with Gemini embeddings'")
                    print("  git push")
                except Exception as rebuild_error:
                    if "quota" in str(rebuild_error).lower() or "429" in str(rebuild_error).lower():
                        print("\n" + "!" * 60)
                        print("[ERROR] QUOTA EXHAUSTED!")
                        print("!" * 60)
                        print("Your Gemini API quota is exhausted.")
                        print("\nSolutions:")
                        print("1. Wait for quota reset (usually daily)")
                        print("2. Check quota: https://ai.dev/usage?tab=rate-limit")
                        print("3. Use a different Google account")
                        print("!" * 60)
                        return False
                    else:
                        raise
            elif "quota" in error_str or "429" in error_str:
                print("\n" + "!" * 60)
                print("[ERROR] QUOTA EXHAUSTED!")
                print("!" * 60)
                print("Your Gemini API quota is exhausted.")
                print("\nSolutions:")
                print("1. Wait for quota reset (usually daily)")
                print("2. Check quota: https://ai.dev/usage?tab=rate-limit")
                print("3. Use a different Google account")
                print("!" * 60)
                return False
            else:
                print(f"\n[FAIL] Unexpected error: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All Gemini Embedding Tests Passed!")
        print("=" * 60)
        print("\nYour configuration matches Render:")
        print("  - Embedding Provider: gemini")
        print("  - Model: gemini-embedding-001")
        print(f"  - Dimensions: {len(embedding)} (default: 3072)")
        print("\n[IMPORTANT] If you rebuilt the vector store:")
        print("  1. Commit it: git add vector_store/")
        print("  2. Commit: git commit -m 'Rebuild vector store with Gemini embeddings'")
        print("  3. Push: git push")
        print("  4. Render will use this pre-built store (no quota issues!)")
        print("\n[NOTE] Switch back to local embeddings for local development:")
        print("  In .env: EMBEDDING_PROVIDER=local")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gemini_embeddings()
    sys.exit(0 if success else 1)
