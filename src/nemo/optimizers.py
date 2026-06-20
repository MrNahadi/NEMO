"""Optimization routines for NEMO."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .config import (
    BASELINE_PARAMETERS_MM,
    FAILED_OBJECTIVE_VALUE,
    PARAMETER_SPECS,
    physical_to_scaled,
    scaled_to_physical,
)
from .evaluation import evaluate_request, make_run_id
from .logger import append_evaluation, cache_key_from_parameters
from .schemas import EvaluationRequest, EvaluationResponse


Objective = Callable[[list[float]], float]


@dataclass(frozen=True)
class NelderMeadResult:
    best_scaled: list[float]
    best_parameters_mm: dict[str, float]
    best_objective: float
    evaluations: int
    iterations: int


def nelder_mead(
    objective: Objective,
    start_scaled: list[float],
    *,
    max_iter: int = 80,
    initial_step: float = 0.12,
    tolerance: float = 1.0e-6,
) -> tuple[list[float], float, int, int]:
    """Pure-Python bounded Nelder-Mead on scaled [0, 1] variables."""

    n = len(start_scaled)
    simplex = [_clip_scaled(start_scaled, expected_len=n)]
    for index in range(n):
        vertex = list(start_scaled)
        vertex[index] += initial_step
        if vertex[index] > 1.0:
            vertex[index] = start_scaled[index] - initial_step
        simplex.append(_clip_scaled(vertex, expected_len=n))

    values = [objective(vertex) for vertex in simplex]
    evaluations = len(values)

    alpha = 1.0
    gamma = 2.0
    rho = 0.5
    sigma = 0.5

    completed_iterations = 0
    for completed_iterations in range(1, max_iter + 1):
        order = sorted(range(len(simplex)), key=lambda i: values[i])
        simplex = [simplex[i] for i in order]
        values = [values[i] for i in order]

        if max(values) - min(values) < tolerance:
            break

        centroid = [
            sum(vertex[dim] for vertex in simplex[:-1]) / n for dim in range(n)
        ]
        worst = simplex[-1]

        reflected = _clip_scaled(
            [centroid[dim] + alpha * (centroid[dim] - worst[dim]) for dim in range(n)],
            expected_len=n,
        )
        reflected_value = objective(reflected)
        evaluations += 1

        if values[0] <= reflected_value < values[-2]:
            simplex[-1] = reflected
            values[-1] = reflected_value
            continue

        if reflected_value < values[0]:
            expanded = _clip_scaled(
                [
                    centroid[dim] + gamma * (reflected[dim] - centroid[dim])
                    for dim in range(n)
                ],
                expected_len=n,
            )
            expanded_value = objective(expanded)
            evaluations += 1
            if expanded_value < reflected_value:
                simplex[-1] = expanded
                values[-1] = expanded_value
            else:
                simplex[-1] = reflected
                values[-1] = reflected_value
            continue

        contracted = _clip_scaled(
            [centroid[dim] + rho * (worst[dim] - centroid[dim]) for dim in range(n)],
            expected_len=n,
        )
        contracted_value = objective(contracted)
        evaluations += 1
        if contracted_value < values[-1]:
            simplex[-1] = contracted
            values[-1] = contracted_value
            continue

        best = simplex[0]
        for index in range(1, len(simplex)):
            simplex[index] = _clip_scaled(
                [best[dim] + sigma * (simplex[index][dim] - best[dim]) for dim in range(n)],
                expected_len=n,
            )
            values[index] = objective(simplex[index])
        evaluations += len(simplex) - 1

    order = sorted(range(len(simplex)), key=lambda i: values[i])
    best_index = order[0]
    return simplex[best_index], values[best_index], evaluations, completed_iterations


def optimize_analytical(
    *,
    run_id: str | None = None,
    start_parameters_mm: dict[str, float] | None = None,
    max_iter: int = 80,
    output_csv: str | Path | None = None,
) -> NelderMeadResult:
    """Run bounded Nelder-Mead using the analytical fallback evaluator."""

    active_run_id = run_id or make_run_id()
    start_parameters = start_parameters_mm or BASELINE_PARAMETERS_MM
    start_scaled = physical_to_scaled(start_parameters)
    cache: dict[tuple[float, ...], EvaluationResponse] = {}
    iteration_counter = 0

    def objective(scaled: list[float]) -> float:
        nonlocal iteration_counter
        parameters = scaled_to_physical(scaled)
        key = cache_key_from_parameters(parameters)
        if key in cache:
            response = cache[key]
            return response.metrics.objective_value or FAILED_OBJECTIVE_VALUE

        request = EvaluationRequest(
            run_id=active_run_id,
            iteration=iteration_counter,
            mode="analytical",
            parameters_mm=parameters,
        )
        iteration_counter += 1
        response = evaluate_request(request)
        cache[key] = response
        if output_csv is not None:
            append_evaluation(output_csv, request, response)
        return response.metrics.objective_value or FAILED_OBJECTIVE_VALUE

    best_scaled, best_value, evaluations, iterations = nelder_mead(
        objective,
        start_scaled,
        max_iter=max_iter,
    )
    return NelderMeadResult(
        best_scaled=best_scaled,
        best_parameters_mm=scaled_to_physical(best_scaled),
        best_objective=best_value,
        evaluations=evaluations,
        iterations=iterations,
    )


def _clip_scaled(values: list[float], *, expected_len: int | None = None) -> list[float]:
    expected = expected_len or len(PARAMETER_SPECS)
    if len(values) != expected:
        raise ValueError(f"Expected {expected} scaled values")
    return [min(max(float(value), 0.0), 1.0) for value in values]
