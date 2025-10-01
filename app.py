import streamlit as st
import docx
import re
from io import BytesIO
import streamlit.components.v1 as components  # for dynamic logo

# --- App title and dynamic logo ---
st.set_page_config(page_title="SF VP Spacing & Meta Checker", layout="wide")

# Dynamic logo based on theme
components.html(
    """
    <script>
        const bg = window.getComputedStyle(document.body).backgroundColor;
        let streamlitLogo = document.getElementById("company-logo");
        if (!streamlitLogo) {
            streamlitLogo = document.createElement("img");
            streamlitLogo.id = "company-logo";
            streamlitLogo.style.width = "150px";
            document.body.prepend(streamlitLogo);
        }
        if (bg.includes("255, 255, 255")) {
            streamlitLogo.src = "logo_1.png"; // black logo for light background
        } else {
            streamlitLogo.src = "logo.png";   // white logo for dark background
        }
    </script>
    """,
    height=0,
)

st.title("SF VP Spacing & Meta Checker")
