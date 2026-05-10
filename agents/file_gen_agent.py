"""
File Generation Agent — Handles Excel, PDF, and image generation requests.
"""

from services.excel_gen import generate_inventory_excel, generate_schedule_excel
from services.pdf_gen import generate_invoice_pdf, generate_menu_pdf
from services.image_gen import generate_menu_image


async def handle_file_gen(message: str, context: dict) -> dict:
    """Route file generation requests based on context data."""
    msg_lower = message.lower()

    # Excel: inventory
    if context.get("inventory_items"):
        path = await generate_inventory_excel(context["inventory_items"])
        return {"message": "Inventory spreadsheet generated.", "file": path}

    # Excel: schedule
    if context.get("schedule_entries"):
        path = await generate_schedule_excel(context["schedule_entries"])
        return {"message": "Schedule spreadsheet generated.", "file": path}

    # PDF: invoice
    if context.get("invoice_data"):
        path = await generate_invoice_pdf(context["invoice_data"])
        return {"message": "Invoice PDF generated.", "file": path}

    # PDF: menu
    if context.get("menu_data"):
        path = await generate_menu_pdf(context["menu_data"])
        return {"message": "Menu PDF generated.", "file": path}

    # Image: menu photo
    if "photo" in msg_lower or "image" in msg_lower or context.get("dish_description"):
        desc = context.get("dish_description", message)
        path = await generate_menu_image(desc)
        return {"message": "Menu photo generated.", "file": path}

    return {
        "message": "File Gen agent ready. Provide context with inventory_items, "
                   "schedule_entries, invoice_data, menu_data, or dish_description."
    }
