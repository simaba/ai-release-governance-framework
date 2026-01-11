"""
Simple, explainable risk scoring scaffold for AI-enabled features.

This is intentionally lightweight and designed for adaptation.
"""

from dataclasses import dataclass
from enum import Enum


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class RiskInputs:
    safety_impact: int  # 1-5
    regulatory_exposure: int  # 1-5
    uncertainty_sensitivity: int  # 1-5
    operational_complexity: int  # 1-5
    observability_maturity: int  # 1-5 (higher is better)
    fallback_readiness: int  # 1-5 (higher is better)


def score_risk(inputs: RiskInputs) -> tuple[int, RiskTier]:
    """
    Returns (score, tier). Higher score indicates higher release risk.
    """
    # Base risk drivers
    score = (
        inputs.safety_impact
        + inputs.regulatory_exposure
        + inputs.uncertainty_sensitivity
        + inputs.operational_complexity
    )

    # Risk reducers (subtract because higher maturity reduces risk)
    score -= (inputs.observability_maturity - 1)
    score -= (inputs.fallback_readiness - 1)

    # Clamp to reasonable bounds
    score = max(1, min(score, 20))

    if score <= 7:
        return score, RiskTier.LOW
    if score <= 13:
        return score, RiskTier.MEDIUM
    return score, RiskTier.HIGH
