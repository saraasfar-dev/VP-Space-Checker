import streamlit as st
from docx import Document
import io
import re

st.title("Vendor Profile Tag Checker 📄")

st.write("Upload a `.docx` file, and I’ll highlight lines where spaces exist after tags (like #vns# Cegid) and give you a corrected file.")

uploaded_file = st.file_uploader("Choose a .docx file", type=["docx"])

if uploaded_file is not None:
    # Load the document
    doc = Document(io.BytesIO(uploaded_file.read()))
    
    issues = []
    pattern = re.compile(r"(#\w+#)\s+")  # tag followed by space

    # Check each paragraph
    for i, para in enumerate(doc.paragraphs, start=1):
        text = para.text
        match = pattern.search(text)
        if match:
            issues.append(f"Line {i}: {text}")
            # Auto-fix: remove the space after the tag
            fixed_text = pattern.sub(r"\1", text)
            para.text = fixed_text  # replace paragraph text

    if issues:
        st.error("⚠️ Found spacing issues after tags:")
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
    else:
        st.success("✅ No spacing issues found!")
