"""
Core Agent Dispatcher — Analyzes user prompts and routes to specialized sub-agents.
Uses the LLM factory for provider-agnostic classification.
"""

from enum import Enum
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from utils.llm_factory import call_llm


class AgentType(str, Enum):
    KITCHEN_OPS = "kitchen_ops"
    FINANCE = "finance"
    CAREER_OPS = "career_ops"
    WEB_SEARCH = "web_search"
    FILE_GEN = "file_gen"
    RAG = "rag"
    RECOMMENDATION = "recommendation"
    GENERAL = "general"


CLASSIFIER_PROMPT = """You are a routing classifier for KitchenOS-AI.
Given the user's message, respond with EXACTLY one of these labels:
kitchen_ops, finance, career_ops, web_search, file_gen, rag, recommendation, general

Rules:
- kitchen_ops: images, OCR, receipts, inventory scanning, staff briefing
- finance: costing, revenue, profit, waste, food cost percentage
- career_ops: CV, resume, cover letter, job application, job description
- web_search: search, find online, market prices, scrape, lookup
- file_gen: generate PDF, create spreadsheet, export report, create menu
- rag: questions about recipes, SOP, food safety, kitchen procedures, knowledge base, how to cook
- recommendation: recommend menu, suggest dish, what should I cook, menu suggestion, pairing
- general: anything else

Respond with the label only, no explanation."""


TONE_PROMPTS = {
    "formal": "Respond in a formal, professional tone. Use proper language and structured responses.",
    "casual": "Respond in a casual, relaxed tone. Use simple language and be conversational.",
    "friendly": "Respond in a warm, friendly tone. Be helpful and approachable.",
}


class Orchestrator:
    """Routes user prompts to the correct sub-agent."""

    def __init__(self):
        self._handlers: dict[AgentType, callable] = {}

    def register(self, agent_type: AgentType, handler: callable):
        self._handlers[agent_type] = handler
        logger.info(f"[Orchestrator] Registered handler for '{agent_type.value}'")

    async def classify(self, user_message: str) -> AgentType:
        """Use LLM to classify the user's intent."""
        label = await call_llm(CLASSIFIER_PROMPT, user_message, temperature=0)
        label = label.strip().lower()
        try:
            return AgentType(label)
        except ValueError:
            return AgentType.GENERAL

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def dispatch(self, user_message: str, context: dict | None = None) -> dict:
        """Classify and route to the appropriate handler."""
        agent_type = await self.classify(user_message)
        logger.info(f"[Orchestrator] Routed to '{agent_type.value}'")

        handler = self._handlers.get(agent_type)
        if not handler:
            return {
                "agent": agent_type.value,
                "response": f"Agent '{agent_type.value}' is not yet implemented.",
                "status": "not_implemented",
            }

        # Inject tone into context
        ctx = context or {}
        tone = ctx.get("tone", "friendly")
        ctx["tone_instruction"] = TONE_PROMPTS.get(tone, TONE_PROMPTS["friendly"])

        result = await handler(user_message, ctx)
        return {"agent": agent_type.value, "response": result, "status": "ok"}


# Singleton instance
orchestrator = Orchestrator()
