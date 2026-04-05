"""Parametric yield curve fitting: Nelson-Siegel and Svensson models.

Nelson-Siegel (1987) — 4 parameters:

    y(τ) = β₀ + β₁ · [(1-e^(-τ/λ)) / (τ/λ)]
                + β₂ · [(1-e^(-τ/λ)) / (τ/λ) − e^(-τ/λ)]

    β₀  long-term level (y → β₀ as τ → ∞)
    β₁  short-term slope (y → β₀+β₁ as τ → 0)
    β₂  medium-term curvature / hump
    λ   decay factor (controls where the hump peaks)

Svensson (1994) — 6 parameters: adds a second hump term for better
long-end fit. Central banks (ECB, Bundesbank) publish official curves
using NSS — six parameters compress the whole term structure into
something interpretable and forecastable.

Cubic spline is the non-parametric alternative: passes exactly through
observed points, but can oscillate between them. No economic
interpretation of parameters — just an interpolator.
"""

import numpy as np
from scipy.optimize import minimize
from scipy.interpolate import CubicSpline


def nelson_siegel(
    tau: float, beta0: float, beta1: float, beta2: float, lam: float
) -> float:
    """Evaluate Nelson-Siegel at maturity tau (years). Returns yield in percent."""
    if tau < 1e-6:
        return beta0 + beta1
    x = tau / lam
    factor1 = (1 - np.exp(-x)) / x
    factor2 = factor1 - np.exp(-x)
    return beta0 + beta1 * factor1 + beta2 * factor2


def nelson_siegel_svensson(
    tau: float,
    beta0: float, beta1: float, beta2: float, beta3: float,
    lam1: float, lam2: float,
) -> float:
    """Evaluate Nelson-Siegel-Svensson at maturity tau. Returns yield in percent."""
    ns = nelson_siegel(tau, beta0, beta1, beta2, lam1)
    if tau < 1e-6:
        return ns
    x2 = tau / lam2
    factor = (1 - np.exp(-x2)) / x2 - np.exp(-x2)
    return ns + beta3 * factor


def fit_nelson_siegel(
    maturities: np.ndarray, yields: np.ndarray
) -> tuple[dict[str, float], np.ndarray, float]:
    """Fit Nelson-Siegel to observed yields. Returns (params, fitted, rmse)."""
    def objective(params):
        b0, b1, b2, lam = params
        if lam <= 0.01:
            return 1e10
        fitted = np.array([nelson_siegel(t, b0, b1, b2, lam) for t in maturities])
        return np.sum((fitted - yields) ** 2)

    b0_init = float(yields[-1])
    b1_init = float(yields[0] - yields[-1])
    x0 = [b0_init, b1_init, 0.0, 1.5]

    result = minimize(
        objective, x0, method="Nelder-Mead",
        options={"maxiter": 10000, "xatol": 1e-8},
    )

    b0, b1, b2, lam = result.x
    fitted = np.array([nelson_siegel(t, b0, b1, b2, lam) for t in maturities])
    rmse = float(np.sqrt(np.mean((fitted - yields) ** 2)))
    params = {
        "beta0": round(b0, 4), "beta1": round(b1, 4),
        "beta2": round(b2, 4), "lambda": round(lam, 4),
    }
    return params, fitted, rmse


def fit_svensson(
    maturities: np.ndarray, yields: np.ndarray
) -> tuple[dict[str, float], np.ndarray, float]:
    """Fit Nelson-Siegel-Svensson to observed yields. Returns (params, fitted, rmse)."""
    def objective(params):
        b0, b1, b2, b3, lam1, lam2 = params
        if lam1 <= 0.01 or lam2 <= 0.01:
            return 1e10
        fitted = np.array([
            nelson_siegel_svensson(t, b0, b1, b2, b3, lam1, lam2)
            for t in maturities
        ])
        return np.sum((fitted - yields) ** 2)

    b0_init = float(yields[-1])
    b1_init = float(yields[0] - yields[-1])
    x0 = [b0_init, b1_init, 0.0, 0.0, 1.5, 3.0]

    result = minimize(
        objective, x0, method="Nelder-Mead",
        options={"maxiter": 20000, "xatol": 1e-8},
    )

    b0, b1, b2, b3, lam1, lam2 = result.x
    fitted = np.array([
        nelson_siegel_svensson(t, b0, b1, b2, b3, lam1, lam2)
        for t in maturities
    ])
    rmse = float(np.sqrt(np.mean((fitted - yields) ** 2)))
    params = {
        "beta0": round(b0, 4), "beta1": round(b1, 4),
        "beta2": round(b2, 4), "beta3": round(b3, 4),
        "lambda1": round(lam1, 4), "lambda2": round(lam2, 4),
    }
    return params, fitted, rmse


def cubic_spline_interpolate(
    maturities: np.ndarray, yields: np.ndarray, target_maturities: np.ndarray
) -> np.ndarray:
    """Interpolate yields at target maturities via cubic spline."""
    cs = CubicSpline(maturities, yields)
    return cs(target_maturities)
