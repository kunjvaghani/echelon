import os
import datetime
import time
import random
from typing import Tuple, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from src.database.db_connection import Database
from src.otp_service import generate_otp, send_email_otp

class AuthService:
    def __init__(self):
        self.db = Database()

    def register_user(self, user_data: dict) -> Tuple[bool, str]:
        """
        Registers a new user.
        - Hashes password
        - Generates OTP
        - Stores user with is_verified=False
        - Sends OTP
        """
        email = user_data.get('email')
        password = user_data.get('password')
        
        if not email or not password:
            return False, "Email and Password are required."

        # Check if user already exists
        existing_user = self.db.get_user(email)
        if existing_user:
            return False, "User already exists."

        # Hash Password
        password_hash = generate_password_hash(password)
        user_data['password_hash'] = password_hash
        del user_data['password'] # Remove plain password

        # Generate OTP
        otp = generate_otp()
        expiry = time.time() + 300 # 5 minutes

        user_data['otp'] = otp
        user_data['otp_expiry'] = expiry
        user_data['is_verified'] = False

        # Create User
        if self.db.create_user(user_data):
            # Send Email
            sent, msg = send_email_otp(email, otp)
            if sent:
                return True, "Registration successful. Please verify your email."
            else:
                # User created but email failed. Ideally rollback or allow resend.
                return True, f"Registration successful but email failed: {msg}. Please request resend."
        
        return False, "Database error during registration."

    def login_user(self, email, password) -> Tuple[bool, str, Optional[dict]]:
        """
        Authenticates a user.
        Returns: (Success, Message, UserData)
        """
        user = self.db.get_user_by_credentials(email)
        if not user:
            return False, "Invalid email or password.", None

        if not check_password_hash(user.get('password_hash', ''), password):
            return False, "Invalid email or password.", None

        if not user.get('is_verified'):
            return False, "Account not verified. Please verify your email.", None

        return True, "Login successful.", user

    def verify_email(self, email, otp) -> Tuple[bool, str]:
        """
        Verifies the user's email using OTP.
        """
        user = self.db.get_user(email)
        if not user:
            return False, "User not found."

        # ALWAYS check OTP to prevent bypass, even if already verified
        stored_otp = user.get('otp')
        expiry = user.get('otp_expiry', 0)

        if not stored_otp:
             return False, "No OTP found. Please request a new one."

        if time.time() > expiry:
            return False, "OTP has expired. Please request a new one."

        if stored_otp.strip() == otp.strip():
            if not user.get('is_verified'):
                 self.db.update_user_verification(email, True)
            # Clear OTP
            self.db.store_otp(email, None, 0) 
            return True, "Email verified successfully."
        
        return False, "Invalid OTP."

    def send_login_otp(self, email) -> Tuple[bool, str]:
        """
        Sends OTP for Login (works for verified and unverified).
        """
        user = self.db.get_user(email)
        if not user:
            return False, "User not found."
        
        otp = generate_otp()
        expiry = time.time() + 300 # 5 minutes
        
        self.db.store_otp(email, otp, expiry)
        sent, msg = send_email_otp(email, otp)
        
        return sent, msg

    def verify_login_otp(self, email, otp) -> Tuple[bool, str, Optional[dict]]:
        """
        Verifies OTP and returns User object for login.
        """
        success, msg = self.verify_email(email, otp)
        if success:
            user = self.db.get_user(email)
            return True, "Login successful.", user
        return False, msg, None

    def resend_verification_otp(self, email) -> Tuple[bool, str]:
        """
        Resends OTP to an unverified user.
        """
        user = self.db.get_user(email)
        if not user:
            return False, "User not found."
        
        # Now we can just use send_login_otp logic but keep the name for API compatibility
        return self.send_login_otp(email)

    def close(self):
        self.db.close()
