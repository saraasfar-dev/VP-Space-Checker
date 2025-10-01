# app.py
import streamlit as st
from docx import Document
from io import BytesIO
import re

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
    # Read bytes once (we'll create two Document objects from it)
    data = uploaded.read()

    # Original text for meta checks (use the original content, before fixes)
    orig_doc_for_meta = Document(BytesIO(data))
    full_text_for_meta = "\n".join([p.text for p in orig_doc_for_meta.paragraphs])

    # Document we will modify in-place (preserve formatting where possible)
    doc = Document(BytesIO(data))

    spacing_issue_lines = []  # keep original para text for display when fixed

    tag_pattern = re.compile(r"#\w+#")  # matches #tag#
    # For each paragraph, find whitespace around tags and remove those whitespace characters
    for para in doc.paragraphs:
        # Build original paragraph text from runs
        runs = para.runs
        if not runs:
            continue
        orig_text = "".join([r.text for r in runs])
        if not orig_text:
            continue

        # find all tags in the paragraph
        intervals = []  # intervals of characters to remove (spaces)
        for m in tag_pattern.finditer(orig_text):
            tag_s, tag_e = m.start(), m.end()

            # remove whitespace immediately before tag (if any)
            l = tag_s
            while l - 1 >= 0 and orig_text[l - 1].isspace():
                l -= 1
            if l < tag_s:
                intervals.append((l, tag_s))

            # remove whitespace immediately after tag (if any)
            r = tag_e
            while r < len(orig_text) and orig_text[r].isspace():
                r += 1
            if r > tag_e:
                intervals.append((tag_e, r))

        if not intervals:
            continue  # nothing to remove in this paragraph

        # merge overlapping intervals
        merged = merge_intervals(intervals)

        # mark that this paragraph had spacing issues (show original before fix)
        spacing_issue_lines.append(orig_text)

        # create a boolean mask whether to keep each character (True -> keep)
        keep_mask = [True] * len(orig_text)
        for s, e in merged:
            for i in range(s, e):
                if 0 <= i < len(orig_text):
                    keep_mask[i] = False

        # Now update runs by slicing from the original text using keep_mask
        # Compute run boundaries (global indices)
        boundaries = []
        idx = 0
        for r in runs:
            run_len = len(r.text)
            boundaries.append((idx, idx + run_len))
            idx += run_len

        # If sums don't match (defensive), rebuild paragraph as single run fallback
        if idx != len(orig_text):
            # fallback: replace paragraph text directly (may change formatting)
            new_text = "".join([c for i, c in enumerate(orig_text) if keep_mask[i]])
            para.clear()  # remove runs
            para.add_run(new_text)
        else:
            # Update each run preserving formatting by assigning new substring
            for (start, end), r in zip(boundaries, runs):
                # new text for this run: only characters with keep_mask True
                new_run_text_chars = [orig_text[i] for i in range(start, end) if keep_mask[i]]
                new_run_text = "".join(new_run_text_chars)
                r.text = new_run_text  # preserve run formatting, only changing text

    # Display spacing issues that were fixed (show original lines)
    st.subheader("🔧 Lines with spacing issues (auto-fixed)")
    if spacing_issue_lines:
        st.warning("The lines below had spacing problems and were corrected in the downloadable file:")
        for line in spacing_issue_lines:
            st.code(line)
    else:
        st.success("✅ No spacing issues found!")

    # Prepare corrected file for download (saved once)
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    st.download_button(
        label="⬇️ Download corrected DOCX",
        data=buf,
        file_name="corrected_vendor_profile.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
