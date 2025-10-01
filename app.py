# app.py
import streamlit as st
from docx import Document
from io import BytesIO
import re

# helper to escape HTML for safe rendering in Streamlit
def st_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )

st.set_page_config(page_title="Vendor Profile Checker", layout="wide")
st.title("📄 Vendor Profile Checker")
st.write("Upload a DOCX file. The app auto-fixes spacing around tags and flags meta length issues.")

uploaded = st.file_uploader("Upload DOCX", type=["docx"])

def merge_intervals(intervals):
    if not intervals:
        return []
    intervals.sort()
    merged = [list(intervals[0])]
    for s, e in intervals[1:]:
        if s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return merged

if uploaded:
    data = uploaded.read()

    # Keep one copy for meta checks
    orig_doc_for_meta = Document(BytesIO(data))
    full_text_for_meta = "\n".join([p.text for p in orig_doc_for_meta.paragraphs])

    # Copy for fixing spacing issues
    doc = Document(BytesIO(data))
    spacing_issue_lines = []

    tag_pattern = re.compile(r"#\w+#")

    for para in doc.paragraphs:
        runs = para.runs
        if not runs:
            continue
        orig_text = "".join([r.text for r in runs])
        if not orig_text:
            continue

        intervals = []
        for m in tag_pattern.finditer(orig_text):
            tag_s, tag_e = m.start(), m.end()

            # whitespace before
            l = tag_s
            while l - 1 >= 0 and orig_text[l - 1].isspace():
                l -= 1
            if l < tag_s:
                intervals.append((l, tag_s))

            # whitespace after
            r = tag_e
            while r < len(orig_text) and orig_text[r].isspace():
                r += 1
            if r > tag_e:
                intervals.append((tag_e, r))

        if not intervals:
            continue

        merged = merge_intervals(intervals)
        spacing_issue_lines.append(orig_text)

        keep_mask = [True] * len(orig_text)
        for s, e in merged:
            for i in range(s, e):
                if 0 <= i < len(orig_text):
                    keep_mask[i] = False

        # rebuild run text
        boundaries = []
        idx = 0
        for r in runs:
            run_len = len(r.text)
            boundaries.append((idx, idx + run_len))
            idx += run_len

        if idx != len(orig_text):
            new_text = "".join([c for i, c in enumerate(orig_text) if keep_mask[i]])
            para.clear()
            para.add_run(new_text)
        else:
            for (start, end), r in zip(boundaries, runs):
                new_run_text_chars = [orig_text[i] for i in range(start, end) if keep_mask[i]]
                r.text = "".join(new_run_text_chars)

    # show spacing issues
    st.subheader("🔧 Lines with spacing issues (auto-fixed)")
    if spacing_issue_lines:
        st.warning("The lines below had spacing problems and were corrected in the downloadable file:")
        for line in spacing_issue_lines:
            st.code(line)
    else:
        st.success("✅ No spacing issues found!")

    # corrected DOCX download
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    st.download_button(
        label="⬇️ Download corrected DOCX",
        data=buf,
        file_name="corrected_vendor_profile.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    # meta checks
    st.subheader("🔎 Meta Title & Description Length Issues")
    meta_patterns = {
        "Meta Title": (re.compile(r"#smts#(.*?)#smte#", re.DOTALL | re.IGNORECASE), 80),
        "Meta Description": (re.compile(r"#smds#(.*?)#smde#", re.DOTALL | re.IGNORECASE), (130, 180)),
        "Review Meta Title": (re.compile(r"#rmts#(.*?)#rmte#", re.DOTALL | re.IGNORECASE), 80),
        "Review Meta Description": (re.compile(r"#rmds#(.*?)#rmde#", re.DOTALL | re.IGNORECASE), (130, 180)),
        "Alternative Meta Title": (re.compile(r"#amts#(.*?)#amte#", re.DOTALL | re.IGNORECASE), 80),
    }

    any_meta_issue = False
    for label, (pattern, limit) in meta_patterns.items():
        for m in pattern.finditer(full_text_for_meta):
            content = m.group(1).strip()
            length = len(content)
            if isinstance(limit, tuple):
                mn, mx = limit
                if length < mn or length > mx:
                    any_meta_issue = True
                    st.markdown(
                        f"**{label} ({length} chars)**: "
                        f"<span style='color:red'>{st_escape(content)}</span>",
                        unsafe_allow_html=True,
                    )
            else:
                if length > limit:
                    any_meta_issue = True
                    st.markdown(
                        f"**{label} ({length} chars)**: "
                        f"<span style='color:red'>{st_escape(content)}</span>",
                        unsafe_allow_html=True,
                    )

    if not any_meta_issue:
        st.success("✅ All meta titles and descriptions are within specified limits.")
