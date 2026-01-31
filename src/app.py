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
    st.title("🛡️ Synthetic Identity Fraud Detection System")
    st.sidebar.title("Navigation")  
    
    app_mode = st.sidebar.selectbox("Choose Mode", 
        ["Home", "Register (Baseline)", "Verify (e-KYC)", "Admin Dashboard"])

    if app_mode == "Home":
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

    elif app_mode == "Register (Baseline)":
        st.header("📝 User Registration (Baseline Creation)")
        st.markdown("Create a verified identity baseline. This data will be used to detect fraud in future transactions.")

        with st.form("registration_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("1. Personal Details")
                full_name = st.text_input("Full Name (as on ID)")
                email = st.text_input("Email Address (Unique ID)")
                dob = st.date_input("Date of Birth")
                phone = st.text_input("Phone Number")
            
            with col2:
                st.subheader("2. Identity Document")
                doc_type = st.selectbox("Select Document Type", ["Aadhaar Card", "PAN Card", "Driving License", "Passport"])
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
                if not full_name or not email or not uploaded_file or not selfie_image:
                    st.error("❌ Please fill all fields and capture both document and selfie.")
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

                        # 3. Simulate Embeddings/Behavior (Placeholder until modules linked)
                        # In next steps, we will call face_utils.get_embedding(selfie_path)
                        dummy_embedding = b'\x00' * 128 
                        dummy_behavior = "{'avg_flight': 0.2}"

                        # 4. Save to SQLite
                        # Check if user exists
                        if db.get_user(email):
                            st.warning("⚠️ User with this email already registered!")
                        else:
                            cursor = db.conn.cursor()
                            cursor.execute('''
                                INSERT INTO users (username, full_name, face_embedding, behavior_baseline)
                                VALUES (?, ?, ?, ?)
                            ''', (email, full_name, dummy_embedding, dummy_behavior))
                            db.conn.commit()
                            
                            st.success(f"✅ Registration Successful! Data saved to {user_folder}")
                            st.balloons()
                            
                        db.close()
                        
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                    
                    # Debug Preview
                    with st.expander("Debug Preview"):
                        st.image(uploaded_file, caption="Uploaded Doc", width=200)
                        st.write(f"Doc Type: {doc_type}")

    elif app_mode == "Verify (e-KYC)":
        st.header("e-KYC Verification")
        # TODO: Implement Verification Flow
        st.info("Verification module placeholder")

    elif app_mode == "Admin Dashboard":
        st.header("Fraud Analytics")
        # TODO: Implement Admin Dashboard
        st.info("Admin dashboard placeholder")

if __name__ == "__main__":
    main()
