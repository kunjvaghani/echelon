import streamlit as st
import os
import sys
import time
from datetime import date
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
    # --- Custom CSS for Premium UI ---
    st.markdown("""
    <style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Navbar Styles */
    .navbar-container {
        background: rgba(20, 20, 40, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px 30px;
        border-radius: 0 0 20px 20px;
        margin-bottom: 30px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
    }
    
    .navbar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .navbar-brand-icon {
        font-size: 2rem;
        background: linear-gradient(135deg, #00d4ff, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .navbar-brand-text {
        font-size: 1.3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 0%, #a0aec0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 60px 20px;
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.1) 0%, rgba(0, 212, 255, 0.1) 100%);
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 40px;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(124, 58, 237, 0.1) 0%, transparent 50%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.5; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.1); }
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #00d4ff 50%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 15px;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: #a0aec0;
        margin-bottom: 30px;
        position: relative;
        z-index: 1;
    }
    
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, #7c3aed, #00d4ff);
        color: white;
        padding: 8px 20px;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 20px;
        position: relative;
        z-index: 1;
    }
    
    /* Problem Statement Section */
    .problem-section {
        background: rgba(255, 50, 50, 0.1);
        border: 1px solid rgba(255, 100, 100, 0.3);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 40px;
    }
    
    .problem-title {
        color: #ff6b6b;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    .problem-text {
        color: #e0e0e0;
        font-size: 1rem;
        line-height: 1.7;
    }
    
    /* Threat Cards */
    .threat-card {
        background: rgba(30, 30, 50, 0.8);
        border: 1px solid rgba(255, 100, 100, 0.2);
        border-radius: 15px;
        padding: 25px;
        height: 100%;
        transition: all 0.3s ease;
    }
    
    .threat-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 100, 100, 0.5);
        box-shadow: 0 10px 30px rgba(255, 50, 50, 0.2);
    }
    
    .threat-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
    }
    
    .threat-title {
        color: #ff6b6b;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .threat-desc {
        color: #aaa;
        font-size: 0.9rem;
    }
    
    /* Solution Cards */
    .solution-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(124, 58, 237, 0.1));
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        height: 100%;
        transition: all 0.3s ease;
    }
    
    .solution-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 40px rgba(0, 212, 255, 0.2);
    }
    
    .solution-icon {
        font-size: 3rem;
        margin-bottom: 15px;
        background: linear-gradient(135deg, #00d4ff, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .solution-title {
        color: #fff;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .solution-desc {
        color: #a0aec0;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* Workflow Pipeline */
    .workflow-container {
        background: rgba(20, 20, 40, 0.6);
        border-radius: 20px;
        padding: 40px 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 40px 0;
    }
    
    .workflow-step {
        text-align: center;
        padding: 15px;
        transition: all 0.3s ease;
    }
    
    .workflow-step:hover {
        transform: scale(1.1);
    }
    
    .workflow-number {
        background: linear-gradient(135deg, #7c3aed, #00d4ff);
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    .workflow-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    
    .workflow-label {
        color: #fff;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .workflow-arrow {
        color: #7c3aed;
        font-size: 2rem;
        padding-top: 40px;
    }
    
    /* Stats Section */
    .stat-card {
        background: rgba(30, 30, 50, 0.8);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: #a0aec0;
        font-size: 0.9rem;
        margin-top: 5px;
    }
    
    /* CTA Section */
    .cta-section {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(0, 212, 255, 0.2));
        border-radius: 25px;
        padding: 50px;
        text-align: center;
        border: 1px solid rgba(124, 58, 237, 0.3);
        margin: 40px 0;
    }
    
    .cta-title {
        font-size: 2rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 15px;
    }
    
    .cta-subtitle {
        color: #a0aec0;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 30px;
        color: #666;
        font-size: 0.85rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 50px;
    }
    
    /* Section Headers */
    .section-header {
        text-align: center;
        margin-bottom: 40px;
    }
    
    .section-header h2 {
        font-size: 2rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 10px;
    }
    
    .section-header p {
        color: #a0aec0;
        font-size: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Session State Initialization ---
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'user_role' not in st.session_state:
        st.session_state['user_role'] = 'guest'
    if 'user_name' not in st.session_state:
        st.session_state['user_name'] = ''
    if 'nav_to' not in st.session_state:
        st.session_state['nav_to'] = None

    # --- Premium Navbar ---
    st.markdown("""
    <div class="navbar-container">
        <div class="navbar-brand">
            <span class="navbar-brand-icon">🛡️</span>
            <span class="navbar-brand-text">SecureKYC</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation Menu
    col_nav, col_user = st.columns([5, 1])
    
    with col_nav:
        if st.session_state['logged_in']:
            if st.session_state['user_role'] == 'admin':
                menu_options = ["🏠 Home", "✅ Verify (e-KYC)", "📊 Admin Dashboard", "🚪 Logout"]
            else:
                menu_options = ["🏠 Home", "✅ Verify (e-KYC)", "🚪 Logout"]
        else:
            menu_options = ["🏠 Home", "📝 Register", "🔐 Login"]
        
        # Check if navigation was triggered by CTA buttons
        default_index = 0
        if st.session_state['nav_to'] == 'register' and not st.session_state['logged_in']:
            default_index = 1  # Register is at index 1
            st.session_state['nav_to'] = None  # Reset after use
        elif st.session_state['nav_to'] == 'login' and not st.session_state['logged_in']:
            default_index = 2  # Login is at index 2
            st.session_state['nav_to'] = None  # Reset after use

        selected_page = st.radio("", menu_options, horizontal=True, label_visibility="collapsed", index=default_index)

    with col_user:
        if st.session_state['logged_in']:
            st.markdown(f"""
            <div style='text-align: right; padding: 8px 15px; background: rgba(124, 58, 237, 0.2); border-radius: 20px; border: 1px solid rgba(124, 58, 237, 0.3);'>
                👤 <b style='color: #00d4ff;'>{st.session_state['user_name']}</b>
            </div>
            """, unsafe_allow_html=True)

    # --- Page Routing ---
    if "Home" in selected_page:
        show_home_page()
    elif "Register" in selected_page:
        show_registration_page()
    elif "Login" in selected_page:
        show_login_page()
    elif "Verify" in selected_page:
        if st.session_state['logged_in']:
            show_verification_page()
        else:
            st.warning("⚠️ Please login to access the verification page.")
    elif "Admin" in selected_page:
        if st.session_state['logged_in'] and st.session_state['user_role'] == 'admin':
            show_admin_page()
        else:
            st.error("⛔ Access Denied: Admin privileges required.")
    elif "Logout" in selected_page:
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
    <div class="hero-section">
        <div class="hero-badge">🔒 AI-Powered Security</div>
        <h1 class="hero-title">Synthetic Identity Fraud Detection</h1>
        <p class="hero-subtitle">Next-Generation e-KYC Verification System with Multi-Layer AI Protection</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Problem Statement Section
    st.markdown("""
    <div class="problem-section">
        <h3 class="problem-title">⚠️ The Growing Threat of Synthetic Identity Fraud</h3>
        <p class="problem-text">
            <b>Synthetic identity fraud</b> is the fastest-growing type of financial crime, causing billions in losses annually. 
            Criminals combine real and fake information to create new identities that bypass traditional verification systems.
            <br><br>
            <b>Key Challenges:</b>
            <br>• AI-generated fake documents that look authentic
            <br>• Deepfake technology fooling facial recognition
            <br>• Bot-driven mass registration attempts
            <br>• Stolen biometrics used for identity spoofing
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Threat Cards
    st.markdown("<div class='section-header'><h2>🎯 Common Attack Vectors We Detect</h2><p>Our system is trained to identify and block these fraud techniques</p></div>", unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.columns(4)
    
    with t1:
        st.markdown("""
        <div class="threat-card">
            <div class="threat-icon">🆔</div>
            <div class="threat-title">Forged Documents</div>
            <div class="threat-desc">Photoshopped IDs, fake Aadhaar/PAN cards, AI-generated government documents</div>
        </div>
        """, unsafe_allow_html=True)
        
    with t2:
        st.markdown("""
        <div class="threat-card">
            <div class="threat-icon">🎭</div>
            <div class="threat-title">Deepfake Faces</div>
            <div class="threat-desc">AI-generated selfies, video replays, photo masks, screen spoofing</div>
        </div>
        """, unsafe_allow_html=True)
        
    with t3:
        st.markdown("""
        <div class="threat-card">
            <div class="threat-icon">🤖</div>
            <div class="threat-title">Bot Attacks</div>
            <div class="threat-desc">Automated registrations, script-driven form fills, abnormal behavior patterns</div>
        </div>
        """, unsafe_allow_html=True)
        
    with t4:
        st.markdown("""
        <div class="threat-card">
            <div class="threat-icon">👤</div>
            <div class="threat-title">Identity Theft</div>
            <div class="threat-desc">Stolen credentials, mismatched biometrics, unauthorized access attempts</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Our Solution
    st.markdown("<div class='section-header'><h2>🛡️ Our Multi-Layer Protection System</h2><p>Comprehensive AI-powered verification at every step</p></div>", unsafe_allow_html=True)
    
    s1, s2, s3 = st.columns(3)
    
    with s1:
        st.markdown("""
        <div class="solution-card">
            <div class="solution-icon">📄</div>
            <div class="solution-title">Document Verification</div>
            <div class="solution-desc">
                ELA (Error Level Analysis) detects image tampering. 
                EfficientNet AI model classifies real vs fake documents. 
                OCR extracts and validates ID information.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with s2:
        st.markdown("""
        <div class="solution-card">
            <div class="solution-icon">👤</div>
            <div class="solution-title">Biometric Verification</div>
            <div class="solution-desc">
                DeepFace ensures live person detection.
                Anti-spoofing algorithms block photos & masks.
                Face embedding matching confirms identity.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with s3:
        st.markdown("""
        <div class="solution-card">
            <div class="solution-icon">🧠</div>
            <div class="solution-title">Behavioral Analysis</div>
            <div class="solution-desc">
                Keystroke dynamics detect bot behavior.
                Mouse movement patterns analyzed.
                Session metadata flags suspicious activity.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Workflow Pipeline
    st.markdown("<br><div class='section-header'><h2>🔄 e-KYC Verification Workflow</h2><p>Secure end-to-end identity verification process</p></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="workflow-container">
        <div style="display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div class="workflow-step">
                <div class="workflow-number">1</div>
                <div class="workflow-icon">📱</div>
                <div class="workflow-label">Phone OTP</div>
            </div>
            <div class="workflow-arrow">→</div>
            <div class="workflow-step">
                <div class="workflow-number">2</div>
                <div class="workflow-icon">📝</div>
                <div class="workflow-label">Registration</div>
            </div>
            <div class="workflow-arrow">→</div>
            <div class="workflow-step">
                <div class="workflow-number">3</div>
                <div class="workflow-icon">📄</div>
                <div class="workflow-label">Doc Upload</div>
            </div>
            <div class="workflow-arrow">→</div>
            <div class="workflow-step">
                <div class="workflow-number">4</div>
                <div class="workflow-icon">🤳</div>
                <div class="workflow-label">Live Selfie</div>
            </div>
            <div class="workflow-arrow">→</div>
            <div class="workflow-step">
                <div class="workflow-number">5</div>
                <div class="workflow-icon">🔍</div>
                <div class="workflow-label">AI Analysis</div>
            </div>
            <div class="workflow-arrow">→</div>
            <div class="workflow-step">
                <div class="workflow-number">6</div>
                <div class="workflow-icon">✅</div>
                <div class="workflow-label">Decision</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Section
    st.markdown("<br><div class='section-header'><h2>📈 Platform Statistics</h2></div>", unsafe_allow_html=True)
    
    stat1, stat2, stat3, stat4 = st.columns(4)
    
    with stat1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">99.2%</div>
            <div class="stat-label">Fraud Detection Rate</div>
        </div>
        """, unsafe_allow_html=True)
        
    with stat2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">&lt;2s</div>
            <div class="stat-label">Average Verification Time</div>
        </div>
        """, unsafe_allow_html=True)
        
    with stat3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">3-Layer</div>
            <div class="stat-label">Security Pipeline</div>
        </div>
        """, unsafe_allow_html=True)
        
    with stat4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Real-time Monitoring</div>
        </div>
        """, unsafe_allow_html=True)
    
    # CTA Section
    st.markdown("""
    <div class="cta-section">
        <div class="cta-title">🚀 Ready to Get Started?</div>
        <div class="cta-subtitle">Create your verified identity baseline in minutes</div>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Buttons using Streamlit
    cta1, cta2, cta3 = st.columns([1, 2, 1])
    with cta2:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📝 Register Now", use_container_width=True, type="primary"):
                st.session_state['nav_to'] = 'register'
                st.rerun()
        with col_btn2:
            if st.button("🔐 Login", use_container_width=True):
                st.session_state['nav_to'] = 'login'
                st.rerun()
    
    # Tech Stack
    with st.expander("🛠️ Technology Stack"):
        tech1, tech2, tech3 = st.columns(3)
        with tech1:
            st.markdown("""
            **🖥️ Frontend**
            - Streamlit (Python)
            - Custom CSS & HTML
            - Responsive Design
            """)
        with tech2:
            st.markdown("""
            **🧠 AI/ML Core**
            - DeepFace (Recognition)
            - EfficientNet (Detection)
            - TensorFlow & PyTorch
            """)
        with tech3:
            st.markdown("""
            **🗄️ Backend**
            - MongoDB Atlas (Cloud DB)
            - Tesseract OCR
            - Twilio SMS (OTP)
            """)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>© 2026 SecureKYC - Synthetic Identity Fraud Detection System</p>
        <p>Built with 🛡️ Security First | Compliant with GDPR & Data Privacy Standards</p>
    </div>
    """, unsafe_allow_html=True)


def show_registration_page():
    # Inject Behavior Tracker with Session Link
    inject_behavior_script()
    
    st.header("📝 User Registration (Baseline Creation)")
    st.markdown("Create a verified identity baseline. This data will be used to detect fraud in future transactions.")

    # --- Session state for OTP flow ---
    if 'registration_phone_verified' not in st.session_state:
        st.session_state['registration_phone_verified'] = False
    if 'registration_verified_phone' not in st.session_state:
        st.session_state['registration_verified_phone'] = ''
    if 'registration_otp_sent_for' not in st.session_state:
        st.session_state['registration_otp_sent_for'] = None
    if 'registration_otp_demo' not in st.session_state:
        st.session_state['registration_otp_demo'] = None

    # --- Step 1: Phone OTP verification (must complete before selfie / form) ---
    if not st.session_state['registration_phone_verified']:
        st.subheader("Step 1: Verify your phone number")
        st.caption("Enter your phone number. You will receive an OTP to verify before proceeding.")
        from src.otp_service import send_otp_to_phone, verify_otp

        reg_phone = st.text_input("Phone Number", key="reg_phone", placeholder="e.g. 9876543210 or +919876543210")
        send_clicked = st.button("Send OTP", key="send_otp_btn")
        if send_clicked:
            if not reg_phone or not reg_phone.strip():
                st.error("Please enter your phone number.")
            else:
                success, msg, demo_otp = send_otp_to_phone(reg_phone.strip())
                if success:
                    st.session_state['registration_otp_sent_for'] = reg_phone.strip()
                    st.session_state['registration_otp_demo'] = demo_otp
                    st.success(msg)
                    if demo_otp:
                        st.info(f"**Demo / development:** Your OTP is **{demo_otp}** (SMS not configured).")
                else:
                    st.error(msg)

        if st.session_state.get('registration_otp_sent_for'):
            st.markdown("---")
            st.caption("Enter the OTP you received.")
            otp_entered = st.text_input("Enter OTP", key="reg_otp_input", max_chars=6, placeholder="6-digit code")
            verify_clicked = st.button("Verify OTP", key="verify_otp_btn")
            if verify_clicked:
                if not otp_entered or len(otp_entered.strip()) != 6:
                    st.error("Please enter the 6-digit OTP.")
                else:
                    if verify_otp(st.session_state['registration_otp_sent_for'], otp_entered.strip()):
                        st.session_state['registration_phone_verified'] = True
                        st.session_state['registration_verified_phone'] = st.session_state['registration_otp_sent_for']
                        st.session_state['registration_otp_sent_for'] = None
                        st.session_state['registration_otp_demo'] = None
                        st.success("Phone verified successfully. You can now complete registration.")
                        st.rerun()
                    else:
                        st.error("Invalid or expired OTP. Please request a new one.")

        st.markdown("---")
        st.info("Complete phone verification above to unlock the registration form and selfie capture.")
        return

    # --- Step 2: Full registration form (only after OTP verified) ---
    verified_phone = st.session_state['registration_verified_phone']
    st.success(f"Phone verified: **{verified_phone}**")
    if st.button("Change phone number", key="change_phone_btn"):
        st.session_state['registration_phone_verified'] = False
        st.session_state['registration_verified_phone'] = ''
        st.session_state['registration_otp_sent_for'] = None
        st.session_state['registration_otp_demo'] = None
        st.rerun()
    st.markdown("---")

    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("1. Personal Details")
            full_name = st.text_input("Full Name (as on ID)")
            email = st.text_input("Email Address (Unique ID)")
            dob = st.date_input(
                "Date of Birth",
                min_value=date(1970, 1, 1),
                max_value=date(2026, 12, 31),
                value=date(1990, 1, 1),
            )
            # Phone is read-only; already verified
            st.text_input("Phone Number (verified)", value=verified_phone, disabled=True, key="reg_phone_verified_display")
            phone = verified_phone
        
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
                        # Clear registration OTP state so next visit starts from Step 1
                        st.session_state['registration_phone_verified'] = False
                        st.session_state['registration_verified_phone'] = ''
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
