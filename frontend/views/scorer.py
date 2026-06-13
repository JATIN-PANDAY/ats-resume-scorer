import streamlit as st
import json
import os
from openai import AzureOpenAI
from frontend.services import api_client
from frontend.components.dashboard import display_results_dashboard

# --- CONFIGURATION ---
# Note: It is best practice to store these in an environment variable or secrets.toml
AZURE_ENDPOINT = "YOUR_AZURE_ENDPOINT_HERE"
AZURE_API_KEY = "YOUR_AZURE_API_KEY_HERE"
DEPLOYMENT_NAME = "gpt-4o" 

def _analyze_with_azure(resume_text, job_desc):
    """Analyzes the resume using Azure AI Foundry (GPT-4o)."""
    client = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version="2024-05-01-preview"
    )

    prompt = f"""
    You are an expert recruiter. Analyze this resume: {resume_text}
    Against this job description: {job_desc}
    Return ONLY a valid JSON object with: 
    'score' (int 0-100), 'strengths' (list), 'missing_skills' (list).
    Do not include any extra text.
    """

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful assistant providing structured JSON output."},
            {"role": "user", "content": prompt}
        ]
    )
    
    content = response.choices[0].message.content
    clean_text = content.replace("```json", "").replace("```", "")
    return json.loads(clean_text)

def render() -> None:
    st.title("🎯 ATS Resume Scorer")
    analysis_mode = st.radio("Select Analysis Mode:", ["General ATS Score", "Job Description Comparison"], horizontal=True)
    
    # UI Setup
    left, right = st.columns(2)
    with left:
        resume_file = st.file_uploader("Choose your resume file", type=["pdf", "txt", "docx"])
    with right:
        jd_text = st.text_area("Paste job description:", height=200) if analysis_mode == "Job Description Comparison" else ""

    if not resume_file:
        st.info("👆 Upload your resume to begin.")
        return

    if st.button("🚀 Analyze Resume", type="primary"):
        st.session_state.pop("scorer_analysis", None)
        resume_text = resume_file.getvalue().decode("utf-8", errors="ignore")
        
        with st.spinner("Analyzing your resume with Azure AI..."):
            try:
                # 1. Attempt to use local backend
                analysis = api_client.analyze_resume(
                    resume_file=resume_file,
                    access_token=st.session_state.get("access_token", ""),
                    job_description=jd_text,
                )
            except Exception:
                # 2. Fallback to Azure AI Foundry if backend fails
                st.warning("Backend unreachable. Switching to Azure AI Foundry Engine...")
                analysis = _analyze_with_azure(resume_text, jd_text)
            
            st.session_state["scorer_analysis"] = analysis
            st.success("✅ Analysis complete!")
            display_results_dashboard(analysis)

    elif st.session_state.get("scorer_analysis"):
        display_results_dashboard(st.session_state["scorer_analysis"])