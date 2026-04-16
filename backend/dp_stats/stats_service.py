from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from .budget_manager import BudgetManager
from .cache_service import DPResultCache
from .mechanisms import DPParams, privatize_count, privatize_counts_dict

@dataclass
class StatsService:
    budget_manager: BudgetManager
    cache: DPResultCache

    def get_private_total_count(
        self,
        user_id: str,
        query_key: str,
        true_count: int,
        epsilon: float,
        now: datetime,
    ) -> dict:
        cached = self.cache.get(user_id, "total_count", query_key, now)
        if cached is not None:
            return {"value": cached, "source": "cache"}

        today = now.date()
        if not self.budget_manager.can_spend(user_id, epsilon, today):
            raise ValueError("Privacy budget exceeded")

        params = DPParams(epsilon=epsilon, sensitivity=1.0)
        noisy_count = privatize_count(true_count, params)

        self.budget_manager.spend(user_id, epsilon, today)
        self.cache.set(user_id, "total_count", query_key, noisy_count, now)

        return {"value": noisy_count, "source": "fresh_dp"}

    def get_private_distribution(
        self,
        user_id: str,
        query_key: str,
        true_counts: Dict[str, int],
        epsilon: float,
        now: datetime,
    ) -> dict:
        cached = self.cache.get(user_id, "distribution", query_key, now)
        if cached is not None:
            return {"value": cached, "source": "cache"}

        today = now.date()
        if not self.budget_manager.can_spend(user_id, epsilon, today):
            raise ValueError("Privacy budget exceeded")

        params = DPParams(epsilon=epsilon, sensitivity=1.0)
        noisy_counts = privatize_counts_dict(true_counts, params)

        self.budget_manager.spend(user_id, epsilon, today)
        self.cache.set(user_id, "distribution", query_key, noisy_counts, now)

        return {"value": noisy_counts, "source": "fresh_dp"}
