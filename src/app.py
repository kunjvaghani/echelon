import streamlit as st
import os
import sys
from PIL import Image
import numpy as np
import cv2

# Add project root to path so 'src' module can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.face_verification.face_utils import FaceVerifier
from src.doc_verification.doc_utils import DocumentVerifier

# Set page config
st.set_page_config(
    page_title="Synthetic Identity Fraud Detection",
    page_icon="🛡️",
    layout="wide"
)

@st.cache_resource
def get_models():
    """Load and cache models to avoid reloading on every interaction"""
    face_verifier = FaceVerifier()
    doc_verifier = DocumentVerifier()
    return face_verifier, doc_verifier

def load_image(image_file):
    """Convert Streamlit file buffer to OpenCV BGR format"""
    image = Image.open(image_file)
    image = np.array(image.convert('RGB'))
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

def main():
    # --- Session State Initialization ---
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'user_role' not in st.session_state:
        st.session_state['user_role'] = 'guest'
    if 'user_name' not in st.session_state:
        st.session_state['user_name'] = ''

    # --- Top Navbar ---
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Define available pages based on auth status
        if st.session_state['logged_in']:
            if st.session_state['user_role'] == 'admin':
                menu_options = ["Home", "Verify (e-KYC)", "Admin Dashboard", "Logout"]
            else:
                menu_options = ["Home", "Verify (e-KYC)", "Logout"]
        else:
            menu_options = ["Home", "Register", "Login"]

        # Use a horizontal radio button as a Navbar equivalent
        selected_page = st.radio("", menu_options, horizontal=True, label_visibility="collapsed")

    with col2:
        if st.session_state['logged_in']:
            # Minimal user profile display
            st.markdown(f"<div style='text-align: right; padding-top: 5px;'>👤 <b>{st.session_state['user_name']}</b></div>", unsafe_allow_html=True)
            # st.caption(f"Role: {st.session_state['user_role']}")
    
    st.markdown("---") # Separator

    # --- Page Routing ---
    
    if selected_page == "Home":
        show_home_page()
    
    elif selected_page == "Register":
        show_registration_page()
        
    elif selected_page == "Login":
        show_login_page()
        
    elif selected_page == "Verify (e-KYC)":
        if st.session_state['logged_in']:
            show_verification_page()
        else:
            st.warning("Please login to access this page.")
            
    elif selected_page == "Admin Dashboard":
        if st.session_state['logged_in'] and st.session_state['user_role'] == 'admin':
             show_admin_page()
        else:
             st.error("⛔ Access Denied: Admin privileges required.")
             
    elif selected_page == "Logout":
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = 'guest'
        st.session_state['user_name'] = ''
        st.rerun()

# --- Page Functions ---



# --- Behavioral Analysis Integration ---
import streamlit.components.v1 as components
from src.behavior_analysis.behavior_utils import BehaviorServer
import uuid

# Initialize Background Server (Singleton)
@st.cache_resource
def init_behavior_server():
    return BehaviorServer()

behavior_server = init_behavior_server()

def inject_behavior_script():
    """
    Injects the passive JavaScript tracker with a synchronized Session ID.
    """
    if 'behavior_session_id' not in st.session_state:
        st.session_state['behavior_session_id'] = str(uuid.uuid4())

    session_id = st.session_state['behavior_session_id']
    
    try:
        js_path = os.path.join(os.path.dirname(__file__), 'behavior_analysis', 'behavior_tracker.js')
        with open(js_path, 'r') as f:
            js_code = f.read()
            
        # Inject Python Session ID into JS scope
        html_code = f"""
        <script>
            window.PYTHON_SESSION_ID = "{session_id}";
            {js_code}
        </script>
        """
        components.html(html_code, height=0, width=0) # Invisible
    except Exception as e:
        print(f"Error injecting JS: {e}")

# --- Page Functions ---

