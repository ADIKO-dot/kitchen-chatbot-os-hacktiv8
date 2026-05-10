"""
Kitchen Ops Agent — Handles vision/OCR tasks and document processing.
Registered with the orchestrator as the 'kitchen_ops' handler.
"""

from loguru import logger
from services.vision import extract_text
from services.document_parser import parse_document


async def handle_kitchen_ops(message: str, context: dict) -> dict:
    """
    Process kitchen operations requests.
    If image_bytes are in context, run OCR + structured extraction.
    Otherwise, treat as a text-based kitchen query.
    """
    image_bytes = context.get("image_bytes")

    if image_bytes:
        logger.info(f"[KitchenOps] Processing image: {context.get('filename', 'unknown')}")
        # OCR extraction
        raw_text = await extract_text(image_bytes)
        if not raw_text:
            return {"message": "Could not extract text from the image.", "data": None}

        # Structured parsing
        structured = await parse_document(raw_text)
        return {
            "message": f"Extracted {structured.get('type', 'document')} data from image.",
            "raw_text": raw_text,
            "data": structured,
        }

    # No image — general kitchen ops text query
    return {"message": "Kitchen Ops ready. Upload an image of a receipt, inventory list, or schedule for processing."}
