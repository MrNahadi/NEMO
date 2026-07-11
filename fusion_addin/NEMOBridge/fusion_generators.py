"""Native Fusion geometry generators for registered NEMO parts.

Fusion uses centimetres internally. Public NEMO part definitions use the units
declared in their JSON manifests, currently millimetres and unitless percent.
"""

from __future__ import annotations

import json
import math
import os

import adsk.core
import adsk.fusion


ATTRIBUTE_GROUP = "NEMO"
GENERATOR_VERSION = "2.0"
GENERATED_OCCURRENCE_NAME = "NEMO_GENERATED"


def load_definition(config, part_id):
    here = os.path.dirname(__file__)
    directory = config.get(
        "part_definition_dir", "../../src/nemo/parts/definitions"
    )
    if not os.path.isabs(directory):
        directory = os.path.abspath(os.path.join(here, directory))
    path = os.path.join(directory, f"{part_id}.json")
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def generate_part(design, definition, parameters, log):
    """Replace the generated occurrence with a deterministic native model."""

    _remove_previous_geometry(design, log)
    _replace_user_parameters(design, definition, parameters)
    root = design.rootComponent
    occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    component = occurrence.component
    # Newer Fusion Assembly/Hybrid documents expose Occurrence.name as
    # read-only.  Naming the generated object is helpful but must not prevent
    # geometry generation, so use the component name where supported and rely
    # on attributes for deterministic cleanup.
    try:
        component.name = f"NEMO_{definition['part_id']}"
    except Exception as exc:
        log(f"Could not rename generated component: {exc}")
    component.attributes.add(ATTRIBUTE_GROUP, "part_id", definition["part_id"])
    component.attributes.add(ATTRIBUTE_GROUP, "generator_version", GENERATOR_VERSION)

    generators = {
        "bracket": _generate_bracket,
        "padeye": _generate_padeye,
        "stabilizer": _generate_stabilizer,
    }
    generator = generators.get(definition["part_id"])
    if generator is None:
        raise RuntimeError(f"No Fusion generator for {definition['part_id']}")
    selectors = generator(component, definition, parameters, log)
    _assign_material(component, definition["material"]["name"], log)
    design.attributes.add(ATTRIBUTE_GROUP, "part_id", definition["part_id"])
    design.attributes.add(ATTRIBUTE_GROUP, "generator_version", GENERATOR_VERSION)
    return component, selectors


def collect_boundary_metadata(component, selectors):
    payload = {
        "schema_version": 1,
        "units": "cm",
        "component": component.name,
        "generator_version": GENERATOR_VERSION,
        "boundaries": {},
    }
    for role, selector in selectors.items():
        faces = [face for face in component.bRepBodies.item(0).faces] if component.bRepBodies.count else []
        matched = [face for face in faces if _face_matches(face, selector)]
        payload["boundaries"][role] = {
            "selector": selector,
            "faces": [_face_signature(face) for face in matched],
        }
        for face in matched:
            try:
                face.attributes.add(ATTRIBUTE_GROUP, "boundary_role", role)
            except Exception:
                pass
    return payload


def write_boundary_metadata(path, metadata):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
        handle.write("\n")
    os.replace(tmp, path)


def _remove_previous_geometry(design, log):
    root = design.rootComponent
    for index in range(root.occurrences.count - 1, -1, -1):
        occurrence = root.occurrences.item(index)
        component = occurrence.component
        generated = occurrence.name == GENERATED_OCCURRENCE_NAME
        try:
            generated = generated or component.attributes.itemByName(
                ATTRIBUTE_GROUP, "generator_version"
            ) is not None
        except Exception:
            pass
        if generated:
            try:
                occurrence.deleteMe()
            except Exception as exc:
                log(f"Could not remove prior generated occurrence: {exc}")


def _replace_user_parameters(design, definition, values):
    parameters = design.userParameters
    for spec in definition["parameters"]:
        existing = parameters.itemByName(spec["name"])
        unit = "" if spec["unit"] == "%" else spec["unit"]
        expression = str(float(values[spec["name"]]))
        if unit:
            expression += f" {unit}"
        if existing:
            existing.expression = expression
        else:
            parameters.add(
                spec["name"],
                adsk.core.ValueInput.createByString(expression),
                unit,
                spec["description"],
            )


