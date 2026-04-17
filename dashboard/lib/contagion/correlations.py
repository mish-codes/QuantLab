"""Rolling correlation and epicenter aggregation helpers.

Kept deliberately pure (no Streamlit imports) so tests are fast and
the logic is reusable from notebooks.
"""
from __future__ import annotations

import pandas as pd


def rolling_corr(
    s1: pd.Series, s2: pd.Series, window: int = 7
) -> pd.Series:
    """Pearson rolling correlation between two aligned series.

    Returns an all-NaN Series when `window` exceeds the length of the
    input; callers should handle this (the Streamlit page guards via
    `if len(aligned) < CORRELATION_WINDOW`).
    """
    return s1.rolling(window=window).corr(s2)


def middle_east_index(events: pd.DataFrame) -> pd.Series:
    """Daily simple mean of the epicenter-tagged closing values.

    Assumes `events` is the long-format DataFrame returned by the loader
    (columns: date, ticker, asset_role, close). Returns a Series indexed
    by date (the dtype matches whatever the `date` column carries —
    typically `pd.Timestamp` when loaded from parquet).

    Duplicate `(date, ticker)` rows are silently averaged by
    `pivot_table`'s default `aggfunc='mean'`. The ETL is expected to
    produce clean non-duplicated rows; if duplicates ever appear, that
    is a bug in the data pipeline, not in this function.

    Returns an empty Series if no rows have `asset_role == "epicenter"`.
    """
    epi = events[events["asset_role"] == "epicenter"]
    # Pivot → one column per ticker → row-mean → Series
    wide = epi.pivot_table(index="date", columns="ticker", values="close")
    return wide.mean(axis=1)
