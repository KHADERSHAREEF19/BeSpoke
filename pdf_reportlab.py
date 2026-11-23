# ============================================================
# pdf_reportlab.py
# Renders the tailored resume and cover letter straight to PDF
# with ReportLab — no Microsoft Word or LibreOffice required.
# ============================================================

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

NAVY = HexColor("#1F4E79")
LINK_BLUE = HexColor("#0563C1")
GREY = HexColor("#555555")

PAGE_W, PAGE_H = A4
CONTENT_W = PAGE_W - 2 * 17 * mm


def _styles():
    return {
        "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=17,
                               textColor=NAVY, alignment=TA_CENTER, spaceAfter=1),
        "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=9.2,
                                  textColor=GREY, alignment=TA_CENTER, spaceAfter=0),
        "links": ParagraphStyle("links", fontName="Helvetica", fontSize=9.2,
                                textColor=LINK_BLUE, alignment=TA_CENTER, spaceAfter=2),
        "heading": ParagraphStyle("heading", fontName="Helvetica-Bold", fontSize=11,
                                 textColor=NAVY, spaceBefore=7, spaceAfter=1),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.8,
                               leading=12.4, alignment=TA_JUSTIFY, spaceAfter=2),
        "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=9.8,
                                 leading=12.4, leftIndent=11, bulletIndent=2,
                                 spaceAfter=1.2),
        "role": ParagraphStyle("role", fontName="Helvetica", fontSize=10,
                               leading=12.6, spaceBefore=4, spaceAfter=0),
        "dates": ParagraphStyle("dates", fontName="Helvetica-Bold", fontSize=10,
                                leading=12.6, alignment=2),
        "location": ParagraphStyle("location", fontName="Helvetica-Oblique",
                                   fontSize=9, textColor=GREY, spaceAfter=1),
        "skill": ParagraphStyle("skill", fontName="Helvetica", fontSize=9.8,
                                leading=12.4, spaceAfter=1.2),
    }


def _heading(story, text, styles):
    story.append(Paragraph(text.upper(), styles["heading"]))
    story.append(HRFlowable(width="100%", thickness=0.9, color=NAVY,
                            spaceBefore=0, spaceAfter=3))


def _link(url, text):
    return f'<link href="{url}" color="#0563C1"><u>{text}</u></link>'


def render_resume_pdf(path, role_title, profile, skills_dict, certs, experience, projects):
    styles = _styles()
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        topMargin=13 * mm, bottomMargin=13 * mm,
        leftMargin=17 * mm, rightMargin=17 * mm,
        title=f"{profile['PERSONAL']['name']} — Resume",
    )
    story = []
    personal = profile["PERSONAL"]

    story.append(Paragraph(personal["name"], styles["name"]))

    contact_bits = [role_title, personal["location"]]
    from core import phone_line
    contact_bits.append(phone_line(personal))
    contact_bits.append(_link("mailto:" + personal["email"], personal["email"]))
    story.append(Paragraph(" | ".join(contact_bits), styles["contact"]))

    link_bits = [
        _link(personal["linkedin"], _display(personal["linkedin"])),
        _link(personal["github"], _display(personal["github"])),
        _link(personal["portfolio"], _display(personal["portfolio"])),
    ]
    story.append(Paragraph(" | ".join(link_bits), styles["links"]))

    _heading(story, "Professional Summary", styles)
    story.append(Paragraph(
        profile["SUMMARY_TEMPLATE"].format(role_title=role_title,
                                           cert_line=profile["CERT_LINE"]),
        styles["body"]))

    _heading(story, "Professional Experience", styles)
    for job in experience:
        row = Table(
            [[Paragraph(f"<b>{job['title']}</b> | {job['company']}", styles["role"]),
              Paragraph(job["dates"], styles["dates"])]],
            colWidths=[CONTENT_W - 46 * mm, 46 * mm],
        )
        row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(row)
        if job.get("location"):
            story.append(Paragraph(job["location"], styles["location"]))
        for bullet in job["bullets"]:
            story.append(Paragraph(bullet["text"], styles["bullet"], bulletText="•"))

    _heading(story, "Security Projects", styles)
    for project in projects:
        name = project["name"]
        if project.get("url"):
            name = _link(project["url"], name)
        story.append(Paragraph(
            f"<b>{name}</b>{project['subtitle']}", styles["role"]))
        for bullet in project["bullets"]:
            story.append(Paragraph(bullet["text"], styles["bullet"], bulletText="•"))

    _heading(story, "Core Skills", styles)
    for category, skill_list in skills_dict.items():
        names = ", ".join(skill["skill"] for skill in skill_list)
        story.append(Paragraph(f"<b>{category}:</b> {names}", styles["skill"]))

    _heading(story, "Certifications", styles)
    for cert in certs:
        text = cert["name"]
        if cert.get("status") == "in_progress":
            text += " — In Progress"
        story.append(Paragraph(text, styles["bullet"], bulletText="•"))

    _heading(story, "Education", styles)
    education = profile["EDUCATION"]
    row = Table(
        [[Paragraph(f"<b>{education['degree']}</b> | {education['university']}",
                    styles["role"]),
          Paragraph(education["dates"], styles["dates"])]],
        colWidths=[CONTENT_W - 46 * mm, 46 * mm],
    )
    row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(row)
    if education.get("location"):
        story.append(Paragraph(education["location"], styles["location"]))
    story.append(Paragraph(education["cgpa"], styles["skill"]))

    _heading(story, "Leadership & Achievements", styles)
    for achievement in profile["ACHIEVEMENTS"]:
        story.append(Paragraph(achievement, styles["bullet"], bulletText="•"))

    doc.build(story)


def render_letter_pdf(path, paragraphs, job, profile):
    styles = _styles()
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        topMargin=18 * mm, bottomMargin=18 * mm,
        leftMargin=20 * mm, rightMargin=20 * mm,
        title=f"Cover Letter — {job['company']}",
    )
    story = []
    personal = profile["PERSONAL"]

    story.append(Paragraph(personal["name"], styles["name"]))
    from core import phone_line
    story.append(Paragraph(
        f"{personal['location']} | {phone_line(personal)} | "
        f'{_link("mailto:" + personal["email"], personal["email"])}',
        styles["contact"]))
    story.append(Paragraph(
        f'{_link(personal["linkedin"], _display(personal["linkedin"]))} | '
        f'{_link(personal["github"], _display(personal["github"]))} | '
        f'{_link(personal["portfolio"], _display(personal["portfolio"]))}',
        styles["links"]))
    story.append(Spacer(1, 10))

    import datetime
    story.append(Paragraph(datetime.date.today().strftime("%d %B %Y"), styles["body"]))
    story.append(Paragraph(f"{job['hiring_manager']}<br/>{job['company']}", styles["body"]))
    story.append(Paragraph(f"Dear {job['hiring_manager']},", styles["body"]))
    for para in paragraphs:
        story.append(Paragraph(para, styles["body"]))
    story.append(Paragraph("Sincerely,", styles["body"]))
    story.append(Paragraph(personal["name"].title(), styles["body"]))

    doc.build(story)


def _display(url):
    from core import display_url
    return display_url(url)
