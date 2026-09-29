# ============================================================
# tailor_resume.py
# Reads resume_data.py + job_description.txt
# Reorders content by JD relevance and generates DOCX + report
# NEVER invents content — only reorders existing content
# ============================================================

import re
from job_details import COMPANY
from pdf_export import export_pdf
from docx import Document
from docx.shared import Pt, Mm, Emu, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from resume_data import (
    PERSONAL, SUMMARY_TEMPLATE, CERT_LINE, CERTIFICATIONS, SKILLS,
    EXPERIENCE, PROJECTS, EDUCATION, ACHIEVEMENTS, ACCEPTABLE_ROLE_TITLES
)

# Keywords checked against every JD.
# Includes tools you do NOT have, so missing requirements are reported honestly.
IMPORTANT_KEYWORDS = [
    "soc", "siem", "edr", "xdr", "sentinel", "defender", "kql",
    "incident response", "incident management", "alert triage",
    "threat detection", "threat hunting", "threat intelligence",
    "security monitoring", "log analysis", "phishing", "malware",
    "mitre", "vulnerability", "vulnerability assessment",
    "remediation", "containment", "escalation", "documentation",
    "reporting", "postmortem", "post-incident", "runbook", "playbook",
    "patch", "forensic", "firewall", "fortigate", "active directory",
    "splunk", "wazuh", "qradar", "arcsight", "rsa", "logrhythm",
    "wireshark", "python", "linux", "windows", "tcp/ip", "dns",
    "cloud", "azure", "aws", "compliance", "risk assessment",
    "penetration testing", "nist", "iso 27001", "pci dss", "gdpr",
    "soar", "automation", "scripting",
]


def kw_in(keyword, text):
    """Match whole words. Short keywords cannot match inside longer words."""
    keyword = keyword.lower()
    if len(keyword) <= 4:
        pattern = r"(?<![a-z0-9])" + re.escape(keyword) + r"s?(?![a-z0-9])"
    else:
        pattern = r"(?<![a-z0-9])" + re.escape(keyword)
    return re.search(pattern, text) is not None


def score_item(keywords, jd_lower):
    return sum(1 for keyword in keywords if kw_in(keyword, jd_lower))


def display_url(url):
    """https://www.linkedin.com/in/x -> linkedin.com/in/x"""
    return re.sub(r"^https?://(?:www\.)?", "", url).rstrip("/")


def load_jd(filepath="job_description.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        raise SystemExit(
            "job_description.txt was not found in the same folder as tailor_resume.py."
        )


def detect_role_title(jd_lower):
    best_title = PERSONAL["role_label"]
    best_count = 0
    for title in ACCEPTABLE_ROLE_TITLES:
        pattern = r"(?<![a-z0-9])" + re.escape(title.lower()) + r"(?![a-z0-9])"
        count = len(re.findall(pattern, jd_lower))
        if count > best_count:
            best_title = title
            best_count = count
    return best_title


def reorder_bullets(bullets, jd_lower):
    pinned = [b for b in bullets if b.get("pin")]
    rest = [b for b in bullets if not b.get("pin")]
    rest.sort(
        key=lambda b: (
            -score_item(b.get("keywords", []), jd_lower),
            b.get("priority", 99),
        )
    )
    return pinned + rest


def reorder_skills(skills_dict, jd_lower):
    return {
        category: sorted(
            skill_list,
            key=lambda skill: -score_item(skill["keywords"], jd_lower),
        )
        for category, skill_list in skills_dict.items()
    }


def reorder_certs(certs, jd_lower):
    return sorted(
        certs,
        key=lambda cert: -score_item(cert["keywords"], jd_lower),
    )


def reorder_projects(projects, jd_lower):
    def project_score(project):
        keywords = [
            keyword
            for bullet in project["bullets"]
            for keyword in bullet.get("keywords", [])
        ]
        return -score_item(keywords, jd_lower)

    return sorted(projects, key=project_score)


def resume_plain_text(role_title, skills_dict, certs, experience, projects):
    """Build the actual visible resume text used for scoring."""
    parts = [SUMMARY_TEMPLATE.format(role_title=role_title, cert_line=CERT_LINE)]

    for job in experience:
        parts.extend([job["title"], job["company"]])
        parts.extend(bullet["text"] for bullet in job["bullets"])

    for project in projects:
        parts.extend([project["name"], project["subtitle"]])
        parts.extend(bullet["text"] for bullet in project["bullets"])

    for category, skill_list in skills_dict.items():
        parts.append(category)
        parts.extend(skill["skill"] for skill in skill_list)

    parts.extend(cert["name"] for cert in certs)
    parts.extend(ACHIEVEMENTS)
    return " ".join(parts).lower()


