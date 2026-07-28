"""File-based JSON handshake helpers for external Python and Fusion."""

from __future__ import annotations

from contextlib import contextmanager
import json
import os
import time
from pathlib import Path
from typing import Any, Iterator, Mapping

from .schemas import EvaluationRequest, EvaluationResponse


REQUEST_FILE = "request.json"
RESPONSE_FILE = "response.json"
CHANNEL_LOCK_FILE = "fusion_channel.lock"
ATOMIC_REPLACE_ATTEMPTS = 8


def write_json_atomic(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f"{target.stem}.tmp{target.suffix}")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    last_error: OSError | None = None
    for attempt in range(ATOMIC_REPLACE_ATTEMPTS):
        try:
            os.replace(tmp, target)
            return
        except OSError as exc:
            last_error = exc
            if attempt == ATOMIC_REPLACE_ATTEMPTS - 1:
                break
            time.sleep(min(0.05 * (2**attempt), 1.0))
    raise OSError(
        f"Could not atomically replace {target} after "
        f"{ATOMIC_REPLACE_ATTEMPTS} attempts: {last_error}"
    ) from last_error


@contextmanager
def serialized_fusion_channel(
    run_dir: str | Path,
    *,
    timeout_s: float = 240.0,
    poll_s: float = 0.1,
) -> Iterator[None]:
    """Hold an inter-process lock for the shared Fusion request channel."""

    lock_path = Path(run_dir) / CHANNEL_LOCK_FILE
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+b")
    handle.seek(0, os.SEEK_END)
    if handle.tell() == 0:
        handle.write(b"\0")
        handle.flush()
    deadline = time.monotonic() + timeout_s
    acquired = False
    try:
        while time.monotonic() < deadline:
            handle.seek(0)
            try:
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
            except OSError:
                time.sleep(poll_s)
        if not acquired:
            raise TimeoutError(
                "Timed out waiting for the serialized Fusion channel lock "
                f"at {lock_path} after {timeout_s:g}s."
            )
        yield
    finally:
        if acquired:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


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
    timeout_s: float = 240.0,
    poll_s: float = 0.5,
) -> EvaluationResponse:
    """Wait for a matching Fusion response file."""

    response_path = Path(run_dir) / RESPONSE_FILE
    deadline = time.monotonic() + timeout_s
    last_error: Exception | None = None
    last_response: tuple[str, int, str] | None = None

    while time.monotonic() < deadline:
        if response_path.exists():
            try:
                response = read_response(response_path)
            except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
                last_error = exc
            else:
                last_response = (
                    response.run_id,
                    response.iteration,
                    response.status,
                )
                if response.run_id == run_id and response.iteration == iteration:
                    return response
        time.sleep(poll_s)

    request_path = Path(run_dir) / REQUEST_FILE
    request_state = _file_state(request_path)
    response_state = _file_state(response_path)
    observed = (
        "none"
        if last_response is None
        else (
            f"run_id={last_response[0]} iteration={last_response[1]} "
            f"status={last_response[2]}"
        )
    )
    read_error = f"; last read error={last_error}" if last_error else ""
    raise TimeoutError(
        f"Timed out after {timeout_s:g}s waiting for Fusion response "
        f"run_id={run_id} iteration={iteration}; request.json {request_state}; "
        f"response.json {response_state}; last observed response={observed}"
        f"{read_error}."
    )


def _file_state(path: Path) -> str:
    try:
        stat = path.stat()
    except FileNotFoundError:
        return "is missing"
    except OSError as exc:
        return f"could not be inspected ({exc})"
    age_s = max(0.0, time.time() - stat.st_mtime)
    return f"exists, {stat.st_size} bytes, modified {age_s:.1f}s ago"
