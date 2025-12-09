# ================================================================
#                SIMPLE DOMAIN-ONLY AUTH (NO PASSWORD)
# ================================================================
import streamlit as st

ALLOWED_DOMAIN = st.secrets["auth"]["allowed_domain"]

# Session state init
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None

def show_login_page():
    st.title("Software Finder – Secure Login")
    st.write("Enter your SoftwareFinder work email to access this tool.")

    email = st.text_input("Work Email")

    if st.button("Continue"):
        if not email.endswith(ALLOWED_DOMAIN):
            st.error(f"Access restricted to {ALLOWED_DOMAIN} users.")
            return

        st.session_state.authenticated = True
        st.session_state.user_email = email
        st.success("Access granted.")

# Gatekeeper
if not st.session_state.authenticated:
    show_login_page()
    st.stop()
