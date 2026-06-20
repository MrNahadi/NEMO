"""NEMO external optimization package."""

from .config import BASELINE_PARAMETERS_MM, PARAMETER_SPECS
from .evaluation import evaluate_design, evaluate_request

__all__ = [
    "BASELINE_PARAMETERS_MM",
    "PARAMETER_SPECS",
    "evaluate_design",
    "evaluate_request",
]
