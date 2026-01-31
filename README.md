# Synthetic Identity Fraud Detection

## Overview
This project is an **AI-driven e-KYC system** designed to detect synthetic identities by correlating:
- **Document Authenticity** (Forgery detection, OCR)
- **Face Biometrics** (Liveness, matching)
- **Behavioral Analytics** (User interaction patterns)

## Setup Instructions

### 1. Prerequisites
- Python 3.10–3.11 (TensorFlow is not available for Python 3.12+ on Windows)
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed and added to PATH.

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Usage
Run the main Streamlit application:
```bash
streamlit run src/app.py
```

## Architecture
- **Frontend**: Streamlit
- **ML Core**: DeepFace, OpenCV, Scikit-learn, PyTorch
- **Database**: SQLite (for demo) / MongoDB (ready)
