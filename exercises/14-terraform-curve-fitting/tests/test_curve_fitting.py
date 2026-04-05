import numpy as np
import pytest

from curve_fitting import (
    nelson_siegel,
    nelson_siegel_svensson,
    fit_nelson_siegel,
    fit_svensson,
    cubic_spline_interpolate,
)


class TestNelsonSiegel:
    def test_level_component(self):
        """beta0 is the long-term rate (as tau → ∞)."""
        rate = nelson_siegel(tau=30.0, beta0=5.0, beta1=0.0, beta2=0.0, lam=1.0)
        assert rate == pytest.approx(5.0, abs=0.01)

    def test_slope_component(self):
        """At tau ≈ 0, NS → beta0 + beta1."""
        rate = nelson_siegel(tau=0.01, beta0=5.0, beta1=-2.0, beta2=0.0, lam=1.0)
        assert rate == pytest.approx(3.0, abs=0.1)

    def test_curvature_component(self):
        """beta2 creates a hump at intermediate maturities."""
        short = nelson_siegel(tau=0.5, beta0=5.0, beta1=0.0, beta2=3.0, lam=2.0)
        mid = nelson_siegel(tau=2.0, beta0=5.0, beta1=0.0, beta2=3.0, lam=2.0)
        long = nelson_siegel(tau=20.0, beta0=5.0, beta1=0.0, beta2=3.0, lam=2.0)
        assert mid > short or mid > long


class TestNelsonSiegelSvensson:
    def test_reduces_to_ns_when_beta3_zero(self):
        ns = nelson_siegel(tau=5.0, beta0=5.0, beta1=-1.0, beta2=2.0, lam=1.5)
        nss = nelson_siegel_svensson(
            tau=5.0, beta0=5.0, beta1=-1.0, beta2=2.0, beta3=0.0,
            lam1=1.5, lam2=1.0,
        )
        assert nss == pytest.approx(ns, abs=0.001)


class TestFitNelsonSiegel:
    def test_fits_normal_curve(self):
        maturities = np.array([0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0])
        yields = np.array([4.80, 4.70, 4.50, 4.30, 4.20, 4.15, 4.18, 4.25, 4.40, 4.45])

        params, fitted, rmse = fit_nelson_siegel(maturities, yields)

        assert "beta0" in params
        assert "beta1" in params
        assert "beta2" in params
        assert "lambda" in params
        assert len(fitted) == len(maturities)
        assert rmse < 0.2

    def test_fitted_values_close_to_input(self):
        maturities = np.array([1.0, 2.0, 5.0, 10.0])
        yields = np.array([4.0, 4.2, 4.5, 4.8])

        _, fitted, _ = fit_nelson_siegel(maturities, yields)

        np.testing.assert_allclose(fitted, yields, atol=0.3)


class TestFitSvensson:
    def test_fits_humped_curve(self):
        maturities = np.array([0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0])
        yields = np.array([4.80, 4.90, 5.10, 5.20, 5.15, 4.90, 4.70, 4.50, 4.40, 4.45])

        params, fitted, rmse = fit_svensson(maturities, yields)

        assert "beta3" in params
        assert "lambda2" in params
        assert rmse < 0.2


class TestCubicSpline:
    def test_interpolates_between_points(self):
        maturities = np.array([1.0, 2.0, 5.0, 10.0, 30.0])
        yields = np.array([4.0, 4.2, 4.5, 4.8, 5.0])
        target = np.array([3.0, 7.0, 20.0])

        interpolated = cubic_spline_interpolate(maturities, yields, target)

        assert len(interpolated) == 3
        assert 4.2 < interpolated[0] < 4.5
        assert 4.5 < interpolated[1] < 4.8

    def test_exact_at_knot_points(self):
        maturities = np.array([1.0, 5.0, 10.0])
        yields = np.array([4.0, 4.5, 5.0])

        interpolated = cubic_spline_interpolate(maturities, yields, maturities)

        np.testing.assert_allclose(interpolated, yields, atol=0.001)