def _generate_bracket(component, definition, p, log):
    length = _cm(p["baseplate_length"])
    width = _cm(p["baseplate_width"])
    thickness = _cm(p["baseplate_thickness"])
    rib_height = _cm(p["rib_height"])
    rib_thickness = _cm(p["rib_thickness"])
    fillet_radius = _cm(p["fillet_radius"])
    bolt_radius = _cm(definition["fixed_geometry"]["bolt_hole_diameter_mm"]) / 2.0

    _extrude_centered_rectangle(
        component, component.xYConstructionPlane, length, width, thickness, "Bracket base"
    )

    # Four mounting holes are positioned symmetrically near the plate corners.
    # Their diameter is fixed by the part manifest and is not optimized.
    hole_x = length / 2.0 - max(1.5 * bolt_radius, length * 0.10)
    hole_y = width / 2.0 - max(1.5 * bolt_radius, width * 0.12)
    for x in (-hole_x, hole_x):
        for y in (-hole_y, hole_y):
            sketch = component.sketches.add(component.xYConstructionPlane)
            sketch.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(x, y, 0), bolt_radius
            )
            _extrude_profile(
                component,
                _largest_profile(sketch),
                thickness,
                adsk.fusion.FeatureOperations.CutFeatureOperation,
                "Bracket mounting hole",
            )

    # The analytical model treats each rib as a full-length triangular plate:
    # 0.5 * baseplate_length * rib_height * rib_thickness.  Build that exact
    # geometry in the X-Z plane and place two ribs symmetrically across Y.
    rib_y_centers = (-width * 0.28, width * 0.28)
    for y_center in rib_y_centers:
        plane_y = y_center - rib_thickness / 2.0
        plane = _offset_plane(
            component, component.xZConstructionPlane, plane_y
        )
        sketch = component.sketches.add(plane)
        model_points = [
            adsk.core.Point3D.create(-length / 2.0, plane_y, thickness),
            adsk.core.Point3D.create(length / 2.0, plane_y, thickness),
            adsk.core.Point3D.create(0, plane_y, thickness + rib_height),
        ]
        points = [sketch.modelToSketchSpace(point) for point in model_points]
        _closed_polyline(sketch, points)
        _extrude_profile(
            component,
            _largest_profile(sketch),
            rib_thickness,
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
            "Bracket rib",
        )
    _try_bracket_fillet(
        component,
        fillet_radius,
        thickness,
        length,
        rib_thickness,
        rib_y_centers,
        log,
    )
    return {
        "fixed_support": {
            "kind": "cylinder",
            "radius": bolt_radius,
            "tolerance": max(0.002, bolt_radius * 0.01),
        },
        "equipment_load": {
            "kind": "upper_rib_face",
            "z_min": thickness + rib_height * 0.25,
            "normal_z_min": 0.05,
        },
    }


