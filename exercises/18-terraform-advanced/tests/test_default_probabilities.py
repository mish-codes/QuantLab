import numpy as np
import pytest

from default_probabilities import (
    bootstrap_hazard_rates,
    default_probability_term_structure,
    expected_loss,
    survival_curve,
)


class TestBootstrapHazardRates:
    def test_single_tenor(self):
        """100 bps CDS, 40% recovery → λ ≈ 0.0167."""
        rates = bootstrap_hazard_rates({"1Y": 100}, recovery_rate=0.40)
        assert "0-1Y" in rates
        assert rates["0-1Y"] == pytest.approx(0.0167, abs=0.001)

    def test_piecewise_rates_increase_with_steeper_curve(self):
        """If 5Y spread > 1Y spread, the 1Y-5Y interval hazard should be higher."""
        rates = bootstrap_hazard_rates(
            {"1Y": 50, "5Y": 150}, recovery_rate=0.40
        )
        assert rates["1Y-5Y"] > rates["0-1Y"]

    def test_flat_curve_gives_constant_hazard(self):
        """Flat CDS curve → all interval hazard rates should be equal."""
        rates = bootstrap_hazard_rates(
            {"1Y": 100, "3Y": 100, "5Y": 100}, recovery_rate=0.40
        )
        values = list(rates.values())
        for v in values[1:]:
            assert v == pytest.approx(values[0], abs=0.0001)

    def test_hazard_rates_non_negative(self):
        """Even with inverted spreads, hazard rates are floored at 0."""
        rates = bootstrap_hazard_rates(
            {"1Y": 200, "5Y": 100}, recovery_rate=0.40
        )
        for v in rates.values():
            assert v >= 0.0


class TestSurvivalCurve:
    def test_survival_starts_at_one(self):
        times, surv = survival_curve({"1Y": 100, "5Y": 150})
        assert surv[0] == pytest.approx(1.0)

    def test_survival_decreases(self):
        times, surv = survival_curve({"1Y": 100, "5Y": 150})
        # Survival should be monotonically non-increasing
        for i in range(1, len(surv)):
            assert surv[i] <= surv[i - 1] + 1e-10

    def test_higher_spread_lower_survival(self):
        _, surv_low = survival_curve({"1Y": 50, "5Y": 80})
        _, surv_high = survival_curve({"1Y": 200, "5Y": 300})
        # At 5 years, high-spread entity should have lower survival
        assert surv_high[-1] < surv_low[-1]


class TestDefaultProbabilityTermStructure:
    def test_increasing_with_tenor(self):
        probs = default_probability_term_structure(
            {"1Y": 100, "3Y": 120, "5Y": 150}
        )
        assert probs["5Y"] > probs["3Y"] > probs["1Y"]

    def test_zero_spread_zero_default(self):
        probs = default_probability_term_structure({"1Y": 0, "5Y": 0})
        assert probs["1Y"] == pytest.approx(0.0, abs=0.001)
        assert probs["5Y"] == pytest.approx(0.0, abs=0.001)

    def test_known_value(self):
        """100 bps, 40% recovery, 1Y → ~1.65% default prob."""
        probs = default_probability_term_structure({"1Y": 100}, recovery_rate=0.40)
        assert probs["1Y"] == pytest.approx(0.0165, abs=0.002)


class TestExpectedLoss:
    def test_basic_calculation(self):
        """PD=5%, LGD=60%, EAD=$1M → EL=$30,000."""
        el = expected_loss(default_prob=0.05, lgd=0.60, exposure=1_000_000)
        assert el == pytest.approx(30_000, abs=1)

    def test_zero_pd_zero_loss(self):
        el = expected_loss(default_prob=0.0, lgd=0.60, exposure=1_000_000)
        assert el == 0.0

    def test_full_default_full_lgd(self):
        el = expected_loss(default_prob=1.0, lgd=1.0, exposure=500_000)
        assert el == pytest.approx(500_000, abs=1)
