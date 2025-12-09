import streamlit as st
import random
import smtplib
from email.mime.text import MIMEText

# ================================================================
#                     AUTHENTICATION BLOCK
# ================================================================

ALLOWED_DOMAIN = "@softwarefinder.com"

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = None
if "email_verified" not in st.session_state:
    st.session_state.email_verified = None

def send_email(receiver_email, otp_code):
    sender_email = st.secrets["email"]["sender"]           # Your Outlook email
    sender_password = st.secrets["email"]["app_password"]  # App password from Outlook

    msg = MIMEText(f"Your VP Checker verification code is: {otp_code}")
    msg["Subject"] = "Your VP Checker Login Code"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Email error: {e}")
        return False

# Step 1: Enter email
def show_email_page():
    st.title("Software Finder – Secure Login")
    st.write("Enter your work email to continue.")

    email = st.text_input("Work Email")
    if st.button("Send Verification Code"):
        if not email.endswith(ALLOWED_DOMAIN):
            st.error(f"Access restricted to {ALLOWED_DOMAIN} users.")
            return

        otp = random.randint(1000, 9999)
        st.session_state.generated_otp = otp
        st.session_state.email_verified = email

        if send_email(email, otp):
            st.success("Verification code sent to your inbox.")
            st.session_state.otp_sent = True
        else:
            st.error("Failed to send the code. Check your email credentials.")

# Step 2: Enter OTP
def show_otp_page():
    st.title("Enter Verification Code")
    user_otp = st.text_input("4-digit code", max_chars=4)
    if st.button("Verify"):
        if user_otp == str(st.session_state.generated_otp):
            st.success("Authentication successful!")
            st.session_state.authenticated = True
        else:
            st.error("Incorrect code. Please try again.")

# ---- Gatekeeper ----
if not st.session_state.authenticated:
    if not st.session_state.otp_sent:
        show_email_page()
    else:
        show_otp_page()
    st.stop()  # prevent the main app from running
