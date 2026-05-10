"""
Document Parser — Converts raw OCR text into structured JSON using LLM.
"""

import json
from loguru import logger
from utils.llm_factory import call_llm

PARSER_PROMPT = """You are a document data extractor for a kitchen/restaurant operation.
Given raw OCR text from a scanned document, extract structured data as JSON.

Detect the document type and respond with the appropriate schema:

For RECEIPTS/INVOICES:
{"type": "receipt", "vendor": "...", "date": "...", "items": [{"name": "...", "qty": ..., "unit": "...", "price": ...}], "total": ...}

For INVENTORY LISTS:
{"type": "inventory", "items": [{"name": "...", "qty": ..., "unit": "..."}]}

For SCHEDULES:
{"type": "schedule", "entries": [{"staff": "...", "date": "...", "shift": "..."}]}

If the text is unclear, do your best to extract what's available. Always return valid JSON only."""


async def parse_document(ocr_text: str) -> dict:
    """Send OCR text to LLM for structured extraction."""
    try:
        text = await call_llm(PARSER_PROMPT, f"OCR Text:\n{ocr_text}", temperature=0)
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"[DocParser] Failed to parse LLM response as JSON: {e}")
        return {"type": "unknown", "raw_text": ocr_text, "error": str(e)}
