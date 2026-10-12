#   🧠 ResumeIQ — AI-Powered Resume Optimizer Agent

**Analyze your resume. Match job requirements. Optimize your next application.**

ResumeIQ is an AI-powered resume analysis and optimization tool built with Streamlit and LangGraph. It compares your resume against a target job description, identifies relevant skills and keyword gaps, and helps you create a more targeted, job-specific resume.

Powered by Google Gemini, ResumeIQ can generate personalized recommendations, an optimized resume draft, and a tailored cover letter. It also supports a rules-based fallback mode, allowing users to perform core resume analysis even when AI generation is unavailable.

## ✨ Features

- **Resume Upload & Text Extraction** — Upload PDF or DOCX resumes or paste resume text directly.
- **Job Description Matching** — Analyze your resume against a target role, company, and job description.
- **Keyword & Skill Gap Analysis** — Identify matched terms, missing keywords, and potential areas for improvement.
- **Resume Alignment Estimate** — View a transparent keyword-coverage estimate to understand how closely your resume aligns with the job description.
- **AI-Powered Recommendations** — Generate actionable suggestions to improve resume content and relevance using Google Gemini.
- **Optimized Resume Generation** — Create a job-specific resume draft based on the original resume and target job requirements.
- **AI Cover Letter Generation** — Generate a tailored cover letter for your target role.
- **Editable Resume Draft** — Review and edit generated content before exporting.
- **Multiple Export Formats** — Download the optimized resume as DOCX or PDF.
- **Rules-Based Fallback** — Continue using core analysis features when Gemini is unavailable.
- **Analysis History** — Review locally stored analysis metadata through the History page.
- **Custom Navigation** — Navigate between Home, History, and About using the Streamlit sidebar.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive user interface |
| LangGraph | Resume analysis and review workflow |
| Google Gemini | AI-powered recommendations and content generation |
| PyPDF / PDF parsing library | PDF text extraction |
| python-docx | DOCX processing and export |
| ReportLab / PDF export library | PDF generation |
| SQLite | Local analysis history |

*The table describes the intended responsibilities of the stack; confirm the exact PDF parsing and export libraries against `requirements.txt` before publishing.*

## 📁 Project Structure

```text
ResumeIQ/
├── frontend.py           # Streamlit UI and navigation
├── agent.py              # LangGraph analysis workflow
├── resume_optimizer.py   # Extraction, matching, AI generation, exports
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment configuration (optional)
├── .gitignore            # Files excluded from version control
└── README.md             # Project documentation
```

The actual repository may contain additional files, tests, configuration, and local database files.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or newer
- pip
- Git (optional, for cloning the repository)
- A Google Gemini API key for AI-powered generation

Core rules-based analysis can work without a Gemini API key, provided the required application dependencies are installed.

### 1. Clone the repository

```bash
git clone https://github.com/Sumitjaiswal9334/ai_resume_optimizer_agent.git
cd ai_resume_optimizer_agent
```

Replace the repository URL if your actual GitHub repository uses a different name.

### 2. Create a virtual environment

**Windows — PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this command in the current terminal and try activating again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Use a model identifier supported by your Google Gemini API account and the installed SDK. If the configured model is unavailable, update `GEMINI_MODEL` to a supported model.

**Security note:** Never hardcode API keys in your Python files or expose them in the frontend. Keep `.env` out of Git, and use `.env.example` with placeholder values when sharing configuration instructions.

### 5. Run the application

```bash
streamlit run frontend.py
```

Open the local URL displayed in the terminal, usually:

`http://localhost:8501`

## 🧪 Testing & Validation

Run the automated tests, if included in the repository:

```bash
pytest -q
```

Check the main Python files for syntax errors:

```bash
python -m py_compile frontend.py agent.py resume_optimizer.py
```

These commands check test results and Python syntax, respectively. Passing the syntax check does not guarantee that API calls, document exports, or the full application workflow will work correctly.

## 📊 How ResumeIQ Works

1. **Input** — Upload a resume or paste its text, then provide the target job description.
2. **Extraction** — Extract readable text from the uploaded document.
3. **Analysis** — Compare resume terms with job-related terms and identify potential gaps.
4. **Recommendations** — Generate improvement suggestions using Gemini when available.
5. **Optimization** — Create a tailored resume draft and cover letter.
6. **Review & Export** — Review and edit the generated content before downloading it.
7. **History** — Review locally saved analysis metadata.

## 📐 Understanding the Alignment Estimate

ResumeIQ calculates an estimated keyword-coverage score using the following general approach:

**Alignment estimate = matched extracted job terms / total extracted job terms × 100**

The exact result depends on the terms extracted and the implementation in `resume_optimizer.py`.

This score is a heuristic, not an official ATS score. It may not fully recognize synonyms, equivalent skills, context, transferable experience, or differences in terminology. A higher score does not guarantee that a resume will pass an ATS screening or lead to an interview.

## 🔐 Privacy & Security

- **Local history:** The application stores analysis metadata locally, such as timestamps, target roles, company names, scores, counts, and short summaries.
- **Resume content:** Full resume text is not stored in the local history database, according to the current application design.
- **AI processing:** When Gemini is enabled, relevant resume and job-description content is sent to Google's API for processing. Review the provider's current privacy terms before submitting sensitive information.
- **API key protection:** Keep credentials in environment variables and never commit `.env` or expose secrets in client-facing code.
- **Local database:** Delete `resume_optimizer.db` to remove its locally stored analysis metadata, after confirming the actual database path and filename used by your application.

Only upload documents and personal information you are authorized to process.

## ⚠️ Limitations

- Scanned PDFs and image-only documents require OCR, which is not included in the current implementation.
- Keyword matching may miss synonyms and semantic relationships between skills.
- AI-generated recommendations and resume content can contain inaccuracies and require human review.
- The application does not independently verify employment history, qualifications, or resume claims.
- Live job searching and automatic job application submission are not included.
- The alignment estimate is not a hiring prediction and does not guarantee interviews or job offers.
- AI generation depends on API availability, model access, quotas, and configuration.

## 🔮 Potential Improvements

- Semantic resume-to-job matching using embeddings.
- More detailed skill-gap analysis and transferable-skill detection.
- Resume templates with customizable formatting.
- Job-specific achievement and bullet-point suggestions.
- Support for additional document formats and OCR.
- Exportable analysis reports and richer history management.
- Unit and integration tests for document extraction, scoring, and export workflows.

## 👨‍💻 Author

**Sumit Jaiswal**  
B.S. Computer Science and Data Analytics, IIT Patna

- **GitHub:** [Sumitjaiswal9334](https://github.com/Sumitjaiswal9334)
- **Portfolio:** [Visit Portfolio](https://sumit-kr-jaiswal-portfolio.netlify.app)

## 📄 License

Add a `LICENSE` file if you intend to distribute the project under an open-source license. Until a license is specified, do not assume that others have permission to reuse or redistribute the code.

---

**ResumeIQ — Make every application more targeted, one resume at a time.**
