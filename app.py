import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# ================================================================
#                     AUTHENTICATION BLOCK
# ================================================================

# Allowed domain
ALLOWED_DOMAIN = "@softwarefinder.com"

# ---- USER CREDENTIALS (move these to secrets.toml) ----
# Example format inside .streamlit/secrets.toml:

# [auth]
# emails = ["sara.asfar@softwarefinder.com", "john.doe@softwarefinder.com"]
# passwords = ["hashed_pw_1", "hashed_pw_2"]

emails = st.secrets["auth"]["emails"]
passwords = st.secrets["auth"]["passwords"]  # must be hashed

# Convert to authenticator structure
credentials = {"usernames": {}}
for i, email in enumerate(emails):
    if email.endswith(ALLOWED_DOMAIN):
        credentials["usernames"][email] = {
            "email": email,
            "name": email.split("@")[0],
            "password": passwords[i]
        }

# Authentication setup
authenticator = stauth.Authenticate(
    credentials,
    "sf_vp_checker",
    "auth_token",
    cookie_expiry_days=1
)

# Login form
name, auth_status, username = authenticator.login("Login", "main")

if auth_status is False:
    st.error("Incorrect email or password.")

elif auth_status is None:
    st.warning(f"Use your {ALLOWED_DOMAIN} email.")

else:
    if not username.endswith(ALLOWED_DOMAIN):
        st.error("Access restricted to Software Finder employees only.")
        st.stop()

    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Logged in as {username}")
