# pdf_export.py
import os
import shutil
import subprocess


def export_pdf(docx_path):
    """Convert DOCX to PDF. Returns the PDF path, or None if no converter exists."""
    docx_path = os.path.abspath(docx_path)
    pdf_path = os.path.splitext(docx_path)[0] + ".pdf"

    # Option 1: Microsoft Word (Windows/macOS) via docx2pdf
    try:
        from docx2pdf import convert
        convert(docx_path, pdf_path)
        if os.path.exists(pdf_path):
            return pdf_path
    except Exception:
        pass

    # Option 2: LibreOffice (any OS)
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf",
             "--outdir", os.path.dirname(docx_path), docx_path],
            check=True, capture_output=True,
        )
        if os.path.exists(pdf_path):
            return pdf_path

    print("PDF export skipped: install MS Word + 'pip install docx2pdf', or LibreOffice.")
    return None