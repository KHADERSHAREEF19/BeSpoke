# ============================================================
# engine.py
# Orchestrates one tailoring run for both the CLI scripts and
# the web app. Loads the profile, runs the reordering, renders
# DOCX + PDF outputs and returns the ATS match report.
# ============================================================

import json
import os
import re

import core
import pdf_reportlab

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_PATH = os.path.join(BASE_DIR, "profile.json")

PROFILE_KEYS = [
    "PERSONAL", "SUMMARY_TEMPLATE", "CERTS_SHORT", "CERT_LINE",
    "CERTIFICATIONS", "SKILLS", "EXPERIENCE", "PROJECTS",
    "EDUCATION", "ACHIEVEMENTS", "ACCEPTABLE_ROLE_TITLES",
]


def profile_from_module(module):
    """Convert resume_data.py's module globals into a plain dict."""
    return {key: getattr(module, key) for key in PROFILE_KEYS}


def load_profile():
    """Web-editable profile.json wins; otherwise fall back to resume_data.py."""
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        validate_profile(data)
        return data

    import resume_data
    return profile_from_module(resume_data)


def validate_profile(data):
    missing = [key for key in PROFILE_KEYS if key not in data]
    if missing:
        raise ValueError("Profile is missing keys: " + ", ".join(missing))
    for key in ("PERSONAL", "EDUCATION"):
        if not isinstance(data[key], dict):
            raise ValueError(f"Profile key '{key}' must be an object.")
    for key in ("CERTIFICATIONS", "EXPERIENCE", "PROJECTS", "ACHIEVEMENTS",
                "ACCEPTABLE_ROLE_TITLES"):
        if not isinstance(data[key], list):
            raise ValueError(f"Profile key '{key}' must be a list.")
    if not isinstance(data["SKILLS"], dict):
        raise ValueError("Profile key 'SKILLS' must be an object.")
    return True


def safe_slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "_", text or "").strip("_") or "Company"


def run_generation(profile, jd_text, job, out_dir):
    """Tailor resume + cover letter for one job. Returns a result dict.

    job = {"company", "role", "hiring_manager", "why_company"}
    """
    jd_lower = jd_text.lower()

    role_title = core.detect_role_title(jd_lower, profile)
    skills = core.reorder_skills(profile["SKILLS"], jd_lower)
    certs = core.reorder_certs(profile["CERTIFICATIONS"], jd_lower)
    projects = core.reorder_projects(profile["PROJECTS"], jd_lower)
    experience = [
        dict(entry, bullets=core.reorder_bullets(entry["bullets"], jd_lower))
        for entry in profile["EXPERIENCE"]
    ]

    resume_text = core.resume_plain_text(
        role_title, profile, skills, certs, experience, projects)
    report = core.generate_match_report(jd_lower, resume_text)

    name_slug = safe_slug(profile["PERSONAL"]["name"].title())
    company_slug = safe_slug(job["company"])

    resume_docx = os.path.join(out_dir, f"{name_slug}_Resume_{company_slug}.docx")
    resume_pdf = os.path.join(out_dir, f"{name_slug}_Resume_{company_slug}.pdf")
    letter_docx = os.path.join(out_dir, f"{name_slug}_Cover_Letter_{company_slug}.docx")
    letter_pdf = os.path.join(out_dir, f"{name_slug}_Cover_Letter_{company_slug}.pdf")

    core.build_resume_docx(role_title, profile, skills, certs, experience, projects).save(resume_docx)
    pdf_reportlab.render_resume_pdf(
        resume_pdf, role_title, profile, skills, certs, experience, projects)

    letter_paragraphs = core.build_letter_paragraphs(jd_lower, job, profile)
    core.build_letter_docx(letter_paragraphs, job, profile).save(letter_docx)
    pdf_reportlab.render_letter_pdf(letter_pdf, letter_paragraphs, job, profile)

    return {
        "role_title": role_title,
        "report": report,
        "files": [
            {"label": "Tailored Resume — PDF", "filename": os.path.basename(resume_pdf),
             "kind": "pdf"},
            {"label": "Tailored Resume — DOCX", "filename": os.path.basename(resume_docx),
             "kind": "docx"},
            {"label": "Cover Letter — PDF", "filename": os.path.basename(letter_pdf),
             "kind": "pdf"},
            {"label": "Cover Letter — DOCX", "filename": os.path.basename(letter_docx),
             "kind": "docx"},
        ],
    }


def print_report(report, stream=None):
    """Console version of the ATS keyword report."""
    import sys
    stream = stream or sys.stdout

    print(f"\nEstimated JD match: {report['percentage']}%", file=stream)
    print("This is a keyword-overlap estimate for this JD only, "
          "not a universal ATS score.", file=stream)
    print(f"Tracked JD keywords: {len(report['jd_keywords'])} | "
          f"Present in resume: {len(report['matched'])}", file=stream)

    print("\n--- MATCHED ---", file=stream)
    for keyword in report["matched"]:
        print(f"  ✅ {keyword}", file=stream)

    print("\n--- IN THE JD BUT NOT IN YOUR RESUME ---", file=stream)
    if report["missing"]:
        for keyword in report["missing"]:
            print(f"  ❌ {keyword}", file=stream)
        print("\nAdd a missing keyword only if you genuinely have that skill.",
              file=stream)
    else:
        print("  No tracked gaps found.", file=stream)
