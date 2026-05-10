"""
Web Scraper Service — Async Playwright-based scraper with basic anti-bot bypass.
"""

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from loguru import logger


async def scrape_page(url: str, selector: str | None = None) -> dict:
    """
    Scrape a web page using Playwright (headless Chromium).
    Bypasses basic anti-bot with realistic headers and JS rendering.

    url: target URL
    selector: optional CSS selector to extract specific content
    Returns: {"url": str, "title": str, "content": str}
    """
    logger.info(f"[Scraper] Scraping: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()

        # Block unnecessary resources for speed
        await page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", lambda route: route.abort())

        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        # Wait for dynamic content
        await page.wait_for_timeout(2000)

        html = await page.content()
        title = await page.title()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # Remove script/style noise
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    if selector:
        elements = soup.select(selector)
        content = "\n".join(el.get_text(strip=True, separator=" ") for el in elements)
    else:
        content = soup.get_text(strip=True, separator="\n")

    # Trim excessive whitespace
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    content = "\n".join(lines[:200])  # Cap at 200 lines

    logger.info(f"[Scraper] Extracted {len(content)} chars from {url}")
    return {"url": url, "title": title, "content": content}
