import streamlit as st
from docx import Document
import io

st.title("Vendor Profile Tag Checker 📄")

st.write("Upload a `.docx` file, and I’ll highlight lines with spaces between tags and text.")

uploaded_file = st.file_uploader("Choose a .docx file", type=["docx"])

if uploaded_file is not None:
    # Load document
    doc = Document(io.BytesIO(uploaded_file.read()))
    
    issues = []
    for i, para in enumerate(doc.paragraphs, start=1):
        text = para.text.strip()
        if text.startswith("<") and ">" in text:
            # Check if there’s a space after the tag
            tag_end = text.find(">")
            if text[tag_end+1:].startswith(" "):
                issues.append(f"Line {i}: {text}")

    if issues:
        st.error("Found spacing issues after tags!")
        for issue in issues:
            st.write(issue)
    else:
        st.success("✅ No spacing issues found!")