def _generate_padeye(component, definition, p, log):
    base_length = _cm(p["base_length"])
    base_width = _cm(p["base_width"])
    base_t = _cm(p["base_thickness"])
    lug_height = _cm(p["lug_height"])
    lug_t = _cm(p["lug_thickness"])
    neck = _cm(p["neck_width"])
    gusset_height = _cm(p["gusset_height"])
    gusset_t = _cm(p["gusset_thickness"])
    pin_radius = _cm(definition["fixed_geometry"]["pin_hole_diameter_mm"]) / 2.0

    _extrude_centered_rectangle(
        component, component.xYConstructionPlane, base_length, base_width, base_t, "Doubler plate"
    )
    root_width = min(base_length * 0.62, neck * 1.8)
    lug_plane = _offset_plane(component, component.xZConstructionPlane, -lug_t / 2.0)
    lug_sketch = component.sketches.add(lug_plane)
    pin_z = base_t + lug_height - neck / 2.0
    points = [
        adsk.core.Point3D.create(-root_width / 2.0, base_t, 0),
        adsk.core.Point3D.create(-neck / 2.0, pin_z, 0),
        adsk.core.Point3D.create(0, base_t + lug_height, 0),
        adsk.core.Point3D.create(neck / 2.0, pin_z, 0),
        adsk.core.Point3D.create(root_width / 2.0, base_t, 0),
    ]
    _closed_polyline(lug_sketch, points)
    _extrude_profile(
        component,
        _largest_profile(lug_sketch),
        lug_t,
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
        "Tapered lifting lug",
    )

    hole_sketch = component.sketches.add(lug_plane)
    hole_sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, pin_z, 0), pin_radius
    )
    _extrude_profile(
        component,
        _largest_profile(hole_sketch),
        lug_t,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
        "Pin hole",
    )

    gusset_run = min(base_width * 0.42, lug_height * 0.72)
    for x in (-neck * 0.45, neck * 0.45 - gusset_t):
        plane = _offset_plane(component, component.yZConstructionPlane, x)
        sketch = component.sketches.add(plane)
        points = [
            adsk.core.Point3D.create(lug_t / 2.0, base_t, 0),
            adsk.core.Point3D.create(lug_t / 2.0, base_t + gusset_height, 0),
            adsk.core.Point3D.create(lug_t / 2.0 + gusset_run, base_t, 0),
        ]
        _closed_polyline(sketch, points)
        _extrude_profile(
            component,
            _largest_profile(sketch),
            gusset_t,
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
            "Side gusset",
        )

    _try_fillet(component, _cm(p["fillet_radius"]), log)
    return {
        "fixed_support": {"kind": "bbox", "z_max": 0.01},
        "pin_bearing": {
            "kind": "cylinder",
            "radius": pin_radius,
            "center_z": pin_z,
            "tolerance": 0.03,
        },
    }


def _generate_stabilizer(component, definition, p, log):
    g = definition["fixed_geometry"]
    span = _cm(g["span_mm"])
    root_chord = _cm(g["root_chord_mm"])
    tip_chord = _cm(g["tip_chord_mm"])
    sweep = math.tan(math.radians(float(g["sweep_deg"]))) * span
    flange_t = _cm(g["root_flange_thickness_mm"])
    skin = _cm(p["skin_thickness"])

    _extrude_centered_rectangle(
        component,
        component.xYConstructionPlane,
        _cm(g["root_flange_length_mm"]),
        _cm(g["root_flange_width_mm"]),
        flange_t,
        "Root mounting flange",
    )

    root_plane = _offset_plane(component, component.xYConstructionPlane, flange_t)
    tip_plane = _offset_plane(component, component.xYConstructionPlane, flange_t + span)
    outer_root = _airfoil_profile(component, root_plane, root_chord, 0.0, 0.0)
    outer_tip = _airfoil_profile(component, tip_plane, tip_chord, sweep, 0.0)
    outer_body = _loft_profiles(
        component,
        [outer_root, outer_tip],
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
        "NACA 0015 outer envelope",
    )

    inner_root_plane = _offset_plane(component, component.xYConstructionPlane, flange_t + skin)
    inner_tip_plane = _offset_plane(
        component, component.xYConstructionPlane, flange_t + span - skin
    )
    inner_root = _airfoil_profile(
        component, inner_root_plane, root_chord - 2.0 * skin, skin, skin
    )
    inner_tip = _airfoil_profile(
        component, inner_tip_plane, tip_chord - 2.0 * skin, sweep + skin, skin
    )
    inner_body = _loft_profiles(
        component,
        [inner_root, inner_tip],
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        "Inner cavity tool",
    )
    _cut_body(component, outer_body, inner_body, "Hollow stabilizer skin")

    front = p["front_spar_position"] / 100.0
    rear = p["rear_spar_position"] / 100.0
    _add_spar(component, flange_t + skin, span - 2.0 * skin, root_chord, tip_chord, sweep, front, _cm(p["front_spar_thickness"]), "Front spar")
    _add_spar(component, flange_t + skin, span - 2.0 * skin, root_chord, tip_chord, sweep, rear, _cm(p["rear_spar_thickness"]), "Rear spar")

    for index, station in enumerate(g["rib_stations"], start=1):
        z = flange_t + float(station) * span - _cm(p["rib_thickness"]) / 2.0
        chord = root_chord + (tip_chord - root_chord) * float(station)
        x_offset = sweep * float(station) + skin
        plane = _offset_plane(component, component.xYConstructionPlane, z)
        profile = _airfoil_profile(component, plane, chord - 2.0 * skin, x_offset, skin)
        _extrude_profile(
            component,
            profile,
            _cm(p["rib_thickness"]),
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
            f"Internal rib {index}",
        )

    _add_root_insert(component, flange_t, p, root_chord, log)
    _try_fillet(component, _cm(p["root_fillet_radius"]), log)
    _try_split_pressure_bands(component, flange_t, span, log)

    selectors = {"fixed_support": {"kind": "bbox", "z_max": 0.01}}
    weights = definition["load"]["pressure_weights"]
    for index, weight in enumerate(weights, start=1):
        selectors[f"pressure_band_{index}"] = {
            "kind": "pressure_band",
            "z_min": flange_t + span * (index - 1) / 4.0,
            "z_max": flange_t + span * index / 4.0,
            "normal_y_min": 0.05,
            "relative_weight": float(weight),
        }
    selectors["tip_monitor"] = {
        "kind": "bbox",
        "z_min": flange_t + span - 0.02,
    }
    return selectors


