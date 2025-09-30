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

    # --- Check spacing issues around hashtags ---
    spacing_pattern = re.compile(r"(#\w+#)\s+|\s+(#\w+#)")
    spacing_issues = []

    for i, para in enumerate(all_paragraphs, start=1):
        if spacing_pattern.search(para):
            spacing_issues.append(f"Line {i}: {para}")

    st.subheader("🔍 Spacing Issues")
    if spacing_issues:
        for issue in spacing_issues:
            st.error(issue)
    else:
        st.success("✅ No spacing issues found!")

    # --- Check meta title/description length ---
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
