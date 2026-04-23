"""Cached data-loading helpers shared across stock analysis pages."""
import pandas as pd
import streamlit as st
from data import fetch_stock_history


@st.cache_data(show_spinner=False, ttl=3600)
def load_stock_data(ticker: str, period: str) -> pd.DataFrame:
    """Fetch OHLCV history with a 1-hour cache."""
    return fetch_stock_history(ticker, period)


@st.cache_data(show_spinner=False, ttl=3600)
def load_returns(ticker: str, period: str) -> pd.Series:
    """Fetch daily close returns with a 1-hour cache."""
    df = fetch_stock_history(ticker, period)
    return df["Close"].pct_change().dropna()
