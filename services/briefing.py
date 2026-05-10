"""
Staff Briefing Generator — LLM prompt template for pre-service briefings.
"""

from utils.llm_factory import call_llm

BRIEFING_TEMPLATE = """You are a Head Chef / Restaurant Manager generating a Pre-Service Staff Briefing.
Given the following operational data, produce a clear, structured briefing that staff can read in 2 minutes.

FORMAT:
## Pre-Service Briefing — {date}

### Reservations & Covers
(Summarize total covers, peak times)

### VIP Guests
(List VIPs with preferences/allergies if known)

### 86'd Items (Out of Stock)
(List unavailable items and suggested alternatives)

### Specials
(Today's specials if provided)

### Key Reminders
(Any operational notes, events, or focus areas)

Keep it concise, professional, and actionable."""


async def generate_briefing(data: dict) -> str:
    """Generate a staff briefing from operational data."""
    context_parts = [f"Date: {data.get('date', 'Today')}"]

    reservations = data.get("reservations", [])
    total_covers = sum(r.get("covers", 0) for r in reservations)
    context_parts.append(f"Total Reservations: {len(reservations)} ({total_covers} covers)")
    for r in reservations:
        context_parts.append(f"  - {r.get('time', '?')} | {r.get('name', 'Guest')} x{r.get('covers', 1)} {r.get('notes', '')}")

    vips = data.get("vips", [])
    if vips:
        context_parts.append(f"\nVIPs: {len(vips)}")
        for v in vips:
            context_parts.append(f"  - {v.get('name', '?')}: {v.get('preferences', 'No notes')}")

    eighty_sixed = data.get("eighty_sixed", [])
    if eighty_sixed:
        context_parts.append(f"\n86'd Items: {', '.join(eighty_sixed)}")

    specials = data.get("specials", [])
    if specials:
        context_parts.append(f"\nSpecials: {', '.join(specials)}")

    notes = data.get("notes", "")
    if notes:
        context_parts.append(f"\nAdditional Notes: {notes}")

    context_block = "\n".join(context_parts)
    return await call_llm(
        BRIEFING_TEMPLATE.format(date=data.get("date", "Today")),
        context_block,
        temperature=0.3,
    )
