from __future__ import annotations

import pandas as pd

from dashboard.formatting import best_candidate_table


def test_best_candidate_table_uses_homogeneous_string_values() -> None:
    candidate = pd.DataFrame(
        [
            {
                "part_id": "padeye",
                "mass_kg": 8.89727544,
                "feasible": True,
                "error_message": float("nan"),
            }
        ]
    )

    display = best_candidate_table(candidate)

    assert display.to_dict(orient="records") == [
        {"Field": "part_id", "Value": "padeye"},
        {"Field": "mass_kg", "Value": "8.89728"},
        {"Field": "feasible", "Value": "True"},
        {"Field": "error_message", "Value": ""},
    ]
    assert all(isinstance(value, str) for value in display["Value"])
