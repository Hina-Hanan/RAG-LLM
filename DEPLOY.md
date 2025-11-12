# Deployment Guide for Render

This guide will help you deploy the RAG Chatbot to Render.

## Prerequisites

1. A GitHub account
2. A Render account (sign up at https://render.com)
3. Your Google Gemini API key

## Step 1: Prepare Your Repository

1. Make sure all files are committed to your Git repository:
   ```bash
   git add .
   git commit -m "Add frontend and deployment config"
   git push
   ```

2. Ensure your `.env` file is NOT committed (it should be in `.gitignore`)

## Step 2: Deploy to Render

### Option A: Using Render Dashboard (Recommended)

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"Web Service"**
3. **Connect your repository** (GitHub/GitLab/Bitbucket)
4. **Select your repository** from the list
5. **Configure the service**:
   - **Name**: `rag-chatbot` (or any name you prefer)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 75`
   - **Plan**: Free (or choose a paid plan)

6. **Add Environment Variables**:
   - `LLM_PROVIDER` = `gemini`
   - `EMBEDDING_PROVIDER` = `gemini` ⚠️ **MUST be `gemini` for Render free tier** (not `local`)
   - `MODEL_NAME` = `gemini-2.5-flash` (or `gemini-pro`)
   - `GOOGLE_API_KEY` = `your_actual_api_key_here`
   - `LOCAL_EMBEDDING_MODEL` = `all-MiniLM-L6-v2` (not used if EMBEDDING_PROVIDER=gemini)
   - `VECTOR_STORE_PATH` = `./vector_store`
   - `DOCUMENTS_PATH` = `./documents`
   - `TOP_K_RESULTS` = `7`
   
   **⚠️ IMPORTANT**: `EMBEDDING_PROVIDER` must be `gemini` (not `local`) because:
   - Local embeddings require sentence-transformers (~500MB RAM)
   - Render free tier only has 512MB RAM total
   - Using `local` would exceed memory limit and crash

7. **Click "Create Web Service"**

### Option B: Using render.yaml (Automatic)

If you have `render.yaml` in your repository:

1. Go to Render Dashboard
2. Click "New +" → "Blueprint"
3. Connect your repository
4. Render will automatically detect `render.yaml` and configure everything
5. You'll still need to add `GOOGLE_API_KEY` in the Environment Variables section

## Step 3: Pre-Build Vector Store (IMPORTANT for Free Tier!)

**⚠️ CRITICAL**: To avoid quota issues on Render free tier, pre-build your vector store locally:

### Why Pre-Build?

- **Avoids API quota limits** during deployment
- **Faster deployment** (no embedding generation)
- **Works reliably** on free tier

### How to Pre-Build:

**⚠️ CRITICAL**: Build with **Gemini embeddings** (not local) to match Render configuration!

1. **Build locally with Gemini embeddings**:
   ```bash
   # Set Gemini embeddings in .env
   # EMBEDDING_PROVIDER=gemini
   # GOOGLE_API_KEY=your_key_here
   
   # Build vector store (will use Gemini API - check quota first!)
   python build_vector_store.py
   ```
   
   **Note**: This requires Gemini API quota. Check quota at: https://ai.dev/usage?tab=rate-limit
   
   **Alternative**: If quota is exhausted, wait for daily reset or use a different Google account.

2. **Commit the vector store**:
   ```bash
   git add vector_store/
   git commit -m "Add pre-built vector store with Gemini embeddings (3072 dim)"
   git push
   ```

3. **On Render**: Set `EMBEDDING_PROVIDER=gemini` (must match what you used to build!)
   
   **Why match?** Vector store dimensions must match:
   - Built with Gemini (3072 dim) → Load with Gemini (3072 dim) ✅
   - Built with Local (384 dim) → Load with Local (384 dim) ✅
   - **Cannot mix** - dimensions must match!

**Note**: See `FREE_TIER_SETUP.md` for detailed instructions.

### Upload Documents

Add your PDF/DOCX files to the `documents/` folder and commit:
```bash
git add documents/
git commit -m "Add documents"
git push
```

## Step 4: Monitor Deployment

1. Watch the build logs in Render dashboard
2. The first deployment may take 5-10 minutes (downloading dependencies)
   - If you pre-built the vector store, it will load quickly (no embedding generation)
   - If not pre-built, it will use Gemini API (may hit quota limits)
3. Once deployed, your app will be available at: `https://your-app-name.onrender.com`

## Step 5: Test Your Deployment

1. Visit your app URL: `https://your-app-name.onrender.com`
2. You should see the chat interface
3. Try asking a question about your documents

## Important Notes for Render

### Free Tier Limitations

- **Spins down after 15 minutes of inactivity**: First request after spin-down may take 30-60 seconds
- **512MB RAM limit**: May need to use smaller embedding models
- **100GB bandwidth/month**: Usually sufficient for moderate use

### Performance Tips

1. **Use Gemini embeddings** (`EMBEDDING_PROVIDER=gemini`): Required for Render free tier (512MB RAM limit)
   - Local embeddings require ~500MB RAM (exceeds free tier limit)
   - Gemini embeddings use ~150MB RAM (fits in free tier)
2. **Pre-build vector store**: Commit your `vector_store/` folder to avoid API calls during deployment
   - Build with Gemini embeddings locally (when quota available)
   - Commit to Git
   - Render loads pre-built store (no quota issues!)
3. **Gemini embedding dimensions**: Default is 3072 (works fine for RAG)

### Troubleshooting

**Issue: Build fails**
- Check build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility

**Issue: App crashes on startup**
- Check environment variables are set correctly
- Verify API keys are valid
- Check startup logs for errors

**Issue: Slow first request**
- This is normal on free tier (cold start)
- Consider upgrading to a paid plan for always-on service

**Issue: Memory errors**
- Ensure `EMBEDDING_PROVIDER=gemini` (not `local`)
- Local embeddings exceed 512MB RAM limit on free tier
- Reduce `TOP_K_RESULTS` value
- Consider upgrading RAM (Standard plan: $25/month for 1GB)

**Issue: Dimension mismatch errors**
- Vector store must be built with same embedding provider as Render
- If built with local (384 dim), rebuild with Gemini (3072 dim)
- See `FREE_TIER_SETUP.md` for detailed instructions

## Alternative: Deploy to Other Platforms

### Railway
1. Connect GitHub repository
2. Railway auto-detects Python
3. Add environment variables
4. Deploy!

### Heroku
1. Install Heroku CLI
2. `heroku create your-app-name`
3. `git push heroku main`
4. Set environment variables: `heroku config:set GOOGLE_API_KEY=your_key`

### Fly.io
1. Install flyctl
2. `fly launch`
3. Follow prompts
4. Set secrets: `fly secrets set GOOGLE_API_KEY=your_key`

## Support

For issues specific to Render, check:
- Render Docs: https://render.com/docs
- Render Community: https://community.render.com

