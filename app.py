# At the top of your main file
from auth import require_authentication, show_logout_button

# Wrap ALL your existing app code like this:
if require_authentication():
    show_logout_button()  # Adds logout to sidebar
    
    # ===== YOUR EXISTING APP CODE GOES HERE =====
    # (all your current st.title, st.write, charts, etc.)
    # =============================================

"""
VP Space Checker - OTP Authentication Module
============================================

CONFIGURATION:
Set these secrets in Streamlit Cloud (Settings > Secrets) or as environment variables:

In Streamlit Cloud secrets.toml format:
    SENDGRID_API_KEY = "your-sendgrid-api-key"
    OTP_SENDER_EMAIL = "noreply@softwarefinder.com"

Or as environment variables:
    export SENDGRID_API_KEY="your-sendgrid-api-key"
    export OTP_SENDER_EMAIL="noreply@softwarefinder.com"

USAGE:
Import and call require_authentication() at the top of your main app:

    from auth import require_authentication
    
    if require_authentication():
        # Your existing app code goes here
        st.write("Welcome to VP Space Checker!")
        # ... rest of your app
"""

import streamlit as st
import random
import time
import re
import os
from datetime import datetime, timedelta

# Try to import SendGrid - install with: pip install sendgrid
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

# =============================================================================
# CONFIGURATION - Adjust these values as needed
# =============================================================================

# Allowed email domain (only emails ending with this domain can log in)
ALLOWED_DOMAIN = "@softwarefinder.com"

# OTP settings
OTP_EXPIRY_MINUTES = 10  # OTP valid for this many minutes
MAX_OTP_ATTEMPTS = 5     # Maximum verification attempts per OTP
MAX_RESEND_COUNT = 3     # Maximum times user can resend OTP

# Email settings (fetched from secrets/environment)
def get_sendgrid_api_key():
    """Get SendGrid API key from secrets or environment."""
    try:
        return st.secrets["SENDGRID_API_KEY"]
    except (KeyError, FileNotFoundError):
        return os.environ.get("SENDGRID_API_KEY", "")

def get_sender_email():
    """Get sender email from secrets or environment."""
    try:
        return st.secrets["OTP_SENDER_EMAIL"]
    except (KeyError, FileNotFoundError):
        return os.environ.get("OTP_SENDER_EMAIL", "noreply@softwarefinder.com")


# =============================================================================
# OTP GENERATION AND EMAIL SENDING
# =============================================================================

def generate_otp():
    """Generate a 6-digit numeric OTP."""
    return str(random.randint(100000, 999999))


def send_otp_email(email: str, otp: str) -> tuple[bool, str]:
    """
    Send OTP email using SendGrid.
    
    Args:
        email: Recipient email address
        otp: The OTP code to send
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not SENDGRID_AVAILABLE:
        return False, "SendGrid library not installed. Run: pip install sendgrid"
    
    api_key = get_sendgrid_api_key()
    sender_email = get_sender_email()
    
    if not api_key:
        return False, "SendGrid API key not configured. Please set SENDGRID_API_KEY."
    
    if not sender_email:
        return False, "Sender email not configured. Please set OTP_SENDER_EMAIL."
    
    # Create email content
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
        <p style="color: #999; font-size: 12px;">
            If you didn't request this code, you can safely ignore this email.
        </p>
    </body>
    </html>
    """
    
    plain_content = f"""Your one-time login code is: {otp}

This code will expire in {OTP_EXPIRY_MINUTES} minutes.

If you didn't request this code, you can safely ignore this email."""
    
    message = Mail(
        from_email=sender_email,
        to_emails=email,
        subject=subject,
        html_content=html_content,
        plain_text_content=plain_content
    )
    
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        if response.status_code in [200, 201, 202]:
            return True, "OTP sent successfully!"
        else:
            # Log status but don't expose details to user
            print(f"SendGrid returned status: {response.status_code}")
            return False, "Failed to send email. Please try again."
            
    except Exception as e:
        # Log error but don't expose details to user
        print(f"SendGrid error: {str(e)}")
        return False, "Failed to send email. Please check your configuration."


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def is_valid_email_format(email: str) -> bool:
    """Check if email has a valid format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_allowed_domain(email: str) -> bool:
    """Check if email is from the allowed domain."""
    return email.lower().endswith(ALLOWED_DOMAIN.lower())


def is_otp_expired() -> bool:
    """Check if the current OTP has expired."""
    if "otp_created_at" not in st.session_state:
        return True
    
    created_at = st.session_state.otp_created_at
    expiry_time = created_at + timedelta(minutes=OTP_EXPIRY_MINUTES)
    return datetime.now() > expiry_time


def get_remaining_time() -> int:
    """Get remaining seconds until OTP expires."""
    if "otp_created_at" not in st.session_state:
        return 0
    
    created_at = st.session_state.otp_created_at
    expiry_time = created_at + timedelta(minutes=OTP_EXPIRY_MINUTES)
    remaining = (expiry_time - datetime.now()).total_seconds()
    return max(0, int(remaining))


# =============================================================================
# SESSION STATE MANAGEMENT
# =============================================================================

def init_session_state():
    """Initialize session state variables if they don't exist."""
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
    """Clear OTP-related session state."""
    st.session_state.otp_code = None
    st.session_state.otp_created_at = None
    st.session_state.otp_attempts = 0
    st.session_state.otp_resend_count = 0
    st.session_state.otp_sent = False
    st.session_state.pending_email = None


