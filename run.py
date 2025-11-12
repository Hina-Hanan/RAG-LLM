"""
Quick start script for RAG Chatbot

This script helps set up and run the RAG chatbot application.
"""

import os
import sys
from pathlib import Path


def check_environment():
    """Check if environment is properly set up."""
    print("Checking environment...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠ Warning: .env file not found!")
        print("Please copy env.example to .env and fill in your API keys.")
        return False
    
    # Check if documents directory exists
    docs_dir = Path("documents")
    if not docs_dir.exists():
        print(f"Creating documents directory...")
        docs_dir.mkdir(exist_ok=True)
        print("⚠ Please add PDF or DOCX files to the documents/ directory")
    
    # Check if documents exist
    pdf_files = list(docs_dir.glob("*.pdf"))
    docx_files = list(docs_dir.glob("*.docx"))
    
    if not pdf_files and not docx_files:
        print("⚠ Warning: No PDF or DOCX files found in documents/ directory")
        print("The application will fail to start without documents.")
        print("You can:")
        print("  1. Add PDF/DOCX files to the documents/ directory")
        print("  2. Run python setup_documents.py to download sample documents")
        return False
    
    print(f"✓ Found {len(pdf_files)} PDF files and {len(docx_files)} DOCX files")
    return True


def main():
    """Main function."""
    print("=" * 60)
    print("RAG Chatbot - Quick Start")
    print("=" * 60)
    print()
    
    # Check environment
    if not check_environment():
        print()
        print("Setup incomplete. Please fix the issues above.")
        sys.exit(1)
    
    print()
    print("Environment check passed!")
    print()
    print("Starting RAG Chatbot API server...")
    print("API will be available at http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    # Import and run the app
    try:
        from app import main as run_app
        run_app()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
    except Exception as e:
        print(f"\n\nError starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

