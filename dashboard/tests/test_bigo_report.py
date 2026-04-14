"""Tests for the Big O report builders."""

import plotly.graph_objects as go

from lib.bigo.problems import PROBLEMS
from lib.bigo.runner import ProblemResult, VariantResult, NPoint
from lib.bigo.report import build_complexity_chart, build_variant_card


def _fake_result():
    problem = PROBLEMS["fibonacci"]
    variant_results = []
    for variant in problem.variants:
        points = [
            NPoint(n=5,  wall_ms=0.01),
            NPoint(n=10, wall_ms=0.1),
            NPoint(n=15, wall_ms=1.0),
            NPoint(n=20, wall_ms=10.0),
        ]
        variant_results.append(VariantResult(variant=variant, points=points))
    return ProblemResult(problem=problem, variant_results=variant_results)


def test_build_complexity_chart_returns_figure():
    fig = build_complexity_chart(_fake_result())
    assert isinstance(fig, go.Figure)
    # One trace per variant minimum (theoretical overlays are extras)
    assert len(fig.data) >= 4
    # Log-log axes
    assert fig.layout.xaxis.type == "log"
    assert fig.layout.yaxis.type == "log"


def test_build_variant_card_shape():
    result = _fake_result()
    for vr in result.variant_results:
        card = build_variant_card(vr)
        assert "headline" in card
        assert vr.variant.label in card["headline"]
        assert vr.variant.big_o in card["headline"]
        assert "rows" in card
        assert len(card["rows"]) == len(vr.points)
        for row in card["rows"]:
            assert "n" in row
            assert "status" in row
