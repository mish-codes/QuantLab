"""Standard stock analysis input controls."""
import streamlit as st

_DEFAULT_PERIODS = ["1mo", "3mo", "6mo", "1y", "2y", "5y"]


def stock_input_panel(
    default_ticker: str = "AAPL",
    periods: list | None = None,
    default_period: str = "1y",
) -> tuple[str, str]:
    """Render ticker + period selectors. Returns (ticker, period)."""
    if periods is None:
        periods = _DEFAULT_PERIODS
    idx = periods.index(default_period) if default_period in periods else 0
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Ticker Symbol", value=default_ticker).upper().strip()
    with col2:
        period = st.selectbox("Period", periods, index=idx)
    return ticker, period
