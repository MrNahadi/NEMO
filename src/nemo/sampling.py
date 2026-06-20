"""Sampling helpers for Week 6 design-space exploration."""

from __future__ import annotations

import random

from .config import PARAMETER_SPECS


def random_samples(count: int, *, seed: int | None = None) -> list[dict[str, float]]:
    rng = random.Random(seed)
    samples: list[dict[str, float]] = []
    for _ in range(count):
        samples.append(
            {
                spec.name: rng.uniform(spec.lower_mm, spec.upper_mm)
                for spec in PARAMETER_SPECS
            }
        )
    return samples


def latin_hypercube_samples(count: int, *, seed: int | None = None) -> list[dict[str, float]]:
    """Generate simple Latin-hypercube samples without external dependencies."""

    if count <= 0:
        return []

    rng = random.Random(seed)
    columns: dict[str, list[float]] = {}
    for spec in PARAMETER_SPECS:
        values: list[float] = []
        span = spec.upper_mm - spec.lower_mm
        for index in range(count):
            low = index / count
            high = (index + 1) / count
            unit = rng.uniform(low, high)
            values.append(spec.lower_mm + unit * span)
        rng.shuffle(values)
        columns[spec.name] = values

    return [
        {spec.name: columns[spec.name][index] for spec in PARAMETER_SPECS}
        for index in range(count)
    ]
