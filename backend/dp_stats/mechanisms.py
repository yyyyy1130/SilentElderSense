from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class DPParams:
    epsilon: float
    sensitivity: float = 1.0

    def __post_init__(self):
        if self.epsilon <= 0:
            raise ValueError("epsilon must be > 0")
        if self.sensitivity <= 0:
            raise ValueError("sensitivity must be > 0")

def sample_laplace(scale: float) -> float:
    if scale <= 0:
        raise ValueError("scale must be > 0")
    return float(np.random.laplace(loc=0.0, scale=scale))

def privatize_count(true_count: int, params: DPParams) -> int:
    if true_count < 0:
        raise ValueError("true_count must be >= 0")
    scale = params.sensitivity / params.epsilon
    noisy_value = true_count + sample_laplace(scale)
    return max(0, int(round(noisy_value)))

def privatize_counts_dict(true_counts: dict[str, int], params: DPParams) -> dict[str, int]:
    result = {}
    for key, value in true_counts.items():
        result[key] = privatize_count(value, params)
    return result
