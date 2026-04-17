"""Load the committed contagion events parquet.

Kept minimal and side-effect-free; the Streamlit page wraps this in
`@st.cache_data` at the page layer to avoid importing Streamlit here.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "contagion" / "events.parquet"


def load_events(
    *, path: Optional[Path] = None, period: Optional[str] = None
) -> pd.DataFrame:
    """Return the events DataFrame, optionally filtered by period.

    Columns: date, period, ticker, asset_role, country, close.
    """
    p = Path(path) if path is not None else DEFAULT_PATH
    if not p.exists():
        raise FileNotFoundError(
            f"Events parquet not found at {p}. Run "
            f"`python scripts/fetch_contagion_data.py` to generate it."
        )
    df = pd.read_parquet(p)
    if period is not None:
        df = df[df["period"] == period].reset_index(drop=True)
    return df
