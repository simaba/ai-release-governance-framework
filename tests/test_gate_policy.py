import unittest

from gate_policy import (
    DecisionContext,
    ReleaseDecision,
    assess_release,
    build_decision_context,
)
from risk_scoring import RiskInputs


LOW_RISK = RiskInputs(
    safety_impact=1,
    regulatory_exposure=1,
    uncertainty_sensitivity=1,
    operational_complexity=1,
    observability_maturity=1,
    fallback_readiness=1,
)


def low_evidence(**overrides):
    evidence = {
        "domain_and_data_coverage": True,
        "uncertainty_handling": True,
        "monitoring_and_observability": True,
    }
    evidence.update(overrides)
    return evidence


class ReleasePolicyTests(unittest.TestCase):
    def test_release_when_all_required_gates_are_satisfied(self):
        assessment = assess_release(LOW_RISK, low_evidence())
        self.assertEqual(assessment.decision, ReleaseDecision.RELEASE)
        self.assertEqual(assessment.missing_gates, [])

    def test_release_with_conditions_when_only_non_hard_gate_is_missing(self):
        assessment = assess_release(
            LOW_RISK,
            low_evidence(domain_and_data_coverage=False),
        )
        self.assertEqual(
            assessment.decision,
            ReleaseDecision.RELEASE_WITH_CONDITIONS,
        )

    def test_hold_when_hard_gate_is_missing(self):
        assessment = assess_release(
            LOW_RISK,
            low_evidence(monitoring_and_observability=False),
        )
        self.assertEqual(assessment.decision, ReleaseDecision.HOLD)

    def test_do_not_release_requires_explicit_terminal_context(self):
        assessment = assess_release(
            LOW_RISK,
            low_evidence(),
            DecisionContext(critical_failure=True),
        )
        self.assertEqual(assessment.decision, ReleaseDecision.DO_NOT_RELEASE)

    def test_each_terminal_context_maps_to_do_not_release(self):
        contexts = [
            DecisionContext(critical_failure=True),
            DecisionContext(prohibited_condition=True),
            DecisionContext(unacceptable_residual_risk=True),
        ]
        for context in contexts:
            with self.subTest(context=context):
                assessment = assess_release(LOW_RISK, low_evidence(), context)
                self.assertEqual(
                    assessment.decision,
                    ReleaseDecision.DO_NOT_RELEASE,
                )

    def test_defer_is_an_explicit_owner_decision(self):
        assessment = assess_release(
            LOW_RISK,
            low_evidence(),
            DecisionContext(defer_reason="Awaiting external dependency evidence."),
        )
        self.assertEqual(assessment.decision, ReleaseDecision.DEFER)
        self.assertIn("Awaiting external dependency evidence.", assessment.rationale[0])

    def test_terminal_condition_takes_precedence_over_defer(self):
        assessment = assess_release(
            LOW_RISK,
            low_evidence(),
            DecisionContext(
                critical_failure=True,
                defer_reason="Awaiting another review.",
            ),
        )
        self.assertEqual(assessment.decision, ReleaseDecision.DO_NOT_RELEASE)

    def test_string_false_does_not_silently_pass_a_gate(self):
        evidence = low_evidence()
        evidence["monitoring_and_observability"] = "false"
        with self.assertRaisesRegex(
            ValueError,
            "evidence.monitoring_and_observability must be a boolean",
        ):
            assess_release(LOW_RISK, evidence)

    def test_unknown_evidence_field_is_rejected(self):
        evidence = low_evidence(unknown_gate=True)
        with self.assertRaisesRegex(ValueError, "unsupported evidence fields"):
            assess_release(LOW_RISK, evidence)

    def test_legacy_symbolic_aliases_remain_available(self):
        self.assertIs(ReleaseDecision.GO, ReleaseDecision.RELEASE)
        self.assertIs(
            ReleaseDecision.CONDITIONAL_GO,
            ReleaseDecision.RELEASE_WITH_CONDITIONS,
        )
        self.assertIs(ReleaseDecision.NO_GO, ReleaseDecision.DO_NOT_RELEASE)


class DecisionContextParsingTests(unittest.TestCase):
    def test_empty_context_uses_safe_defaults(self):
        self.assertEqual(build_decision_context({}), DecisionContext())

    def test_context_is_parsed_without_boolean_string_coercion(self):
        with self.assertRaisesRegex(ValueError, "critical_failure must be a boolean"):
            build_decision_context({"critical_failure": "false"})

    def test_blank_defer_reason_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "defer_reason must not be blank"):
            build_decision_context({"defer_reason": "   "})

    def test_unknown_context_field_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported decision_context fields"):
            build_decision_context({"prohibitted_condition": True})


if __name__ == "__main__":
    unittest.main()
