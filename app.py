import streamlit as st
import re
import io
from docx import Document

# --- Function to extract text from uploaded DOCX ---
def extract_text_from_docx(uploaded_file):
    doc = Document(uploaded_file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

# --- Function to check and fix spacing issues between tags and text ---
def check_spacing_issues(text):
    issues = []
    corrected_text = text

    # Regex: Find tags like #vns#, #vne#, etc. and remove extra spaces around them
    pattern = r"(#\w+#)\s+|\s+(#\w+#)"
    matches = re.finditer(pattern, text)

    for match in matches:
        issues.append(match.group().strip())

    # Fix: remove spaces between tags and text
    corrected_text = re.sub(r"\s*(#\w+#)\s*", r"\1", corrected_text)

    return issues, corrected_text

# --- Function to check meta title and description length ---
def check_meta_limits(text):
    issues = []

    # Meta Title
    title_pattern = r"#smts#(.*?)#smte#"
    title_match = re.search(title_pattern, text, re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()
        if len(title) > 80:
            issues.append(("Meta Title", title, len(title), "❌ Too long"))
        else:
            issues.append(("Meta Title", title, len(title), "✅ OK"))

    # Meta Description
    desc_pattern = r"#smds#(.*?)#smde#"
    desc_match = re.search(desc_pattern, text, re.DOTALL)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) > 180:
            issues.append(("Meta Description", desc, len(desc), "❌ Too long"))
        else:
            issues.append(("Meta Description", desc, len(desc), "✅ OK"))

    return issues

# --- Function to create corrected DOCX ---
def create_corrected_docx(corrected_text):
    doc = Document()
    for line in corrected_text.split("\n"):
        doc.add_paragraph(line)
    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()

# --- Streamlit App ---
st.title("📄 Vendor Profile Checker")

uploaded_file = st.file_uploader("Upload a DOCX file", type=["docx"])

if uploaded_file is not None:
    text = extract_text_from_docx(uploaded_file)

    # --- Spacing Issues ---
    st.subheader("🔍 Checking Tag Spacing Issues")
    spacing_issues, corrected_text = check_spacing_issues(text)

    if spacing_issues:
        st.error(f"Found {len(spacing_issues)} spacing issues:")
        for issue in spacing_issues:
            st.write(f"- {issue}")
    else:
        st.success("✅ No spacing issues found!")

    # --- Meta Title & Description Length ---
    st.subheader("📏 Checking Meta Title & Description Lengths")
    results = check_meta_limits(text)

    for label, content, length, status in results:
        if "❌" in status:
            st.error(f"{label} ({length} chars): {status}\n\n{content}")
        else:
            st.success(f"{label} ({length} chars): {status}\n\n{content}")

    # --- Download Corrected DOCX ---
    st.subheader("⬇️ Download Corrected File")
    corrected_file = create_corrected_docx(corrected_text)
    st.download_button(
        label="Download Corrected DOCX",
        data=corrected_file,
        file_name="corrected_vendor_profile.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
