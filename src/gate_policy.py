"""Operational gate policy for risk-tiered AI release decisions."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from risk_scoring import RiskInputs, RiskTier, score_risk


class ReleaseDecision(str, Enum):
    """Canonical release outcomes used by the governance framework."""

    RELEASE = "release"
    RELEASE_WITH_CONDITIONS = "release_with_conditions"
    HOLD = "hold"
    DO_NOT_RELEASE = "do_not_release"
    DEFER = "defer"

    # Backward-compatible symbolic aliases for earlier callers.
    GO = RELEASE
    CONDITIONAL_GO = RELEASE_WITH_CONDITIONS
    NO_GO = DO_NOT_RELEASE


GATE_LABELS = {
    "domain_and_data_coverage": "G1. Domain and data coverage",
    "uncertainty_handling": "G2. Uncertainty handling",
    "fallback_and_degraded_mode": "G3. Fallback and degraded mode",
    "monitoring_and_observability": "G4. Monitoring and observability",
    "human_escalation_and_override": "G5. Human escalation and override",
    "incident_response_and_recovery": "G6. Incident response and recovery",
    "accountability_signoff": "G7. Accountability sign-off",
    "post_release_review_plan": "G8. Post-release review plan",
}


REQUIRED_GATES = {
    RiskTier.LOW: [
        "domain_and_data_coverage",
        "uncertainty_handling",
        "monitoring_and_observability",
    ],
    RiskTier.MEDIUM: [
        "domain_and_data_coverage",
        "uncertainty_handling",
        "fallback_and_degraded_mode",
        "monitoring_and_observability",
        "human_escalation_and_override",
        "post_release_review_plan",
    ],
    RiskTier.HIGH: [
        "domain_and_data_coverage",
        "uncertainty_handling",
        "fallback_and_degraded_mode",
        "monitoring_and_observability",
        "human_escalation_and_override",
        "incident_response_and_recovery",
        "accountability_signoff",
        "post_release_review_plan",
    ],
}


HARD_GATES = {
    RiskTier.LOW: ["monitoring_and_observability"],
    RiskTier.MEDIUM: [
        "fallback_and_degraded_mode",
        "monitoring_and_observability",
        "human_escalation_and_override",
    ],
    RiskTier.HIGH: [
        "fallback_and_degraded_mode",
        "monitoring_and_observability",
        "incident_response_and_recovery",
        "accountability_signoff",
    ],
}

# Backward-compatible alias for callers using the former name.
CRITICAL_GATES = HARD_GATES


@dataclass(frozen=True)
class DecisionContext:
    """Explicit decision facts that cannot be inferred from gate evidence alone."""

    critical_failure: bool = False
    prohibited_condition: bool = False
    unacceptable_residual_risk: bool = False
    defer_reason: Optional[str] = None


@dataclass
class ReleaseAssessment:
    score: int
    tier: RiskTier
    decision: ReleaseDecision
    required_gates: List[str]
    satisfied_gates: List[str]
    missing_gates: List[str]
    rationale: List[str]


def assess_release(
    risk_inputs: RiskInputs,
    evidence: Dict[str, bool],
    decision_context: Optional[DecisionContext] = None,
) -> ReleaseAssessment:
    """Assess a release using risk-tier gates and explicit decision context.

    Gate evidence can establish release, conditional release, or hold. A terminal
    do-not-release outcome requires an explicit critical/prohibited/unacceptable
    condition. Deferral is also explicit because it represents an owner decision,
    not merely missing evidence.
    """

    unknown_evidence = sorted(set(evidence) - set(GATE_LABELS))
    if unknown_evidence:
        raise ValueError(
            "unsupported evidence fields: " + ", ".join(unknown_evidence)
        )
    for gate, value in evidence.items():
        if not isinstance(value, bool):
            raise ValueError(f"evidence.{gate} must be a boolean")

    score, tier = score_risk(risk_inputs)
    required_gates = REQUIRED_GATES[tier]
    satisfied_gates = [gate for gate in required_gates if evidence.get(gate, False)]
    missing_gates = [gate for gate in required_gates if not evidence.get(gate, False)]
    context = decision_context or DecisionContext()

    rationale: List[str] = []
    terminal_reasons: List[str] = []
    if context.critical_failure:
        terminal_reasons.append("a critical failure")
    if context.prohibited_condition:
        terminal_reasons.append("a prohibited condition")
    if context.unacceptable_residual_risk:
        terminal_reasons.append("unacceptable residual risk")

    if terminal_reasons:
        decision = ReleaseDecision.DO_NOT_RELEASE
        rationale.append(
            "Do not release because the decision context records "
            + ", ".join(terminal_reasons)
            + "."
        )
    elif context.defer_reason:
        decision = ReleaseDecision.DEFER
        rationale.append(f"Decision deferred: {context.defer_reason}")
    elif not missing_gates:
        decision = ReleaseDecision.RELEASE
        rationale.append("All required gates for the assessed risk tier are satisfied.")
    else:
        hard_missing = [gate for gate in HARD_GATES[tier] if gate in missing_gates]
        if hard_missing:
            decision = ReleaseDecision.HOLD
            rationale.append(
                "One or more hard control gates are missing; release is on hold pending remediation or evidence."
            )
        else:
            decision = ReleaseDecision.RELEASE_WITH_CONDITIONS
            rationale.append("Required non-hard gates remain incomplete, but no hard gate is missing.")
            rationale.append(
                "A conditional release should include enforceable scope, owner, deadline, monitoring, and stop conditions."
            )

    if tier == RiskTier.HIGH:
        rationale.append("High-risk releases require explicit accountability and incident response readiness.")
    elif tier == RiskTier.MEDIUM:
        rationale.append("Medium-risk releases should use phased rollout and tighter monitoring discipline.")
    else:
        rationale.append("Low-risk releases should still preserve rollback and basic observability.")

    return ReleaseAssessment(
        score=score,
        tier=tier,
        decision=decision,
        required_gates=required_gates,
        satisfied_gates=satisfied_gates,
        missing_gates=missing_gates,
        rationale=rationale,
    )


def build_risk_inputs(data: Dict[str, int]) -> RiskInputs:
    return RiskInputs(
        safety_impact=data["safety_impact"],
        regulatory_exposure=data["regulatory_exposure"],
        uncertainty_sensitivity=data["uncertainty_sensitivity"],
        operational_complexity=data["operational_complexity"],
        observability_maturity=data["observability_maturity"],
        fallback_readiness=data["fallback_readiness"],
    )


def build_decision_context(data: Dict[str, object]) -> DecisionContext:
    """Build and validate explicit decision context from profile data."""

    allowed_fields = {
        "critical_failure",
        "prohibited_condition",
        "unacceptable_residual_risk",
        "defer_reason",
    }
    unknown_fields = sorted(set(data) - allowed_fields)
    if unknown_fields:
        raise ValueError(
            "unsupported decision_context fields: " + ", ".join(unknown_fields)
        )

    def read_bool(key: str) -> bool:
        value = data.get(key, False)
        if not isinstance(value, bool):
            raise ValueError(f"decision_context.{key} must be a boolean")
        return value

    defer_reason = data.get("defer_reason")
    if defer_reason is not None:
        if not isinstance(defer_reason, str):
            raise ValueError("decision_context.defer_reason must be a string or null")
        defer_reason = defer_reason.strip()
        if not defer_reason:
            raise ValueError("decision_context.defer_reason must not be blank")

    return DecisionContext(
        critical_failure=read_bool("critical_failure"),
        prohibited_condition=read_bool("prohibited_condition"),
        unacceptable_residual_risk=read_bool("unacceptable_residual_risk"),
        defer_reason=defer_reason,
    )
