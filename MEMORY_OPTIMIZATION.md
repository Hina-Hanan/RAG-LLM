# Memory Optimization Guide for Render Free Tier

## Problem

Render free tier provides **512MB RAM**, but the application dependencies require more:
- `sentence-transformers` + PyTorch: ~500-600MB
- Other dependencies: ~100-150MB
- **Total: ~650-750MB** (exceeds 512MB limit)

## Solution: Use Gemini Embeddings on Render

### Why Gemini Embeddings?

- **Low Memory**: ~150MB total (no PyTorch needed)
- **Works on Free Tier**: Fits within 512MB limit
- **API-Based**: No local model downloads
- **Fast Startup**: No model loading time

### Trade-offs

- **Quota Limits**: Free tier has daily/minute limits
- **API Calls**: Requires internet connection
- **Cost**: Free tier is limited, may need to wait for quota reset

## Configuration

### For Render Deployment

**render.yaml** (already configured):
```yaml
envVars:
  - key: EMBEDDING_PROVIDER
    value: gemini  # Uses API, saves memory
```

**requirements.txt** (already updated):
- `sentence-transformers` is commented out
- Only installs lightweight dependencies

### For Local Development

**Keep using local embeddings** (in `.env`):
```env
EMBEDDING_PROVIDER=local
```

Then install sentence-transformers locally:
```bash
pip install sentence-transformers>=2.2.0
```

## Memory Comparison

| Embedding Type | RAM Usage | Works on Free Tier? | Notes |
|----------------|-----------|---------------------|-------|
| Local (sentence-transformers) | ~600MB | ❌ No | Free, no API calls, offline |
| Gemini API | ~150MB | ✅ Yes | API quota limits on free tier |
| OpenAI API | ~150MB | ✅ Yes | Requires paid API key |

## Gemini Embeddings Quota

**Model**: `gemini-embedding-001` (stable, recommended)
- **Output Dimensions**: 768 (recommended), supports 128-3072
- **Input Token Limit**: 2,048 tokens per request
- **Note**: `models/embedding-001` is deprecated (will be removed Oct 2025)

**Free Tier Limits:**
- Daily quota: Limited (varies by account)
- Per-minute quota: Limited
- **Current Status**: Your account shows quota limit of 0

**Reference**: [Gemini Embeddings Documentation](https://ai.google.dev/gemini-api/docs/embeddings)

**Solutions:**
1. **Wait for quota reset** (usually daily)
2. **Use a different Google account** with fresh quota
3. **Upgrade Google AI Studio** (if available)
4. **Use local embeddings locally**, Gemini on Render (if quota available)

## Alternative: Upgrade Render Plan

If you need local embeddings:

- **Starter Plan** ($7/month): Still 512MB RAM
- **Standard Plan** ($25/month): 1GB RAM - enough for sentence-transformers

## Current Setup

✅ **Render**: Configured to use Gemini embeddings (low memory)
✅ **Local**: Can use local embeddings (install sentence-transformers separately)
✅ **Requirements**: Optimized for Render (sentence-transformers excluded)

## Testing

To test Gemini embeddings locally:
```bash
# Set environment variable
set EMBEDDING_PROVIDER=gemini  # Windows
export EMBEDDING_PROVIDER=gemini  # Linux/Mac

# Run app
python app.py
```

**Note**: If you get quota errors, wait for quota reset or use local embeddings.

## Recommendations

1. **For Render Free Tier**: Use Gemini embeddings (already configured)
2. **For Local Development**: Use local embeddings (better performance, no API calls)
3. **If Quota Exhausted**: 
   - Wait for daily reset
   - Or upgrade Render to Standard plan ($25/month) for 1GB RAM
   - Then use local embeddings on Render

## Summary

✅ **Fixed**: Removed sentence-transformers from requirements.txt for Render
✅ **Fixed**: Updated render.yaml to use Gemini embeddings
✅ **Fixed**: Code handles missing sentence-transformers gracefully
✅ **Result**: App will use ~150MB RAM instead of ~600MB

The app should now deploy successfully on Render free tier!

