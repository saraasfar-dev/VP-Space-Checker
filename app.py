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
        file_name="corrected_vendor_profile.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # --- 2️⃣ Check meta title & description lengths ---
    st.subheader("📏 Meta Title & Description Lengths")

    def check_meta_limits(text):
        issues = []
        patterns = {
            "Meta Title": ("#smts#", "#smte#", 80),
            "Meta Description": ("#smds#", "#smde#", 180),
            "Review Meta Title": ("#rmts#", "#rmte#", 80),
            "Review Meta Description": ("#rmds#", "#rmde#", 180),
            "Alternative Meta Title": ("#amts#", "#amte#", 80)
        }
        for label, (start_tag, end_tag, limit) in patterns.items():
            match = re.search(f"{re.escape(start_tag)}(.*?){re.escape(end_tag)}", text, re.DOTALL)
            if match:
                content = match.group(1).strip()
                if len(content) > limit:
                    issues.append((label, content, len(content), "❌ Too long"))
                else:
                    issues.append((label, content, len(content), "✅ OK"))
        return issues

    meta_issues = check_meta_limits(full_text)
    for label, content, length, status in meta_issues:
        if "❌" in status:
            st.error(f"{label} ({length} chars): {status}\n\n{content}")
        else:
            st.success(f"{label} ({length} chars): {status}\n\n{content}")
