import streamlit as st
from docx import Document
import io
import re

st.title("Vendor Profile Tag Checker 📄")

st.write("Upload a `.docx` file, and I’ll highlight lines where spaces exist between a tag (like #vns#) and the text.")

uploaded_file = st.file_uploader("Choose a .docx file", type=["docx"])

if uploaded_file is not None:
    # Load the document
    doc = Document(io.BytesIO(uploaded_file.read()))
    
    issues = []
    # Pattern: look for hashtag tags followed by a space (e.g., #vns# Text)
    pattern = re.compile(r"(#\w+#)\s+")

    for i, para in enumerate(doc.paragraphs, start=1):
        text = para.text
        match = pattern.search(text)
        if match:
            issues.append(f"Line {i}: {text}")

    if issues:
        st.error("⚠️ Found spacing issues after tags:")
        for issue in issues:
            st.write(issue)
    else:
        st.success("✅ No spacing issues found!")
