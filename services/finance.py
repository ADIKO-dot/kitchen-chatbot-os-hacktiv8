"""
Financial Calculations Service — Food cost %, gross profit, and revenue tracking.
"""

from dataclasses import dataclass


@dataclass
class CostingResult:
    food_cost_pct: float
    gross_profit: float
    revenue: float
    cost_of_goods: float


def calculate_food_cost(cost_of_goods: float, revenue: float) -> CostingResult:
    """
    Calculate food cost percentage and gross profit.
    Food Cost % = (Cost of Goods / Revenue) * 100
    Gross Profit = Revenue - Cost of Goods
    """
    if revenue <= 0:
        raise ValueError("Revenue must be greater than zero")

    food_cost_pct = (cost_of_goods / revenue) * 100
    gross_profit = revenue - cost_of_goods

    return CostingResult(
        food_cost_pct=round(food_cost_pct, 2),
        gross_profit=round(gross_profit, 2),
        revenue=round(revenue, 2),
        cost_of_goods=round(cost_of_goods, 2),
    )


def calculate_menu_price(cost_per_portion: float, target_food_cost_pct: float) -> float:
    """Calculate the selling price to achieve a target food cost %."""
    if target_food_cost_pct <= 0 or target_food_cost_pct >= 100:
        raise ValueError("Target food cost % must be between 0 and 100")
    return round(cost_per_portion / (target_food_cost_pct / 100), 2)


def daily_revenue_summary(transactions: list[dict]) -> dict:
    """
    Summarize daily revenue from a list of transactions.
    Each transaction: {"item": str, "qty": int, "price": float, "cost": float}
    """
    total_revenue = sum(t["qty"] * t["price"] for t in transactions)
    total_cogs = sum(t["qty"] * t["cost"] for t in transactions)
    result = calculate_food_cost(total_cogs, total_revenue) if total_revenue > 0 else None

    return {
        "total_revenue": round(total_revenue, 2),
        "total_cogs": round(total_cogs, 2),
        "gross_profit": round(total_revenue - total_cogs, 2),
        "food_cost_pct": result.food_cost_pct if result else 0,
        "transaction_count": len(transactions),
    }
