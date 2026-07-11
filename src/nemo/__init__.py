"""NEMO multi-part external optimization package."""

from .config import BASELINE_PARAMETERS_MM, PARAMETER_SPECS
from .evaluation import evaluate_design, evaluate_request
from .parts import get_part_definition, list_part_definitions

__all__ = [
    "BASELINE_PARAMETERS_MM",
    "PARAMETER_SPECS",
    "evaluate_design",
    "evaluate_request",
    "get_part_definition",
    "list_part_definitions",
]
