"""Full term structure of default probabilities from CDS curves.

Builds on exercise 15's constant-hazard shortcut with:
- Piecewise-constant hazard rates (different lambda for each tenor interval)
- Survival curves: S(T) = exp(-integral_0^T lambda(t) dt)
- Expected loss: EL = PD x LGD x EAD
- Recovery-rate sensitivity analysis

The piecewise bootstrap is still an approximation (it uses the simplified
CDS_spread ~ lambda_avg x LGD relationship rather than exact premium/
protection leg cash flows), but it captures the key feature that market
spreads can imply different default intensities at different horizons.
"""

from __future__ import annotations

import numpy as np

CDS_TENOR_YEARS = {"1Y": 1.0, "2Y": 2.0, "3Y": 3.0, "5Y": 5.0, "7Y": 7.0, "10Y": 10.0}
TENOR_ORDER = ["1Y", "2Y", "3Y", "5Y", "7Y", "10Y"]


def bootstrap_hazard_rates(
    cds_spreads: dict[str, float],
    recovery_rate: float = 0.40,
) -> dict[str, float]:
    """Bootstrap piecewise-constant hazard rates from a CDS term structure.

    For each successive tenor interval, the interval-specific hazard rate
    is derived so that the cumulative hazard integrates to the level implied
    by the observed CDS spread at that tenor.

    Args:
        cds_spreads: Tenor label -> CDS spread in bps.
        recovery_rate: Expected recovery rate (0..1).

    Returns:
        Dict mapping interval labels (e.g. "0-1Y", "1Y-5Y") to hazard rates.
    """
    lgd = 1.0 - recovery_rate
    ordered = [(t, cds_spreads[t]) for t in TENOR_ORDER if t in cds_spreads]

    hazard_rates: dict[str, float] = {}
    cum_hazard = 0.0
    prev_years = 0.0

    for tenor, spread_bps in ordered:
        years = CDS_TENOR_YEARS[tenor]
        dt = years - prev_years

        # Average hazard rate implied by the CDS spread out to this tenor
        lambda_avg = (spread_bps / 10000.0) / lgd
        cum_hazard_target = lambda_avg * years

        # Interval-specific hazard: what lambda is needed in [prev, years]
        # to bring cumulative hazard from where it was to the new target
        lambda_i = (cum_hazard_target - cum_hazard) / dt if dt > 0 else lambda_avg
        lambda_i = max(lambda_i, 0.0)  # floor at 0 for inverted curves

        interval = f"{int(prev_years)}Y-{tenor}" if prev_years > 0 else f"0-{tenor}"
        hazard_rates[interval] = round(lambda_i, 6)

        cum_hazard = cum_hazard_target
        prev_years = years

    return hazard_rates


def survival_curve(
    cds_spreads: dict[str, float],
    recovery_rate: float = 0.40,
    time_points: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Calculate the survival probability curve S(T) = exp(-lambda_avg * T).

    Args:
        cds_spreads: Tenor label -> CDS spread in bps.
        recovery_rate: Recovery rate (0..1).
        time_points: Times in years (defaults to 0..10 in 0.5-year steps).

    Returns:
        (times, survival_probabilities) arrays.
    """
    if time_points is None:
        time_points = np.arange(0, 11, 0.5)

    ordered = [(t, cds_spreads[t]) for t in TENOR_ORDER if t in cds_spreads]
    lgd = 1.0 - recovery_rate

    survival = np.ones_like(time_points, dtype=float)
    for i, t in enumerate(time_points):
        if t == 0:
            continue
        # Use the spread from the nearest tenor >= t (flat extrapolation beyond last)
        lambda_avg = 0.0
        for tenor, spread_bps in ordered:
            years = CDS_TENOR_YEARS[tenor]
            if years >= t:
                lambda_avg = (spread_bps / 10000.0) / lgd
                break
        else:
            lambda_avg = (ordered[-1][1] / 10000.0) / lgd

        survival[i] = np.exp(-lambda_avg * t)

    return time_points, survival


def default_probability_term_structure(
    cds_spreads: dict[str, float],
    recovery_rate: float = 0.40,
) -> dict[str, float]:
    """Cumulative default probability at each CDS tenor.

    P(default by T) = 1 - exp(-lambda_avg * T)

    Returns:
        Tenor label -> cumulative default probability.
    """
    lgd = 1.0 - recovery_rate
    probs: dict[str, float] = {}
    for tenor in TENOR_ORDER:
        if tenor not in cds_spreads:
            continue
        years = CDS_TENOR_YEARS[tenor]
        lambda_avg = (cds_spreads[tenor] / 10000.0) / lgd
        probs[tenor] = round(1.0 - np.exp(-lambda_avg * years), 6)
    return probs


def expected_loss(
    default_prob: float,
    lgd: float,
    exposure: float,
) -> float:
    """Expected loss = PD x LGD x EAD.

    Args:
        default_prob: Probability of default (0..1).
        lgd: Loss given default (0..1).
        exposure: Exposure at default (dollar amount).

    Returns:
        Expected loss in dollars.
    """
    return round(default_prob * lgd * exposure, 2)
