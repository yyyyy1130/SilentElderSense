from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from .budget_manager import BudgetManager
from .cache_service import DPResultCache
from .mechanisms import DPParams, privatize_count, privatize_counts_dict

@dataclass
class StatsService:
    budget_manager: BudgetManager
    cache: DPResultCache

    def get_private_stats(
        self,
        user_id: str,
        query_key: str,
        stats: Dict[str, Any],
        epsilon: float,
        now: datetime,
        check_budget: bool = True,
    ) -> dict:
        """
        对整个统计对象一次性加噪

        Args:
            user_id: 用户 ID
            query_key: 查询键
            stats: 包含 total, by_type, by_risk, by_status 的统计对象
            epsilon: 隐私预算（单次消耗）
            now: 当前时间
            check_budget: 是否检查预算限制（生产环境 True，开发环境 False）

        Returns:
            {"value": 加噪后的 stats, "source": "cache" 或 "fresh_dp"}
        """
        # 检查缓存
        cached = self.cache.get(user_id, "stats", query_key, now)
        if cached is not None:
            return {"value": cached, "source": "cache"}

        # 检查预算（仅生产环境）
        if check_budget:
            today = now.date()
            if not self.budget_manager.can_spend(user_id, epsilon, today):
                raise ValueError("Privacy budget exceeded")

        params = DPParams(epsilon=epsilon, sensitivity=1.0)

        # 一次性加噪所有统计值
        noisy_stats = {}
        noisy_stats['total'] = privatize_count(stats.get('total', 0), params)
        noisy_stats['by_type'] = privatize_counts_dict(stats.get('by_type', {}), params)
        noisy_stats['by_risk'] = privatize_counts_dict(stats.get('by_risk', {}), params)
        noisy_stats['by_status'] = privatize_counts_dict(stats.get('by_status', {}), params)

        # 消耗预算（仅生产环境）
        if check_budget:
            today = now.date()
            self.budget_manager.spend(user_id, epsilon, today)

        self.cache.set(user_id, "stats", query_key, noisy_stats, now)

        return {"value": noisy_stats, "source": "fresh_dp"}
