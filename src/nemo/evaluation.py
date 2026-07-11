"""Part-aware analytical and Fusion evaluation dispatch."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Mapping

from .config import FAILED_OBJECTIVE_VALUE, validate_parameters
from .parts import DEFAULT_PART_ID, PartDefinition, get_part_definition
from .parts.analytical import analytical_values
from .schemas import EvaluationRequest, EvaluationResponse, Metrics


def make_run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def evaluate_design(
    parameters: Mapping[str, float] | None = None,
    *,
    part_id: str = DEFAULT_PART_ID,
    run_id: str = "manual",
    iteration: int = 0,
    mode: str = "analytical",
    artifact_formats: tuple[str, ...] = (),
) -> EvaluationResponse:
    definition = get_part_definition(part_id)
    request = EvaluationRequest(
        run_id=run_id,
        iteration=iteration,
        mode=mode,
        part_id=definition.part_id,
        parameters=dict(parameters or definition.baseline_parameters),
        artifact_formats=artifact_formats,
    )
    return evaluate_request(request)


def evaluate_request(request: EvaluationRequest) -> EvaluationResponse:
    try:
        definition = get_part_definition(request.part_id)
    except KeyError as exc:
        return _failed_response(request, str(exc))

    if request.mode not in ("analytical", "fusion", "fusion_cad", "open_fea"):
        return _failed_response(request, f"Mode '{request.mode}' is not available.")
    if request.mode == "open_fea":
        return _failed_response(
            request,
            "The open_fea evaluator contract is reserved for the Gmsh/CalculiX stage and is not configured.",
        )

    errors = validate_parameters(request.parameters, definition.part_id)
    if errors:
        return _failed_response(request, "; ".join(errors))

    if request.mode in ("fusion", "fusion_cad"):
        return _evaluate_fusion(request, definition)

    volume, mass, stress, fos, deflection = analytical_values(
        definition, request.parameters
    )
    partial = Metrics(mass, stress, fos, deflection, None, volume)
    return EvaluationResponse(
        run_id=request.run_id,
        iteration=request.iteration,
        status="ok",
        metrics=replace(partial, objective_value=objective_from_metrics(partial, definition)),
        part_id=definition.part_id,
        schema_version=2,
    )


def is_feasible(
    metrics: Metrics,
    part: str | PartDefinition = DEFAULT_PART_ID,
) -> bool:
    definition = part if isinstance(part, PartDefinition) else get_part_definition(part)
    return (
        metrics.factor_of_safety is not None
        and metrics.max_deflection_mm is not None
        and metrics.factor_of_safety >= definition.constraints.min_factor_of_safety
        and metrics.max_deflection_mm <= definition.constraints.max_deflection_mm
    )


def objective_from_metrics(
    metrics: Metrics,
    part: str | PartDefinition = DEFAULT_PART_ID,
) -> float:
    definition = part if isinstance(part, PartDefinition) else get_part_definition(part)
    if (
        metrics.mass_kg is None
        or metrics.factor_of_safety is None
        or metrics.max_deflection_mm is None
    ):
        return FAILED_OBJECTIVE_VALUE

    constraints = definition.constraints
    fos_shortfall = max(0.0, constraints.min_factor_of_safety - metrics.factor_of_safety)
    deflection_excess = max(0.0, metrics.max_deflection_mm - constraints.max_deflection_mm)
    fos_penalty = (fos_shortfall / constraints.min_factor_of_safety) ** 2
    deflection_penalty = (deflection_excess / constraints.max_deflection_mm) ** 2
    return metrics.mass_kg + constraints.penalty_weight * (fos_penalty + deflection_penalty)


def _evaluate_fusion(
    request: EvaluationRequest,
    definition: PartDefinition,
) -> EvaluationResponse:
    from .handshake import wait_for_response, write_request

    run_dir = Path("data/runs/active")
    run_dir.mkdir(parents=True, exist_ok=True)
    write_request(run_dir, request)
    try:
        response = wait_for_response(
            run_dir,
            run_id=request.run_id,
            iteration=request.iteration,
            timeout_s=120.0,
        )
    except TimeoutError as exc:
        return _failed_response(request, f"Fusion timeout: {exc}")

    # CAD-only Fusion responses intentionally do not fabricate structural metrics.
    return replace(response, part_id=definition.part_id, schema_version=2)


def _failed_response(request: EvaluationRequest, error: str) -> EvaluationResponse:
    return EvaluationResponse(
        run_id=request.run_id,
        iteration=request.iteration,
        status="failed",
        metrics=Metrics(None, None, None, None, FAILED_OBJECTIVE_VALUE, None),
        error=error,
        part_id=request.part_id,
        schema_version=2,
    )
