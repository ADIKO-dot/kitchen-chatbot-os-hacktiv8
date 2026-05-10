"""
Memory Service — Session-based conversation history.
Stores recent messages per session for context-aware responses.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

MAX_HISTORY = 20  # max messages per session


@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class MemoryStore:
    """In-memory conversation store keyed by session_id."""

    def __init__(self):
        self._sessions: dict[str, list[Message]] = defaultdict(list)

    def add(self, session_id: str, role: str, content: str):
        msgs = self._sessions[session_id]
        msgs.append(Message(role=role, content=content))
        # Trim to max
        if len(msgs) > MAX_HISTORY:
            self._sessions[session_id] = msgs[-MAX_HISTORY:]

    def get_history(self, session_id: str) -> list[dict]:
        """Return history as list of dicts for LLM context."""
        return [{"role": m.role, "content": m.content} for m in self._sessions[session_id]]

    def clear(self, session_id: str):
        self._sessions[session_id] = []

    def list_sessions(self) -> list[str]:
        return list(self._sessions.keys())


# Singleton
memory_store = MemoryStore()
