from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Tuple

@dataclass
class BudgetManager:
    daily_limit: float = 3.0
    usage: Dict[Tuple[str, date], float] = field(default_factory=dict)

    def can_spend(self, user_id: str, epsilon: float, today: date) -> bool:
        spent = self.usage.get((user_id, today), 0.0)
        return spent + epsilon <= self.daily_limit

    def spend(self, user_id: str, epsilon: float, today: date) -> None:
        spent = self.usage.get((user_id, today), 0.0)
        new_value = spent + epsilon
        if new_value > self.daily_limit:
            raise ValueError("Privacy budget exceeded")
        self.usage[(user_id, today)] = new_value

    def get_spent(self, user_id: str, today: date) -> float:
        return self.usage.get((user_id, today), 0.0)
