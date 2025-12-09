import streamlit as st
import streamlit_authenticator as stauth

# ---- USER DATABASE ----
users = {
    "john": {
        "email": "john@softwarefinder.com",
        "name": "John Smith",
        "password": stauth.Hasher(["password123"]).generate()[0]
    },
    "emma": {
        "email": "emma@softwarefinder.com",
        "name": "Emma Brown",
        "password": stauth.Hasher(["mysecurepass"]).generate()[0]
    }
}

# ---- AUTHENTICATION CONFIG ----
credentials = {
    "usernames": {
        username: {
            "email": user["email"],
            "name": user["name"],
            "password": user["password"],
        }
        for username, user in users.items()
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "cookie_name",
    "cookie_key",
    cookie_expiry_days=1
)

# ---- LOGIN FORM ----
name, auth_status, username = authenticator.login("Login", "main")

# ---- DOMAIN CHECK ----
if auth_status:
    if not username.endswith("@softwarefinder.com") and not credentials["usernames"][username]["email"].endswith("@softwarefinder.com"):
        st.error("Access denied: Email domain not allowed.")
        st.stop()

elif auth_status is False:
    st.error("Incorrect email or password.")
elif auth_status is None:
    st.warning("Please enter your login details.")

# ---- PROTECTED CONTENT ----
st.success(f"Welcome {name}!")
st.write("Your app content here…")
