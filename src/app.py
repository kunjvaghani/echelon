import streamlit as st
import os
import sys

# Add project root to path so 'src' module can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set page config
st.set_page_config(
    page_title="Synthetic Identity Fraud Detection",
    page_icon="🛡️",
    layout="wide"
)

def main():
    # --- Session State Initialization ---
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'user_role' not in st.session_state:
        st.session_state['user_role'] = 'guest'
    if 'user_name' not in st.session_state:
        st.session_state['user_name'] = ''

    # --- Top Navbar ---
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
    # st.title("🛡️ Synthetic Identity Fraud Detection System")
    st.markdown("### 🚀 Next-Gen AI Powered e-KYC Verification")
    st.markdown("---")

    # --- Feature Cards ---
    st.subheader("🌟 Core Capabilities")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="padding: 20px; border: 1px solid #333; border-radius: 10px; text-align: center;">
            <h1>📄</h1>
            <h3>Doc Forgery</h3>
            <p>Detects AI-generated IDs & edits using <b>EfficientNet</b> & <b>ELA Analysis</b>.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style="padding: 20px; border: 1px solid #333; border-radius: 10px; text-align: center;">
            <h1>👤</h1>
            <h3>Face Biometrics</h3>
            <p>Ensures liveness & identity match using <b>DeepFace</b> & <b>Anti-Spoofing</b>.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="padding: 20px; border: 1px solid #333; border-radius: 10px; text-align: center;">
            <h1>🖱️</h1>
            <h3>Behavioral Patterns</h3>
            <p>Tracks value input speed & anomalies to flag <b>Bot-like interactions</b>.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Pipeline Visualization ---
    st.subheader("🔄 End-to-End Verification Pipeline")
    st.info("The system processes users through a multi-stage security filter:")
    
    steps = ["1. User Registration", "2. Document Scan (OCR + Forgery)", "3. Liveness Check", "4. Behavior Analysis", "5. Fraud Risk Scoring", "6. Final Decision"]
    st.progress(100)
    st.write(" ➡️ ".join(steps))

    # --- Project Roadmap / About ---
    with st.expander("🗺️ Project Roadmap & Architecture"):
        st.markdown("""
        - **Phase 1**: Core Module Implementation (Face, Doc, Behavior)
        - **Phase 2**: Integration & Testing
        - **Phase 3**: Polish & Real-world Piloting
        
        *Built with Streamlit, OpenCV, DeepFace, and Scikit-learn.*
        """)

    st.markdown("---")

    # --- Footer: Guidelines ---
    st.subheader("🏛️ Government KYC Guidelines")
    f_col1, f_col2 = st.columns(2)
    
    with f_col1:
        st.markdown("**✅ How to perform valid KYC:**")
        st.markdown("- Ensure lighting is sufficient for selfies.")
        st.markdown("- ID Documents must be placed on a plain dark background.")
        st.markdown("- Do not wear sunglasses or hats during verification.")
    
    with f_col2:
        st.markdown("**⚠️ Common Rejection Reasons:**")
        st.markdown("- Blurry or cropped ID images.")
        st.markdown("- Mismatch between ID photo and live face.")
        st.markdown("- Suspiciously fast form filling (Bot detected).")
    
    st.caption("© 2026 Synthetic Fraud Detection Team. Compliant with Data Privacy Standards.")


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
                st.success(f"Welcome back, {user.get('full_name')}!")
                if decision == "MANUAL_REVIEW":
                    st.warning("⚠️ Security Note: Unusual interaction pattern detected.")
                st.rerun()
            else:
                st.error("Invalid Credentials")

def show_verification_page():


    st.header("e-KYC Verification")
    st.info("Verification module coming soon...")

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
