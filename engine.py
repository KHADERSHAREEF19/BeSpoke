# ============================================================
# engine.py
# Orchestrates one tailoring run for the CLI scripts and the
# web app: loads the profile, scores the JD, reorders content,
# renders DOCX + PDF outputs and returns everything the UI needs
# (score, keyword breakdown, before/after preview data).
# ============================================================

import json
import os
import re

import ats
import core
import html_preview
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


def save_profile(data):
    validate_profile(data)
    with open(PROFILE_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
    return PROFILE_PATH


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


def enrich(profile):
    """Fill in JD-matchable keywords for items that lack them.

    Content typed into resume_data.py ships with curated keywords;
    content parsed from an uploaded resume does not — so we tag it
    automatically from the ATS concept dictionary before reordering.
    """
    def kws_for(item, text_key):
        item = dict(item)
        item["keywords"] = item.get("keywords") or ats.auto_keywords(
            item.get(text_key, ""))
        return item

    skills = {
        category: [kws_for(skill, "skill") for skill in skill_list]
        for category, skill_list in profile.get("SKILLS", {}).items()
    }
    certs = [kws_for(cert, "name") for cert in profile.get("CERTIFICATIONS", [])]
    experience = [
        {**job, "bullets": [kws_for(bullet, "text") for bullet in job.get("bullets", [])]}
        for job in profile.get("EXPERIENCE", [])
    ]
    projects = [
        {**project,
         "bullets": [kws_for(bullet, "text") for bullet in project.get("bullets", [])]}
        for project in profile.get("PROJECTS", [])
    ]
    return {"SKILLS": skills, "CERTIFICATIONS": certs,
            "EXPERIENCE": experience, "PROJECTS": projects}


def snapshot(role_title, skills, certs, experience, projects):
    return {
        "role_title": role_title,
        "skills": skills,
        "certs": certs,
        "experience": experience,
        "projects": projects,
    }


def run_generation(profile, jd_text, job, out_dir,
                   cover_letter=True, uae_cover_letter=False):
    """Tailor resume (+ optional UAE cover letter) for one job.

    Returns a result dict with the ATS report, file list and the
    before/after snapshots used by the preview panes.
    """
    jd_lower = jd_text.lower()
    tags = enrich(profile)

    role_title = core.detect_role_title(jd_lower, profile)
    skills = core.reorder_skills(tags["SKILLS"], jd_lower)
    certs = core.reorder_certs(tags["CERTIFICATIONS"], jd_lower)
    projects = core.reorder_projects(tags["PROJECTS"], jd_lower)
    experience = [
        dict(entry, bullets=core.reorder_bullets(entry["bullets"], jd_lower))
        for entry in tags["EXPERIENCE"]
    ]

    report = ats.score(jd_text, profile)

    name_slug = safe_slug(profile["PERSONAL"].get("name", "Resume").title())
    company_slug = safe_slug(job["company"])

    resume_docx = os.path.join(out_dir, f"{name_slug}_Resume_{company_slug}.docx")
    resume_pdf = os.path.join(out_dir, f"{name_slug}_Resume_{company_slug}.pdf")

    core.build_resume_docx(role_title, profile, skills, certs, experience,
                           projects).save(resume_docx)
    pdf_reportlab.render_resume_pdf(
        resume_pdf, role_title, profile, skills, certs, experience, projects)

    files = [
        {"label": "Tailored Resume — PDF", "filename": os.path.basename(resume_pdf),
         "kind": "pdf"},
        {"label": "Tailored Resume — DOCX", "filename": os.path.basename(resume_docx),
         "kind": "docx"},
    ]

    if cover_letter:
        letter_docx = os.path.join(out_dir, f"{name_slug}_Cover_Letter_{company_slug}.docx")
        letter_pdf = os.path.join(out_dir, f"{name_slug}_Cover_Letter_{company_slug}.pdf")
        letter_paragraphs = core.build_letter_paragraphs(jd_lower, job, profile)
        core.build_letter_docx(letter_paragraphs, job, profile,
                               uae=uae_cover_letter).save(letter_docx)
        pdf_reportlab.render_letter_pdf(letter_pdf, letter_paragraphs, job,
                                        profile, uae=uae_cover_letter)
        suffix = " (UAE)" if uae_cover_letter else ""
        files += [
            {"label": f"Cover Letter{suffix} — PDF",
             "filename": os.path.basename(letter_pdf), "kind": "pdf"},
            {"label": f"Cover Letter{suffix} — DOCX",
             "filename": os.path.basename(letter_docx), "kind": "docx"},
        ]

    baseline = snapshot(
        profile["PERSONAL"].get("role_label", ""), profile["SKILLS"],
        profile["CERTIFICATIONS"], profile["EXPERIENCE"], profile["PROJECTS"])
    tailored = snapshot(role_title, skills, certs, experience, projects)

    return {
        "role_title": role_title,
        "report": report,
        "files": files,
        "cover_letter": cover_letter,
        "uae_cover_letter": uae_cover_letter,
        "preview_before": html_preview.render_resume_html(profile, **{
            "role_title": baseline["role_title"], "skills": baseline["skills"],
            "certs": baseline["certs"], "experience": baseline["experience"],
            "projects": baseline["projects"]}),
        "preview_after": html_preview.render_resume_html(profile, **{
            "role_title": tailored["role_title"], "skills": tailored["skills"],
            "certs": tailored["certs"], "experience": tailored["experience"],
            "projects": tailored["projects"]}),
    }


def print_report(report, stream=None):
    """Console version of the ATS report."""
    import sys
    stream = stream or sys.stdout

    print(f"\nWeighted JD match: {report['score']}%", file=stream)
    print(f"Matched {report['matched_count']} of {report['concept_count']} "
          "tracked concepts from this JD.", file=stream)
    if report.get("years_required"):
        print(f"JD experience requirement detected: {report['years_required']}+ years",
              file=stream)

    print("\n--- MATCHED ---", file=stream)
    for concept in report["matched"]:
        print(f"  ✓ {concept['name']} ({concept['category']})", file=stream)

    print("\n--- IN THE JD BUT NOT IN YOUR RESUME ---", file=stream)
    if report["missing"]:
        for concept in report["missing"]:
            print(f"  ✗ {concept['name']} ({concept['category']})", file=stream)
        print("\nAdd a missing keyword only if you genuinely have that skill.",
              file=stream)
    else:
        print("  No tracked gaps found.", file=stream)
