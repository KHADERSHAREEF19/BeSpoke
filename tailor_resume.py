# ============================================================
# tailor_resume.py  (CLI)
# Reads resume_data.py / profile.json + job_description.txt
# Reorders content by JD relevance and generates DOCX + PDF.
# NEVER invents content — only reorders existing content.
#
# Usage:
#   python3 tailor_resume.py
# ============================================================

import os
import tempfile

from job_details import COMPANY
from engine import load_profile, run_generation, print_report


def load_jd(filepath="job_description.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        raise SystemExit(
            "job_description.txt was not found in the same folder as tailor_resume.py."
        )


def main():
    print("=" * 60)
    print("RESUME TAILORING ENGINE")
    print("=" * 60)

    profile = load_profile()
    jd_text = load_jd().strip()

    from job_details import HIRING_MANAGER, ROLE, WHY_COMPANY
    job = {
        "company": COMPANY,
        "role": ROLE,
        "hiring_manager": HIRING_MANAGER,
        "why_company": WHY_COMPANY,
    }

    out_dir = tempfile.mkdtemp(prefix="bespoke_")
    result = run_generation(profile, jd_text, job, out_dir)
    print_report(result["report"])

    print(f"\nDetected role title: {result['role_title']}")
    print(f"Saved to: {out_dir}")
    for item in result["files"]:
        print(f"  • {item['label']}")
    print("\nOpen both, compare with your approved resume, then send the PDF.")


if __name__ == "__main__":
    main()
