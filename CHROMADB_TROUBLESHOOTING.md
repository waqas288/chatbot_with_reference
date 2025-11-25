# ChromaDB Streamlit Cloud Troubleshooting Guide

## What We've Done

### ✅ Updated Package Versions
Changed to more stable, Streamlit Cloud-compatible versions:
- `chromadb==0.4.24` (downgraded from 0.5.23)
- `langchain-chroma==0.1.4` (downgraded from 0.2.1)

These versions are known to work better on Streamlit Cloud's Python environment.

---

## Next Steps

### 1. **Wait for Streamlit Cloud to Redeploy** ⏳
After pushing changes, Streamlit Cloud needs to:
- Detect the new commit
- Rebuild the environment
- Install new packages
- Restart the app

**This usually takes 2-5 minutes.**

### 2. **Force a Reboot** (if needed) 🔄
If the app doesn't automatically redeploy:
1. Go to your Streamlit Cloud dashboard
2. Click on your app
3. Click the "⋮" menu (three dots)
4. Select "Reboot app"

### 3. **Check the Logs** 📋
If still getting errors:
1. In Streamlit Cloud, click "Manage app" (bottom right)
2. View the full error logs
3. Look for specific error messages about missing dependencies

---

## Alternative Solution: Use FAISS Instead

If ChromaDB continues to have issues on Streamlit Cloud, you can switch back to FAISS, which is more lightweight and reliable on Streamlit Cloud.

### Option A: Keep ChromaDB Locally, Use FAISS on Cloud

You can detect the environment and use different vector stores:

```python
import os
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings

# Detect if running on Streamlit Cloud
IS_STREAMLIT_CLOUD = os.path.exists("/mount/src")

@st.cache_resource
def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2'
    )
    
    if IS_STREAMLIT_CLOUD:
        # Use FAISS on Streamlit Cloud
        from langchain_community.vectorstores import FAISS
        db = FAISS.load_local(
            "vectorstore/db_faiss",
            embedding_model,
            allow_dangerous_deserialization=True
        )
    else:
        # Use ChromaDB locally
        from langchain_chroma import Chroma
        db = Chroma(
            persist_directory="vectorstore/db_chroma",
            embedding_function=embedding_model
        )
    
    return db
```

### Option B: Fully Switch to FAISS

If you want to use FAISS everywhere:

1. **Update `medibot.py`**:
```python
from langchain_community.vectorstores import FAISS

DB_FAISS_PATH = "vectorstore/db_faiss"

@st.cache_resource
def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2'
    )
    db = FAISS.load_local(
        DB_FAISS_PATH,
        embedding_model,
        allow_dangerous_deserialization=True
    )
    return db
```

2. **Remove from `requirements.txt`**:
   - Remove `chromadb==0.4.24`
   - Remove `langchain-chroma==0.1.4`

3. **Commit both `db_faiss` and `db_chroma` folders** to GitHub (so you have both options)

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'langchain_chroma'"

**Possible Causes:**
1. Streamlit Cloud hasn't redeployed yet
2. Package version incompatibility
3. Missing dependencies

**Solutions:**
- ✅ Wait 5 minutes and refresh
- ✅ Reboot the app manually
- ✅ Try the FAISS alternative above

### Issue: "ImportError: cannot import name 'Chroma'"

**Cause:** Version mismatch between `langchain-chroma` and `chromadb`

**Solution:**
- ✅ We've already fixed this by using compatible versions (0.1.4 and 0.4.24)
- ✅ If still failing, use FAISS instead

### Issue: "Database not found"

**Cause:** `vectorstore/db_chroma/` folder not in GitHub

**Solution:**
```bash
git add vectorstore/db_chroma/
git commit -m "Add ChromaDB database"
git push
```

---

## Recommended Approach

**For Streamlit Cloud Free Tier, I recommend using FAISS** because:
1. ✅ **Lighter weight** - smaller package size
2. ✅ **More reliable** - fewer dependencies
3. ✅ **Faster deployment** - quicker to install
4. ✅ **Well-tested** - proven to work on Streamlit Cloud

**Use ChromaDB locally** for development if you prefer it, then switch to FAISS for deployment.

---

## What to Do Now

1. **Wait 3-5 minutes** for Streamlit Cloud to redeploy with the new package versions
2. **Check if the app works** - refresh your Streamlit Cloud app
3. **If still failing**, check the logs and consider switching to FAISS
4. **Let me know** if you need help implementing the FAISS alternative

The updated requirements have been pushed to GitHub. Your app should redeploy automatically! 🚀
