import streamlit as st
import random
import time
import re
import os
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# =========================
# CONFIG
# =========================
ALLOWED_DOMAIN = "@softwarefinder.com"
OTP_EXPIRY_MINUTES = 1
MAX_OTP_ATTEMPTS = 5
MAX_RESEND_COUNT = 3

# =========================
# SECRETS
# =========================
def get_sendgrid_api_key():
    return st.secrets.get("SENDGRID_API_KEY", "")

def get_sender_email():
    return st.secrets.get("OTP_SENDER_EMAIL", "")

# =========================
# HELPERS
# =========================
def generate_otp():
    return str(random.randint(100000, 999999))

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))

def is_allowed_domain(email: str) -> bool:
    return email.lower().endswith(ALLOWED_DOMAIN)

def is_otp_expired() -> bool:
    if not st.session_state.get("otp_created_at"):
        return True
    return datetime.now() > st.session_state.otp_created_at + timedelta(minutes=OTP_EXPIRY_MINUTES)

def remaining_seconds() -> int:
    expiry = st.session_state.otp_created_at + timedelta(minutes=OTP_EXPIRY_MINUTES)
    return max(0, int((expiry - datetime.now()).total_seconds()))

# =========================
# SENDGRID
# =========================
def send_otp_email(to_email: str, otp: str):
    api_key = get_sendgrid_api_key()
    sender = get_sender_email()

    if not api_key:
        return False, "SENDGRID_API_KEY missing in Streamlit secrets."
    if not sender:
        return False, "OTP_SENDER_EMAIL missing in Streamlit secrets."

    message = Mail(
        from_email=sender,
        to_emails=to_email,
        subject="Your VP Space Checker login code",
        html_content=f"""
        <h2>Your login code</h2>
        <p>Use the code below to sign in:</p>
        <h1 style="letter-spacing:4px;">{otp}</h1>
        <p>This code expires in {OTP_EXPIRY_MINUTES} minutes.</p>
        """
    )

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)

        if response.status_code in (200, 201, 202):
            return True, "OTP sent"
        return False, f"SendGrid failed with status {response.status_code}"

    except Exception as e:
        return False, f"SendGrid error: {str(e)}"

# =========================
# SESSION INIT
# =========================
def init_session():
    defaults = {
        "authenticated": False,
        "otp_sent": False,
        "otp_code": None,
        "otp_created_at": None,
        "otp_attempts": 0,
        "resend_count": 0,
        "pending_email": None,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

def reset_otp():
    st.session_state.update({
        "otp_sent": False,
        "otp_code": None,
        "otp_created_at": None,
        "otp_attempts": 0,
        "resend_count": 0,
        "pending_email": None,
    })

# =========================
# UI
# =========================
def show_login():
    st.markdown("## 🔐 Secure Login")
    st.caption(f"Only {ALLOWED_DOMAIN} emails allowed")

    if not st.session_state.otp_sent:
        email = st.text_input("Work email", placeholder=f"name{ALLOWED_DOMAIN}")

        if st.button("Send OTP", use_container_width=True):
            if not email:
                st.error("Email required")
            elif not is_valid_email(email):
                st.error("Invalid email format")
            elif not is_allowed_domain(email):
                st.error("Email domain not allowed")
            else:
                otp = generate_otp()
                ok, msg = send_otp_email(email, otp)

                if ok:
                    st.session_state.otp_sent = True
                    st.session_state.otp_code = otp
                    st.session_state.otp_created_at = datetime.now()
                    st.session_state.pending_email = email.lower()
                    st.success("OTP sent. Check your inbox.")
                    st.rerun()
                else:
                    st.error(msg)

    else:
        email = st.session_state.pending_email
        st.markdown(f"Code sent to **{email}**")

        if is_otp_expired():
            st.error("OTP expired")
            reset_otp()
            st.rerun()

        seconds = remaining_seconds()
        st.caption(f"Expires in {seconds//60}:{seconds%60:02d}")

        code = st.text_input("6-digit code", max_chars=6)

        if st.button("Verify", use_container_width=True):
            if code == st.session_state.otp_code:
                st.session_state.authenticated = True
                reset_otp()
                st.success("Login successful")
                time.sleep(0.5)
                st.rerun()
            else:
                st.session_state.otp_attempts += 1
                if st.session_state.otp_attempts >= MAX_OTP_ATTEMPTS:
                    st.error("Too many attempts")
                    reset_otp()
                    st.rerun()
                else:
                    st.error("Incorrect code")

        if st.session_state.resend_count < MAX_RESEND_COUNT:
            if st.button("Resend code"):
                st.session_state.resend_count += 1
                otp = generate_otp()
                ok, msg = send_otp_email(email, otp)
                if ok:
                    st.session_state.otp_code = otp
                    st.session_state.otp_created_at = datetime.now()
                    st.success("New code sent")
                    st.rerun()
                else:
                    st.error(msg)

# =========================
# ENTRY POINT
# =========================
def require_authentication():
    init_session()
    if not st.session_state.authenticated:
        show_login()
        return False
    return True
