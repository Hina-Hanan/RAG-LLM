# LangChain 1.0+ Compatibility Fixes

## Summary

Fixed all LangChain 1.0+ import compatibility issues. LangChain 1.0+ reorganized modules into separate packages.

## Changes Made

### 1. `vector_store_manager.py`
- ✅ Fixed: `langchain.text_splitter` → `langchain_text_splitters`
- ✅ Fixed: `langchain.schema` → `langchain_core.documents`
- ✅ Fixed: `langchain.embeddings.base` → `langchain_core.embeddings`
- ✅ Fixed: Made `sentence_transformers` import conditional (only when using local embeddings)

### 2. `llm_manager.py`
- ✅ Fixed: `langchain.chains` → `langchain_classic.chains` (with fallback)
- ✅ Fixed: Moved imports inside method (lazy loading)

### 3. `memory_manager.py`
- ✅ Fixed: `langchain.memory` → `langchain_classic.memory` (with fallback)
- ✅ Fixed: `langchain.schema` → `langchain_core.messages`

### 4. `requirements.txt`
- ✅ Added: `langchain-classic>=1.0.0` (required for chains and memory in LangChain 1.0+)
- ✅ Added: `langchain-text-splitters>=0.0.1` (required for text splitting)

## Import Compatibility Strategy

All imports now use try/except with fallbacks:

```python
# Try LangChain 1.0+ first
try:
    from langchain_classic.module import Class
except ImportError:
    # Fallback to older versions
    from langchain.module import Class
```

This ensures compatibility with both:
- LangChain 1.0+ (Render, newer installs)
- LangChain 0.x (older local installs)

## Testing

After these fixes, the app should:
- ✅ Deploy successfully on Render
- ✅ Work with LangChain 1.0.5+ (what Render installs)
- ✅ Still work locally with older LangChain versions

## Next Steps

1. Commit all changes
2. Push to GitHub
3. Render will auto-deploy
4. Should work without import errors!

## Alternative: GCP Deployment

If Render continues to have issues, see `GCP_DEPLOY.md` for:
- Cloud Run deployment (serverless, 2GB RAM)
- App Engine deployment
- Compute Engine VM deployment
- All support local embeddings without memory issues

