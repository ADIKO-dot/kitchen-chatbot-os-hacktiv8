"""
PDF Generation Service — Creates invoices, menus, and reports using ReportLab.
"""

import os
from datetime import date
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from loguru import logger

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "generated")
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def generate_invoice_pdf(invoice_data: dict) -> str:
    """
    Generate a professional invoice PDF.
    invoice_data: {
        "invoice_no": str, "date": str, "client": str,
        "items": [{"description": str, "qty": int, "unit_price": float}],
        "notes": str (optional)
    }
    """
    filename = f"invoice_{invoice_data.get('invoice_no', 'draft')}_{date.today().isoformat()}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    elements.append(Paragraph("<b>KitchenOS-AI</b>", styles["Title"]))
    elements.append(Paragraph(f"Invoice #{invoice_data.get('invoice_no', 'N/A')}", styles["Heading2"]))
    elements.append(Paragraph(f"Date: {invoice_data.get('date', date.today().isoformat())}", styles["Normal"]))
    elements.append(Paragraph(f"Client: {invoice_data.get('client', 'N/A')}", styles["Normal"]))
    elements.append(Spacer(1, 10*mm))

    # Items table
    items = invoice_data.get("items", [])
    table_data = [["#", "Description", "Qty", "Unit Price", "Total"]]
    grand_total = 0
    for i, item in enumerate(items, 1):
        total = item["qty"] * item["unit_price"]
        grand_total += total
        table_data.append([i, item["description"], item["qty"], f"${item['unit_price']:.2f}", f"${total:.2f}"])
    table_data.append(["", "", "", "TOTAL", f"${grand_total:.2f}"])

    table = Table(table_data, colWidths=[15*mm, 80*mm, 20*mm, 30*mm, 30*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F5496")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(table)

    # Notes
    if invoice_data.get("notes"):
        elements.append(Spacer(1, 10*mm))
        elements.append(Paragraph(f"<b>Notes:</b> {invoice_data['notes']}", styles["Normal"]))

    doc.build(elements)
    logger.info(f"[PDFGen] Created invoice: {filepath}")
    return filepath


async def generate_menu_pdf(menu_data: dict) -> str:
    """
    Generate a formatted menu PDF.
    menu_data: {
        "restaurant": str, "sections": [{"title": str, "items": [{"name": str, "description": str, "price": float}]}]
    }
    """
    filename = f"menu_{date.today().isoformat()}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("MenuTitle", parent=styles["Title"], fontSize=24, spaceAfter=10*mm))
    styles.add(ParagraphStyle("MenuItem", parent=styles["Normal"], fontSize=11, leftIndent=10*mm))
    elements = []

    elements.append(Paragraph(menu_data.get("restaurant", "Menu"), styles["MenuTitle"]))

    for section in menu_data.get("sections", []):
        elements.append(Paragraph(section["title"], styles["Heading2"]))
        elements.append(Spacer(1, 3*mm))
        for item in section.get("items", []):
            line = f"<b>{item['name']}</b> — ${item['price']:.2f}<br/><i>{item.get('description', '')}</i>"
            elements.append(Paragraph(line, styles["MenuItem"]))
            elements.append(Spacer(1, 2*mm))
        elements.append(Spacer(1, 5*mm))

    doc.build(elements)
    logger.info(f"[PDFGen] Created menu: {filepath}")
    return filepath
