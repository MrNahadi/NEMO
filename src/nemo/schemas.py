"""Dataclasses for the versioned JSON request/response contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence

from .parts import DEFAULT_PART_ID


@dataclass(frozen=True, init=False)
class EvaluationRequest:
    run_id: str
    iteration: int
    mode: str
    parameters: dict[str, float]
    part_id: str
    schema_version: int
    artifact_formats: tuple[str, ...]

    def __init__(
        self,
        run_id: str,
        iteration: int,
        mode: str,
        parameters: Mapping[str, float] | None = None,
        *,
        parameters_mm: Mapping[str, float] | None = None,
        part_id: str = DEFAULT_PART_ID,
        schema_version: int = 2,
        artifact_formats: Sequence[str] = (),
    ) -> None:
        selected = parameters if parameters is not None else parameters_mm
        if selected is None:
            raise TypeError("EvaluationRequest requires parameters or parameters_mm")
        object.__setattr__(self, "run_id", str(run_id))
        object.__setattr__(self, "iteration", int(iteration))
        object.__setattr__(self, "mode", str(mode))
        object.__setattr__(self, "parameters", {str(k): float(v) for k, v in selected.items()})
        object.__setattr__(self, "part_id", str(part_id).lower())
        object.__setattr__(self, "schema_version", int(schema_version))
        object.__setattr__(self, "artifact_formats", tuple(str(v).lower() for v in artifact_formats))

    @property
    def parameters_mm(self) -> dict[str, float]:
        """Compatibility alias for schema-v1 bracket callers."""

        return self.parameters

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "EvaluationRequest":
        uses_v2 = "parameters" in payload
        return cls(
            run_id=str(payload["run_id"]),
            iteration=int(payload["iteration"]),
            mode=str(payload.get("mode", "analytical")),
            parameters=dict(payload.get("parameters") or payload.get("parameters_mm") or {}),
            part_id=str(payload.get("part_id", DEFAULT_PART_ID)),
            schema_version=int(payload.get("schema_version", 2 if uses_v2 else 1)),
            artifact_formats=tuple(payload.get("artifact_formats", ())),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "part_id": self.part_id,
            "run_id": self.run_id,
            "iteration": self.iteration,
            "mode": self.mode,
            "parameters": dict(self.parameters),
            "artifact_formats": list(self.artifact_formats),
        }


@dataclass(frozen=True)
class Metrics:
    mass_kg: float | None
    max_stress_mpa: float | None
    factor_of_safety: float | None
    max_deflection_mm: float | None
    objective_value: float | None
    volume_m3: float | None = None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any] | None) -> "Metrics":
        payload = payload or {}
        return cls(
            mass_kg=_optional_float(payload.get("mass_kg")),
            max_stress_mpa=_optional_float(payload.get("max_stress_mpa")),
            factor_of_safety=_optional_float(payload.get("factor_of_safety")),
            max_deflection_mm=_optional_float(payload.get("max_deflection_mm")),
            objective_value=_optional_float(payload.get("objective_value")),
            volume_m3=_optional_float(payload.get("volume_m3")),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvaluationResponse:
    run_id: str
    iteration: int
    status: str
    metrics: Metrics
    error: str | None = None
    part_id: str = DEFAULT_PART_ID
    schema_version: int = 2
    artifacts: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "EvaluationResponse":
        return cls(
            run_id=str(payload["run_id"]),
            iteration=int(payload["iteration"]),
            status=str(payload["status"]),
            metrics=Metrics.from_dict(payload.get("metrics")),
            error=None if payload.get("error") is None else str(payload["error"]),
            part_id=str(payload.get("part_id", DEFAULT_PART_ID)),
            schema_version=int(payload.get("schema_version", 1)),
            artifacts={str(k): str(v) for k, v in dict(payload.get("artifacts") or {}).items()},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "part_id": self.part_id,
            "run_id": self.run_id,
            "iteration": self.iteration,
            "status": self.status,
            "metrics": self.metrics.to_dict(),
            "artifacts": dict(self.artifacts),
            "error": self.error,
        }


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)
