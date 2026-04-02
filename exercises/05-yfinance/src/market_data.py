import numpy as np
import pandas as pd
import yfinance as yf


def fetch_closing_prices(tickers: list[str], period: str = "1y") -> pd.DataFrame:
    """Download closing prices from Yahoo Finance.

    Args:
        tickers: List of stock symbols.
        period: History period (e.g. "1y", "6mo", "5y").

    Returns:
        DataFrame with date index and one column per ticker.
    """
    data = yf.download(tickers, period=period, auto_adjust=True, progress=False)

    if data.empty:
        raise ValueError(f"No data returned for tickers: {tickers}")

    # yfinance returns MultiIndex for multiple tickers
    if isinstance(data.columns, pd.MultiIndex):
        data = data["Close"]
    elif "Close" in data.columns:
        data = data[["Close"]]
        data.columns = tickers

    return data


def validate_data(prices: pd.DataFrame) -> pd.DataFrame:
    """Clean price data: drop leading NaN rows, forward-fill gaps.

    Args:
        prices: Raw price DataFrame from yfinance.

    Returns:
        Cleaned DataFrame with no NaN values.
    """
    # Drop rows where ALL values are NaN (market holidays, etc.)
    prices = prices.dropna(how="all")

    # Drop leading rows with any NaN (ticker didn't exist yet)
    first_valid = prices.apply(lambda col: col.first_valid_index()).max()
    if first_valid is not None:
        prices = prices.loc[first_valid:]

    # Forward-fill remaining gaps (stock halts, missing data)
    prices = prices.ffill()

    return prices


def compute_returns(prices: pd.DataFrame) -> np.ndarray:
    """Convert price DataFrame to numpy array of daily returns.

    Args:
        prices: Cleaned price DataFrame.

    Returns:
        (n_days-1, n_tickers) numpy array of daily percentage returns.
    """
    values = prices.values
    returns = np.diff(values, axis=0) / values[:-1]
    return np.nan_to_num(returns, nan=0.0)
