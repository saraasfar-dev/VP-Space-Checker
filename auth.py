"""
VP Space Checker - OTP Authentication Module
============================================

CONFIGURATION:
Set these secrets in Streamlit Cloud (Settings > Secrets):
    SENDGRID_API_KEY = "EXKAJTC5A8K3W4FZKD9BZGD8"
    OTP_SENDER_EMAIL = "saraasfar@softwarefinder.com"
"""

import streamlit as st
import random
import time
import re
import os
from datetime import datetime, timedelta

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

# CONFIGURATION
ALLOWED_DOMAIN = "@softwarefinder.com"
OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 5
MAX_RESEND_COUNT = 3

def get_sendgrid_api_key():
    try:
        return st.secrets["SENDGRID_API_KEY"]
    except (KeyError, FileNotFoundError):
        return os.environ.get("SENDGRID_API_KEY", "")

def get_sender_email():
    try:
        return st.secrets["OTP_SENDER_EMAIL"]
    except (KeyError, FileNotFoundError):
        return os.environ.get("OTP_SENDER_EMAIL", "noreply@softwarefinder.com")

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email: str, otp: str) -> tuple[bool, str]:
    if not SENDGRID_AVAILABLE:
        return False, "SendGrid library not installed. Run: pip install sendgrid"
    
    api_key = get_sendgrid_api_key()
    sender_email = get_sender_email()
    
    if not api_key:
        return False, "SendGrid API key not configured."
    
    subject = "Your login code for VP Space Checker"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Your Login Code</h2>
        <p>Your one-time login code is:</p>
        <h1 style="font-size: 32px; letter-spacing: 5px; color: #333; 
                   background: #f5f5f5; padding: 15px; display: inline-block; 
                   border-radius: 5px;">{otp}</h1>
        <p style="color: #666;">This code will expire in {OTP_EXPIRY_MINUTES} minutes.</p>
    </body>
    </html>
    """
    
    message = Mail(
        from_email=sender_email,
        to_emails=email,
        subject=subject,
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        if response.status_code in [200, 201, 202]:
            return True, "OTP sent successfully!"
        return False, "Failed to send email. Please try again."
    except Exception as e:
        print(f"SendGrid error: {str(e)}")
        return False, "Failed to send email. Please check your configuration."

def is_valid_email_format(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_allowed_domain(email: str) -> bool:
    return email.lower().endswith(ALLOWED_DOMAIN.lower())

def is_otp_expired() -> bool:
    if "otp_created_at" not in st.session_state:
        return True
    created_at = st.session_state.otp_created_at
    expiry_time = created_at + timedelta(minutes=OTP_EXPIRY_MINUTES)
    return datetime.now() > expiry_time

def get_remaining_time() -> int:
    if "otp_created_at" not in st.session_state:
        return 0
    created_at = st.session_state.otp_created_at
    expiry_time = created_at + timedelta(minutes=OTP_EXPIRY_MINUTES)
    remaining = (expiry_time - datetime.now()).total_seconds()
    return max(0, int(remaining))

def init_session_state():
    defaults = {
        "is_authenticated": False,
        "user_email": None,
        "otp_code": None,
        "otp_created_at": None,
        "otp_attempts": 0,
        "otp_resend_count": 0,
        "otp_sent": False,
        "pending_email": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def clear_otp_state():
    st.session_state.otp_code = None
    st.session_state.otp_created_at = None
    st.session_state.otp_attempts = 0
    st.session_state.otp_resend_count = 0
    st.session_state.otp_sent = False
    st.session_state.pending_email = None

def logout():
    st.session_state.is_authenticated = False
    st.session_state.user_email = None
    clear_otp_state()

def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔐 Login</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>VP Space Checker</p>", unsafe_allow_html=True)
        st.markdown("---")
        if not st.session_state.otp_sent:
            show_email_step()
        else:
            show_otp_step()
    return st.session_state.is_authenticated

def show_email_step():
    st.markdown("##### Enter your work email")
    st.caption(f"Only {ALLOWED_DOMAIN} emails are allowed")
    email = st.text_input("Work Email", placeholder=f"yourname{ALLOWED_DOMAIN}", label_visibility="collapsed", key="email_input")
    
    if st.button("Send OTP", use_container_width=True, type="primary"):
        if not email:
            st.error("Please enter your email address.")
        elif not is_valid_email_format(email):
            st.error("Please enter a valid email address.")
        elif not is_allowed_domain(email):
            st.error(f"Only {ALLOWED_DOMAIN} email addresses are allowed.")
        else:
            otp = generate_otp()
            success, message = send_otp_email(email, otp)
            if success:
                st.session_state.otp_code = otp
                st.session_state.otp_created_at = datetime.now()
                st.session_state.otp_attempts = 0
                st.session_state.otp_resend_count = 0
                st.session_state.otp_sent = True
                st.session_state.pending_email = email.lower()
                st.success("OTP sent! Check your email.")
                st.rerun()
            else:
                st.error(message)

def show_otp_step():
    email = st.session_state.pending_email
    st.markdown(f"##### Enter the code sent to")
    st.markdown(f"**{email}**")
    
    if is_otp_expired():
        st.error("Your code has expired. Please request a new one.")
        show_resend_button()
        return
    
    remaining_attempts = MAX_OTP_ATTEMPTS - st.session_state.otp_attempts
    if remaining_attempts <= 0:
        st.error("Too many failed attempts. Please request a new code.")
        show_resend_button()
        return
    
    remaining_seconds = get_remaining_time()
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    st.caption(f"⏱️ Code expires in {minutes}:{seconds:02d}")
    
    otp_input = st.text_input("Enter 6-digit code", max_chars=6, placeholder="000000", label_visibility="collapsed", key="otp_input")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Verify", use_container_width=True, type="primary"):
            if not otp_input:
                st.error("Please enter the code.")
            elif otp_input == st.session_state.otp_code:
                st.session_state.is_authenticated = True
                st.session_state.user_email = email
                clear_otp_state()
                st.success("✅ Login successful!")
                time.sleep(1)
                st.rerun()
            else:
                st.session_state.otp_attempts += 1
                remaining = MAX_OTP_ATTEMPTS - st.session_state.otp_attempts
                if remaining > 0:
                    st.error(f"Invalid code. {remaining} attempts remaining.")
                else:
                    st.error("Too many failed attempts.")
                    st.rerun()
    with col2:
        show_resend_button()
    
    st.markdown("---")
    if st.button("← Use a different email", use_container_width=True):
        clear_otp_state()
        st.rerun()

def show_resend_button():
    if st.session_state.otp_resend_count >= MAX_RESEND_COUNT:
        st.warning("Maximum resend limit reached.")
        if st.button("Start over", use_container_width=True):
            clear_otp_state()
            st.rerun()
    else:
        remaining_resends = MAX_RESEND_COUNT - st.session_state.otp_resend_count
        if st.button(f"Resend code ({remaining_resends} left)", use_container_width=True):
            email = st.session_state.pending_email
            otp = generate_otp()
            success, message = send_otp_email(email, otp)
            if success:
                st.session_state.otp_code = otp
                st.session_state.otp_created_at = datetime.now()
                st.session_state.otp_attempts = 0
                st.session_state.otp_resend_count += 1
                st.success("New code sent!")
                st.rerun()
            else:
                st.error(message)

def show_logout_button():
    with st.sidebar:
        st.markdown("---")
        if st.session_state.user_email:
            st.caption(f"Logged in as: {st.session_state.user_email}")
        if st.button("🚪 Log out", use_container_width=True):
            logout()
            st.rerun()

def require_authentication() -> bool:
    init_session_state()
    if st.session_state.is_authenticated:
        return True
    else:
        show_login_page()
        return False
