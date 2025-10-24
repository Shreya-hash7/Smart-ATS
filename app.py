import streamlit as st
import PyPDF2 as pdf
import json
from dotenv import load_dotenv
import os

load_dotenv()

# ---------------------
# Mock Gemini API call
# ---------------------
def get_gemini_response(input):
    # Mock response for testing without API calls
    return '{"JD Match": "90%", "MissingKeywords": ["Docker", "TensorFlow"], "Profile Summary": "Strong candidate with AI/ML projects."}'

# ---------------------
# PDF text extraction
# ---------------------
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += str(page.extract_text())
    return text

# ---------------------
# Prompt template (for real API later)
# ---------------------
input_prompt = """
Hey, act like a skilled ATS with deep understanding of tech fields.
Evaluate resume vs job description. Return JSON:
{{"JD Match": "%", "MissingKeywords": [], "Profile Summary": ""}}
resume: {text}
description: {jd}
"""

# ---------------------
# Streamlit App Layout
# ---------------------
st.set_page_config(page_title="Smart ATS", layout="wide")
st.markdown("<h1 style='text-align:center;color:#4B0082;'>Smart ATS Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#555;'>Check your resume compatibility instantly</p>", unsafe_allow_html=True)

# ---------------------
# Sidebar for input
# ---------------------
st.sidebar.title("Resume Input")
jd = st.sidebar.text_area("Paste Job Description")
uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF)", type="pdf")
submit = st.sidebar.button("Submit")

# ---------------------
# Main Results Area
# ---------------------
if submit:
    if uploaded_file is not None and jd.strip() != "":
        # Extract resume text
        text = input_pdf_text(uploaded_file)
        # For real API, replace with: get_gemini_response(input_prompt.format(text=text, jd=jd))
        response = get_gemini_response(input_prompt.format(text=text, jd=jd))

        try:
            result = json.loads(response)
        except:
            st.error("Failed to parse response")
            result = None

        if result:
            st.markdown("<h3 style='color:#4B0082;'>ATS Evaluation Result</h3>", unsafe_allow_html=True)
            
            # ---------------------
            # JD Match Progress Bar (color-coded)
            # ---------------------
            jd_match = int(result.get('JD Match', '0').replace('%',''))
            if jd_match >= 80:
                color = "#4CAF50"  # green
            elif jd_match >= 50:
                color = "#FFC107"  # yellow
            else:
                color = "#F44336"  # red
            st.progress(jd_match)
            st.markdown(f"<h4 style='color:{color};'>{jd_match}% Match with Job Description</h4>", unsafe_allow_html=True)
            
            # ---------------------
            # Missing Keywords Cards
            # ---------------------
            missing = result.get("MissingKeywords", [])
            st.markdown("<b>Missing Keywords:</b>", unsafe_allow_html=True)
            if missing:
                for kw in missing:
                    st.markdown(f"<div style='padding:8px;margin:4px;background-color:#e0f7fa;border-radius:5px;display:inline-block;font-weight:bold;'>{kw}</div>", unsafe_allow_html=True)
            else:
                st.info("No missing keywords! Great job!")
            
            # ---------------------
            # Collapsible Profile Summary
            # ---------------------
            st.markdown("<b>Profile Summary:</b>", unsafe_allow_html=True)
            with st.expander("View Profile Summary"):
                st.write(result.get("Profile Summary"))

            # ---------------------
            # Download Evaluation Button
            # ---------------------
            eval_text = f"JD Match: {jd_match}%\nMissing Keywords: {', '.join(missing) if missing else 'None'}\nProfile Summary: {result.get('Profile Summary')}"
            st.download_button("Download Evaluation", eval_text, file_name="ATS_Evaluation.txt")
    else:
        st.warning("Please upload a resume and paste a job description before submitting.")
