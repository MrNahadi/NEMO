import csv
import tempfile
import unittest
from pathlib import Path

from nemo.validation import load_candidate_rows, select_validation_candidates, write_validation_package


class ValidationPackageTests(unittest.TestCase):
    def test_selects_baseline_plus_lightest_feasible_candidates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "results.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "run_id",
                        "iteration",
                        "mode",
                        "status",
                        "baseplate_length",
                        "baseplate_width",
                        "baseplate_thickness",
                        "rib_height",
                        "rib_thickness",
                        "fillet_radius",
                        "mass_kg",
                        "max_stress_mpa",
                        "factor_of_safety",
                        "max_deflection_mm",
                        "objective_value",
                        "error",
                        "timestamp",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "run_id": "r",
                        "iteration": "1",
                        "mode": "analytical",
                        "status": "ok",
                        "baseplate_length": "150",
                        "baseplate_width": "100",
                        "baseplate_thickness": "5",
                        "rib_height": "45",
                        "rib_thickness": "6",
                        "fillet_radius": "5",
                        "mass_kg": "0.3",
                        "max_stress_mpa": "80",
                        "factor_of_safety": "3.0",
                        "max_deflection_mm": "0.3",
                        "objective_value": "0.3",
                        "error": "",
                        "timestamp": "",
                    }
                )
                writer.writerow(
                    {
                        "run_id": "r",
                        "iteration": "2",
                        "mode": "analytical",
                        "status": "ok",
                        "baseplate_length": "150",
                        "baseplate_width": "100",
                        "baseplate_thickness": "4",
                        "rib_height": "20",
                        "rib_thickness": "3",
                        "fillet_radius": "2",
                        "mass_kg": "0.1",
                        "max_stress_mpa": "500",
                        "factor_of_safety": "0.5",
                        "max_deflection_mm": "5.0",
                        "objective_value": "999",
                        "error": "",
                        "timestamp": "",
                    }
                )

            rows = load_candidate_rows([csv_path])
            candidates = select_validation_candidates(rows, count=1)
            self.assertEqual([c["candidate_id"] for c in candidates], ["baseline", "candidate_01"])

            output_dir = Path(temp_dir) / "validation"
            write_validation_package(candidates, output_dir)
            self.assertTrue((output_dir / "validation_candidates.csv").exists())
            self.assertTrue((output_dir / "VALIDATION_CHECKLIST.md").exists())
            self.assertTrue((output_dir / "fusion_requests" / "baseline_request.json").exists())


if __name__ == "__main__":
    unittest.main()
