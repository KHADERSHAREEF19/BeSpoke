# ============================================================
# parser.py
# Turns an uploaded resume (PDF / DOCX / TXT) into BeSpoke's
# profile structure. Best-effort and format-tolerant: the result
# is shown in the profile editor so you can review it before use.
#
# IMPORTANT: this never writes anything by itself.
# ============================================================

import io
import re

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?"
    r"(linkedin\.com/in/[\w.-]+"
    r"|github\.com/[\w.-]+"
    r"|(?<![\w.@])(?:[a-z0-9-]+\.)+(?:vercel\.app|dev|io|me|com)\b)",
    re.I,
)
LOCATION_RE = re.compile(
    r"\b(Hyderabad,\s*Telangana,\s*India|Dubai,\s*UAE|Abu\s+Dhabi,\s*UAE|"
    r"Sharjah,\s*UAE|Ajman,\s*UAE|Gurugram,\s*India|New\s+Delhi,\s*India|"
    r"Mumbai,\s*India|Bangalore,\s*India|Bengaluru,\s*India|Chennai,\s*India|"
    r"Texas,\s*USA|Chicago,\s*USA|New\s+York,\s*USA|San\s+Francisco,\s*USA)\b",
    re.I,
)
PHONE_RE = re.compile(r"\+\d[\d\s().-]{7,}\d")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/([\w-]+)", re.I)
GITHUB_RE = re.compile(r"github\.com/([\w-]+)", re.I)
DATE_RANGE_RE = re.compile(
    r"(\d{1,2}/\d{4}|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4})"
    r"\s*(?:–|—|-|to|until)\s*"
    r"(\d{1,2}/\d{4}|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}"
    r"|present|current|now|today)",
    re.I,
)
CGPA_RE = re.compile(r"(cgpa|gpa)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*/\s*(\d+)", re.I)
BULLET_CHARS = ("•", "-", "–", "—", "*", "·")

SECTION_ALIASES = {
    "professional summary": "SUMMARY",
    "summary": "SUMMARY",
    "profile summary": "SUMMARY",
    "objective": "SUMMARY",
    "certifications": "CERTS",
    "certification": "CERTS",
    "licenses & certifications": "CERTS",
    "skills": "SKILLS",
    "core skills": "SKILLS",
    "technical skills": "SKILLS",
    "key skills": "SKILLS",
    "competencies": "SKILLS",
    "work experience": "EXPERIENCE",
    "professional experience": "EXPERIENCE",
    "experience": "EXPERIENCE",
    "employment history": "EXPERIENCE",
    "projects": "PROJECTS",
    "academic projects": "PROJECTS",
    "key projects": "PROJECTS",
    "education": "EDUCATION",
    "educational qualifications": "EDUCATION",
    "achievements": "ACHIEVEMENTS",
    "leadership & achievements": "ACHIEVEMENTS",
    "leadership and achievements": "ACHIEVEMENTS",
    "key achievements": "ACHIEVEMENTS",
}


