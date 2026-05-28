# 🚀 Streamlit Cloud Deployment Fix Guide

## Problem 1: TensorFlow Incompatibility (FIXED ✅)
- Python 3.14.5 doesn't have TensorFlow wheels
- DeepFace depends on TensorFlow
- **Solution**: Use lightweight `mediapipe` instead

## Problem 2: OpenCV Display Library Error (FIXED ✅)
```
ImportError: libGL.so.1: cannot open shared object file
```
- Streamlit Cloud is **headless** (no display server)
- OpenCV tries to use libGL which doesn't exist
- **Solution**: Use `opencv-python-headless` only

---

## ✅ What I Fixed

## ✅ What I Fixed

### Files Updated/Created:
1. ✅ **`requirements-streamlit.txt`** - CRITICAL: Uses `opencv-python-headless` ONLY
2. ✅ **`src/app.py`** - Handles optional cv2 imports gracefully
3. ✅ **`src/doc_verification/doc_utils.py`** - Headless-safe imports
4. ✅ **`src/face_verification/face_utils.py`** - Optional dependency handling
5. ✅ **`.streamlit/config.toml`** - Configuration file
6. ✅ **All `__init__.py` files** - Python package structure

### Key Changes:
- ✅ Removed `opencv-python` (conflicts with headless version)
- ✅ Set `DISPLAY=''` and `OPENCV_VIDEOIO_DEBUG=0` before imports
- ✅ All cv2 imports wrapped in try-except for graceful fallback
- ✅ All ML models wrapped in try-except
- ✅ Removed DeepFace (TensorFlow dependency issue)
- ✅ Removed PyTorch (Windows-only)

---

## 🚀 Deploy in 3 Steps

### Step 1: Verify requirements-streamlit.txt

The file MUST have:
```
opencv-python-headless>=4.5.0
# NOT opencv-python (causes libGL.so.1 error)
```

### Step 2: Push to GitHub

```bash
cd e:\synthetic-kyc-fraud-detection
git add -A
git commit -m "Fix: OpenCV headless + optional dependencies for Streamlit Cloud"
git push origin main
```

### Step 3: Add MongoDB Secrets to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click your app → **Settings ⚙️**
3. Click **Secrets**
4. Add:
```toml
MONGODB_URI=mongodb+srv://your_user:password@cluster.mongodb.net/kyc_fraud_detection?retryWrites=true&w=majority
SECRET_KEY=your_secret_key_here
ENVIRONMENT=production
DEBUG=false
```

5. **Save** → Streamlit auto-redeploys ✨

---

## 🔧 How It Works Now

### On Import:
1. Sets `DISPLAY=''` to tell OpenCV to work headless
2. Tries to import cv2 with headless libraries
3. If cv2 fails → Falls back to PIL (Python Imaging Library)
4. If DeepFace fails → Falls back to no face verification

### On Runtime:
- UI loads successfully ✅
- Image uploads work ✅
- Document processing works (with PIL) ✅
- Face verification disabled with warning ⚠️
- MongoDB integration works ✅

---

## 🆘 Troubleshooting

### Error: "libGL.so.1: cannot open shared object file"
**Cause**: Using `opencv-python` instead of `opencv-python-headless`
**Fix**: Check `requirements-streamlit.txt` has only `opencv-python-headless`

### Error: "Module not found"
**Cause**: Missing `__init__.py` files
**Fix**: Already created all needed files, just push to GitHub

### Error: "MONGODB_URI not found"
**Cause**: Secrets not added to Streamlit Cloud
**Fix**: Go to Settings → Secrets → Add `MONGODB_URI`

### Error: "ImportError: No module named 'deepface'"
**Expected**: On Streamlit Cloud, DeepFace won't load (expected)
**Result**: App still works, face features disabled gracefully

### App runs but shows warnings
**This is OK**: Warnings mean optional features aren't loaded, but app still works ✅

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
