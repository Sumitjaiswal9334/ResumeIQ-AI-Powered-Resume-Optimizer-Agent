from __future__ import annotations

import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from agent import optimizer_graph
from resume_optimizer import (
    extract_resume_text,
    match_resume_to_job,
    save_analysis,
    get_history,
    make_docx,
    make_pdf,
)

load_dotenv()

st.set_page_config(
    page_title="ResumeIQ - AI Resume Optimizer Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Theme / styling -----------------------------
st.markdown(
    """
    <style>
    :root { color-scheme: dark; }
    .stApp {
        background: #071225;
        color: #eef2ff;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { right: 1rem; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,#0b1730 0%,#081226 100%);
        border-right: 1px solid #1d2b4d;
    }
    [data-testid="stSidebar"] > div { padding-top: 1.1rem; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label,
    [data-testid="stSidebar"] [data-testid="stRadio"] label p {
        color: #eaf2ff !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover p {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {
        gap: 0.45rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"] {
        gap: 0.65rem !important;
        margin: 0.12rem 0 !important;
        padding: 0.32rem 0.45rem !important;
        border-radius: 8px;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"]:hover {
        background: rgba(92, 117, 190, 0.16);
    }
    .block-container {
        max-width: 1450px;
        padding-top: 1.35rem;
        padding-bottom: 2rem;
    }
    h1,h2,h3,h4,p,label,span,div { }
    .brand {
        display:flex; align-items:center; gap:12px;
        padding: 8px 8px 2px 8px;
    }
    .brand-icon {
        width:30px;height:30px;border-radius:10px;
        display:flex;align-items:center;justify-content:center;
        font-size:26px;
        background:linear-gradient(135deg,#536dff,#a66bff);
        box-shadow:0 8px 24px rgba(100,91,255,.28);
    }
    .brand-name {font-size:25px;font-weight:800;line-height:1.12;color:#f5f7ff;}
    .brand-tag {font-size:12px;color:#a7b6da;margin:10px 0 24px 4px;}
    .nav-caption {color:#94a7d0;font-size:11px;letter-spacing:1.4px;
        font-weight:700;margin:20px 0 7px 5px;}
    .topbar {
        display:flex;justify-content:space-between;align-items:center;
        padding: 2px 0 16px 0;border-bottom:1px solid #1c2b4a;margin-bottom:20px;
        color:#a9b8dc;font-size:13px;
    }
    .topbar > span:first-child {
        font-size:35px;
        z-index: 10;
        font-weight:700;
        color:#dce6ff;
    }
    .top-pill {
        display:inline-block;border:1px solid #343d78;background:#171f4b;
        color:#e6e9ff;padding:8px 14px;border-radius:24px;font-weight:650;
    }
    .hero {
        display:grid;grid-template-columns:1.35fr .9fr;gap:18px;
        align-items:center; padding:27px 28px;border:1px solid #3444a1;
        border-radius:18px;margin-bottom:18px;
        background:radial-gradient(ellipse at 72% 20%,rgba(110,56,220,.48),transparent 42%),
                   linear-gradient(115deg,#172657 0%,#152c68 55%,#172e70 100%);
        box-shadow:0 12px 36px rgba(0,0,0,.15);
    }
    .hero h1 {font-size:29px;line-height:1.22;margin:0 0 12px 0;color:#f5f6ff;}
    .hero h1 span {color:#a99aff;}
    .hero p {font-size:14px;line-height:1.7;color:#d1dcff;margin:0;max-width:590px;}
    .hero-visual {display:flex;align-items:center;justify-content:space-around;gap:14px;}
    .resume-illustration {
        width:132px;height:155px;border-radius:12px;background:#dfe7ff;
        transform:rotate(-5deg);padding:18px 14px;box-shadow:10px 12px 0 rgba(151,174,255,.45);
        color:#7189e9;
    }
    .resume-illustration .avatar {width:25px;height:25px;border-radius:50%;background:#8ba6ff;margin-bottom:10px;}
    .resume-line {height:7px;border-radius:6px;background:#a6b9ff;margin:8px 0;}
    .ai-chip {background:linear-gradient(135deg,#704dff,#bd62ff);border-radius:12px;
        padding:12px;color:white;font-weight:800;font-size:20px;margin-left:-26px;
        box-shadow:0 8px 25px #6245d677;}
    .hero-checks {font-size:13px;line-height:2.6;color:#edf0ff;min-width:155px;}
    .hero-checks span {color:#5ce5d0;font-size:17px;margin-right:8px;}
    .panel {
        background:linear-gradient(145deg,#0e1b33,#0b172c);
        border:1px solid #243657;border-radius:16px;padding:22px;
        margin-bottom:16px;
    }
    .panel h3 {font-size:17px;color:#f0f3ff;margin:0 0 16px 0;}
    .section-title {font-size:17px;font-weight:750;color:#f0f3ff;margin:0 0 14px 0;}
    .step-icon {color:#9b8cff;font-size:21px;margin-right:8px;}
    .benefit {display:flex;gap:13px;margin:16px 0 20px 0;align-items:flex-start;}
    .benefit-icon {min-width:43px;height:43px;border-radius:50%;display:flex;align-items:center;
        justify-content:center;font-size:19px;background:#173b3b;color:#6ce4ba;}
    .benefit-icon.purple {background:#30245d;color:#c3a1ff;}
    .benefit-icon.gold {background:#49351b;color:#ffc65c;}
    .benefit-icon.blue {background:#18375c;color:#76bdff;}
    .benefit-title {font-weight:700;color:#f0f3ff;margin:0 0 4px 0;}
    .benefit-copy {font-size:12px;line-height:1.55;color:#aab9d8;}
    .dream-card {padding:18px;border:1px solid #3848b5;border-radius:13px;
        background:linear-gradient(130deg,#1b286b,#202f83);}
    .dream-card strong {color:#fff;}
    .dream-card p {font-size:12px;color:#b9c7ff;line-height:1.6;margin:10px 0 0 0;}
    .quick-example {background:#0c1930;border:1px solid #243657;border-radius:13px;
        padding:17px 20px;margin-top:1px;}
    .quick-title {font-weight:750;color:#f2f4ff;}
    .muted {font-size:12px;color:#98acd3;}
    .stTextInput label,.stTextArea label,.stFileUploader label,.stSelectbox label {
        color:#c9d5f0 !important;font-size:13px !important;
    }
    .stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"] > div {
        background:#0a162a !important;color:#edf2ff !important;
        border:1px solid #2a3e65 !important;border-radius:9px !important;
    }
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder,
    input::placeholder,
    textarea::placeholder {
        color: #8fa7d8 !important;
        opacity: 1 !important;
    }
    [data-testid="stFileUploader"] section {
        background:#0a162a;border:1px dashed #5269c4;border-radius:12px;
    }
    [data-testid="stFileUploader"] section small {color:#9fb2dc !important;}
    [data-testid="stFileUploader"] section button {
        background: linear-gradient(100deg,#536dff,#8059e8) !important;
        border: 1px solid #8d9bff !important;
        color: #ffffff !important;
        border-radius: 9px !important;
    }
    [data-testid="stFileUploader"] section button:hover {
        background: linear-gradient(100deg,#657cff,#a06cff) !important;
        color: #ffffff !important;
    }
    [data-testid="stFileUploader"] section button p,
    [data-testid="stFileUploader"] section button span {
        color: #ffffff !important;
    }
    .stButton > button {
        border-radius:10px;border:1px solid #5265ee;
        background:linear-gradient(100deg,#657cff,#a96cff);
        color:white;font-weight:750;min-height:43px;
    }
    .stButton > button:hover {border-color:#b3a1ff;color:white;filter:brightness(1.08);}
    .stDownloadButton > button {
        background:#17264a;color:#e7ecff;border:1px solid #394f84;border-radius:9px;
    }
    div[data-testid="stMetric"] {
        background:#0d1a31;border:1px solid #26395e;padding:15px;border-radius:12px;
    }
    div[data-testid="stMetricLabel"] {
        color:#d8e5ff !important;
        font-weight:650 !important;
        opacity:1 !important;
    }
    div[data-testid="stMetricLabel"] * {
        color:#d8e5ff !important;
        opacity:1 !important;
    }
    div[data-testid="stMetricValue"] {
        color:#ffffff !important;
        font-weight:750 !important;
    }
    div[data-testid="stMetricValue"] * {
        color:#ffffff !important;
        opacity:1 !important;
    }
    .stProgress > div > div {background:linear-gradient(90deg,#657cff,#ad6cff);}
    div[data-testid="stTabs"] button {color:#aab9dc;}
    div[data-testid="stTabs"] button[aria-selected="true"] {color:#c7bbff;}
    .sidebar-foot {
        margin-top:26px;padding:15px;border-radius:12px;
        border:1px solid #263a65;background:linear-gradient(145deg,#12234a,#101b38);
        color:#b8c7e8;font-size:12px;line-height:1.6;
    }
    @media (max-width: 850px) {
        .hero {grid-template-columns:1fr;}
        .hero-visual {display:none;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------- Sidebar navigation -----------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
          <div class="brand-icon">🤖</div>
          <div class="brand-name">ResumeIQ</div>
        </div>
        <div class="brand-tag">Better Resume. Bigger Opportunities.</div>
        """,
        unsafe_allow_html=True,
    )
    page = st.radio(
        "Navigation",
        ["🏠  Home", "◷  History", "ⓘ  About"],
        label_visibility="collapsed",
        key="navigation_page",
    )
    st.markdown(
        """
        <div class="sidebar-foot">
          <div style="font-size:15px;font-weight:750;color:#9b8cff;">✦ AI Powered</div>
          <div style="margin-top:8px;">Get personalized resume improvements based on a job description using AI-assisted analysis.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Keep the API key in server environment/session, not in a visible text field.
# Configure GOOGLE_API_KEY in .env or your deployment's secret manager.
api_key = os.getenv("GOOGLE_API_KEY", "").strip()
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

st.markdown(
    """
    <div class="topbar">
      <span>Resume intelligence workspace</span>
      <span class="top-pill">✦ &nbsp; AI Resume Optimizer</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------- Home page -----------------------------
if page.startswith("🏠"):
    st.markdown(
        """
        <div class="hero">
          <div>
            <h1>Turn Your Resume Into<br><span>an Interview Magnet</span></h1>
            <p>Our AI analyzes your resume against the job description and provides personalized suggestions to help you stand out and get more interviews.</p>
          </div>
          <div class="hero-visual">
            <div class="resume-illustration">
              <div class="avatar"></div>
              <div class="resume-line" style="width:85%"></div>
              <div class="resume-line" style="width:68%"></div>
              <div class="resume-line" style="width:90%"></div>
              <div class="resume-line" style="width:58%"></div>
              <div class="resume-line" style="width:78%"></div>
            </div>
            <div class="ai-chip">AI</div>
            <div class="hero-checks">
              <div><span>✓</span> ATS Friendly</div>
              <div><span>✓</span> Keyword Optimization</div>
              <div><span>✓</span> Better Match Score</div>
              <div><span>✓</span> Actionable Suggestions</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.42, 0.9], gap="large")

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title"><span class="step-icon">▤</span>1. Upload Your Resume</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Choose a resume file",
            type=["pdf", "docx"],
            help="Supported formats: PDF and DOCX.",
            label_visibility="collapsed",
        )
        resume_text = ""
        if uploaded is not None:
            try:
                resume_text = extract_resume_text(uploaded.getvalue(), uploaded.name)
                st.success(f"Resume loaded · {len(resume_text.split())} words extracted")
            except Exception as exc:
                st.error(f"Could not read this file: {exc}")

        pasted_resume = st.text_area(
            "Or paste resume text",
            height=150,
            placeholder="Paste your resume text here if you don't want to upload a file...",
            key="pasted_resume",
        )
        if pasted_resume.strip():
            resume_text = pasted_resume.strip()
        candidate_name = st.text_input(
            "Candidate name (optional)",
            placeholder="e.g., Your name",
            key="candidate_name",
        )

        st.markdown('<div class="section-title" style="margin-top:22px;"><span class="step-icon">▤</span>2. Paste the Job Description</div>', unsafe_allow_html=True)
        job_title = st.text_input("Target job title", placeholder="e.g., Machine Learning Engineer")
        company = st.text_input("Company (optional)", placeholder="e.g., Example Technologies")
        job_description = st.text_area(
            "Full job description",
            height=165,
            placeholder="Paste the complete job description here...",
            max_chars=20000,
            label_visibility="collapsed",
        )
        st.caption("Tip: include the responsibilities, required skills, qualifications, and preferred experience for better matching.")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("✦  Optimize Resume", type="primary", use_container_width=True):
            if not resume_text.strip():
                st.error("Upload a PDF/DOCX or paste your resume first.")
            elif len(resume_text.strip()) < 80:
                st.error("The resume text is very short. Please provide a more complete resume.")
            elif not job_description.strip():
                st.error("Paste the target job description first.")
            else:
                with st.spinner("Analyzing your resume and matching it to the job..."):
                    try:
                        graph_result = optimizer_graph.invoke(
                            {
                                "resume_text": resume_text,
                                "job_description": job_description,
                                "job_title": job_title,
                                "company": company,
                                "model": model,
                                "candidate_name": candidate_name,
                            }
                        )
                        match = graph_result["match"]
                        ai_result = graph_result["result"]
                        ai_enabled = bool(os.getenv("GOOGLE_API_KEY", "").strip())
                    except Exception as exc:
                        match = match_resume_to_job(resume_text, job_description, job_title, company)
                        ai_result = {
                            "summary": "AI generation was unavailable, so a rule-based analysis is shown.",
                            "strengths": match.get("matched_keywords", [])[:8],
                            "gaps": match.get("missing_keywords", [])[:10],
                            "recommendations": [
                                "Add relevant keywords only where they accurately reflect your experience.",
                                "Rewrite bullets to show action, scope, and measurable outcomes where evidence exists.",
                                "Keep dates, qualifications, employers, and achievements factual.",
                            ],
                            "optimized_resume": resume_text,
                            "cover_letter": "",
                            "warnings": [f"AI/graph issue: {str(exc)[:220]}"],
                        }
                        ai_enabled = False

                result = {
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                    "job_title": job_title,
                    "company": company,
                    "match": match,
                    "ai": ai_result,
                    "ai_enabled": ai_enabled,
                    "candidate_name": candidate_name,
                }
                st.session_state["last_result"] = result
                save_analysis(result)

    with right:
        st.markdown('<div class="panel"><h3>What You’ll Get</h3>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="benefit">
              <div class="benefit-icon">▣</div>
              <div><div class="benefit-title">Optimized Resume</div>
              <div class="benefit-copy">Tailored to match the job description and highlight relevant skills.</div></div>
            </div>
            <div class="benefit">
              <div class="benefit-icon purple">◈</div>
              <div><div class="benefit-title">Match Score</div>
              <div class="benefit-copy">See how well your resume aligns with the job requirements.</div></div>
            </div>
            <div class="benefit">
              <div class="benefit-icon gold">✦</div>
              <div><div class="benefit-title">Improvement Suggestions</div>
              <div class="benefit-copy">Get actionable tips to make your resume stronger.</div></div>
            </div>
            <div class="benefit">
              <div class="benefit-icon blue">▤</div>
              <div><div class="benefit-title">ATS-Friendly Format</div>
              <div class="benefit-copy">Export a clean, editable resume for your final review.</div></div>
            </div>
            <div class="dream-card">
              <div style="font-size:15px;">🎯 &nbsp; <strong>Your Dream Job<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Is Just a Click Away!</strong></div>
              <p>Let AI do the heavy lifting and help you craft a resume that gets noticed.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="quick-example">
          <div class="quick-title">💡 &nbsp; Quick Example</div>
          <div class="muted" style="margin-top:7px;">Try it with a sample job description or your own to see the analysis in action.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    sample_col, button_col = st.columns([4, 1])
    with sample_col:
        st.caption("Sample role: Machine Learning Engineer · Python, SQL, scikit-learn, model evaluation, deployment")
    with button_col:
        if st.button("Use Sample JD →", use_container_width=True):
            st.session_state["sample_jd_hint"] = True
            st.info("Copy this sample into the Job Description field: Machine Learning Engineer. Requirements: Python, SQL, scikit-learn, pandas, model evaluation, feature engineering, REST APIs, Git, and model deployment. Build and evaluate ML models, clean datasets, communicate findings, and collaborate with engineering teams.")
    st.caption("🔒 Privacy: your resume is not shown in history. Analysis metadata is saved locally to SQLite. If Gemini is configured, relevant text is sent to Google for generation.")

    # ----------------------------- Results -----------------------------
    result = st.session_state.get("last_result")
    if result:
        st.divider()
        st.markdown("## Your Optimization Results")
        match = result.get("match", {})
        ai = result.get("ai", {})
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Alignment estimate", f'{match.get("score", 0)}%')
        m2.metric("Matched terms", len(match.get("matched_keywords", [])))
        m3.metric("Potential gaps", len(match.get("missing_keywords", [])))
        m4.metric("Analysis mode", "AI + rules" if result.get("ai_enabled") else "Rules only")
        st.progress(min(max(float(match.get("score", 0)) / 100, 0.0), 1.0))
        st.caption("This is a keyword/skill coverage estimate, not an official ATS score or a hiring prediction.")

        overview, gaps, optimized, letter, details = st.tabs(
            ["Overview", "Skill gaps", "Optimized resume", "Cover letter", "Details"]
        )
        with overview:
            st.markdown("### Summary")
            st.write(ai.get("summary", ""))
            st.markdown("### What already aligns")
            strengths = ai.get("strengths", [])
            if strengths:
                for item in strengths:
                    st.markdown(f"- {item}")
            else:
                st.info("No specific strengths were returned.")
            st.markdown("### Recommended next actions")
            for item in ai.get("recommendations", []):
                st.markdown(f"- {item}")
            for warning in ai.get("warnings", []):
                st.warning(warning)

        with gaps:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### Matched keywords / skills")
                st.write(", ".join(match.get("matched_keywords", [])) or "No direct matches detected.")
            with c2:
                st.markdown("### Potential gaps")
                st.write(", ".join(match.get("missing_keywords", [])) or "No gaps from the extracted keyword list.")
            st.markdown("### Requirements extracted from the job description")
            st.write(", ".join(match.get("job_keywords", [])) or "No requirements extracted.")
            st.caption("A missing keyword does not automatically mean you lack the skill; it may simply not be mentioned in your resume.")

        with optimized:
            optimized_text = ai.get("optimized_resume", "")
            edited = st.text_area(
                "Review and edit before exporting",
                value=optimized_text,
                height=420,
                key="edited_resume",
            )
            d1, d2 = st.columns(2)
            with d1:
                st.download_button(
                    "⬇ Download DOCX",
                    data=make_docx(edited, result.get("candidate_name", "")),
                    file_name="optimized_resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            with d2:
                st.download_button(
                    "⬇ Download PDF",
                    data=make_pdf(edited, result.get("candidate_name", "")),
                    file_name="optimized_resume.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            st.caption("Review names, dates, metrics, skills, and claims before sending this resume to an employer.")

        with letter:
            cover = ai.get("cover_letter", "")
            if cover:
                edited_cover = st.text_area("Editable cover letter", value=cover, height=320, key="edited_cover")
                st.download_button(
                    "⬇ Download cover letter (.docx)",
                    data=make_docx(edited_cover, result.get("candidate_name", "")),
                    file_name="cover_letter.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            else:
                st.info("No cover letter was generated. Configure a valid Google Gemini API key in the server environment and run the analysis again.")

        with details:
            st.json(
                {
                    "match": match,
                    "ai": ai,
                    "ai_enabled": result.get("ai_enabled", False),
                }
            )

# ----------------------------- History page -----------------------------
elif page.startswith("◷"):
    st.markdown("## 🗂️ Analysis History")
    st.markdown('<p class="muted">Review previous analysis summaries saved on this machine.</p>', unsafe_allow_html=True)
    history = get_history()
    if not history:
        st.info("No saved analyses yet. Go to Home and run an analysis to create a history entry.")
    else:
        for item in history:
            role = item.get("job_title") or "Untitled role"
            company = item.get("company") or "Company not specified"
            with st.expander(f'{item.get("created_at", "Unknown date")}  ·  {role}  ·  {item.get("score", 0)}% alignment'):
                st.write(f"**Company:** {company}")
                st.write(item.get("summary") or "No summary stored.")
                st.caption("Only summary metadata is listed here; full resume text is not displayed in history.")

# ----------------------------- About page -----------------------------
else:
    st.markdown("## ⓘ How AI Resume Optimizer Agent Works")
    st.markdown(
        """
        <div class="panel">
          <h3>Analysis workflow</h3>
          <p>1. Extract text from a PDF/DOCX or accept pasted resume text.</p>
          <p>2. Extract job-relevant terms and calculate a transparent coverage estimate.</p>
          <p>3. Optionally use Google Gemini for recommendations, a tailored resume draft, and a cover letter.</p>
          <p>4. Review the generated draft and export to DOCX or PDF.</p>
          <p>5. Store analysis metadata in local SQLite for later review.</p>
        </div>
        <div class="panel">
          <h3>Privacy & configuration</h3>
          <p>For safety, the API key is not collected in the user-facing UI. Set <code>GOOGLE_API_KEY</code> in your local <code>.env</code> file or deployment secrets.</p>
          <p>Optionally set <code>GEMINI_MODEL</code> to select the model, for example <code>gemini-2.5-flash</code>.</p>
          <p>Resume text is sent to Google only when Gemini generation is enabled. Local analysis metadata is saved to SQLite.</p>
        </div>
        <div class="panel">
          <h3>Important limitations</h3>
          <p>• This is a resume-writing assistant, not an employer's ATS.</p>
          <p>• Keyword matching can miss synonyms and context; manually review the results.</p>
          <p>• The app does not verify claims or guarantee interviews.</p>
          <p>• No live job-search API is included; you provide the job description.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
