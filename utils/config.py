"""
Configuration — loads environment variables and initializes APIKeyManagers
for Gemini, Groq, and Ollama.
"""

import os
from dotenv import load_dotenv
from utils.api_key_manager import APIKeyManager

load_dotenv()


def _parse_keys(env_var: str) -> list[str]:
    """Parse comma-separated API keys from an env variable."""
    raw = os.getenv(env_var, "")
    return [k.strip() for k in raw.split(",") if k.strip()]


# --- Provider Key Managers ---
gemini_keys = APIKeyManager(provider="gemini", keys=_parse_keys("GEMINI_API_KEYS") or ["dummy"])
groq_keys = APIKeyManager(provider="groq", keys=_parse_keys("GROQ_API_KEYS") or ["dummy"])

# --- Ollama config ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# --- Primary provider preference ---
PRIMARY_PROVIDER = os.getenv("PRIMARY_PROVIDER", "gemini")  # "gemini" or "groq"
