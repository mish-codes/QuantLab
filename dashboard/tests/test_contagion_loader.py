"""Unit tests for contagion loader."""
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from lib.contagion import loader


def _write_fixture(path: Path) -> None:
    """Write a small synthetic events parquet for testing."""
    rows = [
        (date(2020, 1, 1), "2020_us_iran", "EIS", "epicenter", "IL", 10.0),
        (date(2020, 1, 1), "2020_us_iran", "^TNX", "safe_haven", "US", 1.8),
        (date(2024, 1, 1), "2024_hormuz", "EIS", "epicenter", "IL", 15.0),
    ]
    df = pd.DataFrame(
        rows, columns=["date", "period", "ticker", "asset_role", "country", "close"]
    )
    df.to_parquet(path, index=False)


def test_load_events_returns_all_rows_when_no_period(tmp_path):
    p = tmp_path / "events.parquet"
    _write_fixture(p)
    df = loader.load_events(path=p)
    assert len(df) == 3


def test_load_events_filters_by_period(tmp_path):
    p = tmp_path / "events.parquet"
    _write_fixture(p)
    df = loader.load_events(path=p, period="2020_us_iran")
    assert len(df) == 2
    assert set(df["period"].unique()) == {"2020_us_iran"}


def test_load_events_raises_when_file_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        loader.load_events(path=tmp_path / "missing.parquet")
