import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


@pytest.fixture
async def session():
    """In-memory SQLite for fast tests."""
    from src.models import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()


class TestScanRecord:
    async def test_save_and_retrieve(self, session):
        from src.db import save_scan, get_recent_scans

        await save_scan(session, tickers=["AAPL", "MSFT"], var_pct=-2.15, narrative="Test narrative")
        scans = await get_recent_scans(session, limit=10)
        assert len(scans) == 1
        assert scans[0].tickers == "AAPL,MSFT"
        assert scans[0].var_pct == pytest.approx(-2.15)
        assert scans[0].narrative == "Test narrative"
