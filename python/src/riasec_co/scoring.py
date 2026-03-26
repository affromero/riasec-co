"""Dirichlet-based Bayesian scoring for RIASEC profiles."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

RIASEC_TYPES = ("R", "I", "A", "S", "E", "C")
MAX_ENTROPY = math.log2(6)


@dataclass(frozen=True)
class DirichletAlpha:
    """Dirichlet concentration parameters for 6 RIASEC types."""

    R: float = 1.0
    I: float = 1.0
    A: float = 1.0
    S: float = 1.0
    E: float = 1.0
    C: float = 1.0

    def __getitem__(self, key: str) -> float:
        return getattr(self, key)

    def update(self, riasec_type: str, response: int, keyed: str) -> DirichletAlpha:
        """Return new alpha with updated concentration for the given type."""
        normalized = (response - 1) / 4 if keyed == "+" else (5 - response) / 4
        values = {t: self[t] for t in RIASEC_TYPES}
        values[riasec_type] += normalized
        return DirichletAlpha(**values)

    @property
    def total(self) -> float:
        return sum(self[t] for t in RIASEC_TYPES)

    def posterior_mean(self) -> dict[str, float]:
        """E[θ_k] = α_k / Σα"""
        s = self.total
        return {t: self[t] / s for t in RIASEC_TYPES}

    @property
    def entropy(self) -> float:
        """Shannon entropy of posterior mean. Max = log2(6) ≈ 2.585."""
        profile = self.posterior_mean()
        return -sum(p * math.log2(p) for p in profile.values() if p > 0)

    @property
    def confidence(self) -> float:
        """1 - (entropy / max_entropy). 0 = uniform, 1 = certain."""
        return 1 - self.entropy / MAX_ENTROPY


def cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:
    """Cosine similarity between two RIASEC profiles."""
    dot = sum(a[t] * b[t] for t in RIASEC_TYPES)
    norm_a = math.sqrt(sum(a[t] ** 2 for t in RIASEC_TYPES))
    norm_b = math.sqrt(sum(b[t] ** 2 for t in RIASEC_TYPES))
    denom = norm_a * norm_b
    return dot / denom if denom > 0 else 0.0


def kl_divergence(p: dict[str, float], q: dict[str, float]) -> float:
    """KL divergence D_KL(P || Q)."""
    return sum(
        p[t] * math.log2(p[t] / q[t])
        for t in RIASEC_TYPES
        if p[t] > 0 and q[t] > 0
    )


def expected_info_gain(alpha: DirichletAlpha, riasec_type: str) -> float:
    """Expected information gain from asking an item of the given type."""
    total_kl = 0.0
    for response in (1, 3, 5):
        new_alpha = alpha.update(riasec_type, response, "+")
        kl = kl_divergence(new_alpha.posterior_mean(), alpha.posterior_mean())
        total_kl += kl / 3
    return total_kl
