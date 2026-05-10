"""
Web Search Agent — Handles search queries and page scraping requests.
"""

from services.web_search import search_web
from services.scraper import scrape_page


async def handle_web_search(message: str, context: dict) -> dict:
    """
    Route web search/scrape requests.
    If a URL is provided in context, scrape it. Otherwise, search DuckDuckGo.
    """
    # Direct scrape if URL provided
    url = context.get("url")
    if url:
        result = await scrape_page(url, selector=context.get("selector"))
        return {"message": f"Scraped: {result['title']}", "data": result}

    # Otherwise, perform a web search
    max_results = context.get("max_results", 5)
    results = await search_web(message, max_results=max_results)
    return {
        "message": f"Found {len(results)} results for: {message}",
        "data": results,
    }
