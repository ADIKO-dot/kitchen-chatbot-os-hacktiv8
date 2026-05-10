"""
KitchenOS-AI Telegram Bot — Text and image interface to the backend API.

Run: python telegram_bot.py
Requires: TELEGRAM_BOT_TOKEN in .env
"""

import os
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from loguru import logger

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍳 *KitchenOS-AI* ready!\n\n"
        "Send me:\n"
        "• Text messages for any query\n"
        "• Photos of receipts/inventory for OCR\n"
        "• /help for commands",
        parse_mode="Markdown",
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Commands:*\n"
        "/start — Initialize bot\n"
        "/help — Show this message\n\n"
        "*Just send:*\n"
        "• Text → routed to the right agent\n"
        "• Photo → OCR + data extraction\n"
        "• Photo + caption → specific instruction on the image",
        parse_mode="Markdown",
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward text messages to the backend /chat endpoint."""
    msg = update.message.text
    await update.message.chat.send_action("typing")

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(f"{API_BASE}/chat", json={"message": msg})

    if resp.status_code == 200:
        data = resp.json()
        response_text = data.get("response", {})
        if isinstance(response_text, dict):
            response_text = response_text.get("message", str(response_text))
        try:
            await update.message.reply_text(f"🤖 [{data.get('agent', '?')}]\n\n{response_text}", parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(f"🤖 [{data.get('agent', '?')}]\n\n{response_text}")
    else:
        await update.message.reply_text("❌ Error communicating with backend.")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download photo and send to /chat/image endpoint."""
    await update.message.chat.send_action("typing")

    photo = update.message.photo[-1]  # highest resolution
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()

    caption = update.message.caption or ""

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{API_BASE}/chat/image",
            params={"message": caption},
            files={"file": ("photo.jpg", bytes(image_bytes), "image/jpeg")},
        )

    if resp.status_code == 200:
        data = resp.json()
        response_text = data.get("response", {})
        if isinstance(response_text, dict):
            msg_text = response_text.get("message", "")
            extracted = response_text.get("data", "")
            reply = f"🤖 [{data.get('agent', '?')}]\n\n{msg_text}"
            if extracted:
                reply += f"\n\n📋 Data:\n```\n{str(extracted)[:3000]}\n```"
            await update.message.reply_text(reply, parse_mode="Markdown")
        else:
            await update.message.reply_text(f"🤖 {response_text}")
    else:
        await update.message.reply_text("❌ Error processing image.")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document uploads (PDFs, spreadsheets, etc.)."""
    await update.message.chat.send_action("typing")

    doc = update.message.document
    file = await doc.get_file()
    file_bytes = await file.download_as_bytearray()

    caption = update.message.caption or "Analyze this document"

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{API_BASE}/chat/image",
            params={"message": caption},
            files={"file": (doc.file_name, bytes(file_bytes), doc.mime_type or "application/octet-stream")},
        )

    if resp.status_code == 200:
        data = resp.json()
        response_text = data.get("response", {})
        if isinstance(response_text, dict):
            response_text = response_text.get("message", str(response_text))
        await update.message.reply_text(f"🤖 {response_text}")
    else:
        await update.message.reply_text("❌ Error processing document.")


def main():
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set in .env")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("[TelegramBot] Starting polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
