# Streamlit Cloud Deployment Guide

## Prerequisites
1. A GitHub repository with your code
2. A Groq API key (free from https://console.groq.com)
3. ChromaDB vectorstore created (run `create_memory_for_llm.py` locally first)

## Steps to Deploy on Streamlit Cloud

### 1. Prepare Your Repository
Make sure your repository includes:
- `medibot.py` (main app file)
- `requirements.txt` (all dependencies)
- `vectorstore/db_chroma/` (ChromaDB database - must be committed to GitHub)
- `.streamlit/secrets.toml` (DO NOT commit this file - add to `.gitignore`)

### 2. Create ChromaDB Vectorstore Locally
Before deploying, you MUST create the ChromaDB vectorstore locally:

```bash
python create_memory_for_llm.py
```

This will create the `vectorstore/db_chroma/` directory with your embeddings.

### 3. Commit Vectorstore to GitHub
The ChromaDB database needs to be in your repository:

```bash
git add vectorstore/db_chroma/
git commit -m "Add ChromaDB vectorstore"
git push
```

### 4. Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `medibot.py`
6. Click "Deploy"

### 5. Configure Secrets on Streamlit Cloud

After deployment, configure your API key:

1. In your app dashboard, click "⋮" (three dots) → "Settings"
2. Go to "Secrets" section
3. Add your secrets in TOML format:

```toml
GROQ_API_KEY = "your-actual-groq-api-key-here"
```

4. Click "Save"
5. Your app will automatically restart with the new secrets

## Local Testing with Secrets

To test locally using Streamlit secrets (instead of `.env`):

1. Create `.streamlit/secrets.toml` in your project root
2. Add your API key:
   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   ```
3. Run: `streamlit run medibot.py`

## Important Notes

- **ChromaDB Database**: The `vectorstore/db_chroma/` folder MUST be in your GitHub repository. Streamlit Cloud cannot create it dynamically.
- **File Size Limit**: Streamlit Cloud has a 1GB repository size limit. If your vectorstore is too large, consider using a cloud storage solution.
- **Secrets Security**: Never commit `.streamlit/secrets.toml` or `.env` files to GitHub. Add them to `.gitignore`.

## Troubleshooting

### "NameError" on deployment
- **Cause**: Missing secrets or incorrect configuration
- **Fix**: Check that secrets are properly configured in Streamlit Cloud settings

### "Vector store not found"
- **Cause**: ChromaDB database not in repository
- **Fix**: Run `create_memory_for_llm.py` locally and commit the `vectorstore/db_chroma/` folder

### "API key error"
- **Cause**: GROQ_API_KEY not set in secrets
- **Fix**: Add the API key in Streamlit Cloud settings → Secrets

## Support
For issues, check:
- Streamlit Cloud logs: Click "Manage app" → "Logs"
- Streamlit documentation: https://docs.streamlit.io/streamlit-community-cloud
