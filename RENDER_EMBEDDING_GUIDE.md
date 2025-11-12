# Render Embedding Configuration Guide

## Which Embedding Works on Render?

**Answer: Gemini Embeddings** ✅

### Current Render Configuration

Looking at `render.yaml`:
```yaml
EMBEDDING_PROVIDER=gemini
```

**Render uses Gemini embeddings** because:
1. ✅ **Low Memory**: ~150MB RAM (fits in 512MB free tier)
2. ✅ **No Heavy Dependencies**: Doesn't need sentence-transformers (~500MB)
3. ✅ **API-Based**: No local model downloads
4. ⚠️ **Quota Limits**: Free tier has daily/minute limits

### Why NOT Local Embeddings on Render?

**Local embeddings (sentence-transformers) won't work** on Render free tier:
- ❌ Requires ~500MB RAM (sentence-transformers + PyTorch)
- ❌ Render free tier only has 512MB total RAM
- ❌ Would exceed memory limit and crash

**Solution**: Use Gemini embeddings on Render, local embeddings locally.

---

## Do You Need to Test Gemini Embeddings Locally?

**YES! Highly Recommended** ✅

### Why Test Locally?

1. **Verify Quota**: Check if you have API quota available
2. **Dimension Compatibility**: Ensure vector store dimensions match
3. **Avoid Deployment Failures**: Catch issues before deploying
4. **Pre-Build Vector Store**: Build locally and commit to Git (avoids quota on Render)

---

## How to Test Gemini Embeddings Locally

### Option 1: Quick Test Script

Run the test script:
```bash
python test_gemini_embeddings_local.py
```

This will:
- ✅ Test Gemini embeddings initialization
- ✅ Generate a test embedding
- ✅ Check dimensions (should be 768)
- ✅ Test vector store loading/building
- ✅ Handle dimension mismatches
- ✅ Detect quota issues

### Option 2: Manual Test

1. **Temporarily switch to Gemini embeddings**:
   ```bash
   # In .env file, change:
   EMBEDDING_PROVIDER=gemini
   ```

2. **Test embeddings**:
   ```bash
   python -c "from vector_store_manager import VectorStore; vs = VectorStore(); emb = vs.embeddings.embed_query('test'); print(f'Dimensions: {len(emb)}')"
   ```
   
   Expected output: `Dimensions: 768`

3. **Test vector store**:
   ```bash
   python -c "from vector_store_manager import initialize_vector_store; vs = initialize_vector_store(force_rebuild=False)"
   ```

4. **If dimension mismatch** (vector store built with local embeddings):
   ```bash
   # Rebuild with Gemini embeddings
   python -c "from vector_store_manager import initialize_vector_store; initialize_vector_store(force_rebuild=True)"
   ```

5. **Switch back to local** (for local development):
   ```bash
   # In .env file:
   EMBEDDING_PROVIDER=local
   ```

---

## Important: Embedding Dimensions Must Match!

### Dimension Mismatch Problem

| Embedding Provider | Dimensions | Compatible? |
|-------------------|------------|-------------|
| Local (sentence-transformers) | 384 | ❌ Cannot mix |
| Gemini (gemini-embedding-001) | 768 | ❌ Cannot mix |
| OpenAI | 1536 | ❌ Cannot mix |

**Rule**: Vector store must be built and loaded with the **same embedding provider**.

### Current Situation

- **Your local vector store**: Built with `local` embeddings (384 dim)
- **Render configuration**: Uses `gemini` embeddings (768 dim)
- **Problem**: Dimensions don't match! ❌

### Solution: Pre-Build with Gemini Embeddings

1. **Test Gemini embeddings locally** (using test script)
2. **Rebuild vector store** with Gemini embeddings:
   ```bash
   # Set EMBEDDING_PROVIDER=gemini in .env
   python build_vector_store.py
   ```
3. **Commit to Git**:
   ```bash
   git add vector_store/
   git commit -m "Rebuild vector store with Gemini embeddings for Render"
   git push
   ```
4. **Deploy on Render**: Will load pre-built store (no quota issues!)

---

## Testing Checklist

Before deploying to Render:

- [ ] Test Gemini embeddings locally (`test_gemini_embeddings_local.py`)
- [ ] Verify quota is available (check: https://ai.dev/usage?tab=rate-limit)
- [ ] Rebuild vector store with Gemini embeddings (if needed)
- [ ] Test full RAG chain with Gemini embeddings
- [ ] Commit pre-built vector store to Git
- [ ] Verify `render.yaml` has `EMBEDDING_PROVIDER=gemini`

---

## Summary

### Render Configuration
- ✅ **Embedding Provider**: `gemini` (configured in render.yaml)
- ✅ **Model**: `gemini-embedding-001` (768 dimensions)
- ✅ **Memory**: ~150MB (fits in free tier)

### Local Testing
- ✅ **Test Gemini embeddings** before deploying
- ✅ **Rebuild vector store** with Gemini embeddings
- ✅ **Commit pre-built store** to avoid quota issues on Render

### Best Practice
1. **Local Development**: Use `local` embeddings (faster, no API calls)
2. **Render Deployment**: Use `gemini` embeddings (low memory)
3. **Pre-Build**: Build vector store with Gemini locally, commit to Git
4. **Result**: Render loads pre-built store (no API calls, no quota issues!)

---

## Quick Commands

```bash
# Test Gemini embeddings
python test_gemini_embeddings_local.py

# Rebuild vector store with Gemini (if test passes)
# Set EMBEDDING_PROVIDER=gemini in .env first
python build_vector_store.py

# Commit pre-built store
git add vector_store/
git commit -m "Pre-built vector store with Gemini embeddings"
git push
```

Now you're ready to deploy to Render! 🚀

