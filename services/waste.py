"""
Waste Management Tracker — Logs food waste and calculates financial loss.
"""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class WasteEntry:
    item: str
    qty: float
    unit: str
    cost_per_unit: float
    reason: str  # e.g. "expired", "overproduction", "spoiled", "dropped"
    date: str = field(default_factory=lambda: date.today().isoformat())

    @property
    def loss(self) -> float:
        return round(self.qty * self.cost_per_unit, 2)


class WasteTracker:
    """In-memory waste log. Tracks entries and computes loss summaries."""

    def __init__(self):
        self._log: list[WasteEntry] = []

    def add(self, item: str, qty: float, unit: str, cost_per_unit: float, reason: str) -> WasteEntry:
        entry = WasteEntry(item=item, qty=qty, unit=unit, cost_per_unit=cost_per_unit, reason=reason)
        self._log.append(entry)
        return entry

    def daily_summary(self, target_date: str | None = None) -> dict:
        """Summarize waste for a given date (defaults to today)."""
        d = target_date or date.today().isoformat()
        entries = [e for e in self._log if e.date == d]
        total_loss = sum(e.loss for e in entries)

        by_reason = {}
        for e in entries:
            by_reason[e.reason] = by_reason.get(e.reason, 0) + e.loss

        return {
            "date": d,
            "entries": len(entries),
            "total_loss": round(total_loss, 2),
            "by_reason": by_reason,
        }

    def weekly_summary(self) -> dict:
        """Aggregate loss across all logged entries."""
        total_loss = sum(e.loss for e in self._log)
        by_item = {}
        for e in self._log:
            by_item[e.item] = by_item.get(e.item, 0) + e.loss

        # Top offenders
        top_items = sorted(by_item.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_entries": len(self._log),
            "total_loss": round(total_loss, 2),
            "top_waste_items": [{"item": k, "loss": round(v, 2)} for k, v in top_items],
        }


# Singleton instance
waste_tracker = WasteTracker()
