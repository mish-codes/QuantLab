"""Problem registry for the Big O demo.

To add a new problem:
1. Implement its algorithm variants in algorithms.py
2. Add a Problem entry below with its variants, n_values, input_factory,
   description, and explainer.
The UI reads PROBLEMS at import time and renders whatever is there.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable

from . import algorithms as A


@dataclass
class AlgorithmVariant:
    key: str
    label: str
    big_o: str
    fn: Callable


@dataclass
class Problem:
    key: str
    label: str
    description: str
    explainer: str
    n_values: list
    input_factory: Callable
    variants: list = field(default_factory=list)


# ─────────────────────────────────────────────────────────────
# Input factories
# ─────────────────────────────────────────────────────────────

def _fib_input(n: int) -> tuple:
    return (n,)


def _pair_input(n: int) -> tuple:
    """Deterministic seeded random array of length n plus a target.

    The target is guaranteed to have a matching pair so every variant
    has meaningful work to do (no early exits on trivially-absent keys).
    """
    rng = random.Random(42 + n)  # seeded per-n for reproducibility
    arr = [rng.randint(0, n * 10) for _ in range(n)]
    # Force a valid pair: target = arr[0] + arr[-1]
    target = arr[0] + arr[-1] if n >= 2 else 0
    return (arr, target)


# ─────────────────────────────────────────────────────────────
# Explainer content
# ─────────────────────────────────────────────────────────────

_FIB_EXPLAINER = """
The Fibonacci sequence is one of the most famous in mathematics:
**0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, ...** Each number is the sum of
the previous two. The sequence appears in nature (sunflower seed
spirals, pinecones, nautilus shells), in art, and in computer science
as the canonical example of a recursive problem with dramatically
different solutions.

We compute **F(n)** — the nth number in the sequence — four ways:

- **Naive recursive** — the textbook definition `F(n) = F(n-1) + F(n-2)`.
  Looks elegant, runs in **O(2ⁿ)** because it recomputes the same values
  exponentially many times. F(35) takes seconds; F(50) takes hours.
- **Iterative** — a single loop tracking the last two values. **O(n)**,
  uses constant memory. The boring, correct solution.
- **Memoized recursive** — same recursion as naive but caches results.
  **O(n)** time and O(n) memory. Demonstrates how a one-line decorator
  collapses an exponential algorithm to linear.
- **Matrix exponentiation** — uses the identity that the Fibonacci
  numbers can be computed via powers of the matrix `[[1,1],[1,0]]`.
  Combined with fast exponentiation it runs in **O(log n)**, which is
  what lets you compute F(1,000,000) in milliseconds.

The whole point of this demo is the gap. On a log-log plot the naive
version curves up sharply and falls off the right side; the iterative
and memoized lines run nearly flat across; the matrix line is the
flattest of all.
""".strip()


_PAIR_EXPLAINER = """
The **Two-Sum** problem: given a list of numbers and a target, return
**True** if any two numbers in the list add up to the target. It's a
classic interview question and a great demonstration of how the right
data structure changes the complexity class.

- **Brute force** — two nested loops checking every pair. **O(n²)**,
  works but quadratic. At n=10,000 that's 100 million comparisons.
- **Sort + two-pointer** — sort the array first (O(n log n)), then
  walk a left pointer up and a right pointer down. **O(n log n)** total,
  dominated by the sort.
- **Hash set, single pass** — for each number `x`, check if `target - x`
  has already been seen. **O(n)** time, O(n) extra memory. Trades space
  for time and wins.

The lesson: a hash set is one of the cheapest "free upgrades" in
programming. Adding a `set()` and a single membership check turns a
quadratic algorithm into a linear one.
""".strip()


# ─────────────────────────────────────────────────────────────
# Registry
# ─────────────────────────────────────────────────────────────

PROBLEMS: dict = {
    "fibonacci": Problem(
        key="fibonacci",
        label="Fibonacci(n)",
        description="Computing the nth Fibonacci number — 4 algorithms.",
        explainer=_FIB_EXPLAINER,
        n_values=[5, 10, 15, 20, 25, 28, 30, 32, 34, 36],
        input_factory=_fib_input,
        variants=[
            AlgorithmVariant("fib_naive",     "Naive recursive",      "O(2^n)",   A.fib_naive),
            AlgorithmVariant("fib_iterative", "Iterative",            "O(n)",     A.fib_iterative),
            AlgorithmVariant("fib_memoized",  "Memoized recursive",   "O(n)",     A.fib_memoized),
            AlgorithmVariant("fib_matrix",    "Matrix exponentiation","O(log n)", A.fib_matrix),
        ],
    ),
    "pair_sum": Problem(
        key="pair_sum",
        label="Pair-sum on array",
        description="Does any two numbers in the list sum to the target? — 3 algorithms.",
        explainer=_PAIR_EXPLAINER,
        n_values=[100, 500, 1000, 2500, 5000, 7500, 10000],
        input_factory=_pair_input,
        variants=[
            AlgorithmVariant("pair_brute",  "Brute force nested loops", "O(n^2)",    A.pair_brute),
            AlgorithmVariant("pair_sorted", "Sort + two-pointer",       "O(n log n)", A.pair_sorted),
            AlgorithmVariant("pair_hash",   "Hash set, single pass",    "O(n)",       A.pair_hash),
        ],
    ),
}
