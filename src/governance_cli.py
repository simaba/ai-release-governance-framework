"""CLI for generating AI release governance reports from a JSON profile."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from gate_policy import GATE_LABELS, assess_release, build_decision_context, build_risk_inputs


def _load_profile(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _serialize_report(profile: Dict[str, Any]) -> Dict[str, Any]:
    risk_inputs = profile.get("risk_inputs")
    if not isinstance(risk_inputs, dict):
        raise ValueError("risk_inputs must be an object")

    evidence = profile.get("evidence", {})
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be an object")

    decision_context = profile.get("decision_context", {})
    if not isinstance(decision_context, dict):
        raise ValueError("decision_context must be an object")

    assessment = assess_release(
        build_risk_inputs(risk_inputs),
        evidence,
        build_decision_context(decision_context),
    )

    return {
        "feature_name": profile.get("feature_name"),
        "release_id": profile.get("release_id"),
        "score": assessment.score,
        "tier": assessment.tier.value,
        "decision": assessment.decision.value,
        "required_gates": [GATE_LABELS[g] for g in assessment.required_gates],
        "satisfied_gates": [GATE_LABELS[g] for g in assessment.satisfied_gates],
        "missing_gates": [GATE_LABELS[g] for g in assessment.missing_gates],
        "rationale": assessment.rationale,
    }


def _as_text(report: Dict[str, Any]) -> str:
    lines = [
        f"Feature: {report['feature_name']}",
        f"Release: {report['release_id']}",
        f"Risk score: {report['score']}",
        f"Risk tier: {report['tier']}",
        f"Decision: {report['decision']}",
        "",
        "Required gates:",
    ]
    lines.extend(f"- {gate}" for gate in report["required_gates"])
    lines.append("")
    lines.append("Missing gates:")
    if report["missing_gates"]:
        lines.extend(f"- {gate}" for gate in report["missing_gates"])
    else:
        lines.append("- None")
    lines.append("")
    lines.append("Rationale:")
    lines.extend(f"- {item}" for item in report["rationale"])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an AI release governance report.")
    parser.add_argument("profile", type=Path, help="Path to the JSON release profile")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    args = parser.parse_args()

    report = _serialize_report(_load_profile(args.profile))

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(_as_text(report))


if __name__ == "__main__":
    main()
