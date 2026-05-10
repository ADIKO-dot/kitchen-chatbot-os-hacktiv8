"""
LLM Factory — Central function to get an LLM instance.
Tries primary provider (Gemini/Groq) with key rotation, falls back to Ollama.
All agents use this instead of directly instantiating LLMs.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from groq import AsyncGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from loguru import logger

from utils.config import gemini_keys, groq_keys, OLLAMA_BASE_URL, OLLAMA_MODEL, PRIMARY_PROVIDER


async def call_llm(
    system_prompt: str,
    user_message: str,
    temperature: float = 0,
    history: list[dict] | None = None,
) -> str:
    """
    Call LLM with automatic provider rotation and fallback.
    Order: PRIMARY_PROVIDER → secondary → Ollama fallback.
    history: optional list of {"role": "user"|"assistant", "content": str}
    Returns the response text.
    """
    providers = (
        [_call_gemini, _call_groq] if PRIMARY_PROVIDER == "gemini"
        else [_call_groq, _call_gemini]
    )
    providers.append(_call_ollama)

    errors = []
    for provider_fn in providers:
        try:
            result = await provider_fn(system_prompt, user_message, temperature, history)
            if result:
                return result
        except Exception as e:
            errors.append(f"{provider_fn.__name__}: {e}")
            logger.warning(f"[LLMFactory] {provider_fn.__name__} failed: {e}")
            continue

    # Check if the issue is missing/exhausted keys
    from utils.config import gemini_keys, groq_keys
    gemini_active = sum(1 for s in gemini_keys._keys if s.enabled and s.key != "dummy")
    groq_active = sum(1 for s in groq_keys._keys if s.enabled and s.key != "dummy")

    if gemini_active == 0 and groq_active == 0:
        return "⚠️ Tidak ada API key yang aktif. Silakan tambahkan API key di halaman Settings (⚙️) agar chatbot bisa berfungsi."

    return "⚠️ Semua API key sedang kena rate limit. Coba lagi dalam beberapa saat, atau tambahkan API key baru di Settings."


async def _call_gemini(system_prompt: str, user_message: str, temperature: float, history: list[dict] | None = None) -> str:
    """Call Gemini via LangChain."""
    key = await gemini_keys.get_key()
    if key == "dummy":
        raise ValueError("No Gemini keys configured")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=key,
            temperature=temperature,
        )
        messages = [SystemMessage(content=system_prompt)]
        if history:
            for h in history:
                if h["role"] == "user":
                    messages.append(HumanMessage(content=h["content"]))
                else:
                    messages.append(AIMessage(content=h["content"]))
        messages.append(HumanMessage(content=user_message))
        response = await llm.ainvoke(messages)
        await gemini_keys.report_success(key)
        return response.content.strip()
    except Exception as e:
        await gemini_keys.report_failure(key)
        raise


async def _call_groq(system_prompt: str, user_message: str, temperature: float, history: list[dict] | None = None) -> str:
    """Call Groq API directly (fast inference)."""
    key = await groq_keys.get_key()
    if key == "dummy":
        raise ValueError("No Groq keys configured")
    try:
        client = AsyncGroq(api_key=key)
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for h in history:
                messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": user_message})
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=temperature,
        )
        await groq_keys.report_success(key)
        return response.choices[0].message.content.strip()
    except Exception as e:
        await groq_keys.report_failure(key)
        raise


async def _call_ollama(system_prompt: str, user_message: str, temperature: float, history: list[dict] | None = None) -> str:
    """Call Ollama as fallback (local or cloud)."""
    logger.info(f"[LLMFactory] Falling back to Ollama ({OLLAMA_MODEL})")
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=temperature,
    )
    messages = [SystemMessage(content=system_prompt)]
    if history:
        for h in history:
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            else:
                messages.append(AIMessage(content=h["content"]))
    messages.append(HumanMessage(content=user_message))
    response = await llm.ainvoke(messages)
    return response.content.strip()
