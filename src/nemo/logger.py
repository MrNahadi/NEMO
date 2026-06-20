"""CSV logging for evaluated designs."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .config import PARAMETER_NAMES
from .schemas import EvaluationRequest, EvaluationResponse


CSV_FIELDS = [
    "run_id",
    "iteration",
    "mode",
    "status",
    *PARAMETER_NAMES,
    "mass_kg",
    "max_stress_mpa",
    "factor_of_safety",
    "max_deflection_mm",
    "objective_value",
    "error",
    "timestamp",
]


def append_evaluation(
    csv_path: str | Path,
    request: EvaluationRequest,
    response: EvaluationResponse,
) -> None:
    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow(evaluation_row(request, response))


def evaluation_row(
    request: EvaluationRequest,
    response: EvaluationResponse,
) -> dict[str, object]:
    metrics = response.metrics
    row: dict[str, object] = {
        "run_id": request.run_id,
        "iteration": request.iteration,
        "mode": request.mode,
        "status": response.status,
        "mass_kg": metrics.mass_kg,
        "max_stress_mpa": metrics.max_stress_mpa,
        "factor_of_safety": metrics.factor_of_safety,
        "max_deflection_mm": metrics.max_deflection_mm,
        "objective_value": metrics.objective_value,
        "error": response.error or "",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    for name in PARAMETER_NAMES:
        row[name] = request.parameters_mm.get(name, "")
    return row


def read_rows(csv_path: str | Path) -> list[dict[str, str]]:
    path = Path(csv_path)
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def cache_key_from_parameters(parameters_mm: dict[str, float], digits: int = 4) -> tuple[float, ...]:
    return tuple(round(float(parameters_mm[name]), digits) for name in PARAMETER_NAMES)


def unique_successful_rows(rows: Iterable[dict[str, str]]) -> dict[tuple[str, ...], dict[str, str]]:
    cache: dict[tuple[str, ...], dict[str, str]] = {}
    for row in rows:
        if row.get("status") != "ok":
            continue
        key = tuple(row.get(name, "") for name in PARAMETER_NAMES)
        cache[key] = row
    return cache
