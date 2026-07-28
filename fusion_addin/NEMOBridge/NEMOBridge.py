"""Fusion 360 bridge and native CAD generator for NEMO."""

from __future__ import annotations

import json
import importlib
import os
import sys
import threading
import time
import traceback

import adsk.core
import adsk.fusion


HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Fusion retains imported Python modules after an add-in is stopped.  Reload the
# generator module whenever this entry point is executed so development fixes
# take effect without stale function objects from the earlier add-in run.
import fusion_generators as _fusion_generators  # noqa: E402

_fusion_generators = importlib.reload(_fusion_generators)
collect_boundary_metadata = _fusion_generators.collect_boundary_metadata
generate_part = _fusion_generators.generate_part
load_definition = _fusion_generators.load_definition
write_boundary_metadata = _fusion_generators.write_boundary_metadata


def _reload_generator_module():
    """Reload generator edits before each serialized Fusion request."""

    global _fusion_generators
    global collect_boundary_metadata
    global generate_part
    global load_definition
    global write_boundary_metadata
    _fusion_generators = importlib.reload(_fusion_generators)
    collect_boundary_metadata = _fusion_generators.collect_boundary_metadata
    generate_part = _fusion_generators.generate_part
    load_definition = _fusion_generators.load_definition
    write_boundary_metadata = _fusion_generators.write_boundary_metadata


APP = None
UI = None
HANDLERS = []
WATCH_THREAD = None
STOP_REQUESTED = False
LAST_MTIME = None
CUSTOM_EVENT_ID = "nemo_bridge_request_ready"


def run(context):
    global APP, UI, WATCH_THREAD, STOP_REQUESTED
    APP = adsk.core.Application.get()
    UI = APP.userInterface
    STOP_REQUESTED = False
    event = APP.registerCustomEvent(CUSTOM_EVENT_ID)
    handler = RequestReadyHandler()
    event.add(handler)
    HANDLERS.append(handler)
    WATCH_THREAD = threading.Thread(target=_watch_loop, daemon=True)
    WATCH_THREAD.start()
    adsk.autoTerminate(False)
    _log("NEMO Bridge v2 started.")
    UI.messageBox("NEMO Bridge started. Watching for multi-part request.json files.")


def stop(context):
    global STOP_REQUESTED
    STOP_REQUESTED = True
    _log("NEMO Bridge stop requested.")
    try:
        if APP:
            APP.unregisterCustomEvent(CUSTOM_EVENT_ID)
    except Exception:
        pass
    adsk.terminate()


class RequestReadyHandler(adsk.core.CustomEventHandler):
    def notify(self, args):
        try:
            _process_request()
        except Exception:
            error = traceback.format_exc()
            _log(error)
            if UI:
                UI.messageBox("NEMO Bridge error:\n" + error)


def _watch_loop():
    global LAST_MTIME
    config = _load_config()
    request_path = os.path.join(_resolve_path(config["handshake_dir"]), "request.json")
    poll_seconds = float(config.get("poll_seconds", 1.0))
    _log(f"Watcher active. request_path={request_path} poll_seconds={poll_seconds}")
    while not STOP_REQUESTED:
        try:
            if os.path.exists(request_path):
                mtime = os.path.getmtime(request_path)
                if LAST_MTIME != mtime:
                    LAST_MTIME = mtime
                    APP.fireCustomEvent(CUSTOM_EVENT_ID, "")
        except Exception as exc:
            _log("Watcher error: " + str(exc))
        time.sleep(poll_seconds)