def show_home_page():
    # Hero Section
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h1 style="font-size: 3rem; margin-bottom: 10px;">🛡️ Synthetic Identity Fraud Detection</h1>
        <p style="font-size: 1.2rem; color: #888;">Next-Gen AI Powered e-KYC Verification System</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # --- Feature Cards (Modern Glassmorphism Style) ---
    st.subheader("🌟 Core Capabilities")
    
    # Custom CSS for cards
    card_style = """
    <div style="
        background-color: #1e1e1e; 
        padding: 25px; 
        border-radius: 15px; 
        border: 1px solid #333; 
        text-align: center; 
        height: 100%;
        transition: transform 0.2s;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    ">
        <div style="font-size: 3rem; margin-bottom: 15px;">ICON_PLACEHOLDER</div>
        <h3 style="margin-bottom: 10px; color: #fff;">TITLE_PLACEHOLDER</h3>
        <p style="color: #aaa; font-size: 0.95rem;">DESC_PLACEHOLDER</p>
    </div>
    """
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(card_style.replace("ICON_PLACEHOLDER", "📄").replace("TITLE_PLACEHOLDER", "Doc Forgery Detection").replace("DESC_PLACEHOLDER", "Detects AI-generated IDs, Photoshop edits, and metadata anomalies using <b>EfficientNet</b> & <b>ELA Analysis</b>."), unsafe_allow_html=True)
        
    with col2:
        st.markdown(card_style.replace("ICON_PLACEHOLDER", "👤").replace("TITLE_PLACEHOLDER", "Biometric Verification").replace("DESC_PLACEHOLDER", "Ensures liveness & identity match. Prevents spoofing attacks using <b>DeepFace</b> & <b>Anti-Spoofing</b> algorithms."), unsafe_allow_html=True)

    with col3:
        st.markdown(card_style.replace("ICON_PLACEHOLDER", "🖱️").replace("TITLE_PLACEHOLDER", "Behavioral Analysis").replace("DESC_PLACEHOLDER", "Tracks session metadata, typing speed, and cursor patterns to flag <b>Bot-like interactions</b>."), unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- Pipeline Visualization ---
    st.subheader("🔄 End-to-End Security Pipeline")
    st.info("The system processes users through a multi-stage security filter to ensure maximum integrity.")
    
    # Custom Step Process
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; background: #0e1117; padding: 20px; border-radius: 10px; overflow-x: auto;">
        <div style="text-align: center; min-width: 100px;">📝<br><small>Register</small></div>
        <div style="font-size: 1.5rem;">➡️</div>
        <div style="text-align: center; min-width: 100px;">📷<br><small>Doc Scan</small></div>
        <div style="font-size: 1.5rem;">➡️</div>
        <div style="text-align: center; min-width: 100px;">😐<br><small>Liveness</small></div>
        <div style="font-size: 1.5rem;">➡️</div>
        <div style="text-align: center; min-width: 100px;">🤖<br><small>Behavior</small></div>
        <div style="font-size: 1.5rem;">➡️</div>
        <div style="text-align: center; min-width: 100px;">✅<br><small>Decision</small></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Tech Stack / About ---
    with st.expander("🛠️ Under the Hood (Tech Stack)"):
        st.markdown("""
        - **Frontend**: Streamlit (Python)
        - **Face Recognition**: DeepFace (FaceNet / VGG-Face)
        - **Document Analysis**: Tesseract OCR, ELA (Error Level Analysis)
        - **Database**: MongoDB Atlas (Cloud)
        - **ML Core**: TensorFlow, PyTorch, Scikit-learn
        """)
        
    st.markdown("---")

    # --- Footer ---
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #666; font-size: 0.8rem;">
        © 2026 Synthetic Fraud Detection Team | Compliant with GDPR & Data Privacy Standards
    </div>
    """, unsafe_allow_html=True)


def show_registration_page():
    # Inject Behavior Tracker with Session Link
    inject_behavior_script()
    
    st.header("📝 User Registration (Baseline Creation)")
    st.markdown("Create a verified identity baseline. This data will be used to detect fraud in future transactions.")

    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("1. Personal Details")
            full_name = st.text_input("Full Name (as on ID)")
            email = st.text_input("Email Address (Unique ID)")
            dob = st.date_input("Date of Birth") # Default format YYYY-MM-DD
            phone = st.text_input("Phone Number")
        
        with col2:
            st.subheader("2. Identity Document")
            doc_type = st.selectbox("Select Document Type", ["Aadhaar Card", "PAN Card", "Driving License", "Passport"])
            doc_id_number = st.text_input(f"{doc_type} Number")
            uploaded_file = st.file_uploader(f"Upload {doc_type} Image", type=['jpg', 'jpeg', 'png'])
            
        st.subheader("3. Biometric Baseline")
        st.info("Look straight into the camera and ensure good lighting.")
        selfie_image = st.camera_input("Capture Live Selfie")

        submitted = st.form_submit_button("🚀 Register Identity")

        # -- Backend Connection --
        from src.database.db_connection import Database
        from src.config import DATA_DIR
        import os
        
        if submitted:
            # --- Behavioral Fraud Check ---
            session_id = st.session_state.get('behavior_session_id')
            risk_score, decision, reasons = behavior_server.get_score(session_id)
            
            # Use columns to show risk signal without breaking flow (or blocking if critical)
            if decision == "REJECT":
                st.error(f"⛔ Registration Blocked: Suspicious Behavior Detected ({risk_score:.2f}). Reasons: {', '.join(reasons)}")
                return # Stop execution
            
            elif decision == "MANUAL_REVIEW":
                st.warning(f"⚠️ Unusual Behavior Detected ({risk_score:.2f}). Flagged for manual review.")
                # We typically proceed but mark the user flag. For this demo, we allow it.
            
            if not full_name or not email or not uploaded_file or not selfie_image or not doc_id_number:
                st.error("❌ Please fill all fields including Document ID and capture both document and selfie.")
            else:
                try:
                    # 1. Initialize DB (Creates folders & tables if missing)
                    db = Database()
                    
                    # 2. Save Images locally
                    user_folder = os.path.join(DATA_DIR, "users", email)
                    os.makedirs(user_folder, exist_ok=True)
                    
                    # Save ID Doc
                    doc_path = os.path.join(user_folder, "id_document.png")
                    with open(doc_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                        
                    # Save Selfie
                    selfie_path = os.path.join(user_folder, "selfie.png")
                    with open(selfie_path, "wb") as f:
                        f.write(selfie_image.getbuffer())

                    # 3. Simulate Embeddings/Behavior
                    dummy_embedding = b'\\x00' * 128 
                    
                    # Store the Real Behavioral Baseline
                    import json
                    behavior_baseline = json.dumps({
                        "risk_score": risk_score,
                        "decision": decision,
                        "reasons": reasons,
                        "session_id": session_id
                    })
                    # 3. Generate Real Face Embedding
                    face_verifier, _ = get_models()
                    
                    # Convert selfie for processing
                    selfie_cv2 = load_image(selfie_image)
                    
                    # Detect and embed
                    cropped_face = face_verifier.detect_face(selfie_cv2)
                    if cropped_face is None:
                        st.error("⚠️ No face detected in selfie! Please try again.")
                        st.stop()
                        
                    real_embedding = face_verifier.get_embedding(cropped_face)
                    if real_embedding is None:
                        st.error("⚠️ Could not generate face embedding. Low quality image?")
                        st.stop()
                        
                    # Convert numpy array to list for MongoDB storage (binary is okay too, but list is safer for JSON)
                    embedding_list = real_embedding.tolist()
                    
                    dummy_behavior = "{'avg_flight': 0.2}"

                    # 4. Save to MongoDB
                    password = str(dob).replace("-", "") # Format: YYYYMMDD
                    
                    user_data = {
                        "email": email,
                        "full_name": full_name,
                        "dob": str(dob),
                        "phone": phone,
                        "document_type": doc_type,
                        "document_id": doc_id_number,
                        "password": password,
                        "face_embedding": dummy_embedding, 
                        "behavior_baseline": behavior_baseline,
                        "face_embedding": embedding_list, # Storing real embedding
                        "behavior_baseline": dummy_behavior,
                        "role": "user"
                    }

                    if db.create_user(user_data):
                        st.success(f"✅ Registration Successful! Your Password is your DOB: {password}")
                        st.caption(f"Behavior Risk: {decision} ({risk_score:.2f})")
                        st.info("Redirecting to Login...")
                    else:
                        st.warning("⚠️ User with this email already registered!")
                            
                    db.close()
                
                except Exception as e:
                    st.error(f"An error occurred: {e}")

def show_login_page():
    # Inject Behavior Tracker
    inject_behavior_script()

    st.header("🔐 User Login")
    
    with st.form("login_form"):
        email = st.text_input("Email Address")
        password = st.text_input("Password (DOB YYYYMMDD)", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            # --- Behavioral Fraud Check ---
            session_id = st.session_state.get('behavior_session_id')
            risk_score, decision, reasons = behavior_server.get_score(session_id)
            
            if decision == "REJECT":
                st.error(f"⛔ Login Blocked: Suspicious Bot-like Behavior. Reasons: {', '.join(reasons)}")
                return
                
            from src.database.db_connection import Database
            db = Database()
            user = db.verify_user(email, password)
            db.close()
            
            if user:
                # User found: user is now a dict
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = user.get('full_name', 'User')
                st.session_state['user_role'] = user.get('role', 'user')
                st.session_state['user_email'] = user.get('email')
                st.success(f"Welcome back, {user.get('full_name')}!")
                if decision == "MANUAL_REVIEW":
                    st.warning("⚠️ Security Note: Unusual interaction pattern detected.")
                st.rerun()
            else:
                st.error("Invalid Credentials")

def show_verification_page():


    st.header("e-KYC Verification")
    st.info("Verification module coming soon...")
    st.header("🕵️ e-KYC Verification")
    st.markdown("Verify your identity by uploading your ID and taking a live selfie.")

    # Load Models
    with st.spinner("Loading AI Models..."):
        face_verifier, doc_verifier = get_models()

    # Layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Document Upload")
        doc_file = st.file_uploader("Upload ID Document", type=['jpg', 'jpeg', 'png'])
        
    with col2:
        st.subheader("2. Live Liveness Check")
        live_selfie = st.camera_input("Take a Selfie")

    # Verify Button
    if st.button("🚀 Run Verification"):
        if not doc_file or not live_selfie:
            st.error("Please provide both ID Document and Live Selfie.")
        else:
            try:
                # --- Step 1: Pre-processing ---
                doc_img = load_image(doc_file)
                selfie_img = load_image(live_selfie)
                
                user_email = st.session_state.get('user_name', '') # Using name as placeholder, but ideally need email from session
                # FIX: We need email to fetch stored embedding. 
                # Assuming 'user_email' was added to session during login attempt earlier. 
                # If not, we might fail. Let's try fetching user from DB using session info if available.
                
                # Retrieve stored user data
                from src.database.db_connection import Database
                db = Database()
                # We need the logged in user's email.
                # In login we set: st.session_state['user_email'] (I added this in previous turn logic)
                current_email = st.session_state.get('user_email')
                
                if not current_email:
                    st.error("Session Error: Could not identify logged-in user.")
                    return

                user_record = db.get_user(current_email)
                db.close()
                
                if not user_record:
                    st.error("User record not found in database.")
                    return

                # --- Step 2: Document Verification ---
                st.info("Analyzing Document...")
                # We can pass user info to validate against OCR text
                user_info = {
                    "name": user_record.get('full_name'),
                    "dob": user_record.get('dob'),
                    "id_number": user_record.get('document_id')
                }
                
                doc_result = doc_verifier.verify_document(doc_img, user_data=user_info)
                
                # --- Step 3: Face Verification ---
                st.info("Verifying Face & Liveness...")
                
                # Liveness
                is_live, liveness_score = face_verifier.check_liveness(selfie_img)
                
                # Matching
                match_score = 0.0
                face_decision = "FAIL"
                
                if is_live:
                    cropped_face = face_verifier.detect_face(selfie_img)
                    if cropped_face is not None:
                        live_embedding = face_verifier.get_embedding(cropped_face)
                        stored_embedding_raw = user_record.get('face_embedding')
                        
                        # Convert stored embedding from database (might be bytes, list, or Binary)
                        stored_embedding = None
                        if stored_embedding_raw:
                            if isinstance(stored_embedding_raw, (list, np.ndarray)):
                                stored_embedding = np.array(stored_embedding_raw, dtype=np.float32)
                            elif isinstance(stored_embedding_raw, bytes):
                                # If stored as bytes, convert back to numpy array
                                try:
                                    stored_embedding = np.frombuffer(stored_embedding_raw, dtype=np.float32)
                                except:
                                    st.warning("Could not decode stored embedding from bytes.")
                        
                        if live_embedding is not None and stored_embedding is not None:
                            match_score, face_decision = face_verifier.verify_with_stored_embedding(live_embedding, stored_embedding)
                        else:
                            st.warning("Could not generate embeddings for comparison.")
                    else:
                        st.warning("Face not detected in selfie.")
                else:
                    st.warning("⚠️ Liveness Check Failed! Possible spoof detected.")

                # --- Step 4: Display Results ---
                st.write("---")
                st.subheader("📝 Verification Report")
                
                res_col1, res_col2 = st.columns(2)
                
                with res_col1:
                    st.markdown("#### 📄 Document Analysis")
                    st.write(f"**Status:** {doc_result['decision']}")
                    st.write(f"**Risk Score:** {doc_result['doc_risk_score']}")
                    
                    with st.expander("View Details"):
                        st.json(doc_result)
                        
                    if doc_result['decision'] == "APPROVE":
                        st.success("Document Verified ✅")
                    elif doc_result['decision'] == "MANUAL_REVIEW":
                        st.warning("Document Needs Review ⚠️")
                    else:
                        st.error("Document Rejected ❌")

                with res_col2:
                    st.markdown("#### 👤 Biometric Analysis")
                    st.write(f"**Liveness:** {'PASS ✅' if is_live else 'FAIL ❌'} ({liveness_score:.2f})")
                    st.write(f"**Face Match:** {face_decision} ({match_score:.2f})")
                    
                    if face_decision == "VERIFIED" and is_live:
                         st.success("Identity Verified ✅")
                    else:
                         st.error("Identity Verification Failed ❌")
                
                # Log attempt
                final_decision = "APPROVED" if (doc_result['decision'] == "APPROVE" and face_decision == "VERIFIED" and is_live) else "REJECTED"
                
                # Safe conversion for scores
                try:
                    face_score_val = float(match_score) if match_score and match_score != b'' else 0.0
                except (ValueError, TypeError):
                    face_score_val = 0.0
                    
                try:
                    liveness_score_val = float(liveness_score) if liveness_score and liveness_score != b'' else 0.0
                except (ValueError, TypeError):
                    liveness_score_val = 0.0
                
                attempt_data = {
                    "user_id": user_record.get('_id'), # MongoDB ObjectId
                    "user_email": current_email,
                    "doc_score": doc_result['doc_risk_score'],
                    "face_score": face_score_val,
                    "liveness_score": liveness_score_val,
                    "final_decision": final_decision,
                    "details": str(doc_result)
                }
                
                # Log to DB
                db = Database()
                db.log_kyc_attempt(attempt_data)
                db.close()
                
                if final_decision == "APPROVED":
                    st.balloons()
                    st.success("🎉 KYC VERIFICATION SUCCESSFUL!")
                else:
                    st.error("⛔ KYC VERIFICATION FAILED. Please try again or contact support.")

            except Exception as e:
                st.error(f"An error occurred during verification: {e}")

def show_admin_page():
    st.header("📊 Admin Dashboard")
    st.markdown("View system logs and registered users.")
    
    from src.database.db_connection import Database
    import pandas as pd
    
    db = Database()
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["👥 Registered Users", "📜 Verification Logs"])
    
    with tab1:
        st.subheader("User Database")
        try:
            # Fetch all users
            users_list = db.get_all_users()
            df_users = pd.DataFrame(users_list)
            
            if not df_users.empty:
                # Select specific columns to display (including new Doc fields)
                display_cols = ['full_name', 'email', 'phone', 'dob', 'document_type', 'document_id', 'role', 'created_at']
                # Ensure validation in case old users don't have these fields
                for col in display_cols:
                    if col not in df_users.columns:
                        df_users[col] = None
                        
                df_users = df_users[display_cols]
                st.dataframe(df_users, use_container_width=True)
            
            st.metric("Total Users", len(df_users))
        except Exception as e:
            st.error(f"Error fetching users: {e}")
            
    with tab2:
        st.subheader("Recent Verification Attempts")
        try:
             logs_list = db.get_all_logs()
             df_logs = pd.DataFrame(logs_list)
             st.dataframe(df_logs, use_container_width=True)
        except Exception as e:
            st.info("No verification logs found yet.")
        except Exception as e:
            st.info("No verification logs found yet.")
            
    db.close()

if __name__ == "__main__":
    main()
