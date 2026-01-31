# Project Roadmap: Synthetic Identity Fraud Detection

This roadmap is designed for a **team of 4 developers**. Each module is independent to allow parallel development.

## 👥 Team Roles & Responsibilities

| Role | Focus Area | Key Files |
| :--- | :--- | :--- |
| **Dev 1 (Lead/Fullstack)** | App UI, Database, Integration | `app.py`, `db_connection.py`, `config.py` |
| **Dev 2 (CV Engineer)** | Face Liveness & Matching | `face_verification/` |
| **Dev 3 (Doc Specialist)** | Document Forgery & OCR | `doc_verification/` |
| **Dev 4 (Data Analyst)** | Behavior Analysis & Fraud Rules | `behavior_analysis/`, `fraud_engine/` |

## 🛠️ Setup Instructions (Important for Team)

All team members **must** use a virtual environment to avoid dependency conflicts.

1.  **Create venv**: `python -m venv venv`
2.  **Activate venv**:
    - Windows: `venv\Scripts\activate`
    - Mac/Linux: `source venv/bin/activate`
3.  **Install Deps**: `pip install -r requirements.txt`

---

## 📅 Phase 1: Core Module Implementation (Weeks 1-2)

### 👤 Dev 2: Face Verification Module
- [ ] **Implement Face Detection** in `face_utils.py`
    - Use `MTCNN` or `Haar Cascades` to crop faces from images.
- [ ] **Implement Embedding Generation**
    - Use `DeepFace.represent()` (FaceNet/ArcFace) to get 128-d vectors.
- [ ] **Implement Liveness Detection**
    - **Basic**: Check for blinking (eye aspect ratio) using `dlib` or `mediapipe`.
    - **Advanced**: Use a texture analysis model (LBP) to detect screens/paper masks.

### 📄 Dev 3: Document Verification Module
- [ ] **Implement OCR Extraction** in `doc_utils.py`
    - Use `pytesseract` to read Name, DOB, and ID Number.
    - Validate date formats and ID patterns (Regex).
- [ ] **Implement Forgery Detection**
    - **Step 1**: Error Level Analysis (ELA) or simple blur detection (`cv2.Laplacian`).
    - **Step 2**: Load a pre-trained `EfficientNet` model to classify "Real" vs "Tampered" (if model file exists).

### 🧠 Dev 4: Behavioral & Fraud Engine
- [ ] **Implement Behavior Baseline** in `behavior_utils.py`
    - Record time taken to fill form fields (keystroke dynamics).
    - Calculate `mean` and `std_dev` for typing speed.
- [ ] **Define Fraud Rules** in `rules.py`
    - Create the weighted formula: `Risk = (0.4 * Face) + (0.4 * Doc) + (0.2 * Behavior)`.
    - Set threshold logic for "Approve" vs "Reject".

### 💻 Dev 1: Database & UI Skeleton
- [ ] **Setup SQLite Tables** in `db_connection.py`
    - Ensure `users` table stores the `face_embedding` (as BLOB or JSON).
- [ ] **Build Streamlit Forms** in `app.py`
    - Create logical flow: `Login` -> `Upload Doc` -> `Take Selfie` -> `Result`.

---

## 🔄 Phase 2: Integration & Testing (Week 3)

- [ ] **Connect Modules in `app.py`**
    - Pass uploaded images to `DocumentVerifier`.
    - Pass webcam frames to `FaceVerifier`.
    - Pass metadata to `BehaviorAnalyzer`.
- [ ] **End-to-End Test**
    - Register a user.
    - Run a verification attempt.
    - Check if data is saved in `kyc_database.db`.

---

## 🚀 Phase 3: Polish & Demo (Week 4)

- [ ] Add "Visual Explanations" (why was it rejected?).
- [ ] Tune thresholds (e.g., is 0.40 cosine similarity too strict?).
- [ ] Prepare presentation slides.
