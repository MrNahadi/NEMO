"""Dynamic CSV and run-metadata logging for NEMO evaluations."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, Mapping

from .parts import DEFAULT_PART_ID, get_part_definition
from .schemas import EvaluationRequest, EvaluationResponse


CORE_FIELDS = ["schema_version", "part_id", "run_id", "iteration", "mode", "status"]
METRIC_FIELDS = [
    "volume_m3",
    "mass_kg",
    "max_stress_mpa",
    "factor_of_safety",
    "max_deflection_mm",
    "objective_value",
    "error",
    "timestamp",
]


def csv_fields(part_id: str = DEFAULT_PART_ID) -> list[str]:
    definition = get_part_definition(part_id)
    return [*CORE_FIELDS, *definition.parameter_names, *METRIC_FIELDS]


CSV_FIELDS = csv_fields(DEFAULT_PART_ID)


def append_evaluation(
    csv_path: str | Path,
    request: EvaluationRequest,
    response: EvaluationResponse,
) -> None:
    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    fields = csv_fields(request.part_id)
    if exists:
        with path.open("r", newline="", encoding="utf-8") as handle:
            existing_fields = next(csv.reader(handle), [])
        if existing_fields != fields:
            raise ValueError(
                f"Run log schema does not match part '{request.part_id}': {path}"
            )
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow(evaluation_row(request, response))


def evaluation_row(
    request: EvaluationRequest,
    response: EvaluationResponse,
) -> dict[str, object]:
    metrics = response.metrics
    row: dict[str, object] = {
        "schema_version": request.schema_version,
        "part_id": request.part_id,
        "run_id": request.run_id,
        "iteration": request.iteration,
        "mode": request.mode,
        "status": response.status,
        "volume_m3": metrics.volume_m3,
        "mass_kg": metrics.mass_kg,
        "max_stress_mpa": metrics.max_stress_mpa,
        "factor_of_safety": metrics.factor_of_safety,
        "max_deflection_mm": metrics.max_deflection_mm,
        "objective_value": metrics.objective_value,
        "error": response.error or "",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    for name in get_part_definition(request.part_id).parameter_names:
        row[name] = request.parameters.get(name, "")
    return row


def write_run_metadata(
    run_dir: str | Path,
    *,
    part_id: str,
    run_id: str,
    run_type: str,
) -> Path:
    definition = get_part_definition(part_id)
    payload = {
        "schema_version": 2,
        "run_id": run_id,
        "run_type": run_type,
        "part_id": part_id,
        "part_name": definition.name,
        "material": {
            "name": definition.material.name,
            "density_kg_m3": definition.material.density_kg_m3,
            "yield_strength_mpa": definition.material.yield_strength_mpa,
            "elastic_modulus_pa": definition.material.elastic_modulus_pa,
        },
        "constraints": {
            "min_factor_of_safety": definition.constraints.min_factor_of_safety,
            "max_deflection_mm": definition.constraints.max_deflection_mm,
        },
        "load": definition.load,
        "parameters": [
            {
                "name": spec.name,
                "unit": spec.unit,
                "lower": spec.lower,
                "upper": spec.upper,
                "baseline": spec.baseline,
                "description": spec.description,
            }
            for spec in definition.parameters
        ],
    }
    path = Path(run_dir) / "run.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def read_rows(csv_path: str | Path) -> list[dict[str, str]]:
    path = Path(csv_path)
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def cache_key_from_parameters(
    parameters: Mapping[str, float],
    digits: int = 4,
    *,
    part_id: str = DEFAULT_PART_ID,
) -> tuple[float, ...]:
    names = get_part_definition(part_id).parameter_names
    return tuple(round(float(parameters[name]), digits) for name in names)


def unique_successful_rows(
    rows: Iterable[dict[str, str]],
    *,
    part_id: str = DEFAULT_PART_ID,
) -> dict[tuple[str, ...], dict[str, str]]:
    names = get_part_definition(part_id).parameter_names
    cache: dict[tuple[str, ...], dict[str, str]] = {}
    for row in rows:
        if row.get("status") != "ok" or row.get("part_id", part_id) != part_id:
            continue
        cache[tuple(row.get(name, "") for name in names)] = row
    return cache