def _add_spar(component, root_z, span, root_chord, tip_chord, sweep, fraction, thickness, name):
    root_plane = _offset_plane(component, component.xYConstructionPlane, root_z)
    tip_plane = _offset_plane(component, component.xYConstructionPlane, root_z + span)
    root_height = _naca_thickness(root_chord, fraction) * 0.88
    tip_height = _naca_thickness(tip_chord, fraction) * 0.88
    root_profile = _rectangle_profile(
        component,
        root_plane,
        root_chord * fraction - thickness / 2.0,
        -root_height / 2.0,
        thickness,
        root_height,
    )
    tip_profile = _rectangle_profile(
        component,
        tip_plane,
        sweep + tip_chord * fraction - thickness / 2.0,
        -tip_height / 2.0,
        thickness,
        tip_height,
    )
    _loft_profiles(
        component,
        [root_profile, tip_profile],
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
        name,
    )


def _add_root_insert(component, flange_t, p, root_chord, log):
    height = root_chord * 0.12
    width = _cm(p["root_insert_thickness"])
    length = _cm(p["root_insert_length"])
    profile = _rectangle_profile(
        component,
        _offset_plane(component, component.xYConstructionPlane, flange_t),
        root_chord * 0.38,
        -height / 2.0,
        width,
        height,
    )
    _extrude_profile(
        component,
        profile,
        length,
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
        "Root reinforcement",
    )


def _airfoil_profile(component, plane, chord, x_offset, y_inset):
    sketch = component.sketches.add(plane)
    points = _naca_points(chord, x_offset, y_inset)
    _closed_polyline(sketch, points)
    return _largest_profile(sketch)


def _naca_points(chord, x_offset, y_inset, count=24):
    upper = []
    lower = []
    for index in range(count + 1):
        theta = math.pi * index / count
        x_fraction = 0.5 * (1.0 - math.cos(theta))
        x = x_offset + chord * x_fraction
        half = _naca_thickness(chord, x_fraction) / 2.0
        upper.append(adsk.core.Point3D.create(x, max(half - y_inset, 0.01), 0))
        lower.append(adsk.core.Point3D.create(x, min(-half + y_inset, -0.01), 0))
    return list(reversed(upper)) + lower[1:]


def _naca_thickness(chord, x_fraction):
    x = min(max(x_fraction, 0.0001), 1.0)
    half = 5.0 * 0.15 * chord * (
        0.2969 * math.sqrt(x)
        - 0.1260 * x
        - 0.3516 * x**2
        + 0.2843 * x**3
        - 0.1015 * x**4
    )
    return max(2.0 * half, chord * 0.016)


