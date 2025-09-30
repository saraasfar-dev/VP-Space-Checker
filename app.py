import streamlit as st
from docx import Document
import io
import re

st.title("📄 Vendor Profile Checker")

uploaded_file = st.file_uploader("Upload a DOCX file", type=["docx"])

if uploaded_file is not None:
    doc = Document(uploaded_file)
    all_paragraphs = [para.text for para in doc.paragraphs]
    full_text = "\n".join(all_paragraphs)

    # --- 1️⃣ Detect and auto-fix spacing issues around hashtags ---
    spacing_pattern = re.compile(r"(#\w+#)\s+|\s+(#\w+#)")
    spacing_issues_lines = []

    for para in doc.paragraphs:
        if spacing_pattern.search(para.text):
            spacing_issues_lines.append(para.text)
            # Auto-fix: remove spaces around hashtags
            para.text = re.sub(r"\s*(#\w+#)\s*", r"\1", para.text)

    st.subheader("🔧 Lines with spacing issues (auto-fixed)")
    if spacing_issues_lines:
        for line in spacing_issues_lines:
            st.write(f"- {line}")
    else:
        st.success("✅ No spacing issues found!")

    # Provide download button for corrected DOCX
    corrected_file = io.BytesIO()
    doc.save(corrected_file)
    corrected_file.seek(0)

    st.download_button(
        label="⬇️ Download Corrected DOCX",
        data=corrected_file,
        fi
