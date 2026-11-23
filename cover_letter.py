# ============================================================
# cover_letter.py  (CLI)
# Builds a tailored cover letter (DOCX + PDF) from
# resume_data.py / profile.json, job_details.py and
# job_description.txt. Uses only real content.
#
# Usage:
#   python3 cover_letter.py
# ============================================================

import os
import tempfile

from job_details import COMPANY, HIRING_MANAGER, ROLE, WHY_COMPANY
from engine import load_profile, run_generation
from tailor_resume import load_jd


def main():
    if not WHY_COMPANY.strip():
        raise SystemExit("Write WHY_COMPANY in job_details.py before generating the letter.")

    profile = load_profile()
    jd_text = load_jd().strip()

    job = {
        "company": COMPANY,
        "role": ROLE,
        "hiring_manager": HIRING_MANAGER,
        "why_company": WHY_COMPANY,
    }

    out_dir = tempfile.mkdtemp(prefix="bespoke_letter_")
    result = run_generation(profile, jd_text, job, out_dir)

    print(f"Cover letter generated for {COMPANY} — {ROLE}")
    for item in result["files"]:
        if "Cover_Letter" in item["filename"]:
            print(f"  • {item['label']} → {os.path.join(out_dir, item['filename'])}")
    print("\nRead it fully before sending, and edit any sentence that doesn't sound like you.")


if __name__ == "__main__":
    main()
