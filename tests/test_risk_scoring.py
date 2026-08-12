import unittest

from risk_scoring import RiskInputs, RiskTier, score_risk


class RiskScoringTests(unittest.TestCase):
    def test_low_medium_and_high_thresholds(self):
        cases = [
            (
                RiskInputs(1, 1, 1, 1, 1, 1),
                4,
                RiskTier.LOW,
            ),
            (
                RiskInputs(3, 2, 2, 1, 1, 1),
                8,
                RiskTier.MEDIUM,
            ),
            (
                RiskInputs(5, 4, 3, 2, 1, 1),
                14,
                RiskTier.HIGH,
            ),
        ]
        for inputs, expected_score, expected_tier in cases:
            with self.subTest(inputs=inputs):
                score, tier = score_risk(inputs)
                self.assertEqual(score, expected_score)
                self.assertEqual(tier, expected_tier)

    def test_risk_inputs_reject_out_of_range_and_non_integer_values(self):
        invalid_values = [0, 6, 2.5, "3", True]
        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    ValueError,
                    "safety_impact must be an integer from 1 to 5",
                ):
                    RiskInputs(value, 1, 1, 1, 1, 1)


if __name__ == "__main__":
    unittest.main()
