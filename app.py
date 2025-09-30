import streamlit as st
from docx import Document
import io
import re

st.title("Vendor Profile Tag Checker 📄")

st.write("Upload a `.docx` file, and I’ll highlight lines with spaces between tags and text.")

uploaded_file = st.file_uploader("Choose a .docx file", type=["docx"])

if uploaded_file is not None:
    # Load the document
    doc = Document(io.BytesIO(uploaded_file.read()))
    
    issues = []
    pattern = re.compile(r">( +)")  # finds one or more spaces right after a closing tag

    for i, para in enumerate(doc.paragraphs, start=1):
        text = para.text
        if pattern.search(text):
            issues.append(f"Line {i}: {text}")

    if issues:
        st.error("⚠️ Found spacing issues after tags:")
        for issue in issues:
            st.write(issue)
    else:
        st.success("✅ No spacing issues found!")
