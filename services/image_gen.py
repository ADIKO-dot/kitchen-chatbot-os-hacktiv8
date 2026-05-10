"""
Image Generation Service — Menu photo mockups via Gemini.
"""

import os
from datetime import date
from loguru import logger
from google import genai

from utils.config import gemini_keys

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "generated")
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def generate_menu_image(description: str, style: str = "professional food photography") -> str:
    """
    Generate a detailed photography brief using Gemini.
    Falls back to saving the prompt as a text file.
    """
    prompt = (
        f"{style}, {description}, "
        "beautifully plated on a white ceramic plate, "
        "soft natural lighting, shallow depth of field, restaurant quality"
    )

    key = await gemini_keys.get_key()
    if key == "dummy":
        return await _fallback_text(description, prompt)

    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Create a very detailed visual description for a food photographer to recreate this dish: {prompt}",
        )
        await gemini_keys.report_success(key)

        filename = f"menu_brief_{date.today().isoformat()}_{abs(hash(description)) % 10000:04d}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w") as f:
            f.write(f"DISH: {description}\n\nPHOTOGRAPHY BRIEF:\n{response.text}")

        logger.info(f"[ImageGen] Created photography brief: {filepath}")
        return filepath

    except Exception as e:
        await gemini_keys.report_failure(key)
        logger.warning(f"[ImageGen] Gemini failed: {e}, using fallback")
        return await _fallback_text(description, prompt)


async def _fallback_text(description: str, prompt: str) -> str:
    filename = f"menu_prompt_{date.today().isoformat()}_{abs(hash(description)) % 10000:04d}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w") as f:
        f.write(f"IMAGE GENERATION PROMPT:\n{prompt}\n\nUse this prompt in any image generator.")
    return filepath
