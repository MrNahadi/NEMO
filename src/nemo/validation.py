"""Prepare part-specific packages for manual Fusion validation."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .evaluation import evaluate_design
from .handshake import write_json_atomic
from .logger import read_rows
from .parts import DEFAULT_PART_ID, get_part_definition
from .schemas import EvaluationRequest


def load_candidate_rows(csv_paths: Iterable[str | Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for csv_path in csv_paths:
        for row in read_rows(csv_path):
            item = dict(row)
            item["source_csv"] = str(csv_path)
            rows.append(item)
    return rows


def select_validation_candidates(
    rows: Iterable[dict[str, str]],
    *,
    part_id: str = DEFAULT_PART_ID,
    count: int = 5,
    min_fos: float | None = None,
    max_deflection_mm: float | None = None,
) -> list[dict[str, object]]:
    definition = get_part_definition(part_id)
    required_fos = definition.constraints.min_factor_of_safety if min_fos is None else min_fos
    allowed_deflection = (
        definition.constraints.max_deflection_mm
        if max_deflection_mm is None
        else max_deflection_mm
    )
    candidates: list[dict[str, object]] = [_baseline_candidate(part_id)]
    seen = {_parameter_key(definition.baseline_parameters, part_id)}

    feasible_rows = [
        row
        for row in rows
        if row.get("status") == "ok"
        and row.get("part_id", part_id) == part_id
        and _float_or_none(row.get("factor_of_safety")) is not None
        and _float_or_none(row.get("max_deflection_mm")) is not None
        and float(row["factor_of_safety"]) >= required_fos
        and float(row["max_deflection_mm"]) <= allowed_deflection
    ]
    feasible_rows.sort(key=lambda row: float(row["mass_kg"]))

    for row in feasible_rows:
        parameters = _parameters_from_row(row, part_id)
        key = _parameter_key(parameters, part_id)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(
            {
                "candidate_id": f"candidate_{len(candidates):02d}",
                "part_id": part_id,
                "source": row.get("source_csv", ""),
                "run_id": row.get("run_id", ""),
                "iteration": int(float(row.get("iteration", 0))),
                "parameters": parameters,
                "parameters_mm": parameters if part_id == DEFAULT_PART_ID else None,
                "analytical_metrics": _metrics_from_row(row),
            }
        )
        if len(candidates) >= count + 1:
            break
    return candidates


def write_validation_package(
    candidates: list[dict[str, object]],
    output_dir: str | Path,
    *,
    part_id: str = DEFAULT_PART_ID,
    run_id: str = "fusion_validation",
    min_fos: float | None = None,
    max_deflection_mm: float | None = None,
) -> None:
    definition = get_part_definition(part_id)
    required_fos = definition.constraints.min_factor_of_safety if min_fos is None else min_fos
    allowed_deflection = (
        definition.constraints.max_deflection_mm
        if max_deflection_mm is None
        else max_deflection_mm
    )
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": 2, "part_id": part_id, "candidates": candidates}
    write_json_atomic(output_path / "validation_candidates.json", payload)
    _write_candidates_csv(output_path / "validation_candidates.csv", candidates, part_id)
    _write_markdown_checklist(
        output_path / "VALIDATION_CHECKLIST.md",
        candidates,
        part_id=part_id,
        min_fos=required_fos,
        max_deflection_mm=allowed_deflection,
    )

    requests_dir = output_path / "fusion_requests"
    requests_dir.mkdir(parents=True, exist_ok=True)
    for index, candidate in enumerate(candidates):
        request = EvaluationRequest(
            run_id=run_id,
            iteration=index,
            mode="fusion_cad",
            part_id=part_id,
            parameters=dict(candidate["parameters"]),
            artifact_formats=("step", "boundary_tags"),
        )
        write_json_atomic(
            requests_dir / f"{candidate['candidate_id']}_request.json",
            request.to_dict(),
        )


def _baseline_candidate(part_id: str) -> dict[str, object]:
    definition = get_part_definition(part_id)
    response = evaluate_design(definition.baseline_parameters, part_id=part_id)
    return {
        "candidate_id": "baseline",
        "part_id": part_id,
        "source": "configured baseline",
        "run_id": "baseline",
        "iteration": 0,
        "parameters": dict(definition.baseline_parameters),
        "parameters_mm": (
            dict(definition.baseline_parameters) if part_id == DEFAULT_PART_ID else None
        ),
        "analytical_metrics": response.metrics.to_dict(),
    }


def _parameters_from_row(row: dict[str, str], part_id: str) -> dict[str, float]:
    return {
        name: float(row[name])
        for name in get_part_definition(part_id).parameter_names
    }


def _parameter_key(
    parameters: dict[str, float],
    part_id: str,
    digits: int = 3,
) -> tuple[float, ...]:
    return tuple(
        round(float(parameters[name]), digits)
        for name in get_part_definition(part_id).parameter_names
    )


def _metrics_from_row(row: dict[str, str]) -> dict[str, float | None]:
    return {
        key: _float_or_none(row.get(key))
        for key in (
            "volume_m3",
            "mass_kg",
            "max_stress_mpa",
            "factor_of_safety",
            "max_deflection_mm",
            "objective_value",
        )
    }


def _float_or_none(value: str | object | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _write_candidates_csv(
    path: Path,
    candidates: list[dict[str, object]],
    part_id: str,
) -> None:
    names = get_part_definition(part_id).parameter_names
    fields = [
        "candidate_id",
        "part_id",
        "source",
        "run_id",
        "iteration",
        *names,
        "volume_m3",
        "mass_kg",
        "max_stress_mpa",
        "factor_of_safety",
        "max_deflection_mm",
        "objective_value",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for candidate in candidates:
            metrics = dict(candidate["analytical_metrics"])
            parameters = dict(candidate["parameters"])
            row = {
                "candidate_id": candidate["candidate_id"],
                "part_id": part_id,
                "source": candidate["source"],
                "run_id": candidate["run_id"],
                "iteration": candidate["iteration"],
                **{name: parameters[name] for name in names},
                **{key: metrics.get(key) for key in fields if key in metrics},
            }
            writer.writerow(row)


def _write_markdown_checklist(
    path: Path,
    candidates: list[dict[str, object]],
    *,
    part_id: str,
    min_fos: float,
    max_deflection_mm: float,
) -> None:
    definition = get_part_definition(part_id)
    lines = [
        f"# Fusion Validation Checklist: {definition.name}",
        "",
        "For each candidate:",
        "",
        "1. Place its request JSON at `data/runs/active/request.json`.",
        "2. Let `NEMOBridge` generate/update the native model and export STEP.",
        "3. Confirm the named boundary faces, solve the Static Stress study manually, and record results.",
        "",
        "| Candidate | Analytical mass kg | Analytical FOS | Analytical deflection mm | Fusion mass kg | Fusion max stress MPa | Fusion FOS | Fusion deflection mm | Pass? | Notes |",
        "| :-- | --: | --: | --: | --: | --: | --: | --: | :-- | :-- |",
    ]
    for candidate in candidates:
        metrics = dict(candidate["analytical_metrics"])
        lines.append(
            f"| {candidate['candidate_id']} | {_fmt(metrics.get('mass_kg'))} | "
            f"{_fmt(metrics.get('factor_of_safety'))} | "
            f"{_fmt(metrics.get('max_deflection_mm'))} |  |  |  |  |  |  |"
        )
    lines.extend(
        [
            "",
            f"Pass criteria: FOS >= {min_fos:g} and max deflection <= {max_deflection_mm:g} mm.",
            "",
            "Report wording: best design found within this parameterized search.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _fmt(value: object) -> str:
    return "" if value is None or value == "" else f"{float(value):.6g}"
