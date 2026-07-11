"""First-order analytical screening models for registered NEMO parts."""

from __future__ import annotations

import math
from typing import Mapping

from .registry import PartDefinition


def analytical_values(
    definition: PartDefinition,
    parameters: Mapping[str, float],
) -> tuple[float, float, float, float, float]:
    """Return volume, mass, stress, FOS, and deflection."""

    evaluators = {
        "bracket": _bracket_values,
        "padeye": _padeye_values,
        "stabilizer": _stabilizer_values,
    }
    try:
        return evaluators[definition.analytical_model](definition, parameters)
    except KeyError as exc:
        raise ValueError(f"No analytical model for '{definition.analytical_model}'") from exc


def _bracket_values(
    definition: PartDefinition,
    p: Mapping[str, float],
) -> tuple[float, float, float, float, float]:
    length = p["baseplate_length"] / 1000.0
    width = p["baseplate_width"] / 1000.0
    base_thickness = p["baseplate_thickness"] / 1000.0
    rib_height = p["rib_height"] / 1000.0
    rib_thickness = p["rib_thickness"] / 1000.0
    fillet_radius = p["fillet_radius"] / 1000.0
    bolt_diameter = float(definition.fixed_geometry["bolt_hole_diameter_mm"]) / 1000.0
    bolt_count = int(definition.fixed_geometry["bolt_hole_count"])
    rib_count = int(definition.fixed_geometry["rib_count"])

    base_volume = length * width * base_thickness
    hole_volume = bolt_count * math.pi * (bolt_diameter / 2.0) ** 2 * base_thickness
    rib_volume = rib_count * 0.5 * length * rib_height * rib_thickness
    fillet_volume = rib_count * 0.25 * math.pi * fillet_radius**2 * max(width * 0.35, rib_thickness)
    volume = max(base_volume - hole_volume + rib_volume + fillet_volume, 1.0e-9)

    load = float(definition.load["design_load_n"])
    lever_arm = max(0.03, 0.35 * length + 0.02)
    moment = load * lever_arm
    base_z = width * base_thickness**2 / 6.0
    rib_z = rib_count * rib_thickness * rib_height**2 / 6.0 * 0.65
    stress_concentration = max(1.08, 1.35 - p["fillet_radius"] / 40.0)
    stress_mpa = moment / max(base_z + rib_z, 1.0e-12) * stress_concentration / 1.0e6

    base_i = width * base_thickness**3 / 12.0
    rib_i = rib_count * rib_thickness * rib_height**3 / 36.0 * 0.45
    deflection_mm = (
        load
        * lever_arm**3
        / (3.0 * definition.material.elastic_modulus_pa * max(base_i + rib_i, 1.0e-14))
        * 1000.0
    )
    mass = volume * definition.material.density_kg_m3
    fos = definition.material.yield_strength_mpa / max(stress_mpa, 1.0e-9)
    return volume, mass, stress_mpa, fos, deflection_mm


def _padeye_values(
    definition: PartDefinition,
    p: Mapping[str, float],
) -> tuple[float, float, float, float, float]:
    base_length = p["base_length"] / 1000.0
    base_width = p["base_width"] / 1000.0
    base_thickness = p["base_thickness"] / 1000.0
    lug_height = p["lug_height"] / 1000.0
    lug_thickness = p["lug_thickness"] / 1000.0
    neck_width = p["neck_width"] / 1000.0
    gusset_height = p["gusset_height"] / 1000.0
    gusset_thickness = p["gusset_thickness"] / 1000.0
    fillet_radius = p["fillet_radius"] / 1000.0
    pin_diameter = float(definition.fixed_geometry["pin_hole_diameter_mm"]) / 1000.0

    lug_root_width = min(base_length * 0.62, neck_width * 1.8)
    lug_area = 0.5 * (lug_root_width + neck_width) * lug_height
    lug_area += 0.25 * math.pi * neck_width**2
    hole_area = math.pi * (pin_diameter / 2.0) ** 2
    lug_volume = max(lug_area - hole_area, 1.0e-8) * lug_thickness
    gusset_run = min(base_width * 0.42, lug_height * 0.72)
    gusset_volume = 2.0 * 0.5 * gusset_run * gusset_height * gusset_thickness
    fillet_volume = math.pi * fillet_radius**2 * (lug_thickness + 2.0 * gusset_thickness) * 0.35
    volume = base_length * base_width * base_thickness + lug_volume + gusset_volume + fillet_volume

    load = float(definition.load["design_load_n"])
    net_area = max((neck_width - pin_diameter) * lug_thickness, 1.0e-9)
    bearing_area = max(pin_diameter * lug_thickness, 1.0e-9)
    edge_distance = max((neck_width - pin_diameter) / 2.0, 0.012)
    shear_out_area = max(2.0 * edge_distance * lug_thickness, 1.0e-9)
    kt = 1.8 + 0.020 / max(fillet_radius, 0.001)
    net_stress = load / net_area * kt
    bearing_stress = load / bearing_area * 1.35
    shear_equivalent = math.sqrt(3.0) * load / shear_out_area

    lateral_load = 0.25 * load
    lug_i = lug_thickness * lug_root_width**3 / 12.0
    gusset_i = 2.0 * gusset_thickness * gusset_height**3 / 36.0 * 0.55
    section_i = max(lug_i + gusset_i, 1.0e-12)
    bending_stress = lateral_load * lug_height * (lug_root_width / 2.0) / section_i
    stress_mpa = max(net_stress, bearing_stress, shear_equivalent, bending_stress) / 1.0e6

    axial_deflection = load * lug_height / (
        definition.material.elastic_modulus_pa * net_area
    )
    lateral_deflection = lateral_load * lug_height**3 / (
        3.0 * definition.material.elastic_modulus_pa * section_i
    )
    deflection_mm = math.hypot(axial_deflection, lateral_deflection) * 1000.0
    mass = volume * definition.material.density_kg_m3
    fos = definition.material.yield_strength_mpa / max(stress_mpa, 1.0e-9)
    return volume, mass, stress_mpa, fos, deflection_mm


