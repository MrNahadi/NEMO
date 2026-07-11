"""Part-aware configuration with backward-compatible bracket constants."""

from __future__ import annotations

from typing import Mapping, Sequence

from .parts import DEFAULT_PART_ID, ParameterSpec, PartDefinition, get_part_definition


BRACKET_DEFINITION = get_part_definition(DEFAULT_PART_ID)
PARAMETER_SPECS: tuple[ParameterSpec, ...] = BRACKET_DEFINITION.parameters
PARAMETER_NAMES: tuple[str, ...] = BRACKET_DEFINITION.parameter_names
BASELINE_PARAMETERS_MM: dict[str, float] = BRACKET_DEFINITION.baseline_parameters
BOUNDS_MM: dict[str, tuple[float, float]] = BRACKET_DEFINITION.bounds

BOLT_HOLE_DIAMETER_MM = float(BRACKET_DEFINITION.fixed_geometry["bolt_hole_diameter_mm"])
BOLT_HOLE_COUNT = int(BRACKET_DEFINITION.fixed_geometry["bolt_hole_count"])
RIB_COUNT = int(BRACKET_DEFINITION.fixed_geometry["rib_count"])

MATERIAL_NAME = BRACKET_DEFINITION.material.name
DENSITY_KG_M3 = BRACKET_DEFINITION.material.density_kg_m3
YIELD_STRENGTH_MPA = BRACKET_DEFINITION.material.yield_strength_mpa
ELASTIC_MODULUS_PA = BRACKET_DEFINITION.material.elastic_modulus_pa
DESIGN_LOAD_N = float(BRACKET_DEFINITION.load["design_load_n"])
MIN_FACTOR_OF_SAFETY = BRACKET_DEFINITION.constraints.min_factor_of_safety
MAX_DEFLECTION_MM = BRACKET_DEFINITION.constraints.max_deflection_mm
PENALTY_WEIGHT = BRACKET_DEFINITION.constraints.penalty_weight
FAILED_OBJECTIVE_VALUE = 1.0e9

EQUIPMENT_MASS_KG = float(BRACKET_DEFINITION.load["equipment_mass_kg"])
DYNAMIC_AMPLIFICATION_FACTOR = float(BRACKET_DEFINITION.load["dynamic_factor"])
GRAVITY_M_S2 = 9.81


def parameter_vector(
    parameters: Mapping[str, float],
    part_id: str = DEFAULT_PART_ID,
) -> list[float]:
    definition = get_part_definition(part_id)
    return [float(parameters[name]) for name in definition.parameter_names]


def baseline_vector(part_id: str = DEFAULT_PART_ID) -> list[float]:
    definition = get_part_definition(part_id)
    return parameter_vector(definition.baseline_parameters, part_id)


def validate_parameters(
    parameters: Mapping[str, float],
    part_id: str = DEFAULT_PART_ID,
) -> list[str]:
    definition = get_part_definition(part_id)
    errors: list[str] = []
    for spec in definition.parameters:
        if spec.name not in parameters:
            errors.append(f"Missing parameter: {spec.name}")
            continue
        value = float(parameters[spec.name])
        if value < spec.lower or value > spec.upper:
            errors.append(
                f"{spec.name}={value:g} {spec.unit} is outside "
                f"[{spec.lower:g}, {spec.upper:g}] {spec.unit}"
            )
    extra = sorted(set(parameters) - set(definition.parameter_names))
    if extra:
        errors.append("Unknown parameters: " + ", ".join(extra))
    return errors


def clip_parameters(
    parameters: Mapping[str, float],
    part_id: str = DEFAULT_PART_ID,
) -> dict[str, float]:
    definition = get_part_definition(part_id)
    return {
        spec.name: min(max(float(parameters[spec.name]), spec.lower), spec.upper)
        for spec in definition.parameters
    }


def physical_to_scaled(
    parameters: Mapping[str, float],
    part_id: str = DEFAULT_PART_ID,
) -> list[float]:
    definition = get_part_definition(part_id)
    return [
        (float(parameters[spec.name]) - spec.lower) / (spec.upper - spec.lower)
        for spec in definition.parameters
    ]


def scaled_to_physical(
    values: Sequence[float],
    part_id: str = DEFAULT_PART_ID,
) -> dict[str, float]:
    definition = get_part_definition(part_id)
    if len(values) != len(definition.parameters):
        raise ValueError(f"Expected {len(definition.parameters)} values, got {len(values)}")
    return {
        spec.name: spec.lower
        + min(max(float(value), 0.0), 1.0) * (spec.upper - spec.lower)
        for value, spec in zip(values, definition.parameters)
    }


def resolve_definition(part: str | PartDefinition = DEFAULT_PART_ID) -> PartDefinition:
    return part if isinstance(part, PartDefinition) else get_part_definition(part)
