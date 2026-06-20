"""File-based JSON handshake helpers for external Python and Fusion."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Mapping

from .schemas import EvaluationRequest, EvaluationResponse


REQUEST_FILE = "request.json"
RESPONSE_FILE = "response.json"


def write_json_atomic(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f"{target.stem}.tmp{target.suffix}")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    os.replace(tmp, target)


def read_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_request(run_dir: str | Path, request: EvaluationRequest) -> Path:
    path = Path(run_dir) / REQUEST_FILE
    write_json_atomic(path, request.to_dict())
    return path


def write_response(run_dir: str | Path, response: EvaluationResponse) -> Path:
    path = Path(run_dir) / RESPONSE_FILE
    write_json_atomic(path, response.to_dict())
    return path


def read_request(path: str | Path) -> EvaluationRequest:
    return EvaluationRequest.from_dict(read_json(path))


def read_response(path: str | Path) -> EvaluationResponse:
    return EvaluationResponse.from_dict(read_json(path))


def wait_for_response(
    run_dir: str | Path,
    *,
    run_id: str,
    iteration: int,
    timeout_s: float = 120.0,
    poll_s: float = 0.5,
) -> EvaluationResponse:
    """Wait for a matching Fusion response file."""

    response_path = Path(run_dir) / RESPONSE_FILE
    deadline = time.monotonic() + timeout_s
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        if response_path.exists():
            try:
                response = read_response(response_path)
            except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
                last_error = exc
            else:
                if response.run_id == run_id and response.iteration == iteration:
                    return response
        time.sleep(poll_s)

    suffix = f" Last read error: {last_error}" if last_error else ""
    raise TimeoutError(
        f"Timed out waiting for response run_id={run_id} iteration={iteration}.{suffix}"
    )