def _stabilizer_values(
    definition: PartDefinition,
    p: Mapping[str, float],
) -> tuple[float, float, float, float, float]:
    geometry = definition.fixed_geometry
    span = float(geometry["span_mm"]) / 1000.0
    root_chord = float(geometry["root_chord_mm"]) / 1000.0
    tip_chord = float(geometry["tip_chord_mm"]) / 1000.0
    flange_length = float(geometry["root_flange_length_mm"]) / 1000.0
    flange_width = float(geometry["root_flange_width_mm"]) / 1000.0
    flange_thickness = float(geometry["root_flange_thickness_mm"]) / 1000.0
    skin = p["skin_thickness"] / 1000.0
    front_t = p["front_spar_thickness"] / 1000.0
    rear_t = p["rear_spar_thickness"] / 1000.0
    rib_t = p["rib_thickness"] / 1000.0
    insert_length = p["root_insert_length"] / 1000.0
    insert_t = p["root_insert_thickness"] / 1000.0
    root_fillet = p["root_fillet_radius"] / 1000.0

    planform_area = 0.5 * (root_chord + tip_chord) * span
    wetted_area = 2.06 * planform_area
    skin_volume = wetted_area * skin
    average_chord = 0.5 * (root_chord + tip_chord)
    front_height = _naca_full_thickness(average_chord, p["front_spar_position"] / 100.0)
    rear_height = _naca_full_thickness(average_chord, p["rear_spar_position"] / 100.0)
    spar_volume = span * (front_height * front_t + rear_height * rear_t)

    rib_volume = 0.0
    for station in geometry["rib_stations"]:
        chord = root_chord + (tip_chord - root_chord) * float(station)
        section_area = 0.1028 * chord**2
        rib_volume += max(section_area - 2.0 * skin * chord, section_area * 0.45) * rib_t
    insert_height = 0.15 * root_chord
    insert_volume = insert_length * insert_height * insert_t
    flange_volume = flange_length * flange_width * flange_thickness
    fillet_volume = 0.5 * math.pi * root_fillet**2 * root_chord
    volume = skin_volume + spar_volume + rib_volume + insert_volume + flange_volume + fillet_volume

    root_depth = 0.15 * root_chord
    cap_width = max(p["rear_spar_position"] - p["front_spar_position"], 10.0) / 100.0 * root_chord
    skin_i = 2.0 * skin * cap_width * (root_depth / 2.0 - skin / 2.0) ** 2
    front_i = front_t * root_depth**3 / 12.0
    rear_i = rear_t * (root_depth * 0.72) ** 3 / 12.0
    insert_i = insert_t * root_depth**3 / 12.0 * min(insert_length / span, 1.0)
    section_i = max(skin_i + front_i + rear_i + insert_i, 1.0e-10)

    load = float(definition.load["design_load_n"])
    root_moment = load * span * 0.40
    kt = max(1.4, 2.8 - root_fillet / 0.030)
    bending_stress = root_moment * (root_depth / 2.0) / section_i
    shear_area = max((front_t + rear_t) * root_depth, 1.0e-8)
    shear_stress = load / shear_area
    stress_mpa = math.sqrt((kt * bending_stress) ** 2 + 3.0 * shear_stress**2) / 1.0e6
    deflection_mm = (
        load
        * span**3
        / (8.0 * definition.material.elastic_modulus_pa * section_i)
        * 1000.0
    )
    mass = volume * definition.material.density_kg_m3
    fos = definition.material.yield_strength_mpa / max(stress_mpa, 1.0e-9)
    return volume, mass, stress_mpa, fos, deflection_mm


def _naca_full_thickness(chord: float, x_fraction: float, thickness_ratio: float = 0.15) -> float:
    x = min(max(x_fraction, 0.001), 0.999)
    half = 5.0 * thickness_ratio * chord * (
        0.2969 * math.sqrt(x)
        - 0.1260 * x
        - 0.3516 * x**2
        + 0.2843 * x**3
        - 0.1015 * x**4
    )
    return max(2.0 * half, chord * 0.02)
