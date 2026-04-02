import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch
from market_data import fetch_closing_prices, compute_returns, validate_data


@pytest.fixture
def mock_prices():
    """Realistic price data with some NaN values (like real market data)."""
    dates = pd.date_range("2025-01-01", periods=10, freq="B")
    return pd.DataFrame({
        "AAPL": [150.0, 152.0, np.nan, 155.0, 153.0, 157.0, 156.0, 160.0, 158.0, 162.0],
        "MSFT": [300.0, 305.0, 308.0, 310.0, 307.0, 312.0, 315.0, 318.0, 316.0, 320.0],
    }, index=dates)


@pytest.fixture
def clean_prices():
    dates = pd.date_range("2025-01-01", periods=5, freq="B")
    return pd.DataFrame({
        "AAPL": [100.0, 105.0, 103.0, 108.0, 110.0],
        "MSFT": [200.0, 210.0, 205.0, 215.0, 220.0],
    }, index=dates)


class TestFetchClosingPrices:
    def test_returns_dataframe(self, mock_prices):
        with patch("market_data.yf.download") as mock_dl:
            mock_dl.return_value = mock_prices
            result = fetch_closing_prices(["AAPL", "MSFT"], period="1y")
            assert isinstance(result, pd.DataFrame)
            assert list(result.columns) == ["AAPL", "MSFT"]

    def test_empty_data_raises(self):
        with patch("market_data.yf.download") as mock_dl:
            mock_dl.return_value = pd.DataFrame()
            with pytest.raises(ValueError, match="No data"):
                fetch_closing_prices(["INVALID"], period="1y")


class TestValidateData:
    def test_fills_nan_forward(self, mock_prices):
        clean = validate_data(mock_prices)
        assert not clean.isna().any().any()

    def test_drops_leading_nans(self):
        dates = pd.date_range("2025-01-01", periods=3, freq="B")
        df = pd.DataFrame({"A": [np.nan, 100.0, 105.0]}, index=dates)
        clean = validate_data(df)
        assert len(clean) == 2


class TestComputeReturns:
    def test_shape(self, clean_prices):
        returns = compute_returns(clean_prices)
        assert returns.shape == (4, 2)  # 5 prices -> 4 returns

    def test_no_nans(self, clean_prices):
        returns = compute_returns(clean_prices)
        assert not np.isnan(returns).any()

    def test_returns_are_percentages(self, clean_prices):
        returns = compute_returns(clean_prices)
        # First return for AAPL: (105-100)/100 = 0.05
        assert returns[0, 0] == pytest.approx(0.05)
