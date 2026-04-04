import pytest
from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from yield_store.models import Base
from yield_store.db import (
    save_par_yields,
    get_par_yields_by_date,
    get_par_yields_range,
    save_spot_curve,
    get_spot_curve_by_date,
    save_bond,
    get_bond_by_isin,
)


@pytest.fixture
async def session():
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s
    await engine.dispose()


class TestParYields:
    async def test_save_and_retrieve(self, session):
        yields_data = {"1M": 5.25, "3M": 5.30, "10Y": 4.30, "30Y": 4.45}
        await save_par_yields(session, date(2026, 4, 4), yields_data)

        result = await get_par_yields_by_date(session, date(2026, 4, 4))
        assert result is not None
        assert result["10Y"] == 4.30
        assert result["30Y"] == 4.45

    async def test_missing_date_returns_none(self, session):
        result = await get_par_yields_by_date(session, date(2099, 1, 1))
        assert result is None

    async def test_upsert_overwrites(self, session):
        await save_par_yields(session, date(2026, 4, 4), {"10Y": 4.30})
        await save_par_yields(session, date(2026, 4, 4), {"10Y": 4.35})

        result = await get_par_yields_by_date(session, date(2026, 4, 4))
        assert result["10Y"] == 4.35

    async def test_range_query(self, session):
        await save_par_yields(session, date(2026, 4, 1), {"10Y": 4.20})
        await save_par_yields(session, date(2026, 4, 2), {"10Y": 4.25})
        await save_par_yields(session, date(2026, 4, 3), {"10Y": 4.30})

        results = await get_par_yields_range(
            session, date(2026, 4, 1), date(2026, 4, 3)
        )
        assert len(results) == 3
        assert results[0]["date"] == date(2026, 4, 1)
        assert results[2]["yields"]["10Y"] == 4.30


class TestSpotCurve:
    async def test_save_and_retrieve(self, session):
        spot_data = {"1Y": 4.80, "2Y": 4.52, "5Y": 4.25, "10Y": 4.35}
        await save_spot_curve(session, date(2026, 4, 4), spot_data)

        result = await get_spot_curve_by_date(session, date(2026, 4, 4))
        assert result is not None
        assert result["2Y"] == 4.52


class TestBond:
    async def test_save_and_retrieve(self, session):
        await save_bond(
            session,
            isin="US912828ZT58",
            coupon=2.875,
            maturity=date(2032, 5, 15),
            face_value=1000.0,
            issue_date=date(2022, 5, 15),
            frequency=2,
        )

        bond = await get_bond_by_isin(session, "US912828ZT58")
        assert bond is not None
        assert bond.coupon == 2.875
        assert bond.frequency == 2

    async def test_missing_isin_returns_none(self, session):
        result = await get_bond_by_isin(session, "DOESNOTEXIST")
        assert result is None
