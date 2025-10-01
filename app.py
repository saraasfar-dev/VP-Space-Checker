import streamlit as st
import pandas as pd

# Set page config (App Name + Logo)
st.set_page_config(
    page_title="SF VP Spacing & Meta Checker",
    page_icon="📝",  # you can replace with logo.png if preferred
    layout="wide"
)

# Display logo and company name at the top
st.image("company_logo.png", width=150)  # Make sure 'company_logo.png' is in the project folder
st.title("SF VP Spacing & Meta Checker")
st.markdown("**Developed by Sarah Asfar – Software Finder**")

# Function to check spacing issues
def check_spacing_issues(text):
    issues = []
    if "  " in text:
        issues.append("Double spaces detected")
    if text.startswith(" "):
        issues.append("Leading space detected")
    if text.endswith(" "):
        issues.append("Trailing space detected")
    return issues

# Function to check title length (<= 80 chars)
def check_title_length(text):
    return len(text) > 80

# Function to check description length (between 130–180 chars)
def check_description_length(text):
    return len(text) < 130 or len(text) > 180

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Collect results
    results = []
    for idx, row in df.iterrows():
        row_issues = {}

        for col in df.columns:
            cell_value = str(row[col])
            issues = check_spacing_issues(cell_value)

            # Title checks
            if any(key in col.lower() for key in ["meta title", "review meta title", "alternative meta title"]):
                if check_title_length(cell_value):
                    issues.append("Meta title exceeds 80 characters")

            # Description checks
            if any(key in col.lower() for key in ["meta description", "review meta description", "alternative meta description"]):
                if check_description_length(cell_value):
                    issues.append("Meta description not in range (130–180 characters)")

            row_issues[col] = ", ".join(issues) if issues else "OK"

        results.append(row_issues)

    results_df = pd.DataFrame(results)

    # Display results
    st.subheader("Validation Results")
    st.dataframe(results_df)

    # Highlight issues
    def highlight_issues(val):
        if val != "OK":
            return "background-color: red; color: white"
        return ""

    st.subheader("Highlighted Results")
    st.dataframe(results_df.style.applymap(highlight_issues))

    # Option to download results
    csv = results_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name="validation_results.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("© 2025 **Software Finder** | Developed by **Sarah Asfar**")
