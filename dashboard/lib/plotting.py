"""Chart builder functions for all four plotting libraries.

Each library has four functions: line, candlestick, bar (volume), histogram (returns).
All accept the same OHLCV DataFrame and return a renderable figure object.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# ── Helpers ─────────────────────────────────────────────────────────

def compute_daily_returns(df: pd.DataFrame) -> pd.Series:
    """Compute daily percentage returns from Close prices."""
    return df["Close"].pct_change().dropna()


def detect_outliers(df: pd.DataFrame, n_std: float = 3.0) -> pd.DataFrame:
    """Flag rows where any numeric column exceeds n_std from its mean.

    Returns a boolean DataFrame (same shape as numeric columns).
    """
    numeric = df.select_dtypes(include=[np.number])
    z_scores = (numeric - numeric.mean()).abs() / numeric.std()
    return z_scores > n_std


# ── Plotly ──────────────────────────────────────────────────────────

def plotly_line_chart(df: pd.DataFrame):
    """Close price line chart using Plotly."""
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"], mode="lines", name="Close",
        line=dict(color="#2a7ae2"),
    ))
    # Mark outlier points
    outliers = detect_outliers(df)
    if outliers["Close"].any():
        mask = outliers["Close"]
        fig.add_trace(go.Scatter(
            x=df.index[mask], y=df["Close"][mask],
            mode="markers", name="Outlier",
            marker=dict(color="red", size=10, symbol="x"),
        ))
    fig.update_layout(title="Close Price (Plotly)", xaxis_title="Date", yaxis_title="Price")
    return fig


def plotly_candlestick(df: pd.DataFrame):
    """OHLC candlestick chart using Plotly."""
    import plotly.graph_objects as go

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name="OHLC",
    )])
    fig.update_layout(title="Candlestick (Plotly)", xaxis_title="Date", yaxis_title="Price")
    return fig


def plotly_volume_bar(df: pd.DataFrame):
    """Volume bar chart using Plotly."""
    import plotly.graph_objects as go

    colors = ["#2a7ae2" if c >= o else "#e24a4a"
              for c, o in zip(df["Close"], df["Open"])]
    fig = go.Figure(data=[go.Bar(
        x=df.index, y=df["Volume"], marker_color=colors, name="Volume",
    )])
    fig.update_layout(title="Volume (Plotly)", xaxis_title="Date", yaxis_title="Volume")
    return fig


def plotly_returns_histogram(df: pd.DataFrame):
    """Daily returns histogram using Plotly."""
    import plotly.graph_objects as go

    returns = compute_daily_returns(df)
    fig = go.Figure(data=[go.Histogram(
        x=returns, nbinsx=40, name="Daily Returns",
        marker_color="#2a7ae2", opacity=0.75,
    )])
    fig.update_layout(title="Daily Returns Distribution (Plotly)",
                      xaxis_title="Return", yaxis_title="Frequency")
    return fig
