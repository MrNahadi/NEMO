"""Load packaged, unit-aware NEMO part definitions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from typing import Any


DEFAULT_PART_ID = "bracket"


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    unit: str
    lower: float
    upper: float
    baseline: float
    description: str

    # Compatibility aliases retained for the original bracket API.
    @property
    def lower_mm(self) -> float:
        return self.lower

    @property
    def upper_mm(self) -> float:
        return self.upper

    @property
    def baseline_mm(self) -> float:
        return self.baseline


@dataclass(frozen=True)
class MaterialSpec:
    name: str
    density_kg_m3: float
    yield_strength_mpa: float
    elastic_modulus_pa: float
    poisson_ratio: float


@dataclass(frozen=True)
class ConstraintSpec:
    min_factor_of_safety: float
    max_deflection_mm: float
    penalty_weight: float


@dataclass(frozen=True)
class PartDefinition:
    part_id: str
    name: str
    description: str
    analytical_model: str
    parameters: tuple[ParameterSpec, ...]
    material: MaterialSpec
    constraints: ConstraintSpec
    load: dict[str, Any]
    fixed_geometry: dict[str, Any]
    boundary_tags: tuple[str, ...]

    @property
    def parameter_names(self) -> tuple[str, ...]:
        return tuple(spec.name for spec in self.parameters)

    @property
    def baseline_parameters(self) -> dict[str, float]:
        return {spec.name: spec.baseline for spec in self.parameters}

    @property
    def bounds(self) -> dict[str, tuple[float, float]]:
        return {spec.name: (spec.lower, spec.upper) for spec in self.parameters}


_CACHE: dict[str, PartDefinition] = {}


def list_part_definitions() -> tuple[PartDefinition, ...]:
    return tuple(get_part_definition(part_id) for part_id in ("bracket", "padeye", "stabilizer"))


def get_part_definition(part_id: str = DEFAULT_PART_ID) -> PartDefinition:
    normalized = str(part_id).strip().lower()
    if normalized in _CACHE:
        return _CACHE[normalized]

    resource = files("nemo.parts.definitions").joinpath(f"{normalized}.json")
    try:
        payload = json.loads(resource.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        choices = ", ".join(definition.part_id for definition in list_part_definitions())
        raise KeyError(f"Unknown part_id '{part_id}'. Available parts: {choices}") from exc

    definition = _definition_from_dict(payload)
    _CACHE[normalized] = definition
    return definition


def _definition_from_dict(payload: dict[str, Any]) -> PartDefinition:
    material = payload["material"]
    constraints = payload["constraints"]
    return PartDefinition(
        part_id=str(payload["part_id"]),
        name=str(payload["name"]),
        description=str(payload["description"]),
        analytical_model=str(payload["analytical_model"]),
        parameters=tuple(
            ParameterSpec(
                name=str(item["name"]),
                unit=str(item["unit"]),
                lower=float(item["lower"]),
                upper=float(item["upper"]),
                baseline=float(item["baseline"]),
                description=str(item["description"]),
            )
            for item in payload["parameters"]
        ),
        material=MaterialSpec(
            name=str(material["name"]),
            density_kg_m3=float(material["density_kg_m3"]),
            yield_strength_mpa=float(material["yield_strength_mpa"]),
            elastic_modulus_pa=float(material["elastic_modulus_pa"]),
            poisson_ratio=float(material["poisson_ratio"]),
        ),
        constraints=ConstraintSpec(
            min_factor_of_safety=float(constraints["min_factor_of_safety"]),
            max_deflection_mm=float(constraints["max_deflection_mm"]),
            penalty_weight=float(constraints.get("penalty_weight", 100.0)),
        ),
        load=dict(payload["load"]),
        fixed_geometry=dict(payload["fixed_geometry"]),
        boundary_tags=tuple(str(value) for value in payload["boundary_tags"]),
    )
