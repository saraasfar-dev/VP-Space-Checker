import streamlit as st
from docx import Document
import io
import re

st.title("Vendor Profile Tag Checker 📄")

st.write("Upload a `.docx` file, and I’ll highlight and fix spacing issues around tags (e.g., #vns#, #sks#, #vne#, #ske#).")

uploaded_file = st.file_uploader("Choose a .docx file", type=["docx"])

if uploaded_file is not None:
    # Load the document
    doc = Document(io.BytesIO(uploaded_file.read()))
    
    issues = []
    # Regex 1: Tag followed by a space (e.g., #tag# Text)
    pattern_after = re.compile(r"(#\w+#)\s+")
    # Regex 2: Space before a tag (e.g., Text #tag#)
    pattern_before = re.compile(r"\s+(#\w+#)")

    # Check each paragraph
    for i, para in enumerate(doc.paragraphs, start=1):
        text = para.text
        original_text = text

        # Detect issues
        if pattern_after.search(text) or pattern_before.search(text):
            issues.append(f"Line {i}: {text}")

            # Auto-fix: remove spaces after and before tags
            text = pattern_after.sub(r"\1", text)
            text = pattern_before.sub(r"\1", text)

            para.text = text  # update the paragraph

    if issues:
        st.error("⚠️ Found spacing issues around tags:")
        for issue in issues:
            st.write(issue)

        # Save corrected document in memory
        corrected_file = io.BytesIO()
        doc.save(corrected_file)
        corrected_file.seek(0)

        st.success("✅ Corrected file ready!")
        st.download_button(
            label="Download Corrected File",
            data=corrected_file,
            file_name="corrected.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