def _extrude_centered_rectangle(component, plane, length, width, distance, name):
    profile = _rectangle_profile(
        component, plane, -length / 2.0, -width / 2.0, length, width
    )
    return _extrude_profile(
        component,
        profile,
        distance,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        name,
    )


def _rectangle_profile(component, plane, x, y, width, height):
    sketch = component.sketches.add(plane)
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x, y, 0),
        adsk.core.Point3D.create(x + width, y + height, 0),
    )
    return _largest_profile(sketch)


def _closed_polyline(sketch, points):
    lines = sketch.sketchCurves.sketchLines
    for start, end in zip(points, points[1:] + points[:1]):
        lines.addByTwoPoints(start, end)


def _largest_profile(sketch):
    if sketch.profiles.count == 0:
        raise RuntimeError("Sketch did not produce a closed profile")
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    return max(profiles, key=lambda profile: abs(profile.areaProperties().area))


def _extrude_profile(component, profile, distance, operation, name):
    features = component.features.extrudeFeatures
    input_ = features.createInput(profile, operation)
    input_.setDistanceExtent(False, adsk.core.ValueInput.createByReal(distance))
    feature = features.add(input_)
    feature.name = name
    return feature.bodies.item(0) if feature.bodies.count else None


def _loft_profiles(component, profiles, operation, name):
    lofts = component.features.loftFeatures
    input_ = lofts.createInput(operation)
    for profile in profiles:
        input_.loftSections.add(profile)
    input_.isSolid = True
    feature = lofts.add(input_)
    feature.name = name
    return feature.bodies.item(0) if feature.bodies.count else None


def _cut_body(component, target, tool, name):
    tools = adsk.core.ObjectCollection.create()
    tools.add(tool)
    input_ = component.features.combineFeatures.createInput(target, tools)
    input_.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    input_.isKeepToolBodies = False
    feature = component.features.combineFeatures.add(input_)
    feature.name = name


def _offset_plane(component, base_plane, distance):
    planes = component.constructionPlanes
    input_ = planes.createInput()
    input_.setByOffset(base_plane, adsk.core.ValueInput.createByReal(distance))
    return planes.add(input_)


def _try_fillet(component, radius, log):
    if component.bRepBodies.count == 0:
        return
    body = component.bRepBodies.item(0)
    edges = adsk.core.ObjectCollection.create()
    for edge in body.edges:
        if edge.boundingBox.minPoint.z <= 0.05:
            edges.add(edge)
    if edges.count == 0:
        return
    try:
        input_ = component.features.filletFeatures.createInput()
        input_.addConstantRadiusEdgeSet(
            edges, adsk.core.ValueInput.createByReal(radius), True
        )
        component.features.filletFeatures.add(input_)
    except Exception as exc:
        log(f"Fillet skipped because Fusion rejected the selected edge set: {exc}")


def _try_bracket_fillet(
    component,
    radius,
    base_thickness,
    rib_length,
    rib_thickness,
    rib_y_centers,
    log,
):
    """Fillet the four long rib-to-baseplate root junctions."""

    if component.bRepBodies.count == 0:
        return
    body = component.bRepBodies.item(0)
    edges = adsk.core.ObjectCollection.create()
    tolerance = 0.01
    for edge in body.edges:
        bbox = edge.boundingBox
        at_plate_top = (
            abs(bbox.minPoint.z - base_thickness) <= tolerance
            and abs(bbox.maxPoint.z - base_thickness) <= tolerance
        )
        long_along_rib = (
            bbox.maxPoint.x - bbox.minPoint.x >= rib_length * 0.95
            and bbox.maxPoint.y - bbox.minPoint.y <= max(0.01, rib_thickness * 0.05)
        )
        edge_y = (bbox.minPoint.y + bbox.maxPoint.y) / 2.0
        at_rib_side = any(
            abs(edge_y - (center + side * rib_thickness / 2.0)) <= tolerance
            for center in rib_y_centers
            for side in (-1.0, 1.0)
        )
        if at_plate_top and long_along_rib and at_rib_side:
            edges.add(edge)
    if edges.count == 0:
        raise RuntimeError(
            "Bracket fillet failed: Fusion found no long rib-to-baseplate root edges."
        )
    try:
        input_ = component.features.filletFeatures.createInput()
        input_.addConstantRadiusEdgeSet(
            edges, adsk.core.ValueInput.createByReal(radius), True
        )
        component.features.filletFeatures.add(input_)
    except Exception as exc:
        raise RuntimeError(
            f"Bracket fillet failed for radius {radius:g} cm: {exc}"
        ) from exc