def extract_text(filename, data):
    """Raw text from a .pdf / .docx / .txt upload."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if lower.endswith(".docx"):
        from docx import Document
        doc = Document(io.BytesIO(data))
        parts = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                parts.append("\t".join(cell.text for cell in row.cells))
        return "\n".join(parts)
    return data.decode("utf-8", errors="ignore")


def _lines(text):
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        line = re.sub(r"[ \t]+", " ", line)
        if line:
            out.append(line)
    return out


def _classify_heading(line):
    key = line.lower().strip().rstrip(":")
    key = re.sub(r"\s+", " ", key)
    return SECTION_ALIASES.get(key)


def _split_sections(lines):
    """Return (header_lines, {section_key: [lines]})."""
    headings = []
    for i, line in enumerate(lines):
        if len(line) < 60 and _classify_heading(line):
            headings.append((i, _classify_heading(line)))

    header = lines[:headings[0][0]] if headings else lines
    sections = {}
    for idx, (start, key) in enumerate(headings):
        end = headings[idx + 1][0] if idx + 1 < len(headings) else len(lines)
        sections.setdefault(key, []).extend(lines[start + 1:end])
    return header, sections


def _looks_like_contact_part(part):
    part = part.strip()
    if not part:
        return None
    if EMAIL_RE.search(part):
        return "email"
    if PHONE_RE.search(part):
        return "phone"
    if LINKEDIN_RE.search(part):
        return "linkedin"
    if GITHUB_RE.search(part):
        return "github"
    if URL_RE.search(part):
        return "portfolio"
    if re.fullmatch(r"[\w .,&'-]{3,40}", part) and "," in part:
        return "location"
    return None


def _parse_header(header_lines):
    personal = {"name": "", "role_label": "", "location": "",
                "phone": "", "uae_phone": "", "email": "",
                "linkedin": "", "github": "", "portfolio": ""}
    meta_candidates = []

    blob = " ".join(header_lines)
    email = EMAIL_RE.search(blob)
    if email:
        personal["email"] = email.group(0).rstrip(".,)")

    phones = []
    for match in PHONE_RE.finditer(blob):
        number = re.sub(r"\s+", " ", match.group(0)).strip(" .,()")
        if number not in phones:
            phones.append(number)
    for number in phones:
        if number.startswith("+971"):
            personal["uae_phone"] = number
        elif not personal["phone"]:
            personal["phone"] = number

    linkedin = LINKEDIN_RE.search(blob)
    if linkedin:
        personal["linkedin"] = "https://www.linkedin.com/in/" + linkedin.group(1).strip("/")
    github = GITHUB_RE.search(blob)
    if github:
        personal["github"] = "https://github.com/" + github.group(1).strip("/")
    for url in URL_RE.finditer(blob):
        candidate = url.group(0)
        if "@" in candidate or "linkedin.com" in candidate or "github.com" in candidate:
            continue
        if not candidate.startswith("http"):
            candidate = "https://" + candidate
        personal["portfolio"] = candidate.rstrip(".,)")
        break

    located = LOCATION_RE.search(blob)
    if located:
        personal["location"] = re.sub(r"\s+", " ", located.group(0)).strip()

    # Name = first short, letter-led line; role label = next such line.
    used_lines = set()
    for i, line in enumerate(header_lines):
        if EMAIL_RE.search(line) or URL_RE.search(line) or PHONE_RE.search(line):
            continue
        if personal["location"] and line == personal["location"]:
            continue
        if not personal["name"] and re.fullmatch(r"[A-Za-z .,'-]{3,40}", line) \
                and len(line.split()) <= 5:
            personal["name"] = line.upper() if line.isupper() else line.title()
            used_lines.add(i)
            continue
        if personal["name"] and not personal["role_label"] and line not in used_lines:
            if re.fullmatch(r"[A-Za-z &/(),.'-]{3,45}", line):
                personal["role_label"] = line
                used_lines.add(i)
                break

    # Location: prefer a '|'-separated contact line, then any city-like line.
    for line in header_lines:
        for part in line.split("|"):
            kind = _looks_like_contact_part(part)
            if kind == "location" and not personal["location"]:
                personal["location"] = part.strip()

    if not personal["location"]:
        for line in header_lines:
            if "@" in line or URL_RE.search(line) or PHONE_RE.search(line):
                continue
            part = line.split("|")[0].strip()
            if "," in part and re.fullmatch(r"[A-Za-z .,()'-]{3,45}", part):
                personal["location"] = part
                break

    return personal


def _clean_bullet(line):
    return line.lstrip("".join(BULLET_CHARS)).strip()


def _split_items(text):
    """Split on commas/semicolons that are NOT inside parentheses."""
    items, buf, depth = [], "", 0
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        if char in ",;" and depth == 0:
            if buf.strip():
                items.append(buf.strip())
            buf = ""
        else:
            buf += char
    if buf.strip():
        items.append(buf.strip())
    return items


def _parse_skills(lines):
    skills = {}
    last_category = None
    for line in lines:
        if ":" in line and len(line.split(":", 1)[0]) < 40:
            category, rest = line.split(":", 1)
            items = _split_items(rest)
            if items:
                skills[category.strip()] = [
                    {"skill": item, "level": "production", "keywords": []}
                    for item in items
                ]
                last_category = category.strip()
        elif line and last_category:
            # wrapped continuation of the previous category's list
            items = _split_items(line.rstrip(";"))
            skills[last_category] += [
                {"skill": item, "level": "production", "keywords": []}
                for item in items
            ]
        elif line and not skills:
            items = _split_items(line)
            if len(items) > 1:
                skills["Core Skills"] = [
                    {"skill": item, "level": "production", "keywords": []}
                    for item in items
                ]
                last_category = "Core Skills"
    return skills


def _is_location_line(line):
    if re.search(r"\((?:remote|hybrid|onsite|on-site)\)", line, re.I):
        return True
    if DATE_RANGE_RE.search(line):
        return False
    return bool(re.fullmatch(r"[A-Za-z .,()&'/()-]{3,50}", line)) and "," in line


def _parse_experience(lines):
    """Entries may be ordered title-first or date-first — classify per line."""
    entries = []
    current = None
    mode = None  # None | "meta" | "bullets"

    def flush():
        nonlocal current
        if current and (current["title"] or current["bullets"]):
            entries.append(current)
        current = None

    for line in lines:
        if DATE_RANGE_RE.search(line):
            flush()
            current = {"dates": line, "title": "", "company": "",
                       "location": "", "bullets": [], "_meta": []}
            mode = "meta"
            continue
        if current is None:
            current = {"dates": "", "title": "", "company": "",
                       "location": "", "bullets": [], "_meta": []}
            mode = "meta"

        stripped = _clean_bullet(line)
        is_bullet = line.startswith(BULLET_CHARS)
        if is_bullet:
            current["bullets"].append(stripped)
            mode = "bullets"
            continue
        if mode == "bullets":
            # wrapped continuation of the previous bullet
            if current["bullets"] and len(line) > 25 and not _is_location_line(line):
                current["bullets"][-1] += " " + line
                continue
            flush()
            current = {"dates": "", "title": "", "company": "",
                       "location": "", "bullets": [], "_meta": []}
            mode = "meta"

        remote_only = re.fullmatch(r"\((remote|hybrid|onsite|on-site)\)", line, re.I)
        if remote_only:
            tag = line.strip("() ").strip()
            current["location"] = (current["location"] + f" ({tag})").strip()
            continue
        if _is_location_line(line):
            if not current["location"]:
                current["location"] = line.strip(" |")
            continue
        current["_meta"].append(line)

    flush()

    for entry in entries:
        meta = [m for m in entry.pop("_meta") if m]
        if meta:
            entry["title"] = meta[0]
            if len(meta) > 1:
                entry["company"] = meta[1]
        entry["bullets"] = [
            {"text": b, "keywords": [], "priority": i + 1}
            for i, b in enumerate(entry["bullets"])
        ]
        entry.setdefault("pin", False)
        for b in entry["bullets"]:
            b.pop("pin", None)
    return entries


def _parse_projects(lines):
    projects = []
    current = None
    for line in lines:
        if line.startswith(BULLET_CHARS):
            if current is None:
                current = {"name": "", "url": None, "subtitle": "", "bullets": []}
            current["bullets"].append(_clean_bullet(line))
            continue
        if current and current["bullets"]:
            # a wrapped bullet line (no "Title: subtitle" colon) continues it
            if ":" not in line and (line.endswith((".", ",", ";"))
                                    or len(line) < 25):
                current["bullets"][-1] += " " + line
                continue
            projects.append(current)
            current = None
        if current is None:
            current = {"name": "", "url": None, "subtitle": "", "bullets": []}
        name, _, subtitle = line.partition(":")
        current["name"] = name.strip()
        current["subtitle"] = (":" + subtitle).strip() if subtitle else ""
        url = re.search(r"https?://\S+", line)
        if url:
            current["url"] = url.group(0).rstrip(".,)")
    if current and (current["name"] or current["bullets"]):
        projects.append(current)

    for project in projects:
        project["bullets"] = [{"text": b, "keywords": []} for b in project["bullets"]]
    return [p for p in projects if p["name"] or p["bullets"]]


def _parse_education(lines):
    degree = university = dates = location = cgpa = ""
    for line in lines:
        if not degree and re.search(r"\b(bachelor|master|b\.?e\.?|b\.?tech|m\.?tech|"
                                    r"mba|diploma|doctorate|ph\.?d)\b", line, re.I):
            degree = line
            continue
        if degree and not university and re.search(r"university|college|institute|"
                                                   r"school", line, re.I):
            university = line
            continue
        if not cgpa:
            match = re.search(
                r"(?:cgpa|gpa)\s*[:\-]?\s*(\d+(?:\.\d+)?)(?:\s*/\s*(\d+))?",
                line, re.I)
            if not match:
                match = re.search(
                    r"(\d+(?:\.\d+)?)(?:\s*/\s*\d+)?\s*(?:cgpa|gpa)", line, re.I)
            if match:
                groups = match.groups()
                value = groups[0]
                scale = groups[1] if len(groups) > 1 else None
                cgpa = f"CGPA: {value}" + (f"/{scale}" if scale else "")
                continue
        if not dates and DATE_RANGE_RE.search(line):
            dates = line
            continue
        if not location and re.fullmatch(r"[A-Za-z .,']{3,40}", line):
            location = line
    if not location and "," in university:
        location = university.rsplit(",", 1)[1].strip()
    return {"degree": degree, "university": university, "dates": dates,
            "location": location, "cgpa": cgpa}


def _ensure_keys(profile):
    defaults = {
        "PERSONAL": {},
        "SUMMARY_TEMPLATE": "{role_title} security professional. {cert_line}",
        "CERTS_SHORT": "",
        "CERT_LINE": "",
        "CERTIFICATIONS": [],
        "SKILLS": {},
        "EXPERIENCE": [],
        "PROJECTS": [],
        "EDUCATION": {},
        "ACHIEVEMENTS": [],
        "ACCEPTABLE_ROLE_TITLES": ["SOC Analyst", "Security Operations Analyst",
                                   "Cybersecurity Analyst", "Security Analyst",
                                   "IAM Analyst", "Identity Analyst"],
    }
    for key, value in defaults.items():
        profile.setdefault(key, value)
    return profile


def parse_resume(text):
    """Best-effort structured profile from raw resume text."""
    lines = _lines(text)
    if not lines:
        raise ValueError("No readable text found in that file.")

    header, sections = _split_sections(lines)
    personal = _parse_header(header)

    summary = " ".join(sections.get("SUMMARY", [])).strip()
    if summary:
        if "{cert_line}" not in summary:
            summary = summary.rstrip(".") + ". {cert_line}"

    certs = [{"name": c, "status": "earned", "keywords": []}
             for c in sections.get("CERTS", []) if len(c) > 3]

    education_lines = sections.get("EDUCATION", [])
    education = _parse_education(education_lines)

    achievements = [_clean_bullet(a) for a in sections.get("ACHIEVEMENTS", [])
                    if len(_clean_bullet(a)) > 10]

    profile = {
        "PERSONAL": personal,
        "SUMMARY_TEMPLATE": summary or "{role_title} security professional. {cert_line}",
        "CERTS_SHORT": ", ".join(c["name"] for c in certs[:3]),
        "CERT_LINE": (f"Holds {', '.join(c['name'] for c in certs[:3])} certifications."
                      if certs else ""),
        "CERTIFICATIONS": certs,
        "SKILLS": _parse_skills(sections.get("SKILLS", [])),
        "EXPERIENCE": _parse_experience(sections.get("EXPERIENCE", [])),
        "PROJECTS": _parse_projects(sections.get("PROJECTS", [])),
        "EDUCATION": education,
        "ACHIEVEMENTS": achievements,
    }
    return _ensure_keys(profile)
