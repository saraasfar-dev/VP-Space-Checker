import streamlit as st
import docx
import io
import re

st.set_page_config(page_title="Vendor Profile Checker", layout="wide")

st.title("📄 Vendor Profile Checker")
st.write("Upload a Vendor Profile (DOCX) to check spacing and meta length issues.")

uploaded_file = st.file_uploader("Upload DOCX", type=["docx"])

if uploaded_file:
    # Load document
    doc = docx.Document(uploaded_file)

    # Collect full text for meta checks
    full_text = "\n".join([para.text for para in doc.paragraphs])

    # --- Spacing Issues Fix ---
    spacing_pattern = re.compile(r"(#\w+#)\s+|\s+(#\w+#)")
    spacing_issues_lines = []

    for para in doc.paragraphs:
        if spacing_pattern.search(para.text):
            spacing_issues_lines.append(para.text)  # Keep original line for display
            para.text = re.sub(r"\s*(#\w+#)\s*", r"\1", para.text)  # Auto-fix spacing

    st.subheader("🔧 Spacing Issues (Auto-Fixed)")
    if spacing_issues_lines:
        st.warning("The following lines had spacing issues and were corrected:")
        for line in spacing_issues_lines:
            st.code(line)
    else:
        st.success("✅ No spacing issues found!")

    # Save corrected DOCX for download
    corrected_file = io.BytesIO()
    doc.save(corrected_file)
    corrected_file.seek(0)

    st.download_button(
        label="⬇️ Download Corrected DOCX",
        data=corrected_file,
        file_name="corrected_vendor_profile.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # --- Meta Titles & Descriptions Check ---
    st.subheader("🔎 Meta Title & Description Length Issues")

    meta_patterns = {
        "Meta Title": (re.compile(r"#smts#(.*?)#smte#", re.DOTALL), 80),
        "Meta Description": (re.compile(r"#smds#(.*?)#smde#", re.DOTALL), 180),
        "Review Meta Title": (re.compile(r"#rmts#(.*?)#rmte#", re.DOTALL), 80),
        "Review Meta Description": (re.compile(r"#rmds#(.*?)#rmde#", re.DOTALL), 180),
        "Alternative Meta Title": (re.compile(r"#amts#(.*?)#amte#", re.DOTALL), 80),
    }

    any_meta_issue = False

    for label, (pattern, limit) in meta_patterns.items():
        matches = pattern.findall(full_text)
        for match in matches:
            text = match.strip()
            if len(text) > limit:  # ✅ Only show exceeded ones
                any_meta_issue = True
                st.markdown(
                    f"**{label} (>{limit} chars)**: "
                    f"<span style='color:red'>{text} "
                    f"({len(text)} chars)</span>",
                    unsafe_allow_html=True
                )

    if not any_meta_issue:
        st.success("✅ All meta titles and descriptions are within limits!")