def _try_split_pressure_bands(component, root_z, span, log):
    if component.bRepBodies.count == 0:
        return
    body = component.bRepBodies.item(0)
    for station in (0.25, 0.5, 0.75):
        try:
            plane = _offset_plane(
                component, component.xYConstructionPlane, root_z + span * station
            )
            faces = adsk.core.ObjectCollection.create()
            for face in body.faces:
                if face.boundingBox.maxPoint.z > root_z and face.boundingBox.minPoint.z < root_z + span:
                    faces.add(face)
            input_ = component.features.splitFaceFeatures.createInput(faces, plane, True)
            component.features.splitFaceFeatures.add(input_)
        except Exception as exc:
            log(f"Pressure band split at {station:g} span skipped: {exc}")


def _assign_material(component, target_name, log):
    app = adsk.core.Application.get()
    target = target_name.lower()
    aliases = [target]
    if "s275" in target:
        aliases.extend(["steel", "mild steel"])
    if "6061" in target:
        aliases.extend(["aluminum 6061", "aluminium 6061"])
    try:
        libraries = app.materialLibraries
        for library_index in range(libraries.count):
            materials = libraries.item(library_index).materials
            for material_index in range(materials.count):
                material = materials.item(material_index)
                name = material.name.lower()
                if any(alias in name for alias in aliases):
                    component.material = material
                    return
    except Exception as exc:
        log(f"Material lookup failed: {exc}")
    log(f"Material '{target_name}' was not found; NEMO will compute mass from CAD volume and configured density.")


def _face_matches(face, selector):
    bbox = face.boundingBox
    kind = selector.get("kind")
    if "z_min" in selector and bbox.maxPoint.z < selector["z_min"]:
        return False
    if "z_max" in selector and bbox.minPoint.z > selector["z_max"]:
        return False
    if kind == "cylinder":
        try:
            geometry = face.geometry
            return abs(float(geometry.radius) - selector["radius"]) <= selector["tolerance"]
        except Exception:
            return False
    if kind == "upper_rib_face":
        signature = _face_signature(face)
        return (
            signature["centroid"][2] >= selector["z_min"]
            and signature["normal"][2] >= selector.get("normal_z_min", 0.0)
        )
    if kind == "pressure_band":
        signature = _face_signature(face)
        return signature["normal"][1] >= selector.get("normal_y_min", 0.0)
    return True


def _face_signature(face):
    # BRepFace exposes area and centroid directly.  areaProperties() belongs
    # to sketch profiles and is not available on BRepFace in current Fusion.
    area = float(face.area)
    try:
        point = face.centroid
    except Exception:
        point = face.pointOnFace
    normal = adsk.core.Vector3D.create(0, 0, 0)
    try:
        ok, normal = face.evaluator.getNormalAtPoint(point)
        if not ok:
            normal = adsk.core.Vector3D.create(0, 0, 0)
    except Exception:
        pass
    bbox = face.boundingBox
    signature = {
        "area_cm2": area,
        "centroid": [point.x, point.y, point.z],
        "normal": [normal.x, normal.y, normal.z],
        "bbox_min": [bbox.minPoint.x, bbox.minPoint.y, bbox.minPoint.z],
        "bbox_max": [bbox.maxPoint.x, bbox.maxPoint.y, bbox.maxPoint.z],
    }
    try:
        geometry = face.geometry
        origin = geometry.origin
        axis = geometry.axis
        signature["cylinder"] = {
            "origin": [origin.x, origin.y, origin.z],
            "axis": [axis.x, axis.y, axis.z],
            "radius_cm": float(geometry.radius),
        }
    except Exception:
        pass
    return signature


def _cm(value_mm):
    return float(value_mm) / 10.0
