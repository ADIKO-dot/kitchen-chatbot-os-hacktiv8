"""
General Agent — Handles general conversation using LLM with memory and tone.
"""

from utils.llm_factory import call_llm

SYSTEM_PROMPT = """You are KitchenOS-AI, a helpful assistant for kitchen/restaurant operations.
You can help with general questions, cooking advice, restaurant management tips, and more.
Be concise and helpful. Respond in the same language as the user.
{tone_instruction}"""


async def handle_general(message: str, context: dict) -> dict:
    tone_instruction = context.get("tone_instruction", "")
    prompt = SYSTEM_PROMPT.format(tone_instruction=tone_instruction)
    history = context.get("history", [])
    response = await call_llm(prompt, message, temperature=0.7, history=history)
    return {"message": response}
