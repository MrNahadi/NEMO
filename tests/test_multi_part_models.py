import unittest

from nemo.evaluation import evaluate_design
from nemo.parts import get_part_definition


class MultiPartAnalyticalTests(unittest.TestCase):
    def test_thinner_padeye_is_lighter_and_weaker(self):
        definition = get_part_definition("padeye")
        baseline = evaluate_design(part_id="padeye")
        thinner = dict(definition.baseline_parameters)
        thinner.update(
            base_thickness=8,
            lug_thickness=12,
            neck_width=80,
            gusset_thickness=6,
            fillet_radius=8,
        )
        response = evaluate_design(thinner, part_id="padeye")
        self.assertLess(response.metrics.mass_kg, baseline.metrics.mass_kg)
        self.assertLess(response.metrics.factor_of_safety, baseline.metrics.factor_of_safety)
        self.assertGreater(response.metrics.max_deflection_mm, baseline.metrics.max_deflection_mm)

    def test_thinner_stabilizer_is_lighter_and_weaker(self):
        definition = get_part_definition("stabilizer")
        baseline = evaluate_design(part_id="stabilizer")
        thinner = dict(definition.baseline_parameters)
        thinner.update(
            skin_thickness=4,
            front_spar_thickness=4,
            rear_spar_thickness=4,
            rib_thickness=3,
            root_insert_thickness=8,
            root_fillet_radius=12,
        )
        response = evaluate_design(thinner, part_id="stabilizer")
        self.assertLess(response.metrics.mass_kg, baseline.metrics.mass_kg)
        self.assertLess(response.metrics.factor_of_safety, baseline.metrics.factor_of_safety)
        self.assertGreater(response.metrics.max_deflection_mm, baseline.metrics.max_deflection_mm)

    def test_unitless_stabilizer_parameters_are_validated(self):
        definition = get_part_definition("stabilizer")
        bad = dict(definition.baseline_parameters)
        bad["front_spar_position"] = 5
        response = evaluate_design(bad, part_id="stabilizer")
        self.assertEqual(response.status, "failed")
        self.assertIn("front_spar_position", response.error)


if __name__ == "__main__":
    unittest.main()
