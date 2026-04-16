from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple

@dataclass
class CacheEntry:
    value: Any
    expires_at: datetime

@dataclass
class DPResultCache:
    ttl_minutes: int = 10
    store: Dict[Tuple[str, str, str], CacheEntry] = field(default_factory=dict)

    def get(self, user_id: str, query_name: str, query_key: str, now: datetime):
        key = (user_id, query_name, query_key)
        entry = self.store.get(key)
        if entry and entry.expires_at > now:
            return entry.value
        return None

    def set(self, user_id: str, query_name: str, query_key: str, value: Any, now: datetime):
        key = (user_id, query_name, query_key)
        self.store[key] = CacheEntry(
            value=value,
            expires_at=now + timedelta(minutes=self.ttl_minutes)
        )
