import streamlit as st
import re

def check_meta_issues(text):
    issues = []

    lines = text.split("\n")
    for i, line in enumerate(lines, start=1):
        clean_line = line.strip()

        # Check for meta titles
        if any(tag in clean_line.lower() for tag in ["meta title", "review meta title", "alternative meta title"]):
            length = len(clean_line)
            if length > 80:
                issues.append((i, clean_line, length, "Meta Title exceeds 80 chars"))

        # Check for meta descriptions
        elif any(tag in clean_line.lower() for tag in ["meta description", "review meta description", "alternative meta description"]):
            length = len(clean_line)
            if length < 130 or length > 180:
                issues.append((i, clean_line, length, "Meta Description outside 130–180 chars"))

    return issues


def main():
    st.title("VP Space & Meta Checker")

    uploaded_file = st.file_uploader("Upload your text/SEO doc", type=["txt", "md", "csv"])
    if uploaded_file:
        text = uploaded_file.read().decode("utf-8")

        st.subheader("Uploaded Content")
        st.text_area("File Content", text, height=300)

        # Run checks
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

        # Allow download of results
        if issues:
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
