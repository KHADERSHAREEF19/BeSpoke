
# 🎯 BeSpoke: Resume Tailoring System

> Automatically tailor your resume and generate cover letters for job applications with ATS keyword matching.

---

## ✨ Features

✅ **Smart Resume Tailoring** — Reorder bullets by job relevance  
✅ **ATS Keyword Matching** — See which skills match the job  
✅ **Auto Cover Letters** — Generate professional letters instantly  
✅ **Dual Output** — DOCX + PDF formats  
✅ **Honest Reporting** — Never invents skills  

---

## 📦 Installation

```bash
pip install python-docx docx2pdf
```

**For PDF export, install LibreOffice:**
- [Download here](https://www.libreoffice.org/download/)

---

## 🚀 Quick Start

**Step 1:** Edit `resume_data.py` with your information

**Step 2:** Paste job description into `job_description.txt`

**Step 3:** Fill in `job_details.py`:
```python
COMPANY = "Company Name"
ROLE = "Job Title"
HIRING_MANAGER = "Manager Name"
WHY_COMPANY = "Why you want this job"
```

**Step 4:** Generate files
```bash
python tailor_resume.py    # → Resume PDF + ATS report
python cover_letter.py     # → Cover Letter PDF
```

---

## 📁 Files

| File | Purpose |
|------|---------|
| `resume_data.py` | Your resume data (edit once) |
| `job_details.py` | Job-specific info (local) |
| `job_description.txt` | Paste JD here (local) |
| `tailor_resume.py` | Main resume script |
| `cover_letter.py` | Cover letter generator |
| `pdf_export.py` | PDF converter |

---

## ⚙️ How It Works

1. 📖 Reads job description
2. 🎯 Detects best role title
3. 🔄 Reorders bullets by relevance
4. 📊 Generates ATS keyword report
5. 📄 Outputs DOCX + PDF

---

## ⚠️ Important

- **ATS score** = estimate for THIS job only
- **Never add** skills you don't have
- **Always edit** the cover letter before sending

---

## 👨‍💻 Author

**Khader Shareef**

📧 [infa.khadershareef@gmail.com](mailto:infa.khadershareef@gmail.com)  
🔗 [LinkedIn: Khader Shareef](https://linkedin.com/in/khader-shareef-madani-129167260)  
🌐 [Khader.dev](https://khadershareef19.vercel.app)

