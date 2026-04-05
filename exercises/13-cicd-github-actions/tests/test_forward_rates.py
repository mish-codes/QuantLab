import pytest

from forward_rates import calculate_forward_rates, forward_rate_between


class TestForwardRateBetween:
    def test_basic_forward_rate(self):
        """f(1,2) from 1Y spot=4% and 2Y spot=5%.

        (1.05)^2 = (1.04) * (1 + f)  =>  f = 1.05^2 / 1.04 - 1 ≈ 6.0096%
        """
        f = forward_rate_between(
            spot_short=4.0, years_short=1.0,
            spot_long=5.0, years_long=2.0,
        )
        assert f == pytest.approx(6.0096, abs=0.01)

    def test_equal_spots_give_same_forward(self):
        f = forward_rate_between(
            spot_short=5.0, years_short=1.0,
            spot_long=5.0, years_long=2.0,
        )
        assert f == pytest.approx(5.0, abs=0.01)

    def test_inverted_gives_lower_forward(self):
        """If long spot < short spot, forward is lower than long spot."""
        f = forward_rate_between(
            spot_short=5.0, years_short=1.0,
            spot_long=4.0, years_long=2.0,
        )
        assert f < 4.0


class TestCalculateForwardRates:
    def test_basic_forward_curve(self):
        spot_curve = {"1Y": 4.0, "2Y": 5.0, "5Y": 5.5}
        forwards = calculate_forward_rates(spot_curve)

        assert "1Y-2Y" in forwards
        assert "2Y-5Y" in forwards
        assert len(forwards) == 2

    def test_single_maturity_returns_empty(self):
        forwards = calculate_forward_rates({"1Y": 4.0})
        assert forwards == {}

    def test_forward_rates_positive_for_normal_curve(self):
        spot_curve = {"1Y": 3.0, "2Y": 3.5, "3Y": 4.0, "5Y": 4.5, "10Y": 5.0}
        forwards = calculate_forward_rates(spot_curve)
        for rate in forwards.values():
            assert rate > 0

    def test_empty_curve_returns_empty(self):
        assert calculate_forward_rates({}) == {}

    def test_forward_values_are_reasonable(self):
        """Forward between two maturities should exceed the long spot for a normal curve."""
        spot_curve = {"1Y": 4.0, "2Y": 4.5, "5Y": 5.0}
        forwards = calculate_forward_rates(spot_curve)
        assert forwards["1Y-2Y"] > spot_curve["2Y"]
