import streamlit as st
from docx import Document
import io

# App title and logo
st.set_page_config(page_title="SF VP Spacing & Meta Checker", layout="wide")
st.image("logo.png", width=150)  # Make sure 'logo.png' exists in your GitHub repo
st.title("SF VP Spacing & Meta Checker")

st.write(
    """
    This tool automatically detects and fixes **spacing issues** in VP documents 
    and checks **meta title/description character limits**.
    
    ---
    """
)

# File upload
uploaded_file = st.file_uploader("Upload a Word file (.docx)", type=["docx"])

def fix_spacing_issues(text):
    """Fix spacing issues between hashtags and words"""
    import re
    corrected = re.sub(r"#\s+([a-zA-Z])", r"#\1", text)   # Fix after #
    corrected = re.sub(r"([a-zA-Z])\s+#", r"\1#", corrected)  # Fix before #
    return corrected

def check_meta_limits(text):
    """Check meta titles (<=80 chars) and meta descriptions (130–180 chars)"""
    issues = []
    lines = text.split("\n")
    for line in lines:
        lower_line = line.lower()
        if any(tag in lower_line for tag in ["meta title:", "review meta title:", "alternative meta title:"]):
            content = line.split(":", 1)[1].strip() if ":" in line else ""
            if len(content) > 80:
                issues.append(f"❌ **Meta Title Too Long ({len(content)} chars):** {line}")
        elif any(tag in lower_line for tag in ["meta description:", "review meta description:", "alternative meta description:"]):
            content = line.split(":", 1)[1].strip() if ":" in line else ""
            if len(content) < 130 or len(content) > 180:
                issues.append(f"❌ **Meta Description Out of Range ({len(content)} chars):** {line}")
    return issues

if uploaded_file:
    # Read the uploaded document
    doc = Document(uploaded_file)
    full_text = []
    corrected_doc = Document()

    spacing_issues_found = False

    for para in doc.paragraphs:
        original_text = para.text
        corrected_text = fix_spacing_issues(original_text)

        # Collect corrected text for download
        corrected_doc.add_paragraph(corrected_text)
        full_text.append(corrected_text)

        # Show lines with spacing issues
        if corrected_text != original_text:
            spacing_issues_found = True
            st.markdown(f"⚠️ **Spacing Fixed:** {original_text} ➝ `{corrected_text}`")

    # Meta title/description validation
    all_text = "\n".join(full_text)
    meta_issues = check_meta_limits(all_text)

    if meta_issues:
        st.subheader("Meta Issues Found")
        for issue in meta_issues:
            st.markdown(f"<span style='color:red'>{issue}</span>", unsafe_allow_html=True)
    else:
        st.success("✅ All meta titles and descriptions are within limits!")

    # Download corrected doc
    corrected_buffer = io.BytesIO()
    corrected_doc.save(corrected_buffer)
    corrected_buffer.seek(0)

    st.download_button(
        label="📥 Download Corrected File",
        data=corrected_buffer,
        file_name="corrected.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

# Footer
st.write("---")
st.markdown(
    "<p style='text-align:center;'>Developed by <b>Sarah Asfar</b></p>",
    unsafe_allow_html=True
)