def logout():
    """Clear all authentication state and log out the user."""
    st.session_state.is_authenticated = False
    st.session_state.user_email = None
    clear_otp_state()


# =============================================================================
# UI COMPONENTS
# =============================================================================

def show_login_page():
    """
    Display the login page with email input and OTP verification.
    
    Returns:
        bool: True if user successfully authenticated, False otherwise
    """
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔐 Login</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>VP Space Checker</p>", 
                    unsafe_allow_html=True)
        st.markdown("---")
        
        if not st.session_state.otp_sent:
            # STEP 1: Email input
            show_email_step()
        else:
            # STEP 2: OTP verification
            show_otp_step()
    
    return st.session_state.is_authenticated


def show_email_step():
    """Display the email input step."""
    st.markdown("##### Enter your work email")
    st.caption(f"Only {ALLOWED_DOMAIN} emails are allowed")
    
    email = st.text_input(
        "Work Email",
        placeholder=f"yourname{ALLOWED_DOMAIN}",
        label_visibility="collapsed",
        key="email_input"
    )
    
    if st.button("Send OTP", use_container_width=True, type="primary"):
        if not email:
            st.error("Please enter your email address.")
        elif not is_valid_email_format(email):
            st.error("Please enter a valid email address.")
        elif not is_allowed_domain(email):
            st.error(f"Only {ALLOWED_DOMAIN} email addresses are allowed.")
        else:
            # Generate and send OTP
            otp = generate_otp()
            success, message = send_otp_email(email, otp)
            
            if success:
                # Store OTP info in session (OTP is not logged)
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
    """Display the OTP verification step."""
    email = st.session_state.pending_email
    st.markdown(f"##### Enter the code sent to")
    st.markdown(f"**{email}**")
    
    # Check if OTP is still valid
    if is_otp_expired():
        st.error("Your code has expired. Please request a new one.")
        show_resend_button()
        return
    
    # Check remaining attempts
    remaining_attempts = MAX_OTP_ATTEMPTS - st.session_state.otp_attempts
    if remaining_attempts <= 0:
        st.error("Too many failed attempts. Please request a new code.")
        show_resend_button()
        return
    
    # Show remaining time
    remaining_seconds = get_remaining_time()
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    st.caption(f"⏱️ Code expires in {minutes}:{seconds:02d}")
    
    # OTP input
    otp_input = st.text_input(
        "Enter 6-digit code",
        max_chars=6,
        placeholder="000000",
        label_visibility="collapsed",
        key="otp_input"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Verify", use_container_width=True, type="primary"):
            if not otp_input:
                st.error("Please enter the code.")
            elif otp_input == st.session_state.otp_code:
                # Success!
                st.session_state.is_authenticated = True
                st.session_state.user_email = email
                clear_otp_state()
                st.success("✅ Login successful!")
                time.sleep(1)
                st.rerun()
            else:
                # Wrong code
                st.session_state.otp_attempts += 1
                remaining = MAX_OTP_ATTEMPTS - st.session_state.otp_attempts
                if remaining > 0:
                    st.error(f"Invalid code. {remaining} attempts remaining.")
                else:
                    st.error("Too many failed attempts.")
                    st.rerun()
    
    with col2:
        show_resend_button()
    
    # Back button
    st.markdown("---")
    if st.button("← Use a different email", use_container_width=True):
        clear_otp_state()
        st.rerun()


def show_resend_button():
    """Display the resend OTP button."""
    if st.session_state.otp_resend_count >= MAX_RESEND_COUNT:
        st.warning("Maximum resend limit reached. Please wait and try again later.")
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
    """
    Display a logout button in the sidebar.
    Call this in your main app to provide logout functionality.
    """
    with st.sidebar:
        st.markdown("---")
        if st.session_state.user_email:
            st.caption(f"Logged in as: {st.session_state.user_email}")
        if st.button("🚪 Log out", use_container_width=True):
            logout()
            st.rerun()


# =============================================================================
# MAIN AUTHENTICATION FUNCTION
# =============================================================================

def require_authentication() -> bool:
    """
    Main authentication wrapper. Call this at the start of your app.
    
    Returns:
        bool: True if user is authenticated, False if showing login page
    
    Usage:
        if require_authentication():
            # Your app code here
            st.write("Welcome!")
            show_logout_button()  # Add logout button to sidebar
    """
    init_session_state()
    
    if st.session_state.is_authenticated:
        return True
    else:
        show_login_page()
        return False


# =============================================================================
# EXAMPLE USAGE (for testing)
# =============================================================================

if __name__ == "__main__":
    """
    Example of how to use this authentication module.
    Replace the content inside the if block with your actual app code.
    """
    
    st.set_page_config(
        page_title="VP Space Checker",
        page_icon="📊",
        layout="wide"
    )
    
    if require_authentication():
        # Add logout button to sidebar
        show_logout_button()
        
        # YOUR EXISTING APP CODE GOES HERE
        st.title("VP Space Checker")
        st.write(f"Welcome, {st.session_state.user_email}!")
        st.write("Your existing app content goes here...")
        
        # Example: Your existing app functions
        # show_main_app()
        # process_data()
        # etc.

