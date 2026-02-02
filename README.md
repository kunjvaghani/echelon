# 🛡️ Synthetic Identity Fraud Detection in Automated e-KYC Systems

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Overview

This project is a state-of-the-art **AI-driven e-KYC (Electronic Know Your Customer) system** designed to combat synthetic identity fraud. By correlating document authenticity, facial biometrics, and behavioral patterns, the system provides a robust, multi-layer defense against sophisticated fraud techniques like AI-generated documents and deepfakes.

### 🎯 Key Problems Solved
- **Forged Documents**: Detection of photoshopped or AI-generated government IDs.
- **Deepfake Faces**: Anti-spoofing and liveness detection to block mask or screen-based attacks.
- **Bot Attacks**: Identification of automated registration patterns through behavioral analysis.
- **Identity Reuse**: Prevention of multiple accounts created with similar biometric or document data.

---

## 🏗️ System Architecture

Our system employs a **3-Layer Security Pipeline** to ensure the highest level of trust:

1.  **Document Verification**: 4-component hybrid AI analysis (Quality, Forgery, OCR, Rules).
2.  **Face Biometrics**: Multi-stage verification including MTCNN detection and FaceNet/ArcFace embeddings.
3.  **Behavioral Analytics**: Passive tracking of user interaction (typing speed, mouse movement) to detect anomalies.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend/UI** | [Streamlit](https://streamlit.io/) (Python-based interactive UI) |
| **Computer Vision** | [OpenCV](https://opencv.org/), [DeepFace](https://github.com/serengil/deepface) |
| **ML Models** | MTCNN, EfficientNetB0, FaceNet, ArcFace, Scikit-learn |
| **OCR Engine** | [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) |
| **Database** | SQLite (Demo) / [MongoDB Atlas](https://www.mongodb.com/atlas) (Production) |
| **Backend** | Python, Flask (API Support) |

---

## 🚀 Getting Started

Follow these instructions to get the project up and running on your local machine.

### 1. Prerequisites
- **Python 3.10 or 3.11** (Note: TensorFlow 2.15 is not compatible with Python 3.12+ on Windows).
- **Tesseract OCR**:
    - Download and install from [here](https://github.com/UB-Mannheim/tesseract/wiki).
    - **Important**: Add the Tesseract installation path (e.g., `C:\Program Files\Tesseract-OCR`) to your system environment variables (PATH).

### 2. Virtual Environment Setup (Recommended)
Creating a virtual environment ensures that the project's dependencies don't conflict with other Python projects on your system.

**Step-by-step Guide:**

1.  **Open your terminal/command prompt** and navigate to the project root folder.
2.  **Create the environment**:
    ```bash
    python -m venv venv
    ```
3.  **Activate the environment**:
    - **Windows**:
      ```bash
      venv\Scripts\activate
      ```
    - **macOS/Linux**:
      ```bash
      source venv/bin/activate
      ```
    *You should see `(venv)` appear at the beginning of your command line prompt.*

### 3. Installation
While the virtual environment is active, install the required packages:

```bash
pip install -r requirements.txt
```

### 4. Configuration
Create a `.env` file in the root directory (copy from `.env.example` if available) and add your configurations:
```env
MONGODB_URI=your_mongodb_connection_string
SECRET_KEY=your_secret_key
# Other project-specific variables
```

---

## 💻 Usage

To launch the main application:

```bash
streamlit run src/app.py
```
The app will open automatically in your default web browser (usually at `http://localhost:8501`).

---

## 🔬 Core Modules

### 📄 Document Verification (`doc_verification/`)
Uses a hybrid approach combining **Error Level Analysis (ELA)** for forgery detection and **EfficientNetB0** for deep features analysis. Tesseract OCR extracts text which is then fuzzy-matched against user input.

### 👤 Face Biometrics (`face_verification/`)
Implements **MTCNN** for high-accuracy face detection and **DeepFace** (FaceNet/ArcFace) for creating unique biometric embeddings. Includes liveness detection to prevent spoofing.

### 🧠 Behavioral Analysis (`behavior_analysis/`)
Passively monitors user interaction patterns during the registration and KYC process. Anomalies in typing rhythm or form completion time are flagged as potential bot activity.

---

## 👥 Project Structure
This project was designed for a 4-member agile team:
- **Lead/Fullstack**: Integration and UI Workflow.
- **CV Engineer**: Biometric Liveness and Matching.
- **Doc Specialist**: Document Forgery Detection and OCR.
- **Data Analyst**: Behavioral Fraud Logic and Decision Engine.

---

## 📜 License
Internal Project - All Rights Reserved. (Change to MIT/Apache if applicable).

---
*Built with 🛡️ Security First principles.*
