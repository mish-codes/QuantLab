"""Big O Demo package.

Public API:
- PROBLEMS, Problem, AlgorithmVariant
- run_problem, ProblemResult, VariantResult, NPoint
- build_complexity_chart, build_variant_card
"""

from .problems import PROBLEMS, Problem, AlgorithmVariant
from .runner import run_problem, ProblemResult, VariantResult, NPoint
from .report import build_complexity_chart, build_variant_card

__all__ = [
    "PROBLEMS",
    "Problem",
    "AlgorithmVariant",
    "run_problem",
    "ProblemResult",
    "VariantResult",
    "NPoint",
    "build_complexity_chart",
    "build_variant_card",
]
