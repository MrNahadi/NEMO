"""Analytical structural fallback evaluator for the NEMO bracket."""

from __future__ import annotations

import math
from datetime import datetime
from typing import Mapping

from .config import (
    BOLT_HOLE_COUNT,
    BOLT_HOLE_DIAMETER_MM,
    BASELINE_PARAMETERS_MM,
    DENSITY_KG_M3,
    DESIGN_LOAD_N,
    ELASTIC_MODULUS_PA,
    FAILED_OBJECTIVE_VALUE,
    MAX_DEFLECTION_MM,
    MIN_FACTOR_OF_SAFETY,
    PENALTY_WEIGHT,
    RIB_COUNT,
    YIELD_STRENGTH_MPA,
    validate_parameters,
)
from .schemas import EvaluationRequest, EvaluationResponse, Metrics


def make_run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def evaluate_design(
    parameters_mm: Mapping[str, float] | None = None,
    *,
    run_id: str = "manual",
    iteration: int = 0,
    mode: str = "analytical",
) -> EvaluationResponse:
    """Evaluate a design directly from a parameter mapping."""

    request = EvaluationRequest(
        run_id=run_id,
        iteration=iteration,
        mode=mode,
        parameters_mm=dict(parameters_mm or BASELINE_PARAMETERS_MM),
    )
    return evaluate_request(request)


def evaluate_request(request: EvaluationRequest) -> EvaluationResponse:
    """Evaluate a JSON-style request.

    The current non-Fusion evaluator supports ``mode='analytical'``. Other modes
    return a controlled failure so the logger and optimizer can continue safely.
    """

    if request.mode != "analytical":
        return _failed_response(
            request,
            f"Mode '{request.mode}' is not available in the external evaluator.",
        )

    errors = validate_parameters(request.parameters_mm)
    if errors:
        return _failed_response(request, "; ".join(errors))

    metrics = _analytical_metrics(request.parameters_mm)
    return EvaluationResponse(
        run_id=request.run_id,
        iteration=request.iteration,
        status="ok",
        metrics=metrics,
        error=None,
    )


def is_feasible(metrics: Metrics) -> bool:
    return (
        metrics.factor_of_safety is not None
        and metrics.max_deflection_mm is not None
        and metrics.factor_of_safety >= MIN_FACTOR_OF_SAFETY
        and metrics.max_deflection_mm <= MAX_DEFLECTION_MM
    )


def objective_from_metrics(metrics: Metrics) -> float:
    if (
        metrics.mass_kg is None
        or metrics.factor_of_safety is None
        or metrics.max_deflection_mm is None
    ):
        return FAILED_OBJECTIVE_VALUE

    fos_shortfall = max(0.0, MIN_FACTOR_OF_SAFETY - metrics.factor_of_safety)
    deflection_excess = max(0.0, metrics.max_deflection_mm - MAX_DEFLECTION_MM)

    fos_penalty = (fos_shortfall / MIN_FACTOR_OF_SAFETY) ** 2
    deflection_penalty = (deflection_excess / MAX_DEFLECTION_MM) ** 2

    return metrics.mass_kg + PENALTY_WEIGHT * (fos_penalty + deflection_penalty)


def _failed_response(request: EvaluationRequest, error: str) -> EvaluationResponse:
    return EvaluationResponse(
        run_id=request.run_id,
        iteration=request.iteration,
        status="failed",
        metrics=Metrics(
            mass_kg=None,
            max_stress_mpa=None,
            factor_of_safety=None,
            max_deflection_mm=None,
            objective_value=FAILED_OBJECTIVE_VALUE,
        ),
        error=error,
    )


def _analytical_metrics(parameters_mm: Mapping[str, float]) -> Metrics:
    """Compute a conservative, reportable first-order bracket estimate.

    This is not a replacement for FEA. It is the planned fallback model used to
    guide the optimizer when Fusion Simulation automation is unavailable. The
    final candidates still need Fusion validation.
    """

    length = parameters_mm["baseplate_length"] / 1000.0
    width = parameters_mm["baseplate_width"] / 1000.0
    base_thickness = parameters_mm["baseplate_thickness"] / 1000.0
    rib_height = parameters_mm["rib_height"] / 1000.0
    rib_thickness = parameters_mm["rib_thickness"] / 1000.0
    fillet_radius = parameters_mm["fillet_radius"] / 1000.0
    bolt_diameter = BOLT_HOLE_DIAMETER_MM / 1000.0

    base_volume = length * width * base_thickness
    hole_volume = BOLT_HOLE_COUNT * math.pi * (bolt_diameter / 2.0) ** 2 * base_thickness
    rib_volume = RIB_COUNT * 0.5 * length * rib_height * rib_thickness
    fillet_volume = RIB_COUNT * 0.25 * math.pi * fillet_radius**2 * max(width * 0.35, rib_thickness)
    volume_m3 = max(base_volume - hole_volume + rib_volume + fillet_volume, 1.0e-9)
    mass_kg = volume_m3 * DENSITY_KG_M3

    lever_arm_m = max(0.03, 0.35 * length + 0.02)
    bending_moment_nm = DESIGN_LOAD_N * lever_arm_m

    base_section_modulus = width * base_thickness**2 / 6.0
    rib_section_modulus = RIB_COUNT * rib_thickness * rib_height**2 / 6.0 * 0.65
    section_modulus = max(base_section_modulus + rib_section_modulus, 1.0e-12)

    stress_concentration = max(1.08, 1.35 - parameters_mm["fillet_radius"] / 40.0)
    max_stress_pa = bending_moment_nm / section_modulus * stress_concentration
    max_stress_mpa = max_stress_pa / 1.0e6
    factor_of_safety = YIELD_STRENGTH_MPA / max(max_stress_mpa, 1.0e-9)

    base_second_moment = width * base_thickness**3 / 12.0
    rib_second_moment = RIB_COUNT * rib_thickness * rib_height**3 / 36.0 * 0.45
    second_moment = max(base_second_moment + rib_second_moment, 1.0e-14)
    max_deflection_m = DESIGN_LOAD_N * lever_arm_m**3 / (
        3.0 * ELASTIC_MODULUS_PA * second_moment
    )
    max_deflection_mm = max_deflection_m * 1000.0

    partial = Metrics(
        mass_kg=mass_kg,
        max_stress_mpa=max_stress_mpa,
        factor_of_safety=factor_of_safety,
        max_deflection_mm=max_deflection_mm,
        objective_value=None,
    )
    return Metrics(
        mass_kg=mass_kg,
        max_stress_mpa=max_stress_mpa,
        factor_of_safety=factor_of_safety,
        max_deflection_mm=max_deflection_mm,
        objective_value=objective_from_metrics(partial),
    )