def generate_match_report(jd_lower, resume_text):
    jd_keywords = [keyword for keyword in IMPORTANT_KEYWORDS if kw_in(keyword, jd_lower)]
    matched = [keyword for keyword in jd_keywords if kw_in(keyword, resume_text)]
    missing = [keyword for keyword in jd_keywords if keyword not in matched]
    percentage = round(len(matched) / len(jd_keywords) * 100) if jd_keywords else 0

    return {
        "percentage": percentage,
        "jd_keywords": jd_keywords,
        "matched": matched,
        "missing": missing,
    }


def build_docx(role_title, skills_dict, certs, experience, projects):
    doc = Document()

    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(14)
    section.bottom_margin = Mm(14)
    section.left_margin = Mm(17)
    section.right_margin = Mm(17)
    right_tab = Emu(section.page_width - section.left_margin - section.right_margin)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    normal.font.size = Pt(10.2)
    normal.paragraph_format.space_after = Pt(1)
    normal.paragraph_format.line_spacing = 1.05

    bullet_style = doc.styles["List Bullet"]
    bullet_style.font.name = "Calibri"
    bullet_style._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    bullet_style.font.size = Pt(10.2)
    bullet_style.paragraph_format.space_after = Pt(1)
    bullet_style.paragraph_format.left_indent = Mm(6)

    def set_font(run, size=10.2, bold=False, italic=False, color=None):
        run.font.name = "Calibri"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
        run.font.size = Pt(size)
        run.bold = bold
        run.italic = italic
        if color:
            run.font.color.rgb = RGBColor(*color)

    def add_link(paragraph, text, url, bold=False, size=None):
        relationship_id = paragraph.part.relate_to(
            url,
            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
            is_external=True,
        )
        hyperlink = OxmlElement("w:hyperlink")
        hyperlink.set(qn("r:id"), relationship_id)

        run = OxmlElement("w:r")
        properties = OxmlElement("w:rPr")

        if bold:
            properties.append(OxmlElement("w:b"))

        fonts = OxmlElement("w:rFonts")
        fonts.set(qn("w:ascii"), "Calibri")
        fonts.set(qn("w:hAnsi"), "Calibri")
        properties.append(fonts)

        if size:
            half_points = str(int(round(size * 2)))
            font_size = OxmlElement("w:sz")
            font_size.set(qn("w:val"), half_points)
            properties.append(font_size)
            complex_size = OxmlElement("w:szCs")
            complex_size.set(qn("w:val"), half_points)
            properties.append(complex_size)

        color = OxmlElement("w:color")
        color.set(qn("w:val"), "0563C1")
        properties.append(color)

        underline = OxmlElement("w:u")
        underline.set(qn("w:val"), "single")
        properties.append(underline)

        run.append(properties)
        text_element = OxmlElement("w:t")
        text_element.set(qn("xml:space"), "preserve")
        text_element.text = text
        run.append(text_element)

        hyperlink.append(run)
        paragraph._p.append(hyperlink)

    def heading(text):
        paragraph = doc.add_paragraph()
        paragraph.paragraph_format.space_before = Pt(8)
        paragraph.paragraph_format.space_after = Pt(3)
        paragraph.paragraph_format.keep_with_next = True
        set_font(paragraph.add_run(text.upper()), size=11.5, bold=True, color=(31, 78, 121))

        properties = paragraph._p.get_or_add_pPr()
        border = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        for key, value in (("val", "single"), ("sz", "8"), ("space", "1"), ("color", "1F4E79")):
            bottom.set(qn("w:" + key), value)
        border.append(bottom)
        properties.append(border)

    def add_role(title, organization, dates, location=None):
        paragraph = doc.add_paragraph()
        paragraph.paragraph_format.space_before = Pt(4)
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.keep_with_next = True
        paragraph.paragraph_format.tab_stops.add_tab_stop(right_tab, WD_TAB_ALIGNMENT.RIGHT)

        set_font(paragraph.add_run(title), size=10.4, bold=True)
        if organization:
            set_font(paragraph.add_run(" | " + organization), size=10.4)
        if dates:
            set_font(paragraph.add_run("\t" + dates), size=10.4, bold=True)

        if location:
            location_paragraph = doc.add_paragraph()
            location_paragraph.paragraph_format.space_after = Pt(1)
            location_paragraph.paragraph_format.keep_with_next = True
            set_font(location_paragraph.add_run(location), size=9.8, italic=True)

    def add_bullet(text):
        paragraph = doc.add_paragraph(style="List Bullet")
        paragraph.paragraph_format.space_after = Pt(1)
        set_font(paragraph.add_run(text), size=10.2)

    def add_skill(label, text):
        paragraph = doc.add_paragraph()
        paragraph.paragraph_format.space_after = Pt(1)
        set_font(paragraph.add_run(label + ": "), size=10.2, bold=True)
        set_font(paragraph.add_run(text), size=10.2)

    def add_project(name, url, subtitle):
        paragraph = doc.add_paragraph()
        paragraph.paragraph_format.space_before = Pt(4)
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.keep_with_next = True
        add_link(paragraph, name, url, bold=True)
        set_font(paragraph.add_run(subtitle), size=10.4, bold=True)

    # Header — full visible URLs, matching the approved resume
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(1)
    set_font(paragraph.add_run(PERSONAL["name"]), size=18, bold=True, color=(31, 78, 121))

    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(0)
    set_font(
        paragraph.add_run(
            f"{role_title} | {PERSONAL['location']} | {PERSONAL['phone']} | "
        ),
        size=9.8,
    )
    add_link(paragraph, PERSONAL["email"], "mailto:" + PERSONAL["email"], size=9.8)

    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(2)
    add_link(paragraph, display_url(PERSONAL["linkedin"]), PERSONAL["linkedin"], size=9.8)
    set_font(paragraph.add_run(" | "), size=9.8)
    add_link(paragraph, display_url(PERSONAL["github"]), PERSONAL["github"], size=9.8)
    set_font(paragraph.add_run(" | "), size=9.8)
    add_link(paragraph, display_url(PERSONAL["portfolio"]), PERSONAL["portfolio"], size=9.8)

    # Summary uses the fixed certification line
    heading("Professional Summary")
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(2)
    set_font(
        paragraph.add_run(
            SUMMARY_TEMPLATE.format(role_title=role_title, cert_line=CERT_LINE)
        ),
        size=10.2,
    )

    heading("Professional Experience")
    for job in experience:
        add_role(job["title"], job["company"], job["dates"], job["location"])
        for bullet in job["bullets"]:
            add_bullet(bullet["text"])

    heading("Security Projects")
    for project in projects:
        add_project(project["name"], project["url"], project["subtitle"])
        for bullet in project["bullets"]:
            add_bullet(bullet["text"])

    heading("Core Skills")
    for category, skill_list in skills_dict.items():
        names = [
            skill["skill"] + (" (in progress)" if skill["level"] == "learning" else "")
            for skill in skill_list
        ]
        add_skill(category, ", ".join(names))

    heading("Certifications")
    for cert in certs:
        text = cert["name"]
        if cert.get("status") == "in_progress":
            text += " — In Progress"
        add_bullet(text)

    heading("Education")
    add_role(
        EDUCATION["degree"],
        EDUCATION["university"],
        EDUCATION["dates"],
        EDUCATION["location"],
    )
    paragraph = doc.add_paragraph()
    set_font(paragraph.add_run(EDUCATION["cgpa"]), size=10.2)

    heading("Leadership & Achievements")
    for achievement in ACHIEVEMENTS:
        add_bullet(achievement)

    return doc


