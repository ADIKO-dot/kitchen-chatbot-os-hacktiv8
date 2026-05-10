"""
RAG Agent — Retrieval-Augmented Generation for kitchen knowledge.
Searches the vector store for relevant context, then generates an answer.
"""

from utils.llm_factory import call_llm
from services.rag import search

RAG_SYSTEM_PROMPT = """You are KitchenOS-AI, a kitchen knowledge expert.
Answer the user's question using ONLY the provided context from the knowledge base.
If the context doesn't contain enough information, say so and provide general guidance.
{tone_instruction}

--- KNOWLEDGE BASE CONTEXT ---
{context}
--- END CONTEXT ---

Rules:
- Cite which source/document you used when possible
- Be accurate and practical
- Respond in the same language as the user"""


async def handle_rag(message: str, context: dict) -> dict:
    """Search knowledge base and generate answer with retrieved context."""
    # Retrieve relevant documents
    results = search(message, n_results=3)

    if not results:
        return {
            "message": "No relevant documents found in the knowledge base. "
                       "Try adding documents first via /rag/add endpoint.",
            "sources": [],
        }

    # Build context string from retrieved docs
    rag_context = "\n\n".join(
        f"[{r['id']}] ({r['metadata'].get('source', 'unknown')}): {r['text']}"
        for r in results
    )

    tone_instruction = context.get("tone_instruction", "")
    prompt = RAG_SYSTEM_PROMPT.format(context=rag_context, tone_instruction=tone_instruction)
    history = context.get("history", [])

    response = await call_llm(prompt, message, temperature=0.3, history=history)

    return {
        "message": response,
        "sources": [{"id": r["id"], "distance": r["distance"]} for r in results],
    }
