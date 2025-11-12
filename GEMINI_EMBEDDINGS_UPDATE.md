# Gemini Embeddings Update - Based on Official Documentation

## Changes Made

Based on the [official Gemini Embeddings documentation](https://ai.google.dev/gemini-api/docs/embeddings), we've updated the code to use the correct model and specifications.

### ✅ Model Name Updated

**Before:**
- `models/embedding-001` (deprecated)

**After:**
- `models/gemini-embedding-001` (stable, recommended)

**Reason**: `models/embedding-001` is deprecated and will be removed in October 2025.

### 📋 Model Specifications

According to the official documentation:

| Property | Value |
|----------|-------|
| **Model ID** | `gemini-embedding-001` |
| **Input Token Limit** | 2,048 tokens |
| **Output Dimensions** | Flexible: 128-3072 |
| **Recommended Dimensions** | 768, 1536, 3072 |
| **Default Dimensions** | 768 (what we're using) |
| **Status** | Stable (recommended) |

### 🔧 Code Changes

**Files Updated:**

1. **`vector_store_manager.py`**
   - Updated model name from `models/embedding-001` to `models/gemini-embedding-001`
   - Added comments about deprecation and dimensions

2. **`build_vector_store.py`**
   - Updated model name in quota check test

3. **Documentation Files**
   - `FREE_TIER_SETUP.md` - Updated model name and dimensions info
   - `MEMORY_OPTIMIZATION.md` - Added model specifications and reference link
   - `QUOTA_FIX_SUMMARY.md` - Added model information

### 📚 Key Information from Documentation

1. **Task Types**: Can specify task types like `SEMANTIC_SIMILARITY` for better performance (not currently implemented, but available)

2. **Output Dimensionality**: Can specify custom dimensions (128-3072), but 768 is recommended and works well

3. **Normalization**: 
   - 3072 dimension embeddings are normalized automatically
   - For 768 and 1536, normalization can be done manually if needed
   - Our current implementation uses 768 (default)

4. **Batch API**: Available for higher throughput at 50% cost (for future optimization)

5. **Deprecation**: 
   - `embedding-001` → Deprecated (removed Oct 2025)
   - `embedding-gecko-001` → Deprecated (removed Oct 2025)
   - `gemini-embedding-exp-03-07` → Deprecated (removed Oct 2025)
   - `gemini-embedding-001` → **Stable (use this)**

### ✅ Verification

- ✅ Model name updated in code
- ✅ Documentation updated
- ✅ No linter errors
- ✅ Compatible with existing vector stores (if rebuilt with new model)

### ⚠️ Important Note

**If you have an existing vector store built with `models/embedding-001`:**
- It will still work until October 2025
- But you should rebuild with `gemini-embedding-001` for future compatibility
- Both models produce 768-dimensional embeddings, so dimensions match

### 🚀 Next Steps

1. **Rebuild vector store** (when quota available):
   ```bash
   python build_vector_store.py
   ```
   This will now use `gemini-embedding-001` automatically.

2. **Commit and push**:
   ```bash
   git add vector_store/
   git commit -m "Rebuild vector store with gemini-embedding-001"
   git push
   ```

3. **Deploy on Render** - will use the updated model

### 📖 Reference

- [Official Gemini Embeddings Documentation](https://ai.google.dev/gemini-api/docs/embeddings)
- [Model Versions](https://ai.google.dev/gemini-api/docs/models/gemini#model-versions)

---

**Status**: ✅ Updated and ready to use!

