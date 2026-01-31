"""
OTP service for phone verification.
Stores OTP in memory with expiry. Optionally sends via Twilio if configured.
"""
import os
import random
import time
from typing import Optional, Tuple

# In-memory store: phone_normalized -> (otp, expiry_timestamp)
_OTP_STORE: dict[str, Tuple[str, float]] = {}
OTP_EXPIRY_SECONDS = 300  # 5 minutes
OTP_LENGTH = 6


def _normalize_phone(phone: str) -> str:
    """Normalize phone to digits only for storage key."""
    return "".join(c for c in phone if c.isdigit()) or phone.strip()


def generate_otp(length: int = OTP_LENGTH) -> str:
    """Generate a numeric OTP."""
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def store_otp(phone: str, otp: Optional[str] = None, expiry_seconds: int = OTP_EXPIRY_SECONDS) -> str:
    """
    Store OTP for phone. Returns the OTP (generated or provided).
    """
    key = _normalize_phone(phone)
    if not key:
        raise ValueError("Invalid phone number")
    otp = otp or generate_otp()
    _OTP_STORE[key] = (otp, time.time() + expiry_seconds)
    return otp


def verify_otp(phone: str, user_entered: str) -> bool:
    """
    Verify user-entered OTP for phone. Returns True if valid and not expired.
    """
    key = _normalize_phone(phone)
    if not key or not user_entered:
        return False
    entry = _OTP_STORE.get(key)
    if not entry:
        return False
    stored_otp, expiry = entry
    if time.time() > expiry:
        del _OTP_STORE[key]
        return False
    if stored_otp.strip() != user_entered.strip():
        return False
    # One-time use: remove after successful verification
    del _OTP_STORE[key]
    return True


def send_otp_to_phone(phone: str) -> Tuple[bool, str, Optional[str]]:
    """
    Generate, store, and send OTP to phone.
    Returns: (success: bool, message: str, otp_for_demo: Optional[str])
    If Twilio is not configured, success is True and otp_for_demo contains the OTP to show in UI.
    """
    phone = (phone or "").strip()
    if not phone:
        return False, "Phone number is required.", None

    key = _normalize_phone(phone)
    if not key or len(key) < 10:
        return False, "Please enter a valid phone number (at least 10 digits).", None

    otp = store_otp(phone)

    # Optional: send via Twilio
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")

    if account_sid and auth_token and from_number:
        try:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            # Ensure phone has + and country code for Twilio
            to_number = phone if phone.startswith("+") else f"+91{key}"  # default India
            client.messages.create(
                body=f"Your verification code is: {otp}. Valid for 5 minutes.",
                from_=from_number,
                to=to_number,
            )
            return True, "OTP sent to your phone.", None
        except Exception as e:
            return False, f"Failed to send SMS: {str(e)}", otp  # Fallback: show OTP for debugging
    else:
        # Demo mode: don't send SMS, return OTP to display in UI
        return True, "OTP generated. Use the code below (SMS not configured).", otp