def _process_request():
    config = _load_config()
    handshake_dir = _resolve_path(config["handshake_dir"])
    request_path = os.path.join(handshake_dir, "request.json")
    response_path = os.path.join(handshake_dir, "response.json")
    request = {"run_id": "unknown", "iteration": -1, "part_id": "bracket"}

    try:
        _reload_generator_module()
        request = _read_json(request_path)
        schema_version = int(request.get("schema_version", 1))
        part_id = str(request.get("part_id", "bracket")).lower()
        parameters = request.get("parameters") or request.get("parameters_mm")
        if not isinstance(parameters, dict):
            raise RuntimeError("Request must contain parameters or parameters_mm")
        definition = load_definition(config, part_id)
        _validate_parameters(definition, parameters)

        design = _active_or_new_design()
        component, selectors = generate_part(
            design,
            definition,
            {key: float(value) for key, value in parameters.items()},
            _log,
        )
        if not design.computeAll():
            raise RuntimeError("Fusion computeAll returned false; inspect timeline health.")

        volume_m3, fusion_mass_kg = _get_component_properties(component)
        density = float(definition["material"]["density_kg_m3"])
        configured_mass_kg = volume_m3 * density
        _log(
            f"Physical properties part={part_id} volume_m3={volume_m3} "
            f"configured_mass_kg={configured_mass_kg} fusion_mass_kg={fusion_mass_kg}"
        )

        artifacts = _export_artifacts(
            design,
            component,
            selectors,
            request,
            config,
        )
        response = {
            "schema_version": max(schema_version, 2),
            "part_id": part_id,
            "run_id": request["run_id"],
            "iteration": request["iteration"],
            "status": "partial",
            "metrics": {
                "volume_m3": volume_m3,
                "mass_kg": configured_mass_kg,
                "max_stress_mpa": None,
                "factor_of_safety": None,
                "max_deflection_mm": None,
                "objective_value": None,
            },
            "artifacts": artifacts,
            "error": (
                "Native CAD generation and mass extraction completed. "
                "Static-stress results require manual Fusion validation."
            ),
        }
        _log(
            f"Processed run_id={request['run_id']} iteration={request['iteration']} "
            f"part_id={part_id} status=partial"
        )
    except Exception as exc:
        response = {
            "schema_version": 2,
            "part_id": request.get("part_id", "bracket"),
            "run_id": request.get("run_id", "unknown"),
            "iteration": request.get("iteration", -1),
            "status": "failed",
            "metrics": {
                "volume_m3": None,
                "mass_kg": None,
                "max_stress_mpa": None,
                "factor_of_safety": None,
                "max_deflection_mm": None,
                "objective_value": 1000000000.0,
            },
            "artifacts": {},
            "error": str(exc),
        }
        _log("Request failed: " + traceback.format_exc())

    _write_json_atomic(response_path, response)
    _log(f"Wrote response_path={response_path}")


def _active_or_new_design():
    _activate_design_workspace()
    design = adsk.fusion.Design.cast(APP.activeProduct)
    if design:
        return design
    APP.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(APP.activeProduct)
    if not design:
        raise RuntimeError("Could not create a Fusion design document.")
    return design


def _get_component_properties(component):
    attempts = (
        lambda: component.getPhysicalProperties(),
        lambda: component.physicalProperties,
    )
    errors = []
    for getter in attempts:
        try:
            properties = getter()
            if callable(properties):
                properties = properties()
            volume_cm3 = properties.volume
            mass_kg = properties.mass
            if callable(volume_cm3):
                volume_cm3 = volume_cm3()
            if callable(mass_kg):
                mass_kg = mass_kg()
            return float(volume_cm3) / 1.0e6, float(mass_kg)
        except Exception as exc:
            errors.append(str(exc))
    raise RuntimeError("Could not read generated component properties: " + " | ".join(errors))


def _export_artifacts(design, component, selectors, request, config):
    formats = [str(value).lower() for value in request.get("artifact_formats", [])]
    if not formats:
        formats = ["step", "boundary_tags"]
    root = _resolve_path(config.get("artifact_dir", "../../data/runs/active/artifacts"))
    safe_run_id = _safe_name(str(request.get("run_id", "manual")))
    iteration = int(request.get("iteration", 0))
    directory = os.path.join(root, safe_run_id)
    os.makedirs(directory, exist_ok=True)
    stem = f"{_safe_name(request.get('part_id', 'bracket'))}_{iteration:04d}"
    artifacts = {}
    export_manager = design.exportManager
    metadata = None
    if "boundary_tags" in formats or "step" in formats:
        metadata = collect_boundary_metadata(component, selectors)
        metadata["part_id"] = request.get("part_id", "bracket")
        metadata["parameters"] = request.get("parameters") or request.get("parameters_mm")
        _validate_generated_artifact(component, metadata)

    if "step" in formats:
        path = os.path.join(directory, stem + ".step")
        options = export_manager.createSTEPExportOptions(path, component)
        if not export_manager.execute(options):
            raise RuntimeError("Fusion STEP export returned false")
        artifacts["step"] = path

    if "stl" in formats:
        path = os.path.join(directory, stem + ".stl")
        options = export_manager.createSTLExportOptions(component, path)
        if not export_manager.execute(options):
            raise RuntimeError("Fusion STL export returned false")
        artifacts["stl"] = path

    if "boundary_tags" in formats or "step" in formats:
        path = os.path.join(directory, stem + ".boundaries.json")
        write_boundary_metadata(path, metadata)
        artifacts["boundary_tags"] = path
    return artifacts


