# ============================================================
# docx_edit.py
# Layout-preserving tailoring: edit the user's ORIGINAL .docx
# in place — reorder their real bullets by JD relevance and
# swap the header role title — while leaving every run, style,
# image, table, header/footer and margin exactly as authored.
#
# Nothing is re-typeset here. That is the whole point.
# ============================================================

import io
import re

from docx import Document

import ats
import core
import parser


def _score(text, jd_lower):
    return sum(1 for keyword in ats.auto_keywords(text)
               if core.kw_in(keyword, jd_lower))


def _is_bullet(paragraph):
    style = (paragraph.style.name or "").lower() if paragraph.style else ""
    text = paragraph.text.strip()
    if "bullet" in style:
        return True
    if text[:1] in ("•", "-", "–", "—", "*", "·"):
        return True
    return False


def _find_section_map(doc):
    """Map paragraph index -> current section key (HEADINGS only)."""
    section = None
    result = {}
    for index, paragraph in enumerate(doc.paragraphs):
        key = parser._classify_heading(paragraph.text.strip())
        if key:
            section = key
        result[index] = section
    return result


def _reorder_group(paragraphs, scores, jd_lower, section, changes):
    """Reorder one contiguous run of bullet paragraphs by JD relevance.

    Moves the underlying XML elements; all formatting travels with them.
    """
    scored = sorted(
        zip(paragraphs, scores),
        key=lambda pair: -pair[1],
    )
    original = list(paragraphs)
    if [p for p, _ in scored] == original:
        return 0

    anchor = original[0]._p.getprevious()
    if anchor is None:
        return 0
    for paragraph, _ in reversed(scored):
        anchor.addnext(paragraph._p)

    moved = [
        (new_index, paragraph.text.strip()[:70])
        for new_index, (paragraph, _) in enumerate(scored, start=1)
    ]
    top = moved[0][1] if moved else ""
    changes.append(
        f"{section or 'Section'}: reordered {len(original)} bullet(s) by JD "
        f"relevance — top bullet is now “{top}”"
    )
    return len(original)


def _replace_role_title(doc, old_title, new_title, changes):
    """Swap the header role title, keeping the run's formatting."""
    if not old_title or not new_title or old_title.strip().lower() == \
            new_title.strip().lower():
        return False

    for paragraph in doc.paragraphs[:15]:
        text = paragraph.text
        if old_title.strip().lower() not in text.lower():
            continue
        new_text = re.sub(re.escape(old_title), new_title, text,
                          count=1, flags=re.I)
        runs = paragraph.runs
        if not runs:
            continue
        runs[0].text = new_text
        for run in runs[1:]:
            run.text = ""
        changes.append(f"Header role title: “{old_title}” → “{new_title}”")
        return True
    return False


def tailor_document(docx_bytes, jd_text, old_title=None, new_title=None,
                    max_bytes=15 * 1024 * 1024):
    """Edit the original resume DOCX. Returns (bytes, changes)."""
    if len(docx_bytes) > max_bytes:
        raise ValueError("That DOCX is larger than 15 MB.")

    doc = Document(io.BytesIO(docx_bytes))
    jd_lower = jd_text.lower()
    changes = []

    paragraphs = doc.paragraphs
    section_map = _find_section_map(doc)

    # Group contiguous bullet runs and reorder each by relevance.
    group = []
    group_sections = set()

    def flush():
        if len(group) >= 2:
            scores = [_score(p.text, jd_lower) for p in group]
            _reorder_group(group, scores, jd_lower,
                           "/".join(sorted(group_sections)), changes)
        group.clear()
        group_sections.clear()

    for index, paragraph in enumerate(paragraphs):
        if _is_bullet(paragraph):
            group.append(paragraph)
            group_sections.add(section_map.get(index) or "")
        else:
            flush()
    flush()

    _replace_role_title(doc, old_title, new_title, changes)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue(), changes
