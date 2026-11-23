# ============================================================
# app.py  —  BeSpoke web app (single page, 3 sections)
#
#   1. Your resume      → upload a PDF/DOCX to refill details,
#                         or edit the profile directly
#   2. Job description  → paste the JD + company details +
#                         optional UAE cover letter
#   3. Result           → weighted ATS match score, keyword
#                         breakdown, BEFORE/AFTER resume preview
#                         and PDF + DOCX downloads
#
# Stateless by design: files are generated in memory and served as
# data-URL downloads, so it runs on Vercel's read-only filesystem.
#
# Run locally:   python3 app.py
# ============================================================

import base64
import json
import os

from flask import (
    Flask, flash, redirect, render_template, request, send_from_directory, url_for,
)

import engine
import html_preview
import parser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

app = Flask(__name__)
app.secret_key = os.environ.get("BESPOKE_SECRET", "bespoke-dev-secret-key")


@app.context_processor
def inject_globals():
    return {"preview_css": html_preview.PREVIEW_CSS}


def _render(profile_json=None, result=None, form=None, scroll_result=False):
    profile = engine.load_profile()
    return render_template(
        "index.html",
        profile_json=profile_json if profile_json is not None
        else json.dumps(profile, indent=2),
        profile=profile,
        result=result,
        form=form or {},
        scroll_result=scroll_result,
    )


def _profile_from_form(form):
    """The tailor form carries the profile JSON typed into section 1,
    so uploads/edits work even where disk persistence is unavailable."""
    raw = (form.get("profile_json") or "").strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
        engine.validate_profile(data)
        return data
    except (ValueError, json.JSONDecodeError) as exc:
        flash(f"The resume details in section 1 are not valid JSON: {exc}", "error")
        return False


@app.route("/")
def index():
    return _render()


@app.route("/upload", methods=["POST"])
def upload():
    upload = request.files.get("resume_file")
    if upload is None or not upload.filename:
        flash("Choose a resume file (PDF or DOCX) first.", "error")
        return redirect(url_for("index"))

    ext = (os.path.splitext(upload.filename)[1] or "").lower()
    if ext not in ALLOWED_EXTENSIONS:
        flash(f"Unsupported file type '{ext}'. Upload a PDF, DOCX or TXT resume.",
              "error")
        return redirect(url_for("index"))

    try:
        text = parser.extract_text(upload.filename, upload.read())
        parsed = parser.parse_resume(text)
        engine.validate_profile(parsed)
    except Exception as exc:
        flash(f"Could not read that resume: {exc}", "error")
        return redirect(url_for("index"))

    flash("Resume imported — review the details below, then press "
          "'Save profile' so applications use them.", "success")
    return _render(profile_json=json.dumps(parsed, indent=2))


@app.route("/tailor", methods=["POST"])
def tailor():
    jd_text = request.form.get("jd", "").strip()
    company = request.form.get("company", "").strip()
    role = request.form.get("role", "").strip()

    form = {
        "jd": jd_text,
        "company": company,
        "role": role,
        "hiring_manager": request.form.get("hiring_manager", "").strip(),
        "why_company": request.form.get("why_company", "").strip(),
        "cover_letter": request.form.get("cover_letter") == "yes",
    }

    if len(jd_text) < 50:
        flash("Paste the full job description (at least a few sentences) — it drives "
              "both the tailoring and the match score.", "error")
        return _render(form=form)
    if not company:
        flash("Add the company name so the files can be named correctly.", "error")
        return _render(form=form)

    profile = _profile_from_form(request.form)
    if profile is False:
        return _render(form=form)
    if profile is None:
        profile = engine.load_profile()

    job = {
        "company": company,
        "role": role or "Security Analyst",
        "hiring_manager": form["hiring_manager"] or "Hiring Manager",
        "why_company": form["why_company"],
    }

    try:
        result = engine.run_generation(
            profile, jd_text, job,
            cover_letter=form["cover_letter"],
            uae_cover_letter=form["cover_letter"],
        )
    except Exception as exc:
        app.logger.exception("generation failed")
        flash(f"Something went wrong while generating: {exc}", "error")
        return _render(form=form)

    for item in result["files"]:
        encoded = base64.b64encode(item.pop("bytes")).decode("ascii")
        item["data_url"] = f"data:{engine.MIME_TYPES[item['kind']]};base64,{encoded}"
        item["size_kb"] = round(len(encoded) * 3 / 4 / 1024)

    result["job"] = job
    return _render(result=result, form=form, scroll_result=True)


@app.route("/api/profile", methods=["POST"])
def save_profile():
    raw = request.form.get("profile_json", "")
    try:
        data = json.loads(raw)
        engine.validate_profile(data)
    except (ValueError, json.JSONDecodeError) as exc:
        flash(f"Could not save the profile: {exc}", "error")
        return _render(profile_json=raw)

    try:
        engine.save_profile(data)
        flash("Resume profile saved. New applications will use this content.",
              "success")
        return _render()
    except OSError:
        # Read-only filesystem (e.g. hosted on Vercel): the details live in
        # the editor and travel with each Tailor request instead.
        flash("This hosting has read-only storage, so the profile is kept in the "
              "details box and reused automatically when you press Tailor. "
              "(Locally it would be saved to profile.json.)", "success")
        return _render(profile_json=raw)


@app.route("/api/profile/reset", methods=["POST"])
def reset_profile():
    try:
        os.remove(engine.PROFILE_PATH)
        flash("Reverted to the content in resume_data.py.", "success")
    except FileNotFoundError:
        flash("No custom profile was stored — already using resume_data.py.",
              "success")
    except OSError:
        flash("Read-only storage here — just clear the details box to start over.",
              "success")
    return _render()


@app.route("/branding/logo.png")
def branding_logo():
    return send_from_directory(BASE_DIR, "bespoke_logo.png")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False)
