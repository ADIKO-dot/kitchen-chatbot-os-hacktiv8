"""
Finance Agent — Handles costing, revenue, waste, and briefing requests.
Supports both structured context data AND natural language queries.
"""

from services.finance import calculate_food_cost, calculate_menu_price, daily_revenue_summary
from services.waste import waste_tracker
from utils.llm_factory import call_llm

FINANCE_PROMPT = """You are KitchenOS-AI's finance calculator.
The user is asking about food cost, menu pricing, or financial calculations.
{tone_instruction}

If the user provides numbers (even in shorthand like "5jt" = 5,000,000), calculate and respond clearly.

Formulas you know:
- Food Cost % = (Cost of Goods / Revenue) × 100
- Gross Profit = Revenue - Cost of Goods
- Menu Price = Cost per Portion ÷ (Target Food Cost % ÷ 100)
- Ideal food cost: 28-35%

Rules:
- Show the calculation step by step
- Format numbers with thousand separators
- Give practical advice based on the result
- Respond in the same language as the user"""


async def handle_finance(message: str, context: dict) -> dict:
    msg_lower = message.lower()

    # Waste logging via structured context
    if "waste" in msg_lower and context.get("waste_entry"):
        entry = context["waste_entry"]
        result = waste_tracker.add(**entry)
        return {"message": f"Logged waste: {result.item} — loss Rp {result.loss:,.0f}", "entry": entry}

    # Waste summary
    if "waste" in msg_lower and not context.get("cost_of_goods"):
        summary = waste_tracker.daily_summary()
        return {"message": f"Today's waste: {summary['entries']} entries, total loss Rp {summary['total_loss']:,.0f}", "data": summary}

    # Structured food cost (from API/frontend form)
    if context.get("cost_of_goods") and context.get("revenue"):
        result = calculate_food_cost(context["cost_of_goods"], context["revenue"])
        return {
            "message": f"Food cost: {result.food_cost_pct}% | Gross profit: Rp {result.gross_profit:,.0f}",
            "data": {"food_cost_pct": result.food_cost_pct, "gross_profit": result.gross_profit},
        }

    # Structured menu pricing
    if context.get("cost_per_portion") and context.get("target_food_cost_pct"):
        price = calculate_menu_price(context["cost_per_portion"], context["target_food_cost_pct"])
        return {"message": f"Recommended menu price: Rp {price:,.0f}", "data": {"menu_price": price}}

    # Natural language — use LLM to understand and calculate
    tone_instruction = context.get("tone_instruction", "")
    prompt = FINANCE_PROMPT.format(tone_instruction=tone_instruction)
    history = context.get("history", [])
    response = await call_llm(prompt, message, temperature=0.3, history=history)
    return {"message": response}
