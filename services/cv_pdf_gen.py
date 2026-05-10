"""
CV PDF Generator — Creates a professionally formatted CV PDF from structured data.
"""

import os
from datetime import date
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from loguru import logger

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "generated")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("Name", fontSize=18, fontName="Helvetica-Bold", spaceAfter=2*mm))
    styles.add(ParagraphStyle("Title", fontSize=12, textColor=colors.HexColor("#555555"), spaceAfter=4*mm))
    styles.add(ParagraphStyle("SectionHead", fontSize=11, fontName="Helvetica-Bold", textColor=colors.HexColor("#2F5496"), spaceBefore=5*mm, spaceAfter=2*mm))
    styles.add(ParagraphStyle("Bullet", fontSize=10, leftIndent=10*mm, bulletIndent=5*mm, spaceAfter=1*mm))
    styles.add(ParagraphStyle("Body", fontSize=10, spaceAfter=2*mm))
    styles.add(ParagraphStyle("Small", fontSize=9, textColor=colors.HexColor("#666666")))
    return styles


async def generate_cv_pdf(cv_data: dict) -> str:
    """Generate a formatted CV PDF from structured CV data."""
    name = cv_data.get("name", "Candidate")
    filename = f"cv_{name.replace(' ', '_').lower()}_{date.today().isoformat()}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=15*mm, bottomMargin=15*mm, leftMargin=18*mm, rightMargin=18*mm)
    styles = _build_styles()
    elements = []

    # Header
    elements.append(Paragraph(name, styles["Name"]))
    elements.append(Paragraph(cv_data.get("title", ""), styles["Title"]))

    contact = cv_data.get("contact", {})
    contact_line = " | ".join(v for v in contact.values() if v)
    if contact_line:
        elements.append(Paragraph(contact_line, styles["Small"]))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#2F5496"), spaceAfter=4*mm))

    # Summary
    if cv_data.get("summary"):
        elements.append(Paragraph("<b>Professional Summary</b>", styles["SectionHead"]))
        elements.append(Paragraph(cv_data["summary"], styles["Body"]))

    # Experience
    experience = cv_data.get("experience", [])
    if experience:
        elements.append(Paragraph("<b>Experience</b>", styles["SectionHead"]))
        for exp in experience:
            elements.append(Paragraph(f"<b>{exp.get('role', '')}</b> — {exp.get('company', '')}", styles["Body"]))
            elements.append(Paragraph(exp.get("period", ""), styles["Small"]))
            for bullet in exp.get("bullets", []):
                elements.append(Paragraph(f"• {bullet}", styles["Bullet"]))
            elements.append(Spacer(1, 2*mm))

    # Education
    education = cv_data.get("education", [])
    if education:
        elements.append(Paragraph("<b>Education</b>", styles["SectionHead"]))
        for edu in education:
            elements.append(Paragraph(f"<b>{edu.get('degree', '')}</b> — {edu.get('institution', '')} ({edu.get('year', '')})", styles["Body"]))

    # Skills
    skills = cv_data.get("skills", [])
    if skills:
        elements.append(Paragraph("<b>Skills</b>", styles["SectionHead"]))
        elements.append(Paragraph(", ".join(skills), styles["Body"]))

    # Certifications
    certs = cv_data.get("certifications", [])
    if certs:
        elements.append(Paragraph("<b>Certifications</b>", styles["SectionHead"]))
        for cert in certs:
            elements.append(Paragraph(f"• {cert}", styles["Bullet"]))

    doc.build(elements)
    logger.info(f"[CVGen] Created CV PDF: {filepath}")
    return filepath


async def generate_cover_letter_pdf(cover_letter: str, name: str = "Candidate") -> str:
    """Generate a cover letter PDF."""
    filename = f"cover_letter_{name.replace(' ', '_').lower()}_{date.today().isoformat()}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=25*mm, bottomMargin=25*mm, leftMargin=25*mm, rightMargin=25*mm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<b>{name}</b>", styles["Title"]))
    elements.append(Paragraph(date.today().strftime("%B %d, %Y"), styles["Normal"]))
    elements.append(Spacer(1, 10*mm))

    for paragraph in cover_letter.split("\n\n"):
        if paragraph.strip():
            elements.append(Paragraph(paragraph.strip(), styles["Normal"]))
            elements.append(Spacer(1, 4*mm))

    doc.build(elements)
    logger.info(f"[CVGen] Created cover letter PDF: {filepath}")
    return filepath
