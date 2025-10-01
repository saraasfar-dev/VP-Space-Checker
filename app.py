import streamlit as st
import base64
import docx
import re

# ---------------- Background ----------------
def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Call background function
add_bg_from_local("background.png")

# ---------------- App Logo & Title ----------------
st.image("logo.png", width=150)  # Make sure 'logo.png' is in the repo
st.title("SF VP Spacing & Meta Checker")

# ---------------- File Upload ----------------
uploaded_file = st.file_uploader("Upload a .docx file", type=["docx"])

if uploaded_file is not None:
    doc = docx.Document(uploaded_file)

    spacing_issues = []
    meta_issues = []

    for i, para in enumerate(doc.paragraphs, start=1):
        text = para.text.strip()

        # Skip empty lines
        if not text:
            continue

        # --------- Spacing Issues ---------
        if "  " in text:  # double spaces
            spacing_issues.append(f"Paragraph {i}: Double spacing found → \"{text}\"")

        if re.search(r"\s([.,!?;:])", text):  # space before punctuation
            spacing_issues.append(f"Paragraph {i}: Space before punctuation → \"{text}\"")

        if re.search(r"[.,!?;:]{2,}", text):  # multiple punctuation marks
            spacing_issues.append(f"Paragraph {i}: Multiple punctuations → \"{text}\"")

        # --------- Meta Description Check (130–180 chars) ---------
        if len(text) < 130 or len(text) > 180:
            meta_issues.append(
                f"Paragraph {i}: Meta description length issue ({len(text)} chars) → \"{text}\""
            )

    # ---------------- Results ----------------
    st.subheader("Spacing Issues")
    if spacing_issues:
        for issue in spacing_issues:
            st.write(issue)
    else:
        st.success("No spacing issues found ✅")

    st.subheader("Meta Description Issues")
    if meta_issues:
        for issue in meta_issues:
            st.write(issue)
    else:
        st.success("All meta descriptions are within the valid range ✅")

# ---------------- Footer ----------------
st.markdown(
    """
    <hr style="border:1px solid #bbb; margin-top:40px; margin-bottom:10px;">
    <div style="text-align:center; font-size:14px; color:gray;">
        Developed by Sarah Asfar © 2025 Software Finder
    </div>
    """,
    unsafe_allow_html=True,
)
