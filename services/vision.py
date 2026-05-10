"""
Vision/OCR Service — Image preprocessing with OpenCV and text extraction via pytesseract.
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
from io import BytesIO
from loguru import logger


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """Apply preprocessing to improve OCR accuracy on receipts/handwritten notes."""
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Denoise
    gray = cv2.fastNlMeansDenoising(gray, h=10)
    # Adaptive threshold for varied lighting (receipts, handwritten)
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return binary


async def extract_text(image_bytes: bytes) -> str:
    """Run OCR on image bytes after preprocessing. Returns raw extracted text."""
    logger.info("[VisionService] Preprocessing image for OCR")
    processed = preprocess_image(image_bytes)

    # pytesseract expects PIL Image or numpy array
    text = pytesseract.image_to_string(processed, lang="eng")
    logger.info(f"[VisionService] Extracted {len(text)} chars")
    return text.strip()
