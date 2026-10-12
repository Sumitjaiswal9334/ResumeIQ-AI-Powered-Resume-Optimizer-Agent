from __future__ import annotations

import json
import os
from datetime import datetime
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv

from agent import optimizer_graph
from resume_optimizer import (
    extract_resume_text, match_resume_to_job, save_analysis, get_history, make_docx, make_pdf,
)

load_dotenv()
st.set_page_config(page_title="AI Resume Optimizer", page_icon="🧠", layout="wide")

st.markdown("""
<style>
.main .block-container {max-width: 1180px; padding-top: 1.5rem;}
.hero {padding: 1.4rem 1.6rem; border-radius: 18px; background: linear-gradient(120deg,#10233f,#1e4b65); color: white; margin-bottom: 1.1rem;}
.hero h1 {margin: 0 0 .4rem 0; font-size: 2.1rem;}
.hero p {margin: 0; opacity: .9;}
div[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.25); padding: 12px; border-radius: 12px;}
</style>
<div class="hero">
<h1>🧠 AI Resume Optimizer</h1>
<p>Understand the job, measure resume alignment, and create a truthful, tailored resume.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Settings")
    st.caption("Google Gemini is optional. Without an API key, deterministic analysis and document export still work.")
    api_key = st.text_input("Google AI API key", type="password", value=os.getenv("GOOGLE_API_KEY", ""))
    model = st.selectbox("Gemini model", ["gemini-3.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"], index=0)
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    st.divider()
    st.markdown("**Privacy**")
    st.caption("Resume text is processed in this app session and saved to local SQLite only when you run an analysis. If Google Gemini is enabled, the relevant text is sent to Google for generation.")
    st.caption("This tool estimates keyword/skill alignment; it does not reproduce any employer's proprietary ATS.")

tab_analyze, tab_history, tab_about = st.tabs(["🚀 Optimize resume", "🗂️ Analysis history", "ℹ️ How it works"])

with tab_analyze:
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.subheader("1. Your resume")
        uploaded = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])
        resume_text = ""
        if uploaded:
            try:
                resume_text = extract_resume_text(uploaded.getvalue(), uploaded.name)
                st.success(f"Extracted {len(resume_text.split())} words from {uploaded.name}")
            except Exception as e:
                st.error(f"Could not read this file: {e}")
        pasted_resume = st.text_area("Or paste resume text", value="", height=250, placeholder="Paste your resume text here…")
        if pasted_resume.strip():
            resume_text = pasted_resume.strip()
        candidate_name = st.text_input("Candidate name (optional)", placeholder="e.g., Sumit Jaiswal")
    with right:
        st.subheader("2. Target job")
        job_title = st.text_input("Job title", placeholder="e.g., Machine Learning Engineer")
        company = st.text_input("Company (optional)", placeholder="e.g., Example Technologies")
        job_description = st.text_area("Paste the full job description", height=250, placeholder="Include responsibilities, requirements, preferred skills, etc.")
        st.caption("For useful matching, include the complete job description rather than only the title.")

    st.subheader("3. Run analysis")
    run = st.button("Analyze & optimize", type="primary", use_container_width=True)
    if run:
        if not resume_text.strip():
            st.error("Upload a PDF/DOCX or paste your resume first.")
        elif len(resume_text.strip()) < 80:
            st.error("The resume text is very short. Please provide a more complete resume.")
        elif not job_description.strip():
            st.error("Paste the target job description first.")
        else:
            with st.spinner("Comparing resume and job requirements…"):
                try:
                    graph_result = optimizer_graph.invoke({
                        "resume_text": resume_text,
                        "job_description": job_description,
                        "job_title": job_title,
                        "company": company,
                        "model": model,
                        "candidate_name": candidate_name,
                    })
                    match = graph_result["match"]
                    ai_result = graph_result["result"]
                    ai_enabled = bool(os.getenv("GOOGLE_API_KEY"))
                except Exception as e:
                    # Fail safely: still show the local keyword analysis and original resume.
                    from resume_optimizer import match_resume_to_job
                    match = match_resume_to_job(resume_text, job_description, job_title, company)
                    ai_result = {
                        "summary": "AI generation or graph execution was unavailable, so the app has produced a rule-based analysis.",
                        "strengths": match["matched_keywords"][:8],
                        "gaps": match["missing_keywords"][:10],
                        "recommendations": [
                            "Add relevant keywords only where they accurately reflect your experience.",
                            "Rewrite bullets to show action, scope, and measurable outcome where evidence exists.",
                            "Keep dates, qualifications, employers, and achievements factual."
                        ],
                        "optimized_resume": resume_text,
                        "cover_letter": "",
                        "warnings": [f"AI/graph issue: {str(e)[:250]}"],
                    }
                    ai_enabled = False
            result = {"created_at": datetime.now().isoformat(timespec="seconds"), "job_title": job_title,
                      "company": company, "match": match, "ai": ai_result, "ai_enabled": ai_enabled,
                      "candidate_name": candidate_name}
            st.session_state["last_result"] = result
            save_analysis(result)

    result = st.session_state.get("last_result")
    if result:
        st.divider()
        st.subheader("Your results")
        match = result["match"]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Alignment estimate", f'{match["score"]}%')
        m2.metric("Matched terms", str(len(match["matched_keywords"])))
        m3.metric("Missing terms", str(len(match["missing_keywords"])))
        m4.metric("Analysis mode", "AI + rules" if result["ai_enabled"] else "Rules only")
        st.progress(match["score"] / 100)
        st.caption("Alignment estimate is a transparent keyword/skill coverage heuristic, not an official ATS score or a hiring prediction.")

        overview, gaps, optimized, letter, raw = st.tabs(["Overview", "Skill gaps", "Optimized resume", "Cover letter", "Details"])
        ai = result["ai"]
        with overview:
            st.markdown("**Summary**")
            st.write(ai.get("summary", ""))
            st.markdown("**What already aligns**")
            strengths = ai.get("strengths", [])
            if strengths:
                for x in strengths: st.markdown(f"- {x}")
            else: st.info("No specific strengths were returned.")
            st.markdown("**Recommended next actions**")
            for x in ai.get("recommendations", []): st.markdown(f"- {x}")
            for warning in ai.get("warnings", []):
                st.warning(warning)
        with gaps:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Matched keywords / skills**")
                st.write(", ".join(match["matched_keywords"]) or "No direct matches detected.")
            with c2:
                st.markdown("**Potential gaps**")
                st.write(", ".join(match["missing_keywords"]) or "No gaps from the extracted keyword list.")
            st.markdown("**Requirements extracted from the job description**")
            st.write(", ".join(match["job_keywords"]) or "No requirements extracted.")
            st.caption("A missing keyword does not automatically mean you lack the skill; it may simply not be mentioned in your resume.")
        with optimized:
            optimized_text = ai.get("optimized_resume", "")
            edited = st.text_area("Review and edit before exporting", value=optimized_text, height=420, key="edited_resume")
            d1, d2 = st.columns(2)
            with d1:
                st.download_button("Download DOCX", data=make_docx(edited, result["candidate_name"]), file_name="optimized_resume.docx",
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            with d2:
                st.download_button("Download PDF", data=make_pdf(edited, result["candidate_name"]), file_name="optimized_resume.pdf",
                                   mime="application/pdf", use_container_width=True)
            st.caption("Always review names, dates, metrics, skills, and claims before sending this resume to an employer.")
        with letter:
            cover = ai.get("cover_letter", "")
            if cover:
                st.text_area("Editable cover letter", value=cover, height=320, key="edited_cover")
                st.download_button("Download cover letter (.docx)", data=make_docx(st.session_state.get("edited_cover", cover), result["candidate_name"]),
                                   file_name="cover_letter.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            else:
                st.info("No cover letter was generated. Enable Google Gemini with a valid key and run analysis again.")
        with raw:
            st.json({"match": match, "ai": ai, "ai_enabled": result["ai_enabled"]})

with tab_history:
    st.subheader("Saved analyses")
    history = get_history()
    if not history:
        st.info("No saved analyses yet. Run an analysis to create a local history entry.")
    else:
        for item in history:
            with st.expander(f'{item["created_at"]} · {item["job_title"] or "Untitled role"} · {item["score"]}% alignment'):
                st.write(f'Company: {item["company"] or "Not specified"}')
                st.write(item["summary"] or "No summary stored.")
                st.caption("Only summary metadata is listed here; full resume text is not displayed in history.")

with tab_about:
    st.markdown("""
    ### Workflow
    1. Extract text from PDF/DOCX or accept pasted resume text.
    2. Extract job-relevant terms and calculate a transparent coverage estimate.
    3. Optionally call a Google Gemini model for recommendations, a tailored resume draft, and a cover letter.
    4. Review the generated draft and export DOCX/PDF.
    5. Store analysis metadata in local SQLite for later review.

    ### Important limitations
    - This is a resume-writing assistant, not an employer's ATS.
    - Keyword matching can miss synonyms and context; manually review the results.
    - The app does not verify claims or guarantee interviews.
    - No live job-search API is included; you provide the job description.
    """)
