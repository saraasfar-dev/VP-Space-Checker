import streamlit as st
import re
from io import StringIO
from docx import Document

def read_docx(file):
    """Extract text from a .docx file"""
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def check_meta_issues(text):
    issues = []
    lines = text.split("\n")
    for i, line in enumerate(lines, start=1):
        clean_line = line.strip()

        # Meta titles check
        if any(tag in clean_line.lower() for tag in ["meta title", "review meta title", "alternative meta title"]):
            length = len(clean_line)
            if length > 80:
                issues.append((i, clean_line, length, "Meta Title exceeds 80 chars"))

        # Meta descriptions check
        elif any(tag in clean_line.lower() for tag in ["meta description", "review meta description", "alternative meta description"]):
            length = len(clean_line)
            if length < 130 or length > 180:
                issues.append((i, clean_line, length, "Meta Description outside 130–180 chars"))

    return issues


def main():
    st.title("VP Space & Meta Checker")

    uploaded_file = st.file_uploader("Upload your SEO doc", type=["txt", "md", "csv", "docx"])
    if uploaded_file:
        if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = read_docx(uploaded_file)
        else:
            text = uploaded_file.read().decode("utf-8")

        st.subheader("Uploaded Content")
        st.text_area("File Content", text, height=300)

        issues = check_meta_issues(text)

        st.subheader("Detected Issues")
        if not issues:
            st.success("✅ No issues found with meta titles or descriptions.")
        else:
            for line_num, content, length, problem in issues:
                st.markdown(
                    f"<span style='color:red;'>Line {line_num} ({length} chars): {problem}</span><br>"
                    f"<code>{content}</code>",
                    unsafe_allow_html=True
                )

            # Download button for issues
            output = "Line | Length | Problem | Content\n"
            output += "-"*80 + "\n"
            for line_num, content, length, problem in issues:
                output += f"{line_num} | {length} | {problem} | {content}\n"

            st.download_button(
                "Download Issues Report",
                output,
                file_name="meta_issues_report.txt"
            )

if __name__ == "__main__":
    main()