def main():
    print("=" * 60)
    print("RESUME TAILORING ENGINE")
    print("=" * 60)

    jd_lower = load_jd("job_description.txt").lower()
    role_title = detect_role_title(jd_lower)
    print(f"Detected role title: {role_title}")

    skills = reorder_skills(SKILLS, jd_lower)
    certs = reorder_certs(CERTIFICATIONS, jd_lower)
    projects = reorder_projects(PROJECTS, jd_lower)
    experience = [
        dict(job, bullets=reorder_bullets(job["bullets"], jd_lower))
        for job in EXPERIENCE
    ]

    resume_text = resume_plain_text(role_title, skills, certs, experience, projects)
    report = generate_match_report(jd_lower, resume_text)

    print(f"\nEstimated JD match: {report['percentage']}%")
    print("This is a keyword-overlap estimate for this JD only, not a universal ATS score.")
    print(
        f"Tracked JD keywords: {len(report['jd_keywords'])} | "
        f"Present in resume: {len(report['matched'])}"
    )

    print("\n--- MATCHED ---")
    for keyword in report["matched"]:
        print(f"  ✅ {keyword}")

    print("\n--- IN THE JD BUT NOT IN YOUR RESUME ---")
    if report["missing"]:
        for keyword in report["missing"]:
            print(f"  ❌ {keyword}")
        print("\nAdd a missing keyword only if you genuinely have that skill.")
    else:
        print("  No tracked gaps found.")

    safe_company = re.sub(r"[^A-Za-z0-9]+", "_", COMPANY).strip("_")
    output_name = f"Khader_Shareef_Resume_{safe_company}.docx"
    build_docx(role_title, skills, certs, experience, projects).save(output_name)
    print(f"\nSaved DOCX: {output_name}")
    pdf = export_pdf(output_name)
    if pdf:
        print(f"Saved PDF:  {pdf}")
    print("Open both, compare with your approved resume, then send the PDF.")


if __name__ == "__main__":
    main()