"""Project constants and parameter scaling helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    lower_mm: float
    upper_mm: float
    baseline_mm: float
    description: str


PARAMETER_SPECS: tuple[ParameterSpec, ...] = (
    ParameterSpec("baseplate_length", 100.0, 200.0, 150.0, "Mounting baseplate length"),
    ParameterSpec("baseplate_width", 80.0, 150.0, 100.0, "Mounting baseplate width"),
    ParameterSpec("baseplate_thickness", 4.0, 15.0, 8.0, "Baseplate thickness"),
    ParameterSpec("rib_height", 20.0, 60.0, 40.0, "Reinforcing rib/gusset height"),
    ParameterSpec("rib_thickness", 3.0, 10.0, 6.0, "Reinforcing rib/gusset thickness"),
    ParameterSpec("fillet_radius", 2.0, 10.0, 5.0, "Rib-to-baseplate fillet radius"),
)

PARAMETER_NAMES: tuple[str, ...] = tuple(spec.name for spec in PARAMETER_SPECS)
BASELINE_PARAMETERS_MM: dict[str, float] = {
    spec.name: spec.baseline_mm for spec in PARAMETER_SPECS
}
BOUNDS_MM: dict[str, tuple[float, float]] = {
    spec.name: (spec.lower_mm, spec.upper_mm) for spec in PARAMETER_SPECS
}

BOLT_HOLE_DIAMETER_MM = 10.0
BOLT_HOLE_COUNT = 4
RIB_COUNT = 2

MATERIAL_NAME = "Aluminum 6061-T6"
DENSITY_KG_M3 = 2700.0
YIELD_STRENGTH_MPA = 276.0
ELASTIC_MODULUS_PA = 68.9e9

EQUIPMENT_MASS_KG = 50.0
DYNAMIC_AMPLIFICATION_FACTOR = 3.0
GRAVITY_M_S2 = 9.81
DESIGN_LOAD_N = EQUIPMENT_MASS_KG * GRAVITY_M_S2 * DYNAMIC_AMPLIFICATION_FACTOR

MIN_FACTOR_OF_SAFETY = 2.5
MAX_DEFLECTION_MM = 0.5

PENALTY_WEIGHT = 100.0
FAILED_OBJECTIVE_VALUE = 1.0e9


def parameter_vector(parameters_mm: Mapping[str, float]) -> list[float]:
    """Return parameter values in canonical optimizer order."""

    return [float(parameters_mm[name]) for name in PARAMETER_NAMES]


def baseline_vector() -> list[float]:
    return parameter_vector(BASELINE_PARAMETERS_MM)


def validate_parameters(parameters_mm: Mapping[str, float]) -> list[str]:
    """Return validation errors for missing or out-of-range parameters."""

    errors: list[str] = []
    for spec in PARAMETER_SPECS:
        if spec.name not in parameters_mm:
            errors.append(f"Missing parameter: {spec.name}")
            continue
        value = float(parameters_mm[spec.name])
        if value < spec.lower_mm or value > spec.upper_mm:
            errors.append(
                f"{spec.name}={value:g} mm is outside "
                f"[{spec.lower_mm:g}, {spec.upper_mm:g}] mm"
            )
    return errors


def clip_parameters(parameters_mm: Mapping[str, float]) -> dict[str, float]:
    """Clip parameters to configured bounds."""

    clipped: dict[str, float] = {}
    for spec in PARAMETER_SPECS:
        value = float(parameters_mm[spec.name])
        clipped[spec.name] = min(max(value, spec.lower_mm), spec.upper_mm)
    return clipped


def physical_to_scaled(parameters_mm: Mapping[str, float]) -> list[float]:
    """Convert physical millimeter parameters to scaled [0, 1] variables."""

    scaled: list[float] = []
    for spec in PARAMETER_SPECS:
        value = float(parameters_mm[spec.name])
        scaled.append((value - spec.lower_mm) / (spec.upper_mm - spec.lower_mm))
    return scaled


def scaled_to_physical(values: list[float] | tuple[float, ...]) -> dict[str, float]:
    """Convert scaled variables to clipped millimeter parameters."""

    if len(values) != len(PARAMETER_SPECS):
        raise ValueError(f"Expected {len(PARAMETER_SPECS)} values, got {len(values)}")
    parameters: dict[str, float] = {}
    for value, spec in zip(values, PARAMETER_SPECS):
        clipped = min(max(float(value), 0.0), 1.0)
        parameters[spec.name] = spec.lower_mm + clipped * (spec.upper_mm - spec.lower_mm)
    return parameters
