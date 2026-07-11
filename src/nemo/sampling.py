"""Part-aware random and Latin-hypercube sampling."""

from __future__ import annotations

import random

from .parts import DEFAULT_PART_ID, get_part_definition


def random_samples(
    count: int,
    *,
    seed: int | None = None,
    part_id: str = DEFAULT_PART_ID,
) -> list[dict[str, float]]:
    definition = get_part_definition(part_id)
    rng = random.Random(seed)
    return [
        {spec.name: rng.uniform(spec.lower, spec.upper) for spec in definition.parameters}
        for _ in range(max(count, 0))
    ]


def latin_hypercube_samples(
    count: int,
    *,
    seed: int | None = None,
    part_id: str = DEFAULT_PART_ID,
) -> list[dict[str, float]]:
    if count <= 0:
        return []

    definition = get_part_definition(part_id)
    rng = random.Random(seed)
    columns: dict[str, list[float]] = {}
    for spec in definition.parameters:
        values = [
            spec.lower
            + rng.uniform(index / count, (index + 1) / count) * (spec.upper - spec.lower)
            for index in range(count)
        ]
        rng.shuffle(values)
        columns[spec.name] = values
    return [
        {spec.name: columns[spec.name][index] for spec in definition.parameters}
        for index in range(count)
    ]
