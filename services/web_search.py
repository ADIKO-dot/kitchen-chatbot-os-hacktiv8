"""
Web Search Service — DuckDuckGo search for real-time information.
"""

from duckduckgo_search import DDGS
from loguru import logger


async def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search DuckDuckGo and return results.
    Returns: [{"title": str, "url": str, "snippet": str}]
    """
    logger.info(f"[WebSearch] Searching: {query}")
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))

    return [
        {"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")}
        for r in results
    ]