def _validate_generated_artifact(component, metadata):
    """Reject structurally incomplete CAD before reporting a partial success."""

    body_count = int(component.bRepBodies.count)
    if body_count != 1:
        raise RuntimeError(
            f"Generated {metadata['part_id']} must contain one connected solid body; "
            f"Fusion reported {body_count}."
        )
    boundaries = metadata.get("boundaries", {})
    for role, payload in boundaries.items():
        if not payload.get("faces"):
            raise RuntimeError(
                f"Generated {metadata['part_id']} boundary role {role!r} matched no faces."
            )
    if metadata.get("part_id") == "bracket":
        support_payload = boundaries.get("fixed_support", {})
        support_faces = support_payload.get("faces", [])
        selector = support_payload.get("selector", {})
        radius = float(selector.get("radius", 0.5))
        parameters = metadata.get("parameters") or {}
        length = float(parameters["baseplate_length"]) / 10.0
        width = float(parameters["baseplate_width"]) / 10.0
        hole_x = length / 2.0 - max(1.5 * radius, length * 0.10)
        hole_y = width / 2.0 - max(1.5 * radius, width * 0.12)
        expected_centres = [
            (x, y) for x in (-hole_x, hole_x) for y in (-hole_y, hole_y)
        ]
        # A physical cylindrical hole can be split into multiple B-Rep faces.
        # Every split-face centroid remains within the cylinder radius of the
        # known parametric hole axis, so verify the four expected axes directly.
        support_count = sum(
            any(
                (face["centroid"][0] - expected_x) ** 2
                + (face["centroid"][1] - expected_y) ** 2
                <= (radius * 1.1) ** 2
                for face in support_faces
            )
            for expected_x, expected_y in expected_centres
        )
        load_count = len(boundaries.get("equipment_load", {}).get("faces", []))
        if support_count != 4:
            raise RuntimeError(
                "Generated bracket must expose four distinct cylindrical bolt-hole "
                f"support regions; Fusion reported {support_count} from "
                f"{len(support_faces)} face segments."
            )
        if load_count < 2:
            raise RuntimeError(
                "Generated bracket must expose at least two upper rib load faces; "
                f"Fusion reported {load_count}."
            )


def _validate_parameters(definition, values):
    expected = {item["name"]: item for item in definition["parameters"]}
    missing = sorted(set(expected) - set(values))
    extra = sorted(set(values) - set(expected))
    errors = []
    if missing:
        errors.append("missing: " + ", ".join(missing))
    if extra:
        errors.append("unknown: " + ", ".join(extra))
    for name, spec in expected.items():
        if name not in values:
            continue
        value = float(values[name])
        if value < float(spec["lower"]) or value > float(spec["upper"]):
            errors.append(
                f"{name}={value:g} outside [{spec['lower']}, {spec['upper']}]"
            )
    if errors:
        raise RuntimeError("Invalid parameters: " + "; ".join(errors))


def _activate_design_workspace():
    for workspace_id in ("FusionSolidEnvironment", "FusionModelingEnvironment"):
        try:
            workspace = UI.workspaces.itemById(workspace_id)
            if workspace:
                workspace.activate()
                time.sleep(0.2)
                return
        except Exception as exc:
            _log(f"Could not activate workspace {workspace_id}: {exc}")


def _load_config():
    with open(os.path.join(HERE, "config.json"), "r", encoding="utf-8") as handle:
        return json.load(handle)


def _resolve_path(path):
    return path if os.path.isabs(path) else os.path.abspath(os.path.join(HERE, path))


def _read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json_atomic(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = os.path.join(os.path.dirname(path), "response.tmp.json")
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    attempts = 8
    last_error = None
    for attempt in range(attempts):
        try:
            os.replace(tmp, path)
            return
        except OSError as exc:
            last_error = exc
            if attempt == attempts - 1:
                break
            delay = min(0.05 * (2**attempt), 1.0)
            _log(
                "response.json replace attempt "
                f"{attempt + 1}/{attempts} failed: {exc}; "
                f"retrying in {delay:g}s"
            )
            time.sleep(delay)
    raise RuntimeError(
        f"Could not replace response.json after {attempts} attempts: "
        f"{last_error}"
    )


def _safe_name(value):
    return "".join(character if character.isalnum() or character in "-_" else "_" for character in str(value))


def _log(message):
    try:
        config = _load_config()
        handshake_dir = _resolve_path(config["handshake_dir"])
        os.makedirs(handshake_dir, exist_ok=True)
        path = os.path.join(handshake_dir, "NEMOBridge.log")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(f"{timestamp} {message}\n")
    except Exception:
        pass
