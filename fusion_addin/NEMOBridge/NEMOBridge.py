"""Fusion 360 add-in bridge for NEMO.

Install/copy the NEMOBridge folder into Fusion's Scripts and Add-Ins location,
or run it directly from this repository if Fusion allows browsing to the folder.

This bridge handles the Week 3 goal: update named user parameters, recompute the
design, and return mass. FEA solve/result automation is the Week 4 spike.
"""

from __future__ import annotations

import json
import os
import threading
import time
import traceback

import adsk.core
import adsk.fusion


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
    UI.messageBox("NEMO Bridge started. Watching for request.json.")


def stop(context):
    global STOP_REQUESTED
    STOP_REQUESTED = True
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
            if UI:
                UI.messageBox("NEMO Bridge error:\n" + traceback.format_exc())


def _watch_loop():
    global LAST_MTIME
    handshake_dir, poll_seconds = _load_config()
    request_path = os.path.join(handshake_dir, "request.json")
    while not STOP_REQUESTED:
        try:
            if os.path.exists(request_path):
                mtime = os.path.getmtime(request_path)
                if LAST_MTIME != mtime:
                    LAST_MTIME = mtime
                    APP.fireCustomEvent(CUSTOM_EVENT_ID, "")
        except Exception:
            pass
        time.sleep(poll_seconds)


def _process_request():
    handshake_dir, _poll_seconds = _load_config()
    request_path = os.path.join(handshake_dir, "request.json")
    response_path = os.path.join(handshake_dir, "response.json")
    request = _read_json(request_path)

    try:
        design = adsk.fusion.Design.cast(APP.activeProduct)
        if not design:
            raise RuntimeError("Active product is not a Fusion design.")

        user_parameters = design.userParameters
        missing = []
        for name, value in request["parameters_mm"].items():
            parameter = user_parameters.itemByName(name)
            if not parameter:
                missing.append(name)
                continue
            parameter.expression = f"{float(value)} mm"
        if missing:
            raise RuntimeError("Missing Fusion user parameters: " + ", ".join(missing))

        recomputed = design.computeAll()
        mass_kg = design.physicalProperties.mass
        status = "partial"
        error = (
            None
            if recomputed
            else "Fusion computeAll returned false; inspect timeline health."
        )
        response = {
            "run_id": request["run_id"],
            "iteration": request["iteration"],
            "status": status,
            "metrics": {
                "mass_kg": mass_kg,
                "max_stress_mpa": None,
                "factor_of_safety": None,
                "max_deflection_mm": None,
                "objective_value": mass_kg,
            },
            "error": error
            or "Mass extraction complete. FEA result extraction remains the Week 4 spike.",
        }
    except Exception as exc:
        response = {
            "run_id": request.get("run_id", "unknown"),
            "iteration": request.get("iteration", -1),
            "status": "failed",
            "metrics": {
                "mass_kg": None,
                "max_stress_mpa": None,
                "factor_of_safety": None,
                "max_deflection_mm": None,
                "objective_value": 1000000000.0,
            },
            "error": str(exc),
        }

    _write_json_atomic(response_path, response)


def _load_config():
    here = os.path.dirname(__file__)
    config_path = os.path.join(here, "config.json")
    with open(config_path, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    handshake_dir = config.get("handshake_dir", "../../data/runs/active")
    if not os.path.isabs(handshake_dir):
        handshake_dir = os.path.abspath(os.path.join(here, handshake_dir))
    os.makedirs(handshake_dir, exist_ok=True)
    return handshake_dir, float(config.get("poll_seconds", 1.0))


def _read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json_atomic(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = os.path.join(os.path.dirname(path), "response.tmp.json")
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    os.replace(tmp, path)
