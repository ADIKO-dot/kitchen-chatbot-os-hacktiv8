"""
APIKeyManager — Round-robin key rotation with cooldown and enable/disable per key.
"""

import asyncio
import time
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class _KeyState:
    key: str
    cooldown_until: float = 0.0
    failures: int = 0
    enabled: bool = True


class APIKeyManager:
    COOLDOWN_SECONDS = 60

    def __init__(self, provider: str, keys: list[str], cooldown: int = 60):
        if not keys:
            raise ValueError(f"No API keys provided for provider '{provider}'")
        self.provider = provider
        self.COOLDOWN_SECONDS = cooldown
        self._keys: list[_KeyState] = [_KeyState(key=k) for k in keys]
        self._index = 0
        self._lock = asyncio.Lock()
        logger.info(f"[APIKeyManager] Initialized '{provider}' with {len(keys)} key(s)")

    async def get_key(self) -> str:
        """Return next available enabled key, skipping cooldown and disabled keys."""
        async with self._lock:
            now = time.time()
            attempts = len(self._keys)

            for _ in range(attempts):
                state = self._keys[self._index]
                self._index = (self._index + 1) % len(self._keys)

                if state.enabled and state.cooldown_until <= now:
                    return state.key

            # All enabled keys on cooldown — wait for soonest
            enabled = [s for s in self._keys if s.enabled]
            if not enabled:
                return "dummy"
            soonest = min(enabled, key=lambda s: s.cooldown_until)
            wait = max(0, soonest.cooldown_until - now)

        if wait > 0:
            await asyncio.sleep(wait)
        return soonest.key

    async def report_failure(self, key: str) -> None:
        async with self._lock:
            for state in self._keys:
                if state.key == key:
                    state.failures += 1
                    state.cooldown_until = time.time() + self.COOLDOWN_SECONDS
                    logger.warning(f"[APIKeyManager] '{self.provider}' key ...{key[-4:]} on cooldown for {self.COOLDOWN_SECONDS}s (total failures: {state.failures})")
                    return

    async def report_success(self, key: str) -> None:
        async with self._lock:
            for state in self._keys:
                if state.key == key:
                    state.failures = 0
                    return

    def add_key(self, key: str) -> None:
        """Add a new key. Removes dummy placeholder."""
        self._keys = [s for s in self._keys if s.key != "dummy"]
        if not any(s.key == key for s in self._keys):
            self._keys.append(_KeyState(key=key))
            logger.info(f"[APIKeyManager] Added key to '{self.provider}' (total: {len(self._keys)})")

    def remove_key(self, key_index: int) -> bool:
        """Remove key by index."""
        if 0 <= key_index < len(self._keys):
            removed = self._keys.pop(key_index)
            logger.info(f"[APIKeyManager] Removed key ...{removed.key[-4:]} from '{self.provider}'")
            if not self._keys:
                self._keys.append(_KeyState(key="dummy", enabled=False))
            return True
        return False

    def toggle_key(self, key_index: int) -> bool | None:
        """Toggle enabled/disabled. Returns new state or None if invalid."""
        if 0 <= key_index < len(self._keys):
            self._keys[key_index].enabled = not self._keys[key_index].enabled
            return self._keys[key_index].enabled
        return None

    def list_keys(self) -> list[dict]:
        """List all keys with masked values."""
        result = []
        for i, s in enumerate(self._keys):
            if s.key == "dummy":
                continue
            masked = s.key[:4] + "●" * (len(s.key) - 8) + s.key[-4:] if len(s.key) > 8 else "●" * len(s.key)
            result.append({
                "index": i,
                "masked": masked,
                "enabled": s.enabled,
                "failures": s.failures,
            })
        return result

    @property
    def available_keys(self) -> int:
        now = time.time()
        return sum(1 for s in self._keys if s.enabled and s.cooldown_until <= now)
