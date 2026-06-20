import unittest

from nemo.config import BASELINE_PARAMETERS_MM
from nemo.evaluation import evaluate_design, is_feasible


class AnalyticalModelTests(unittest.TestCase):
    def test_baseline_is_successful_and_feasible(self):
        response = evaluate_design(BASELINE_PARAMETERS_MM)

        self.assertEqual(response.status, "ok")
        self.assertIsNotNone(response.metrics.mass_kg)
        self.assertGreater(response.metrics.mass_kg, 0)
        self.assertTrue(is_feasible(response.metrics))

    def test_weaker_design_has_lower_mass_and_lower_fos(self):
        baseline = evaluate_design(BASELINE_PARAMETERS_MM)
        thin = dict(BASELINE_PARAMETERS_MM)
        thin["baseplate_thickness"] = 4.0
        thin["rib_height"] = 20.0
        thin["rib_thickness"] = 3.0
        thin_response = evaluate_design(thin)

        self.assertLess(thin_response.metrics.mass_kg, baseline.metrics.mass_kg)
        self.assertLess(
            thin_response.metrics.factor_of_safety,
            baseline.metrics.factor_of_safety,
        )

    def test_out_of_bounds_design_fails_cleanly(self):
        bad = dict(BASELINE_PARAMETERS_MM)
        bad["baseplate_length"] = 10.0
        response = evaluate_design(bad)

        self.assertEqual(response.status, "failed")
        self.assertIn("baseplate_length", response.error)


if __name__ == "__main__":
    unittest.main()
