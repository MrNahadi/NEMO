"""Bounded, part-aware Nelder-Mead optimization routines."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .config import FAILED_OBJECTIVE_VALUE, physical_to_scaled, scaled_to_physical
from .evaluation import evaluate_request, make_run_id
from .logger import append_evaluation, cache_key_from_parameters
from .parts import DEFAULT_PART_ID, get_part_definition
from .schemas import EvaluationRequest, EvaluationResponse


Objective = Callable[[list[float]], float]


@dataclass(frozen=True)
class NelderMeadResult:
    best_scaled: list[float]
    best_parameters_mm: dict[str, float]
    best_objective: float
    evaluations: int
    iterations: int
    part_id: str = DEFAULT_PART_ID

    @property
    def best_parameters(self) -> dict[str, float]:
        return self.best_parameters_mm


def nelder_mead(
    objective: Objective,
    start_scaled: list[float],
    *,
    max_iter: int = 80,
    initial_step: float = 0.12,
    tolerance: float = 1.0e-6,
) -> tuple[list[float], float, int, int]:
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
    alpha, gamma, rho, sigma = 1.0, 2.0, 0.5, 0.5
    completed_iterations = 0

    for completed_iterations in range(1, max_iter + 1):
        order = sorted(range(len(simplex)), key=lambda i: values[i])
        simplex = [simplex[i] for i in order]
        values = [values[i] for i in order]
        if max(values) - min(values) < tolerance:
            break

        centroid = [sum(v[d] for v in simplex[:-1]) / n for d in range(n)]
        worst = simplex[-1]
        reflected = _clip_scaled(
            [centroid[d] + alpha * (centroid[d] - worst[d]) for d in range(n)], n
        )
        reflected_value = objective(reflected)
        evaluations += 1

        if values[0] <= reflected_value < values[-2]:
            simplex[-1], values[-1] = reflected, reflected_value
            continue
        if reflected_value < values[0]:
            expanded = _clip_scaled(
                [centroid[d] + gamma * (reflected[d] - centroid[d]) for d in range(n)], n
            )
            expanded_value = objective(expanded)
            evaluations += 1
            simplex[-1], values[-1] = (
                (expanded, expanded_value)
                if expanded_value < reflected_value
                else (reflected, reflected_value)
            )
            continue

        contracted = _clip_scaled(
            [centroid[d] + rho * (worst[d] - centroid[d]) for d in range(n)], n
        )
        contracted_value = objective(contracted)
        evaluations += 1
        if contracted_value < values[-1]:
            simplex[-1], values[-1] = contracted, contracted_value
            continue

        best = simplex[0]
        for index in range(1, len(simplex)):
            simplex[index] = _clip_scaled(
                [best[d] + sigma * (simplex[index][d] - best[d]) for d in range(n)], n
            )
            values[index] = objective(simplex[index])
        evaluations += len(simplex) - 1

    best_index = min(range(len(simplex)), key=lambda i: values[i])
    return simplex[best_index], values[best_index], evaluations, completed_iterations


def optimize_analytical(
    *,
    part_id: str = DEFAULT_PART_ID,
    run_id: str | None = None,
    start_parameters_mm: dict[str, float] | None = None,
    start_parameters: dict[str, float] | None = None,
    max_iter: int = 80,
    output_csv: str | Path | None = None,
    mode: str = "analytical",
) -> NelderMeadResult:
    definition = get_part_definition(part_id)
    active_run_id = run_id or make_run_id()
    start = start_parameters or start_parameters_mm or definition.baseline_parameters
    start_scaled = physical_to_scaled(start, part_id)
    cache: dict[tuple[float, ...], EvaluationResponse] = {}
    iteration_counter = 0

    def objective(scaled: list[float]) -> float:
        nonlocal iteration_counter
        parameters = scaled_to_physical(scaled, part_id)
        key = cache_key_from_parameters(parameters, part_id=part_id)
        if key in cache:
            value = cache[key].metrics.objective_value
            return FAILED_OBJECTIVE_VALUE if value is None else value

        request = EvaluationRequest(
            run_id=active_run_id,
            iteration=iteration_counter,
            mode=mode,
            part_id=part_id,
            parameters=parameters,
        )
        iteration_counter += 1
        response = evaluate_request(request)
        cache[key] = response
        if output_csv is not None:
            append_evaluation(output_csv, request, response)
        value = response.metrics.objective_value
        return FAILED_OBJECTIVE_VALUE if value is None else value

    best_scaled, best_value, evaluations, iterations = nelder_mead(
        objective, start_scaled, max_iter=max_iter
    )
    return NelderMeadResult(
        best_scaled=best_scaled,
        best_parameters_mm=scaled_to_physical(best_scaled, part_id),
        best_objective=best_value,
        evaluations=evaluations,
        iterations=iterations,
        part_id=part_id,
    )


def _clip_scaled(values: list[float], expected_len: int | None = None) -> list[float]:
    expected = expected_len or len(values)
    if len(values) != expected:
        raise ValueError(f"Expected {expected} scaled values")
    return [min(max(float(value), 0.0), 1.0) for value in values]
