import streamlit as st
import os

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
        st.markdown("""
        ### Welcome to the Advanced e-KYC System
        This system uses AI to detect synthetic identities by analyzing:
        - 📄 **Document Forgery** (AI-generated ID detection)
        - 👤 **Face Biometrics** (Liveness & Matching)
        - 🖱️ **Behavioral Patterns** (Interaction anomalies)
        
        **Get Started:** Select 'Register' to create a baseline identity.
        """)

    elif app_mode == "Register (Baseline)":
        st.header("User Registration")
        # TODO: Implement Registration Flow
        st.info("Registration module placeholder")

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
