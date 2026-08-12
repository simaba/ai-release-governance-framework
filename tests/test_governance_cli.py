import unittest

from governance_cli import _serialize_report


class GovernanceCliTests(unittest.TestCase):
    def _profile(self):
        return {
            "feature_name": "test feature",
            "release_id": "test-1",
            "risk_inputs": {
                "safety_impact": 1,
                "regulatory_exposure": 1,
                "uncertainty_sensitivity": 1,
                "operational_complexity": 1,
                "observability_maturity": 1,
                "fallback_readiness": 1,
            },
            "evidence": {
                "domain_and_data_coverage": True,
                "uncertainty_handling": True,
                "monitoring_and_observability": True,
            },
        }

    def test_legacy_profile_shape_defaults_to_release(self):
        report = _serialize_report(self._profile())
        self.assertEqual(report["decision"], "release")

    def test_profile_can_express_do_not_release(self):
        profile = self._profile()
        profile["decision_context"] = {"prohibited_condition": True}
        report = _serialize_report(profile)
        self.assertEqual(report["decision"], "do_not_release")

    def test_profile_can_express_defer(self):
        profile = self._profile()
        profile["decision_context"] = {
            "defer_reason": "Awaiting supplier evidence."
        }
        report = _serialize_report(profile)
        self.assertEqual(report["decision"], "defer")

    def test_decision_context_must_be_an_object(self):
        profile = self._profile()
        profile["decision_context"] = []
        with self.assertRaisesRegex(ValueError, "decision_context must be an object"):
            _serialize_report(profile)

    def test_evidence_must_be_an_object(self):
        profile = self._profile()
        profile["evidence"] = []
        with self.assertRaisesRegex(ValueError, "evidence must be an object"):
            _serialize_report(profile)

    def test_risk_inputs_must_be_an_object(self):
        profile = self._profile()
        profile["risk_inputs"] = []
        with self.assertRaisesRegex(ValueError, "risk_inputs must be an object"):
            _serialize_report(profile)


if __name__ == "__main__":
    unittest.main()
