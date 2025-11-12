"""
Utility script to download sample documents for testing.

This script downloads publicly available documents (Wikipedia articles, research papers)
to populate the documents directory for testing the RAG chatbot.
"""

import os
import requests
from pathlib import Path


def download_file(url: str, filepath: str):
    """Download a file from URL."""
    print(f"Downloading {filepath}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✓ Downloaded {filepath}")


def setup_sample_documents():
    """Download sample documents for testing."""
    documents_dir = Path("documents")
    documents_dir.mkdir(exist_ok=True)
    
    # Sample documents (you can replace these with your own URLs)
    sample_docs = [
        {
            "url": "https://arxiv.org/pdf/1706.03762.pdf",  # Attention Is All You Need
            "filename": "attention_is_all_you_need.pdf"
        },
        # Add more sample documents here
    ]
    
    print("Setting up sample documents...")
    print("Note: You can add your own PDF/DOCX files to the documents/ directory")
    
    for doc in sample_docs:
        filepath = documents_dir / doc["filename"]
        if not filepath.exists():
            try:
                download_file(doc["url"], str(filepath))
            except Exception as e:
                print(f"Error downloading {doc['filename']}: {e}")
        else:
            print(f"✓ {doc['filename']} already exists")
    
    print("\nSample documents setup complete!")
    print(f"Documents directory: {documents_dir.absolute()}")
    print("You can add more PDF or DOCX files to this directory.")


if __name__ == "__main__":
    setup_sample_documents()

