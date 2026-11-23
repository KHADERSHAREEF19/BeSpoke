# ============================================================
# core.py
# Shared tailoring + rendering logic used by the CLI scripts
# and the BeSpoke web app.
#
# NEVER invents content — it only reorders and renders content
# that already exists in resume_data.py / profile.json.
# ============================================================

import datetime
import re

from docx import Document
from docx.shared import Pt, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

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
    # Identity & access management
    "iam", "identity and access management", "pingone", "sso",
    "single sign-on", "saml", "oidc", "mfa", "multi-factor",
    "rbac", "ciam", "entra id", "privileged access", "pam", "okta",
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


def detect_role_title(jd_lower, profile):
    best_title = profile["PERSONAL"]["role_label"]
    best_count = 0
    for title in profile["ACCEPTABLE_ROLE_TITLES"]:
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


def resume_plain_text(role_title, profile, skills_dict, certs, experience, projects):
    """Build the actual visible resume text used for scoring."""
    parts = [
        profile["SUMMARY_TEMPLATE"].format(
            role_title=role_title, cert_line=profile["CERT_LINE"]
        )
    ]

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
    parts.extend(profile["ACHIEVEMENTS"])
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


def phone_line(personal):
    """'+971 ... (UAE) | +91 ... (India)' when a UAE number exists."""
    phones = personal.get("phone", "")
    uae = personal.get("uae_phone")
    if uae:
        return f"{uae} (UAE) | {phones} (India)"
    return phones


# ------------------------------------------------------------
# DOCX renderers (kept identical to the original CLI output)
# ------------------------------------------------------------

