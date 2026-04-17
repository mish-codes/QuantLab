"""Unit tests for pydeck globe layer builder."""
import pytest

from lib.contagion import globe


def test_correlation_to_color_red_at_plus_one():
    r, g, b, a = globe.correlation_to_color(1.0)
    assert r >= 180 and g < 50 and b < 50


def test_correlation_to_color_green_at_minus_one():
    r, g, b, a = globe.correlation_to_color(-1.0)
    assert g >= 100 and r < 50 and b < 50


def test_correlation_to_color_gray_at_zero():
    r, g, b, a = globe.correlation_to_color(0.0)
    # Midpoint: should be near mid-gray (roughly equal channels)
    assert abs(r - g) < 40 and abs(g - b) < 40


def test_correlation_to_color_clips_out_of_range():
    assert globe.correlation_to_color(2.0) == globe.correlation_to_color(1.0)
    assert globe.correlation_to_color(-2.0) == globe.correlation_to_color(-1.0)


def test_build_arc_layer_returns_one_arc_per_destination():
    arcs = globe.build_arc_rows(
        correlations_by_country={"IN": 0.8, "TR": -0.3, "DE": 0.1, "US": -0.7, "GB": 0.5}
    )
    assert len(arcs) == 5
    countries = {arc["dest_country"] for arc in arcs}
    assert countries == {"IN", "TR", "DE", "US", "GB"}
    for arc in arcs:
        assert len(arc["source"]) == 2   # [lon, lat]
        assert len(arc["target"]) == 2
        assert len(arc["color"]) == 4    # RGBA
