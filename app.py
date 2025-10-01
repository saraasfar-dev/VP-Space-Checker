import streamlit as st
from docx import Document
from io import BytesIO
import re

st.title("VP Spacing & Meta Checker")

# --- Function to fix spacing issues ---
def fix_spacing(text):
    # Remove spaces after and before hashtags
    return re.sub(r"#\s*([a-z]+s?#)", r"#\1", text, flags=re.IGNORECASE)

# --- Function to process document ---
def process_document(uploaded_file):
    doc = Document(uploaded_file)
    corrected_doc = Document()

    # For spacing issues
    spacing_issues = []

    # For meta title/description checks
    meta_issues = []

    for para in doc.paragraphs:
        original_text = para.text
        fixed_text = fix_spacing(original_text)

        # Save corrected paragraph
        corrected_doc.add_paragraph(fixed_text)

        # Detect if spacing was corrected
        if original_text != fixed_text:
            spacing_issues.append(f"❌ {original_text}")

        # Check for meta titles
        if "#smts#" in fixed_text and "#smte#" in fixed_text:
            meta_title = re.search(r"#smts#(.*?)#smte#", fixed_text)
            if meta_title:
                title_text = meta_title.group(1).strip()
                if len(title_text) > 80:
                    meta_issues.append(f"❌ Meta Title ({len(title_text)} chars): {title_text}")

        # Check for meta descriptions
        if "#smds#" in fixed_text and "#smde#" in fixed_text:
            meta_desc = re.search(r"#smds#(.*?)#smde#", fixed_text)
            if meta_desc:
                desc_text = meta_desc.group(1).strip()
                if len(desc_text) < 130 or len(desc_text) > 180:
                    meta_issues.append(f"❌ Meta Description ({len(desc_text)} chars): {desc_text}")

    return corrected_doc, spacing_issues, meta_issues


# --- Upload Section ---
uploaded_file = st.file_uploader("Upload a DOCX file", type="docx")

if uploaded_file:
    corrected_doc, spacing_issues, meta_issues = process_document(uploaded_file)

    # Show spacing issues
    if spacing_issues:
        st.subheader("Spacing Issues (Auto-fixed in download):")
        for issue in spacing_issues:
            st.write(f"<span style='color:red'>{issue}</span>", unsafe_allow_html=True)
    else:
        st.success("✅ No spacing issues found.")

    # Show meta issues
    if meta_issues:
        st.subheader("Meta Title/Description Issues:")
        for issue in meta_issues:
            st.write(f"<span style='color:red'>{issue}</span>", unsafe_allow_html=True)
    else:
        st.success("✅ All meta titles and descriptions are within limits.")

    # Download button
    st.subheader("Download Corrected File")
    buffer = BytesIO()
    corrected_doc.save(buffer)
    buffer.seek(0)
    st.download_button(
        label="Download Corrected DOCX",
        data=buffer,
        file_name="corrected.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