def build_resume_docx(role_title, profile, skills_dict, certs, experience, projects):
    doc = Document()

    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(14)
    section.bottom_margin = Mm(14)
    section.left_margin = Mm(17)
    section.right_margin = Mm(17)
    right_tab = section.page_width - section.left_margin - section.right_margin

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
        if url:
            add_link(paragraph, name, url, bold=True)
        else:
            set_font(paragraph.add_run(name), size=10.4, bold=True, color=(31, 78, 121))
        set_font(paragraph.add_run(subtitle), size=10.4, bold=True)

    personal = profile["PERSONAL"]

    # Header — full visible URLs, matching the approved resume
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(1)
    set_font(paragraph.add_run(personal["name"]), size=18, bold=True, color=(31, 78, 121))

    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(0)
    set_font(
        paragraph.add_run(
            f"{role_title} | {personal['location']} | {phone_line(personal)} | "
        ),
        size=9.8,
    )
    add_link(paragraph, personal["email"], "mailto:" + personal["email"], size=9.8)

    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(2)
    add_link(paragraph, display_url(personal["linkedin"]), personal["linkedin"], size=9.8)
    set_font(paragraph.add_run(" | "), size=9.8)
    add_link(paragraph, display_url(personal["github"]), personal["github"], size=9.8)
    set_font(paragraph.add_run(" | "), size=9.8)
    add_link(paragraph, display_url(personal["portfolio"]), personal["portfolio"], size=9.8)

    # Summary uses the fixed certification line
    heading("Professional Summary")
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(2)
    set_font(
        paragraph.add_run(
            profile["SUMMARY_TEMPLATE"].format(
                role_title=role_title, cert_line=profile["CERT_LINE"]
            )
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
        add_project(project["name"], project.get("url"), project["subtitle"])
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
    education = profile["EDUCATION"]
    add_role(
        education["degree"],
        education["university"],
        education["dates"],
        education["location"],
    )
    paragraph = doc.add_paragraph()
    set_font(paragraph.add_run(education["cgpa"]), size=10.2)

    heading("Leadership & Achievements")
    for achievement in profile["ACHIEVEMENTS"]:
        add_bullet(achievement)

    return doc


UNUSED_SIEM_VENDORS = ["qradar", "arcsight", "logrhythm", "rsa"]


def as_clause(bullet_text):
    """'Triaged real-time alerts...' -> 'triaged real-time alerts...'"""
    text = bullet_text.strip().rstrip(".")
    return text[0].lower() + text[1:]


def _job_relevance(job, jd_lower):
    return sum(score_item(b.get("keywords", []), jd_lower) for b in job["bullets"])


def build_letter_paragraphs(jd_lower, job, profile):
    """Build the cover letter body as a list of paragraph strings.

    The two most relevant roles (by JD keyword overlap) are picked so the
    letter always leads with the experience that matches this posting.
    """
    experience = profile["EXPERIENCE"]
    ranked = sorted(experience, key=lambda j: -_job_relevance(j, jd_lower))
    job1, job2 = ranked[0], ranked[1]
    b1 = reorder_bullets(job1["bullets"], jd_lower)
    b2 = reorder_bullets(job2["bullets"], jd_lower)
    top_project = reorder_projects(profile["PROJECTS"], jd_lower)[0]

    iam_focused = any(
        kw_in(k, jd_lower)
        for k in ("iam", "identity and access management", "pingone", "sso",
                  "saml", "oidc", "mfa", "rbac", "entra id", "ciam")
    )

    if iam_focused:
        intro = (
            f"I am applying for the {job['role']} position at {job['company']}. "
            "I bring hands-on identity and access management experience across "
            "PingOne and Microsoft Entra ID, including SSO integration, adaptive "
            "MFA, RBAC policy management and identity-proofing workflows."
        )
    else:
        intro = (
            f"I am applying for the {job['role']} position at {job['company']}. "
            "I bring hands-on experience in enterprise multi-tenant SOC operations, "
            "including alert triage, incident investigation and first-response "
            "containment using Microsoft Sentinel and Microsoft Defender XDR."
        )

    paragraphs = [
        intro,
        f"In my role as {job1['title']} at {job1['company']}, I {as_clause(b1[0]['text'])}. "
        f"I also {as_clause(b1[1]['text'])}. Earlier, at {job2['company']}, "
        f"I {as_clause(b2[0]['text'])}.",
        f"In my {top_project['name']} project, I {as_clause(top_project['bullets'][0]['text'])}. "
        f"I hold the {profile['CERTS_SHORT']} certifications.",
    ]

    if not iam_focused and any(kw_in(v, jd_lower) for v in UNUSED_SIEM_VENDORS):
        paragraphs.append(
            "My SIEM experience is primarily with Microsoft Sentinel, with lab exposure to "
            "Splunk and Wazuh. The core workflow of log analysis, alert correlation, triage "
            "and escalation carries across platforms, and I am ready to ramp up quickly on "
            "the tools your team uses."
        )

    paragraphs.append(
        f"{job['why_company'].strip()} I would welcome the opportunity to discuss how I can "
        "contribute to your security team. Thank you for your time and consideration."
    )
    return paragraphs


def build_letter_docx(paragraphs, job, profile):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    sec.top_margin = sec.bottom_margin = Mm(20)
    sec.left_margin = sec.right_margin = Mm(22)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(8)
    normal.paragraph_format.line_spacing = 1.1

    def line(text, size=11, bold=False, color=None, center=False, after=8):
        p = doc.add_paragraph()
        if center:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(after)
        r = p.add_run(text)
        r.font.size, r.bold = Pt(size), bold
        if color:
            r.font.color.rgb = RGBColor(*color)

    personal = profile["PERSONAL"]

    # Header (matches resume style)
    line(personal["name"], 18, True, (31, 78, 121), True, 1)
    line(f"{personal['location']} | {phone_line(personal)} | {personal['email']}",
         9.8, center=True, after=0)
    line(f"{display_url(personal['linkedin'])} | {display_url(personal['github'])} | "
         f"{display_url(personal['portfolio'])}", 9.8, center=True, after=14)

    line(datetime.date.today().strftime("%d %B %Y"))
    line(f"{job['hiring_manager']}\n{job['company']}")
    line(f"Dear {job['hiring_manager']},")
    for para in paragraphs:
        line(para)
    line("Sincerely,", after=2)
    line(personal["name"].title())
    return doc
