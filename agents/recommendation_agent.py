"""
Recommendation Agent — Suggests menu items based on food cost, waste data, and preferences.
"""

from utils.llm_factory import call_llm
from services.rag import search
from services.waste import waste_tracker

RECOMMENDATION_PROMPT = """You are KitchenOS-AI's menu recommendation engine.
Based on the user's request, available recipes, and waste/cost data, provide smart recommendations.
{tone_instruction}

--- AVAILABLE RECIPES & KNOWLEDGE ---
{recipes}
--- END RECIPES ---

--- WASTE DATA (items to avoid over-ordering) ---
{waste_info}
--- END WASTE ---

Rules:
- Recommend dishes that minimize waste (use ingredients that are commonly wasted)
- Consider food cost targets (ideal: 28-35%)
- Suggest pairings and upsell opportunities
- Be practical and specific
- Respond in the same language as the user"""


async def handle_recommendation(message: str, context: dict) -> dict:
    """Generate menu recommendations using RAG + waste data."""
    # Get relevant recipes from knowledge base
    results = search(message, n_results=5)
    recipes = "\n\n".join(r["text"] for r in results) if results else "No recipes in knowledge base yet."

    # Get waste summary for context
    waste_summary = waste_tracker.daily_summary()
    waste_info = f"Today's waste: {waste_summary['total_loss']} loss, {waste_summary['entries']} entries."
    if waste_summary.get("by_reason"):
        waste_info += f" Reasons: {waste_summary['by_reason']}"

    tone_instruction = context.get("tone_instruction", "")
    prompt = RECOMMENDATION_PROMPT.format(
        recipes=recipes, waste_info=waste_info, tone_instruction=tone_instruction
    )
    history = context.get("history", [])

    response = await call_llm(prompt, message, temperature=0.7, history=history)

    return {
        "message": response,
        "sources": [r["id"] for r in results] if results else [],
        "waste_context": waste_summary,
    }
