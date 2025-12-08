import streamlit as st
import random
import smtplib
from email.mime.text import MIMEText

# ================================================================
#                     AUTHENTICATION BLOCK
# ================================================================
def send_email(receiver_email, otp_code):
    sender_email = st.secrets["email"]["sender"]
    sender_password = st.secrets["email"]["password"]

    msg = MIMEText(f"Your verification code is: {otp_code}")
    msg["Subject"] = "Your VP Checker Login Code"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        # OUTLOOK SMTP — TLS REQUIRED
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Email error: {e}")
        return False


# Session state initialisation
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False

if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = None


def show_email_page():
    st.title("Software Finder – Secure Login")
    st.write("Enter your work email to continue.")

    email = st.text_input("Work Email (@softwarefinder.com)")

    if st.button("Send Verification Code"):
        if not email.endswith("@softwarefinder.com"):
            st.error("Access restricted to @softwarefinder.com users.")
            return

        otp = random.randint(1000, 9999)
        st.session_state.generated_otp = otp

        if send_email(email, otp):
            st.success("Verification code sent to your inbox.")
            st.session_state.otp_sent = True
        else:
            st.error("Failed to send the code. Try again later.")


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
