# Free Tier Setup Guide - Render Deployment

## Problem: Quota Limits on Free Tier

**Gemini Embeddings Free Tier:**
- Daily quota: Limited (varies)
- Per-minute quota: Limited  
- **Issue**: Quota can be exhausted, causing deployment failures

**Render Free Tier:**
- RAM: 512MB (limited)
- **Issue**: Local embeddings (sentence-transformers) need ~500MB RAM

## Solution: Pre-Build Vector Store Locally

By building the vector store locally and committing it to Git, Render can:
- ✅ Load pre-built store (no API calls needed)
- ✅ Avoid quota limits
- ✅ Faster deployment (no embedding generation)
- ✅ Works with free tier

## Step-by-Step Setup

### Step 1: Build Vector Store Locally

**Option A: Using Local Embeddings (Recommended)**

1. **Install sentence-transformers locally:**
   ```bash
   pip install sentence-transformers>=2.2.0
   ```

2. **Set local embeddings in .env:**
   ```env
   EMBEDDING_PROVIDER=local
   ```

3. **Build the vector store:**
   ```bash
   python build_vector_store.py
   ```
   
   Or manually:
   ```bash
   python -c "from vector_store_manager import initialize_vector_store; initialize_vector_store(force_rebuild=True)"
   ```

**Option B: Using Gemini Embeddings (If quota available)**

1. **Set Gemini embeddings in .env:**
   ```env
   EMBEDDING_PROVIDER=gemini
   GOOGLE_API_KEY=your_key_here
   ```

2. **Build the vector store:**
   ```bash
   python build_vector_store.py
   ```

### Step 2: Commit Vector Store to Git

```bash
# Add the vector_store folder
git add vector_store/

# Commit
git commit -m "Add pre-built vector store for Render deployment"

# Push
git push origin main
```

**Important**: Make sure `vector_store/` is NOT in `.gitignore` (it's commented out by default)

### Step 3: Deploy on Render

1. **Push your code** (with vector_store folder)
2. **Set environment variables in Render:**
   - `EMBEDDING_PROVIDER=gemini` (or whatever you used to build)
   - `GOOGLE_API_KEY=your_key`
   - Other required vars

3. **Deploy** - Render will:
   - Load the pre-built vector store
   - Use same embedding provider to verify (but won't regenerate)
   - **No API calls needed for embeddings!**

## How It Works

### Local Build (Your Computer)
```
Documents → Local Embeddings → FAISS Index → Save to vector_store/
```

### Render Deployment
```
Pre-built vector_store/ → Load FAISS Index → Ready to use!
(No embedding generation, no API calls, no quota issues)
```

## Important Notes

### Embedding Provider Must Match

⚠️ **CRITICAL**: The embedding provider used to BUILD the vector store MUST match the one used to LOAD it.

**Why?** Different embedding models produce different vector dimensions:
- **Local (sentence-transformers)**: 384 dimensions
- **Gemini gemini-embedding-001**: 768 dimensions (recommended, supports 128-3072)
- **OpenAI**: 1536 dimensions

**Note**: `models/embedding-001` is deprecated and will be removed in October 2025. We now use `models/gemini-embedding-001` (stable model).

**Example:**
- Built with: `EMBEDDING_PROVIDER=local` (384 dim) → Must load with `local` (384 dim)
- Built with: `EMBEDDING_PROVIDER=gemini` (768 dim) → Must load with `gemini` (768 dim)

**But wait!** Render doesn't have sentence-transformers installed (we removed it to save memory).

### Solution: Build with Gemini, Load with Gemini (RECOMMENDED)

**Best approach for Render free tier:**

1. **Wait for quota reset** (if exhausted) OR use a different Google account
   - Check quota: https://ai.dev/usage?tab=rate-limit
   - Quotas reset daily (usually at midnight PST)

2. **Build locally with Gemini** (when quota is available):
   ```env
   EMBEDDING_PROVIDER=gemini
   GOOGLE_API_KEY=your_key
   ```
   ```bash
   python build_vector_store.py
   ```

3. **Commit vector_store/** folder:
   ```bash
   git add vector_store/
   git commit -m "Add pre-built vector store (Gemini embeddings)"
   git push
   ```

4. **Deploy on Render** with:
   ```yaml
   EMBEDDING_PROVIDER=gemini
   ```
   - Render loads pre-built store (dimensions match: 768 dim)
   - Uses Gemini embeddings only to verify (minimal/no API calls)
   - **No quota issues** - just loading, not generating embeddings!

### Alternative: Build with Local, Use Different Approach

If you want to use local embeddings:

1. **Build locally** with `EMBEDDING_PROVIDER=local`
2. **On Render**: You'd need sentence-transformers (exceeds 512MB)
3. **Solution**: Upgrade Render to Standard plan ($25/month) for 1GB RAM

## Troubleshooting

### Issue: "Quota exceeded" when building

**Solutions:**

1. **Wait for quota reset** (Recommended)
   - Quotas reset daily (check: https://ai.dev/usage?tab=rate-limit)
   - Usually resets at midnight PST
   - Build vector store after reset

2. **Use a different Google account**
   - Create new Google account
   - Get new API key from https://makersuite.google.com/app/apikey
   - Use fresh quota to build

3. **Use local embeddings** (Alternative)
   - Set `EMBEDDING_PROVIDER=local`
   - Install `sentence-transformers` locally
   - Build vector store (no API calls)
   - **BUT**: On Render, you'd need sentence-transformers too (exceeds 512MB)
   - **Solution**: Upgrade Render to Standard plan ($25/month) for 1GB RAM

### Issue: Vector store won't load on Render

**Causes:**
1. Embedding provider mismatch
2. Vector store not committed to Git
3. File path issues

**Solutions:**
1. Verify `EMBEDDING_PROVIDER` matches build time
2. Check `vector_store/` folder is in Git: `git ls-files vector_store/`
3. Verify paths in `render.yaml`

### Issue: Still hitting quota on Render

**If you pre-built the store:**
- Loading should use minimal/no API calls
- If still hitting quota, check Render logs
- May need to wait for quota reset

## Quick Reference

### For Render Free Tier (Recommended)

```bash
# 1. Build locally with Gemini (when quota available)
EMBEDDING_PROVIDER=gemini python build_vector_store.py

# 2. Commit
git add vector_store/
git commit -m "Pre-built vector store"
git push

# 3. Deploy on Render with EMBEDDING_PROVIDER=gemini
# Render will load pre-built store (no quota issues!)
```

### For Local Development

```bash
# Use local embeddings (better performance)
EMBEDDING_PROVIDER=local
pip install sentence-transformers
python app.py
```

## Summary

✅ **Pre-build vector store locally** → Commit to Git → Render loads it
✅ **No API calls during deployment** → No quota issues
✅ **Works with free tier** → Fits in 512MB RAM
✅ **Fast deployment** → No embedding generation needed

This is the best approach for Render free tier!

