"""Tests for the Big O problem registry."""

from lib.bigo.problems import PROBLEMS, Problem, AlgorithmVariant


def test_registry_has_seed_problems():
    assert "fibonacci" in PROBLEMS
    assert "pair_sum" in PROBLEMS
    fib = PROBLEMS["fibonacci"]
    pair = PROBLEMS["pair_sum"]
    assert isinstance(fib, Problem)
    assert isinstance(pair, Problem)
    assert len(fib.variants) == 4
    assert len(pair.variants) == 3
    assert all(isinstance(v, AlgorithmVariant) for v in fib.variants)
    assert all(isinstance(v, AlgorithmVariant) for v in pair.variants)
    assert fib.explainer.strip()   # non-empty
    assert pair.explainer.strip()
    assert fib.description.strip()
    assert pair.description.strip()
    assert len(fib.n_values) > 0
    assert len(pair.n_values) > 0


def test_input_factory_returns_tuple():
    for key, problem in PROBLEMS.items():
        args = problem.input_factory(problem.n_values[0])
        assert isinstance(args, tuple), f"{key} input_factory must return a tuple"
        # Every variant should be callable with these args
        for variant in problem.variants:
            try:
                variant.fn(*args)
            except Exception as exc:
                raise AssertionError(
                    f"{key}.{variant.key} raised when called with "
                    f"input_factory({problem.n_values[0]}): {exc}"
                )


def test_variant_big_o_labels_non_empty():
    for key, problem in PROBLEMS.items():
        for variant in problem.variants:
            assert variant.big_o.strip(), f"{key}.{variant.key} missing big_o label"
            assert variant.label.strip(), f"{key}.{variant.key} missing label"
            assert variant.key.strip(), f"{key}.{variant.key} missing key"
