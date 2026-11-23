<img src="bespoke_logo.png" alt="BeSpoke Logo" width="499">

## 🎯 BeSpoke: Resume Tailoring System

> One page. Upload your resume, paste a job description, get an accurate ATS
> match score, a before/after preview, and tailored PDF + DOCX downloads.

---

## ✨ How it works — 3 sections on one page

**Two tailoring modes**

- **Edit my uploaded resume in place (recommended)** — upload the **DOCX source**
  of your resume. BeSpoke edits *that exact file*: it reorders your real bullet
  points by JD relevance and swaps the header role title. Your photo, colors,
  fonts, margins and one-page pagination stay exactly as they are. Downloads:
  the edited DOCX (+ optional BeSpoke-style extras). Open the DOCX in Word /
  LibreOffice / Google Docs → *Save as PDF* for a pixel-identical PDF.
- **Rebuild in BeSpoke style** — regenerates a clean one-page resume from your
  structured details. Layout will differ from your original document.

**1 · Your resume** — upload your default resume (PDF / DOCX / TXT). BeSpoke reads
it and fills in all your details; review them and press *Save profile*. You can
also edit the JSON directly, or just keep the built-in content from
`resume_data.py`. For in-place editing use the DOCX version so the layout is
preserved.

**2 · Job description** — paste the full JD, company, role, hiring manager and a
genuine "why this company". Tick **"Generate a UAE cover letter"** only if you
want one (no watermark); leave it unticked and you get only the tailored resume.

**3 · Match & preview** — instantly get:
- 🎯 **Weighted ATS match score** with per-category breakdown bars
- ✅ / ❌ matched vs missing keyword chips
- 👀 **Before vs After** resume panes (same fonts, margins and layout — only the
  order of your real content changes)
- ⬇️ Downloads: tailored resume **PDF + DOCX**, plus the optional UAE cover
  letter **PDF + DOCX**

---

## 🧠 The score

No external API and no hidden service: `ats.py` runs locally and deterministically.

1. Scans the JD against a curated security-domain concept dictionary
   (SOC/SIEM/IAM/cloud/network/GRC/tools/certs/soft skills) with synonyms,
   abbreviations and plural handling.
2. Weights core concepts higher and rewards repeated mentions.
3. Score = weighted coverage = matched weight ÷ total JD weight.
4. It also extracts any "N+ years" requirement from the posting.

This is a **keyword-coverage estimate**, not a secret vendor algorithm — but it is
far closer than raw word matching, and it flags exactly which gaps cost you points.

---

## 🌐 Run it

```bash
pip install -r requirements.txt
python3 app.py          # → http://localhost:8000
```

Uploaded resumes are parsed by `parser.py`; reordering works on uploaded content
too (concepts are auto-tagged from the same dictionary).

---

## ☁️ Deploy on Vercel

The app is **stateless**: documents are generated in memory and delivered as
data-URL downloads, so nothing needs writable disk — which makes Vercel's
read-only serverless filesystem a perfect fit.

- Entry point: `api/index.py` (WSGI → Flask)
- Config: `vercel.json` (`@vercel/python`, all routes → the function)
- Dependencies auto-install from `requirements.txt`

One caveat: on Vercel the **Save profile** button can't write `profile.json`
(read-only storage). Your details stay in the editor and are sent along with
every *Tailor* request automatically, so uploads/edits keep working — only
cross-visit persistence needs local storage or a database add-on.

---

## 🖥️ Command line (optional)

```bash
python3 tailor_resume.py    # resume PDF + DOCX + ATS report
python3 cover_letter.py     # adds a UAE cover letter (edit job_details.py first)
```

Both CLIs share the exact same engine as the web app.

---

## 📁 Files

| File | Purpose |
|------|---------|
| `app.py` | Flask single-page web app |
| `engine.py` | Orchestration, profile loading, keyword auto-tagging |
| `core.py` | Reordering + DOCX renderers |
| `ats.py` | Weighted ATS matcher + concept dictionary |
| `parser.py` | Resume upload → structured profile |
| `html_preview.py` | Before/after HTML resume rendering |
| `pdf_reportlab.py` | Pure-Python PDF rendering |
| `resume_data.py` | Built-in resume data |
| `job_details.py` / `job_description.txt` | Inputs for the CLI |

---

## ⚠️ Important

- **Always read** the generated documents before sending.
- **Never add** keywords you don't genuinely have — BeSpoke reorders real content
  only, and so should you.
- Files land in `generated/` and are auto-cleaned after 6 hours.

---

## 👨‍💻 Author

**Khader Shareef**

📧 [infa.khadershareef@gmail.com](mailto:infa.khadershareef@gmail.com)  
🔗 [LinkedIn: Khader Shareef](https://linkedin.com/in/khader-shareef-madani-129167260)  
🌐 [Khader.dev](https://khadershareef19.vercel.app)
