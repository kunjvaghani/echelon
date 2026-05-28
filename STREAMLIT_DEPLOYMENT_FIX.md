# 🚀 Streamlit Cloud Deployment Fix Guide

## Problem Summary
Your deployment failed because:
1. **Python 3.14.5** on Streamlit Cloud doesn't have TensorFlow wheels
2. **DeepFace requires TensorFlow**, creating an impossible dependency
3. Windows-only markers (`sys_platform == "win32"`) don't apply to Streamlit Cloud's Linux environment

---

## ✅ Solution: 3 Steps to Deploy Successfully

### Step 1: Update Requirements for Streamlit Cloud

Your repository now has **two requirements files**:

- **`requirements.txt`** → For local development (Windows/Mac/Linux)
- **`requirements-streamlit.txt`** → For Streamlit Cloud deployment

The key changes:
- ✅ Removed `deepface` (TensorFlow incompatible with Python 3.14)
- ✅ Removed platform-specific markers for TensorFlow
- ✅ Added `mediapipe` as lightweight face detection alternative
- ✅ Removed `torch` (Windows-only dependency)

### Step 2: Configure Streamlit Cloud Settings

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Fix: Update requirements for Streamlit Cloud compatibility"
   git push origin main
   ```

2. **Go to Streamlit Cloud**:
   - Navigate to https://share.streamlit.io
   - Click on your app: `fraud-detection-kyc`
   - Go to **Settings ⚙️** → **Edit secrets**

3. **Add your MongoDB credentials**:
   ```toml
   MONGODB_URI = "mongodb+srv://your_username:your_password@cluster.mongodb.net/kyc_fraud_detection?retryWrites=true&w=majority"
   SECRET_KEY = "your_secret_key_generated_with_secrets.token_hex(32)"
   ENVIRONMENT = "production"
   DEBUG = false
   ```

4. **In Advanced Settings**, specify the requirements file:
   - **Requirements file path**: `requirements-streamlit.txt`
   - Leave blank if using default `requirements.txt`

### Step 3: Modify app.py for Optional Dependencies

Your `app.py` needs to handle optional ML models gracefully. Replace the imports at the top with:

```python
import streamlit as st
import os
import re
import sys
import time
from datetime import date
from PIL import Image
import numpy as np
import cv2

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try to load ML models - graceful fallback if not available
try:
    from src.face_verification.face_utils import FaceVerifier
    HAS_FACE_VERIFIER = True
except ImportError:
    HAS_FACE_VERIFIER = False
    print("[WARNING] FaceVerifier not available on Streamlit Cloud - using lightweight alternative")

try:
    from src.doc_verification.doc_utils import DocumentVerifier
    HAS_DOC_VERIFIER = True
except ImportError:
    HAS_DOC_VERIFIER = False
    print("[WARNING] DocumentVerifier not available - OCR features disabled")

@st.cache_resource
def get_models():
    """Load and cache models to avoid reloading on every interaction"""
    if HAS_FACE_VERIFIER:
        face_verifier = FaceVerifier()
    else:
        face_verifier = None
        st.warning("⚠️ Face verification models not loaded. Using alternative methods.")
    
    if HAS_DOC_VERIFIER:
        doc_verifier = DocumentVerifier()
    else:
        doc_verifier = None
        st.warning("⚠️ Document verification models not loaded.")
    
    return face_verifier, doc_verifier
```

---

## 📋 Deployment Steps

### For Streamlit Cloud:

```bash
# 1. Commit all changes
cd e:\synthetic-kyc-fraud-detection
git add -A
git commit -m "Fix: Streamlit Cloud compatibility - remove TensorFlow dependency"

# 2. Push to GitHub
git push origin main

# 3. Streamlit Cloud will auto-detect changes and redeploy
# Monitor logs at: https://share.streamlit.io/your-username/fraud-detection-kyc
```

### For Local Development (Windows):

```bash
# Use the original requirements
pip install -r requirements.txt

# Run Streamlit
streamlit run src/app.py
```

### For Production VPS/Docker:

Create `requirements-prod.txt`:
```
# Use this for production servers with proper ML support
-r requirements.txt
tensorflow>=2.13.0  # Only for servers with GPU/proper setup
deepface>=0.0.95
```

---

## 🔧 Alternative: Use Python 3.11 on Streamlit Cloud

If you want to use DeepFace/TensorFlow on Streamlit, you must constrain Python version:

Create `.python-version` file in repo root:
```
3.11.9
```

Then update `requirements.txt`:
```
# Only these versions work on Python 3.11
tensorflow==2.13.1
deepface==0.0.75
```

**However**: Streamlit Cloud free tier has limited resources. Stick with **lightweight models** (Step 1 solution).

---

## 🚨 If You Still Get Errors

### Error: "Package not found"
→ Make sure `.streamlit/config.toml` is committed and doesn't have errors

### Error: "Memory exceeded"
→ Streamlit Cloud free tier has 1GB limit. Disable large model preloading:
```python
@st.cache_resource
def get_models():
    st.warning("Models load on-demand to save memory")
    return None  # Load only when user uploads
```

### Error: "MONGODB_URI not found"
→ Go to **Settings** → **Secrets** and add the credentials

### Error: "Module not found (src.*)"
→ Make sure your directory structure includes `__init__.py` files:
```
src/
  __init__.py  ← Must exist
  app.py
  face_verification/
    __init__.py  ← Must exist
    face_utils.py
  doc_verification/
    __init__.py  ← Must exist
    doc_utils.py
```

---

## ✅ Quick Checklist Before Deploying

- [ ] Updated `requirements.txt` (removed DeepFace/TensorFlow)
- [ ] Created `requirements-streamlit.txt` for Streamlit Cloud
- [ ] Created `.streamlit/config.toml`
- [ ] Updated `app.py` imports to handle optional dependencies
- [ ] Added MongoDB URI to Streamlit Cloud Secrets
- [ ] All `__init__.py` files exist in subdirectories
- [ ] Pushed changes to GitHub
- [ ] Checked logs at https://share.streamlit.io

---

## 📊 Recommended Deployment Architecture

**For Production** (if you need ML models):

```
├── Streamlit Cloud (Frontend UI only)
├── Flask API Server (AWS/Heroku) ← Runs heavy ML models
└── MongoDB Atlas (Database)
```

This way:
- Streamlit Cloud displays results
- Flask API handles heavy computation
- Models run on proper server infrastructure

---

## 🔗 Useful Links

- [Streamlit Deployment Docs](https://docs.streamlit.io/deploy/streamlit-community-cloud)
- [Python Version on Streamlit Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies#python-version)
- [Environment Secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app#set-secret-values)

---

**Need more help?** Check the Streamlit logs: https://share.streamlit.io/kunjvaghani/fraud-detection-kyc/logs
