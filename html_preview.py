# ============================================================
# html_preview.py
# Renders a resume (before or after tailoring) as clean HTML
# with one shared stylesheet, so the two previews are directly
# comparable — same fonts, same margins, same layout.
# Only the content order / role title can differ.
# ============================================================

import html


def _esc(value):
    return html.escape(str(value or ""))


def _contact_lines(profile, role_title):
    personal = profile["PERSONAL"]
    from core import phone_line
    contact = " | ".join(part for part in [role_title, personal.get("location", ""),
                                           phone_line(personal),
                                           personal.get("email", "")] if part)
    links = []
    for key in ("linkedin", "github", "portfolio"):
        url = personal.get(key)
        if url:
            from core import display_url
            links.append(f'<a href="{_esc(url)}">{_esc(display_url(url))}</a>')
    return contact, " | ".join(links)


def render_resume_html(profile, role_title=None, skills=None, certs=None,
                       experience=None, projects=None, label=""):
    """Render one resume variant. Omitted structures fall back to profile order."""
    role_title = role_title or profile["PERSONAL"].get("role_label", "")
    skills = skills or profile.get("SKILLS", {})
    certs = certs or profile.get("CERTIFICATIONS", [])
    experience = experience or profile.get("EXPERIENCE", [])
    projects = projects or profile.get("PROJECTS", [])

    contact, links = _contact_lines(profile, role_title)
    parts = [f'<article class="pv-resume">']

    parts.append(
        f'<header class="pv-header">'
        f'<h1>{_esc(profile["PERSONAL"].get("name", ""))}</h1>'
        f'<p class="pv-contact">{_esc(contact)}</p>'
        f'<p class="pv-links">{links}</p>'
        f'</header>'
    )

    summary = profile.get("SUMMARY_TEMPLATE", "").format(
        role_title=role_title, cert_line=profile.get("CERT_LINE", ""))
    parts.append('<section><h2>Professional Summary</h2>'
                 f'<p>{_esc(summary)}</p></section>')

    parts.append('<section><h2>Professional Experience</h2>')
    for job in experience:
        parts.append(
            '<div class="pv-role"><div class="pv-role-line">'
            f'<span><strong>{_esc(job.get("title", ""))}</strong>'
            + (f' | {_esc(job.get("company", ""))}' if job.get("company") else "")
            + '</span>'
            f'<span class="pv-dates">{_esc(job.get("dates", ""))}</span></div>')
        if job.get("location"):
            parts.append(f'<p class="pv-location">{_esc(job["location"])}</p>')
        parts.append('<ul>')
        for bullet in job.get("bullets", []):
            parts.append(f'<li>{_esc(bullet.get("text", ""))}</li>')
        parts.append('</ul></div>')
    parts.append('</section>')

    if projects:
        parts.append('<section><h2>Security Projects</h2>')
        for project in projects:
            name = project.get("name", "")
            if project.get("url"):
                name = f'<a href="{_esc(project["url"])}">{_esc(name)}</a>'
            parts.append(
                f'<div class="pv-role"><div class="pv-role-line">'
                f'<span><strong>{name}</strong>{_esc(project.get("subtitle", ""))}</span></div>'
                '<ul>'
                + "".join(f'<li>{_esc(b.get("text", ""))}</li>'
                          for b in project.get("bullets", []))
                + '</ul></div>')
        parts.append('</section>')

    parts.append('<section><h2>Core Skills</h2>')
    for category, skill_list in skills.items():
        names = ", ".join(s.get("skill", "") for s in skill_list)
        parts.append(f'<p><strong>{_esc(category)}:</strong> {_esc(names)}</p>')
    parts.append('</section>')

    parts.append('<section><h2>Certifications</h2><ul>')
    for cert in certs:
        text = cert.get("name", "")
        if cert.get("status") == "in_progress":
            text += " — In Progress"
        parts.append(f'<li>{_esc(text)}</li>')
    parts.append('</ul></section>')

    education = profile.get("EDUCATION", {})
    parts.append('<section><h2>Education</h2>')
    if education:
        parts.append(
            f'<div class="pv-role"><div class="pv-role-line">'
            f'<span><strong>{_esc(education.get("degree", ""))}</strong>'
            f' | {_esc(education.get("university", ""))}</span>'
            f'<span class="pv-dates">{_esc(education.get("dates", ""))}</span></div>')
        if education.get("location"):
            parts.append(f'<p class="pv-location">{_esc(education["location"])}</p>')
        if education.get("cgpa"):
            parts.append(f'<p>{_esc(education["cgpa"])}</p>')
    parts.append('</section>')

    achievements = profile.get("ACHIEVEMENTS", [])
    if achievements:
        parts.append('<section><h2>Leadership &amp; Achievements</h2><ul>')
        for achievement in achievements:
            parts.append(f'<li>{_esc(achievement)}</li>')
        parts.append('</ul></section>')

    parts.append('</article>')
    return "".join(parts)


PREVIEW_CSS = """
.pv-wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
@media (max-width: 900px) { .pv-wrap { grid-template-columns: 1fr; } }
.pv-pane { background: #fff; color: #1c2433; border-radius: 12px; overflow: hidden;
           border: 1px solid var(--border); display: flex; flex-direction: column; }
.pv-pane-head { padding: 10px 16px; font-weight: 700; font-size: 0.85rem;
                letter-spacing: 0.6px; text-transform: uppercase; }
.pv-before .pv-pane-head { background: #e8edf6; color: #33415c; }
.pv-after  .pv-pane-head { background: rgba(45,212,191,0.15); color: var(--teal); }
.pv-scroll { max-height: 640px; overflow-y: auto; padding: 22px 26px;
             font-family: Calibri, "Segoe UI", Arial, sans-serif; font-size: 13.5px; }
.pv-resume h1 { text-align: center; color: #1F4E79; font-size: 22px; margin: 0 0 4px; }
.pv-header { text-align: center; border-bottom: 2px solid #1F4E79; padding-bottom: 10px; }
.pv-contact { margin: 2px 0; color: #44506a; font-size: 12px; }
.pv-links { margin: 2px 0; font-size: 12px; }
.pv-links a { color: #0563C1; text-decoration: underline; }
.pv-resume h2 { color: #1F4E79; font-size: 13px; text-transform: uppercase;
               border-bottom: 1px solid #1F4E79; margin: 16px 0 6px; padding-bottom: 2px; }
.pv-role { margin-top: 8px; }
.pv-role-line { display: flex; justify-content: space-between; gap: 12px; }
.pv-dates { font-weight: 700; white-space: nowrap; }
.pv-location { font-style: italic; color: #5a6778; margin: 1px 0; font-size: 12.5px; }
.pv-resume ul { margin: 3px 0 6px; padding-left: 20px; }
.pv-resume li { margin-bottom: 2px; }
.pv-resume section p { margin: 3px 0; }
"""
