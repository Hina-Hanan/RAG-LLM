# Render Deployment Troubleshooting Guide

## Common Issues and Solutions

### Issue: Deployment Times Out or Fails After Long Build

**Symptoms:**
- Build completes successfully
- Deployment starts but fails after 60-90 seconds
- Error: "Deployment failed" or "Timeout"

**Causes:**
1. **Downloading embedding model takes too long** (sentence-transformers)
2. **Building vector store from documents** (if no pre-built store exists)
3. **Render free tier timeout** (90 seconds)
4. **Memory limits** (512MB on free tier)

**Solutions:**

#### 1. Pre-build Vector Store Locally

Before deploying, build your vector store locally and commit it:

```bash
# Build vector store locally
python -c "from vector_store_manager import initialize_vector_store; initialize_vector_store()"

# Commit the vector_store folder
git add vector_store/
git commit -m "Add pre-built vector store"
git push
```

This way, Render won't need to rebuild it.

#### 2. Pre-download Embedding Model

The first time `sentence-transformers` runs, it downloads the model (~90MB). This can timeout on Render.

**Option A:** Pre-download locally and commit (not recommended - large files)

**Option B:** Use a smaller model:
```env
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2  # Smallest, fastest
```

#### 3. Reduce Document Size

If you have large documents:
- Split them into smaller files
- Use fewer documents initially
- Optimize PDFs (remove images, compress)

#### 4. Upgrade Render Plan

Free tier has limitations:
- 512MB RAM
- 90-second timeout
- Spins down after inactivity

Consider upgrading to Starter plan ($7/month) for:
- 512MB RAM (same)
- Longer timeouts
- Always-on service

#### 5. Check Build Logs

In Render dashboard, check:
1. **Build Logs**: Look for errors during `pip install`
2. **Deploy Logs**: Look for errors during startup
3. **Runtime Logs**: Check for memory errors

### Issue: "No documents found"

**Solution:**
- Make sure `documents/` folder is committed to Git
- Check `DOCUMENTS_PATH` environment variable
- Verify PDF/DOCX files are in the repository

### Issue: Memory Errors

**Symptoms:**
- "Killed" or "Out of memory" errors
- App crashes during startup

**Solutions:**
1. Use smaller embedding model: `all-MiniLM-L6-v2`
2. Reduce number of documents
3. Reduce chunk size in `vector_store_manager.py`
4. Upgrade Render plan

### Issue: Slow First Request

**Normal Behavior:**
- Free tier spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- This is expected on free tier

**Solution:**
- Upgrade to paid plan for always-on service
- Or accept the cold start delay

## Optimization Tips

### 1. Commit Pre-built Vector Store

```bash
# Build locally
python app.py  # Let it initialize

# Commit vector_store folder
git add vector_store/
git commit -m "Add pre-built vector store"
git push
```

### 2. Use Smaller Embedding Model

In `render.yaml` or environment variables:
```yaml
LOCAL_EMBEDDING_MODEL: all-MiniLM-L6-v2
```

### 3. Reduce Chunk Size

In `vector_store_manager.py`, reduce chunk size:
```python
chunk_size=500,  # Instead of 1000
chunk_overlap=100,  # Instead of 200
```

### 4. Limit Documents Initially

Start with 1-2 small documents, then add more.

### 5. Monitor Logs

Always check Render logs to see where it's failing:
- Build phase errors
- Startup phase errors
- Runtime errors

## Deployment Checklist

Before deploying to Render:

- [ ] All code committed and pushed to GitHub
- [ ] `.env` file NOT committed (use Render environment variables)
- [ ] `requirements.txt` updated with correct versions
- [ ] `runtime.txt` specifies Python 3.11.9
- [ ] Vector store pre-built (optional but recommended)
- [ ] Documents folder committed (if using Git)
- [ ] Environment variables set in Render dashboard
- [ ] `GOOGLE_API_KEY` set in Render (marked as secret)

## Quick Fixes

### If deployment keeps failing:

1. **Check logs first** - Most issues are visible in logs
2. **Start simple** - Deploy with minimal documents first
3. **Test locally** - Make sure `python app.py` works locally
4. **Verify environment variables** - All required vars are set
5. **Check Python version** - Use 3.11.9 (specified in runtime.txt)

## Getting Help

If issues persist:

1. Check Render logs (most important!)
2. Test locally first: `python app.py`
3. Verify all environment variables are set
4. Check Render status page: https://status.render.com
5. Review Render docs: https://render.com/docs

## Expected Startup Time

- **First deployment**: 5-10 minutes (downloading dependencies + model)
- **Subsequent deployments**: 2-5 minutes
- **After spin-down**: 30-60 seconds (cold start)

If startup takes longer than 5 minutes, check logs for errors.

