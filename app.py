import streamlit as st
import re
from io import BytesIO
from docx import Document

# ========== UTILS ==========

def read_docx(file):
    """Extract text from a .docx file"""
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def fix_spacing_issues(text):
    """
    Fix spacing issues around hashtags (#vns# text #vne# -> #vns#text#vne#).
    Returns corrected text and list of changed lines.
    """
    corrected_lines = []
    lines = text.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines, start=1):
        fixed_line = re.sub(r"\s*#\s*", "#", line)  # remove spaces around hashtags
        fixed_line = re.sub(r"#\s*([a-zA-Z0-9]+)\s*#", r"#\1#", fixed_line)
        if fixed_line != line:
            corrected_lines.append((i, line, fixed_line))
        fixed_lines.append(fixed_line)

    return "\n".join(fixed_lines), corrected_lines

def check_meta_issues(text):
    """
    Detect meta title/description length issues.
    Titles: <= 80 chars
    Descriptions: between 130–180 chars
    """
    issues = []
    lines = text.split("\n")

    for i, line in enumerate(lines, start=1):
        clean_line = line.strip()
        if not clean_line:
            continue

        # Title checks
        if any(tag in clean_line.lower() for tag in ["meta title", "review meta title", "alternative meta title"]):
            length = len(clean_line)
            if length > 80:
                issues.append((i, clean_line, length, "❌ Meta Title exceeds 80 chars"))

        # Description checks
        elif any(tag in clean_line.lower() for tag in ["meta description", "review meta description", "alternative meta description"]):
            length = len(clean_line)
            if length < 130 or length > 180:
                issues.append((i, clean_line, length, "❌ Meta Description not in 130–180 chars range"))

    return issues


def download_docx(corrected_text):
    """Convert corrected text back to a .docx file for download"""
    doc = Document()
    for line in corrected_text.split("\n"):
        doc.add_paragraph(line)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# ========== STREAMLIT APP ==========

def main():
    st.title("📄 VP Space & Meta Checker")

    uploaded_file = st.file_uploader("Upload your SEO doc", type=["txt", "md", "csv", "docx"])
    if uploaded_file:
        # Read file content
        if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = read_docx(uploaded_file)
        else:
            text = uploaded_file.read().decode("utf-8")

        st.subheader("📌 Original Content")
        st.text_area("File Content", text, height=250)

        # --- Fix spacing issues ---
        corrected_text, spacing_changes = fix_spacing_issues(text)

        if spacing_changes:
            st.subheader("✅ Spacing Issues Fixed")
            for line_num, original, fixed in spacing_changes:
                st.markdown(
                    f"**Line {line_num}:** <br>"
                    f"<span style='color:red;'>Before:</span> {original}<br>"
                    f"<span style='color:green;'>After:</span> {fixed}<br>",
                    unsafe_allow_html=True
                )

            # Download corrected docx
            docx_file = download_docx(corrected_text)
            st.download_button(
                "⬇️ Download Corrected File",
                data=docx_file,
                file_name="corrected.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        else:
            st.success("🎉 No spacing issues found!")

        # --- Meta title & description checks ---
        st.subheader("🔎 Meta Title & Description Issues")
        meta_issues = check_meta_issues(corrected_text)

        if not meta_issues:
            st.success("🎉 All meta titles and descriptions are within limits.")
        else:
            for line_num, content, length, problem in meta_issues:
                st.markdown(
                    f"<span style='color:red;'>Line {line_num} ({length} chars): {problem}</span><br>"
                    f"<code>{content}</code>",
                    unsafe_allow_html=True
                )

if __name__ == "__main__":
    main()
