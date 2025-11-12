#!/usr/bin/env python
"""
Script to pre-build vector store locally.
This avoids quota issues on Render by committing a pre-built vector store.

Usage:
    python build_vector_store.py
"""

import os
import sys

def main():
    print("=" * 60)
    print("Vector Store Builder for Render Deployment")
    print("=" * 60)
    print("\nThis script builds the vector store locally so Render")
    print("doesn't need to call the embedding API (saves quota).\n")
    
    # Check current embedding provider
    current_provider = os.getenv("EMBEDDING_PROVIDER", "local")
    print(f"Current EMBEDDING_PROVIDER: {current_provider}")
    
    if current_provider == "gemini":
        print("\n⚠ WARNING: You're using Gemini embeddings.")
        print("This will use API calls and may hit quota limits.")
        print("\nChecking quota status...")
        
        # Try a test embedding to check quota
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            from config import settings
            test_emb = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=settings.google_api_key
            )
            test_emb.embed_query("test")
            print("✓ Quota available - proceeding with build")
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e).lower():
                print("\n" + "!" * 60)
                print("✗ QUOTA EXHAUSTED!")
                print("!" * 60)
                print("\nYour Gemini API quota is exhausted.")
                print("\nSolutions:")
                print("1. Wait for daily quota reset (usually midnight PST)")
                print("   Check: https://ai.dev/usage?tab=rate-limit")
                print("\n2. Use local embeddings instead:")
                print("   - Set EMBEDDING_PROVIDER=local in .env")
                print("   - Install: pip install sentence-transformers")
                print("   - Run this script again")
                print("   - Note: Render will need sentence-transformers too")
                print("\n3. Use a different Google account with fresh quota")
                print("!" * 60)
                return
            else:
                print(f"⚠ Warning: {e}")
                response = input("\nContinue anyway? (y/n): ")
                if response.lower() != 'y':
                    print("Cancelled.")
                    return
    
    print("\nBuilding vector store...")
    print("-" * 60)
    
    try:
        from vector_store_manager import initialize_vector_store
        
        # Build the vector store
        vector_store = initialize_vector_store(force_rebuild=True)
        
        print("\n" + "=" * 60)
        print("✓ SUCCESS: Vector store built successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Commit the vector_store/ folder:")
        print("   git add vector_store/")
        print("   git commit -m 'Add pre-built vector store'")
        print("   git push")
        print("\n2. On Render, the app will load this pre-built store")
        print("   (no API calls needed, no quota issues!)")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ ERROR: Failed to build vector store")
        print("=" * 60)
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("- Check that documents/ folder has PDF/DOCX files")
        print("- Verify EMBEDDING_PROVIDER is set correctly")
        print("- If using local embeddings, ensure sentence-transformers is installed")
        print("- If using Gemini, check API quota at https://ai.dev/usage")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()

