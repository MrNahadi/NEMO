import csv
import tempfile
import unittest
from pathlib import Path

from nemo.evaluation import evaluate_design, is_feasible
from nemo.logger import append_evaluation
from nemo.parts import get_part_definition, list_part_definitions
from nemo.schemas import EvaluationRequest


class PartRegistryTests(unittest.TestCase):
    def test_registry_contains_expected_parts(self):
        self.assertEqual(
            [definition.part_id for definition in list_part_definitions()],
            ["bracket", "padeye", "stabilizer"],
        )
        for definition in list_part_definitions():
            self.assertEqual(len(definition.parameter_names), len(set(definition.parameter_names)))
            self.assertTrue(all(spec.lower < spec.baseline < spec.upper for spec in definition.parameters))

    def test_schema_v1_request_is_backward_compatible(self):
        request = EvaluationRequest.from_dict(
            {
                "run_id": "legacy",
                "iteration": 1,
                "mode": "analytical",
                "parameters_mm": get_part_definition("bracket").baseline_parameters,
            }
        )
        self.assertEqual(request.part_id, "bracket")
        self.assertEqual(request.schema_version, 1)
        self.assertIn("parameters", request.to_dict())

    def test_all_baselines_are_feasible(self):
        for definition in list_part_definitions():
            response = evaluate_design(part_id=definition.part_id)
            self.assertEqual(response.status, "ok")
            self.assertTrue(is_feasible(response.metrics, definition))
            self.assertGreater(response.metrics.volume_m3, 0)

    def test_logger_uses_part_specific_columns(self):
        definition = get_part_definition("padeye")
        request = EvaluationRequest(
            run_id="test",
            iteration=0,
            mode="analytical",
            part_id="padeye",
            parameters=definition.baseline_parameters,
        )
        response = evaluate_design(part_id="padeye")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "results.csv"
            append_evaluation(path, request, response)
            with path.open(newline="", encoding="utf-8") as handle:
                fields = next(csv.reader(handle))
            self.assertIn("part_id", fields)
            self.assertIn("lug_thickness", fields)
            self.assertNotIn("baseplate_length", fields)


if __name__ == "__main__":
    unittest.main()
