"""Run one visible bracket CAD update through the NEMOBridge handshake."""

from __future__ import annotations

import json
from pathlib import Path

from nemo.evaluation import make_run_id
from nemo.handshake import (
    serialized_fusion_channel,
    wait_for_response,
    write_request,
)
from nemo.parts import get_part_definition
from nemo.schemas import EvaluationRequest


HANDSHAKE_DIR = Path("data/runs/active")


def main() -> int:
    """Submit one bracket request and print the matching Fusion response."""

    HANDSHAKE_DIR.mkdir(parents=True, exist_ok=True)
    run_id = make_run_id()
    iteration = 1

    parameters = dict(get_part_definition("bracket").baseline_parameters)
    parameters["baseplate_length"] = 160.0

    request = EvaluationRequest(
        run_id=run_id,
        iteration=iteration,
        mode="fusion_cad",
        part_id="bracket",
        parameters=parameters,
        artifact_formats=("step", "boundary_tags"),
    )

    print(f"Writing request to {HANDSHAKE_DIR / 'request.json'}...")
    print("Waiting for Fusion 360 to process and write response.json (timeout=120s)...")
    try:
        with serialized_fusion_channel(HANDSHAKE_DIR, timeout_s=120.0):
            write_request(HANDSHAKE_DIR, request)
            response = wait_for_response(
                HANDSHAKE_DIR,
                run_id=run_id,
                iteration=iteration,
                timeout_s=120.0,
            )
    except TimeoutError as e:
        print(f"\nTimeout Error: {e}")
        print("Did you start the NEMOBridge Add-in in Fusion 360?")
        return 1

    print("\nSuccess! Received response from Fusion 360:")
    print(json.dumps(response.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
