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
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or choose a paid plan)

6. **Add Environment Variables**:
   - `LLM_PROVIDER` = `gemini`
   - `EMBEDDING_PROVIDER` = `local`
   - `MODEL_NAME` = `gemini-pro` (or `gemini-2.5-flash`)
   - `GOOGLE_API_KEY` = `your_actual_api_key_here`
   - `LOCAL_EMBEDDING_MODEL` = `all-MiniLM-L6-v2`
   - `VECTOR_STORE_PATH` = `./vector_store`
   - `DOCUMENTS_PATH` = `./documents`
   - `TOP_K_RESULTS` = `7`

7. **Click "Create Web Service"**

### Option B: Using render.yaml (Automatic)

If you have `render.yaml` in your repository:

1. Go to Render Dashboard
2. Click "New +" → "Blueprint"
3. Connect your repository
4. Render will automatically detect `render.yaml` and configure everything
5. You'll still need to add `GOOGLE_API_KEY` in the Environment Variables section

## Step 3: Upload Documents

Since Render's file system is ephemeral, you have two options:

### Option A: Include Documents in Repository (Recommended for small files)

1. Add your PDF/DOCX files to the `documents/` folder
2. Commit and push:
   ```bash
   git add documents/
   git commit -m "Add documents"
   git push
   ```

### Option B: Use External Storage (Recommended for large files)

For production, consider using:
- AWS S3
- Google Cloud Storage
- Azure Blob Storage

Then modify `vector_store_manager.py` to download documents on startup.

## Step 4: Monitor Deployment

1. Watch the build logs in Render dashboard
2. The first deployment may take 5-10 minutes (downloading dependencies and embedding model)
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

1. **Use local embeddings** (`EMBEDDING_PROVIDER=local`): No API calls, faster
2. **Pre-build vector store**: Commit your `vector_store/` folder to avoid rebuilding on each deploy
3. **Use smaller models**: `all-MiniLM-L6-v2` is faster than `all-mpnet-base-v2`

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
- Use smaller embedding models
- Reduce `TOP_K_RESULTS` value
- Consider upgrading RAM

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

