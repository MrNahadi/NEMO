"""Dataclasses for the JSON request/response contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class EvaluationRequest:
    run_id: str
    iteration: int
    mode: str
    parameters_mm: dict[str, float]

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "EvaluationRequest":
        return cls(
            run_id=str(payload["run_id"]),
            iteration=int(payload["iteration"]),
            mode=str(payload.get("mode", "analytical")),
            parameters_mm={
                str(key): float(value)
                for key, value in dict(payload["parameters_mm"]).items()
            },
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Metrics:
    mass_kg: float | None
    max_stress_mpa: float | None
    factor_of_safety: float | None
    max_deflection_mm: float | None
    objective_value: float | None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any] | None) -> "Metrics":
        payload = payload or {}
        return cls(
            mass_kg=_optional_float(payload.get("mass_kg")),
            max_stress_mpa=_optional_float(payload.get("max_stress_mpa")),
            factor_of_safety=_optional_float(payload.get("factor_of_safety")),
            max_deflection_mm=_optional_float(payload.get("max_deflection_mm")),
            objective_value=_optional_float(payload.get("objective_value")),
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

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "EvaluationResponse":
        return cls(
            run_id=str(payload["run_id"]),
            iteration=int(payload["iteration"]),
            status=str(payload["status"]),
            metrics=Metrics.from_dict(payload.get("metrics")),
            error=None if payload.get("error") is None else str(payload["error"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "iteration": self.iteration,
            "status": self.status,
            "metrics": self.metrics.to_dict(),
            "error": self.error,
        }


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)
