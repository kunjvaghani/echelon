"""
OTP service for phone verification.
Stores OTP in memory with expiry and rate limiting. 
Supports multiple SMS providers: Twilio, Generic HTTP (e.g., Fast2SMS), and Console (Demo).
"""
import os
import random
import time
import requests
from typing import Optional, Tuple, Dict

# In-memory store
_OTP_STORE: Dict[str, dict] = {}

# Configuration
OTP_EXPIRY_SECONDS = 300  # 5 minutes
OTP_LENGTH = 6
MAX_ATTEMPTS = 3
RATE_LIMIT_WINDOW = 600
COOLDOWN_SECONDS = 60


def _normalize_phone(phone: str) -> str:
    """Normalize phone to digits only."""
    return "".join(c for c in phone if c.isdigit()) or phone.strip()


def generate_otp(length: int = OTP_LENGTH) -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def can_send_otp(phone: str) -> Tuple[bool, str]:
    """Check rate limits."""
    key = _normalize_phone(phone)
    entry = _OTP_STORE.get(key)
    
    if not entry:
        return True, ""
        
    now = time.time()
    
    last_sent = entry.get('last_sent', 0)
    if now - last_sent < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (now - last_sent))
        return False, f"Please wait {remaining} seconds before requesting a new OTP."
        
    if now - last_sent > RATE_LIMIT_WINDOW:
         entry['attempts'] = 0
         
    if entry.get('attempts', 0) >= MAX_ATTEMPTS:
        return False, "Too many OTP attempts. Please try again later."
        
    return True, ""


def store_otp(phone: str, otp: Optional[str] = None, expiry_seconds: int = OTP_EXPIRY_SECONDS) -> str:
    """Store OTP and update counters."""
    key = _normalize_phone(phone)
    if not key:
        raise ValueError("Invalid phone number")
        
    otp = otp or generate_otp()
    now = time.time()
    
    entry = _OTP_STORE.get(key, {'attempts': 0, 'last_sent': 0})
    entry.update({
        'otp': otp,
        'expiry': now + expiry_seconds,
        'last_sent': now,
        'attempts': entry.get('attempts', 0) + 1
    })
    
    _OTP_STORE[key] = entry
    return otp


def verify_otp(phone: str, user_entered: str) -> bool:
    """Verify OTP."""
    key = _normalize_phone(phone)
    if not key or not user_entered:
        return False
        
    entry = _OTP_STORE.get(key)
    if not entry:
        return False
        
    if time.time() > entry.get('expiry', 0):
        del _OTP_STORE[key]
        return False
        
    if entry.get('otp', '').strip() == user_entered.strip():
        del _OTP_STORE[key]
        return True
        
    return False



# [Removed SMS/Phone support as per request]

def _send_via_email(email: str, otp: str) -> Tuple[bool, str]:
    """Send OTP via SMTP Email."""
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")

    if not (sender_email and sender_password):
        return False, "SMTP Email/Password not configured."

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = "Your Verification Code - SecureKYC"

        body = f"""
        <html>
          <body>
            <h2>Verification Code</h2>
            <p>Your OTP is: <strong>{otp}</strong></p>
            <p>This code is valid for 5 minutes.</p>
            <p>If you did not request this, please ignore this email.</p>
          </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True, "OTP sent to your email."
    except Exception as e:
        return False, f"Email Error: {str(e)}"


def send_email_otp(email: str, otp: str) -> Tuple[bool, str]:
    """Public function to send OTP via email."""
    return _send_via_email(email, otp)

def send_otp_to_email(email: str) -> Tuple[bool, str, Optional[str]]:
    """
    Legacy/Standalone: Generate, store, and send OTP to email.
    Returns: (success: bool, message: str, otp_for_demo: Optional[str])
    """
    email = (email or "").strip().lower()
    if not email:
        return False, "Email is required.", None

    # Use email as key for storage
    key = email 
    
    # Rate Limit
    allowed, msg = can_send_otp(key)
    if not allowed:
        return False, msg, None

    otp = store_otp(key)

    # Dispatch
    provider = os.getenv("OTP_PROVIDER", "email").lower()
    
    success = False
    send_msg = ""

    if provider == "email":
        success, send_msg = _send_via_email(key, otp)
    elif provider == "demo":
        success = True
        send_msg = "OTP Generated (Demo Mode)."
    else:
        # Fallback to email if provider set to something else but this function called
        success, send_msg = _send_via_email(key, otp)

    if success:
         demo_otp = otp if (provider == "demo" or not success) else None
         return True, send_msg, demo_otp
    else:
         return False, send_msg, otp
