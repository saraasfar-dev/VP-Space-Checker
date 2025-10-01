import streamlit as st
import docx
import re
from io import BytesIO

# App title and logo
st.set_page_config(page_title="SF VP Spacing & Meta Checker", layout="wide")
st.image("logo.png", width=150)  # Make sure your file in GitHub is named 'logo.png'
st.title("SF VP Spacing & Meta Checker")

st.write("This tool auto-fixes spacing issues in Vendor Profiles and checks Meta Titles/Descriptions for character length compliance.")

# --- Function to fix spacing issues ---
def fix_spacing_issues(doc):
    corrected_doc = docx.Document()
    spacing_issues = []

    for para in doc.paragraphs:
        original_text = para.text
        corrected_text = re.sub(r"#(\w+)#\s+([^#]+?)\s+#(\w+)#", r"#\1#\2#\3#", original_text)

        if original_text != corrected_text:
            spacing_issues.append(original_text.strip())

        corrected_doc.add_paragraph(corrected_text)

    return corrected_doc, spacing_issues

# --- Function to check meta titles and descriptions ---
def check_meta_limits(doc):
    issues = []
    patterns = {
        "Meta Title": r"#smts#(.*?)#smte#",
        "Meta Description": r"#smds#(.*?)#smde#",
        "Review Meta Title": r"#rmts#(.*?)#rmte#",
        "Review Meta Description": r"#rmds#(.*?)#rmde#",
        "Alternative Meta Title": r"#amts#(.*?)#amte#",
        "Alternative Meta Description": r"#amds#(.*?)#amde#"
    }

    for para in doc.paragraphs:
        text = para.text
        for label, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                length = len(content)

                # Meta titles must not exceed 80 chars
                if "Title" in label and length > 80:
                    issues.append(f"<span style='color:red;'>❌ {label} exceeds 80 chars ({length}): {content}</span>")

                # Meta descriptions must be between 130 and 180 chars
                elif "Description" in label and (length < 130 or length > 180):
                    issues.append(f"<span style='color:red;'>❌ {label} out of range (130–180). Length {length}: {content}</span>")

    return issues

# --- File uploader ---
uploaded_file = st.file_uploader("Upload a Vendor Profile (.docx)", type=["docx"])

if uploaded_file:
    doc = docx.Document(uploaded_file)

    # Fix spacing issues
    corrected_doc, spacing_issues = fix_spacing_issues(doc)

    # Check meta issues
    meta_issues = check_meta_limits(doc)

    # Show results
    st.subheader("Spacing Issues Detected (Auto-Fixed in Download):")
    if spacing_issues:
        for issue in spacing_issues:
            st.write(f"- {issue}")
    else:
        st.success("✅ No spacing issues found!")

    st.subheader("Meta Title & Description Issues:")
    if meta_issues:
        for issue in meta_issues:
            st.markdown(issue, unsafe_allow_html=True)
    else:
        st.success("✅ All meta titles and descriptions within limits!")

    # Provide corrected file for download
    buffer = BytesIO()
    corrected_doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        label="📥 Download Corrected File",
        data=buffer,
        file_name="corrected_vendor_profile.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# --- Footer ---
st.write("---")
st.markdown(
    """
    <div style='text-align:center;'>
        <p>Developed by <b>Sarah Asfar</b>  © 2025 Software Finder</p>
    </div>
    """,
    unsafe_allow_html=True
)
