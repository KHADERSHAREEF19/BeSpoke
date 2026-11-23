# ============================================================
# app.py  —  BeSpoke web app
#
# Paste a job description, get an ATS match report plus a
# tailored resume and cover letter (PDF + DOCX downloads).
#
# Run locally:   python3 app.py
# ============================================================

import json
import os
import secrets
import shutil
import time

from flask import (
    Flask, abort, flash, redirect, render_template, request,
    send_from_directory, url_for,
)

import engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATED_DIR = os.path.join(BASE_DIR, "generated")
MAX_AGE_SECONDS = 6 * 60 * 60  # generated files are cleaned after 6 hours

app = Flask(__name__)
app.secret_key = os.environ.get("BESPOKE_SECRET", "bespoke-dev-secret-key")


def _cleanup_old_runs():
    """Delete generated folders older than MAX_AGE_SECONDS."""
    now = time.time()
    try:
        entries = os.listdir(GENERATED_DIR)
    except FileNotFoundError:
        return
    for name in entries:
        path = os.path.join(GENERATED_DIR, name)
        try:
            if now - os.path.getmtime(path) > MAX_AGE_SECONDS:
                shutil.rmtree(path, ignore_errors=True)
        except OSError:
            pass


@app.route("/")
def index():
    profile = engine.load_profile()
    return render_template(
        "index.html",
        profile_json=json.dumps(profile, indent=2),
    )


@app.route("/generate", methods=["POST"])
def generate():
    jd_text = request.form.get("jd", "").strip()
    company = request.form.get("company", "").strip()
    role = request.form.get("role", "").strip()

    if not jd_text:
        flash("Paste the job description first — that is what drives the tailoring.", "error")
        return redirect(url_for("index"))
    if len(jd_text) < 50:
        flash("That job description looks too short to tailor against. Paste the full posting.",
              "error")
        return redirect(url_for("index"))
    if not company:
        flash("Add the company name so the files can be named correctly.", "error")
        return redirect(url_for("index"))

    job = {
        "company": company,
        "role": role or "Security Analyst",
        "hiring_manager": request.form.get("hiring_manager", "").strip() or "Hiring Manager",
        "why_company": request.form.get("why_company", "").strip(),
    }

    try:
        profile = engine.load_profile()
        token = secrets.token_hex(8)
        out_dir = os.path.join(GENERATED_DIR, token)
        os.makedirs(out_dir, exist_ok=True)
        result = engine.run_generation(profile, jd_text, job, out_dir)
    except Exception as exc:  # keep the preview usable even on bad input
        app.logger.exception("generation failed")
        flash(f"Something went wrong while generating: {exc}", "error")
        return redirect(url_for("index"))

    _cleanup_old_runs()
    return render_template(
        "results.html",
        token=token,
        job=job,
        role_title=result["role_title"],
        report=result["report"],
        files=result["files"],
    )


@app.route("/download/<token>/<path:filename>")
def download(token, filename):
    if not token.isalnum():
        abort(404)
    if os.path.basename(filename) != filename:
        abort(404)
    directory = os.path.join(GENERATED_DIR, token)
    if not os.path.isfile(os.path.join(directory, filename)):
        abort(404)
    return send_from_directory(directory, filename, as_attachment=True)


@app.route("/api/profile", methods=["POST"])
def save_profile():
    raw = request.form.get("profile_json", "")
    try:
        data = json.loads(raw)
        engine.validate_profile(data)
    except (ValueError, json.JSONDecodeError) as exc:
        flash(f"Could not save the profile: {exc}", "error")
        return redirect(url_for("index"))

    with open(engine.PROFILE_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
    flash("Resume profile saved. New applications will use this content.", "success")
    return redirect(url_for("index"))


@app.route("/api/profile/reset", methods=["POST"])
def reset_profile():
    try:
        os.remove(engine.PROFILE_PATH)
        flash("Reverted to the content in resume_data.py.", "success")
    except FileNotFoundError:
        flash("No custom profile was stored — already using resume_data.py.", "success")
    return redirect(url_for("index"))


@app.route("/branding/logo.png")
def branding_logo():
    return send_from_directory(BASE_DIR, "bespoke_logo.png")


if __name__ == "__main__":
    os.makedirs(GENERATED_DIR, exist_ok=True)
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False)
