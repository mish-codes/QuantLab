"""Async CRUD operations for yield curves and bonds.

All functions take an AsyncSession and commit before returning, so each
call is one atomic unit of work. The JSON payloads on curve records are
stored as strings; helpers convert to/from dicts at the boundary.
"""

import json
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from yield_store.models import (
    ParYieldRecord,
    SpotCurveRecord,
    BondRecord,
)


async def save_par_yields(
    session: AsyncSession, curve_date: date, yields: dict[str, float]
) -> ParYieldRecord:
    """Save par yields for a date. Upserts — overwrites if the date exists."""
    existing = await session.execute(
        select(ParYieldRecord).where(ParYieldRecord.curve_date == curve_date)
    )
    record = existing.scalar_one_or_none()

    if record:
        record.yields_json = json.dumps(yields)
    else:
        record = ParYieldRecord(
            curve_date=curve_date, yields_json=json.dumps(yields)
        )
        session.add(record)

    await session.commit()
    return record


async def get_par_yields_by_date(
    session: AsyncSession, curve_date: date
) -> dict[str, float] | None:
    """Get par yields for a specific date. Returns None if not found."""
    result = await session.execute(
        select(ParYieldRecord).where(ParYieldRecord.curve_date == curve_date)
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None
    return json.loads(record.yields_json)


async def get_par_yields_range(
    session: AsyncSession, start: date, end: date
) -> list[dict]:
    """Get par yields for an inclusive date range, ordered by date."""
    result = await session.execute(
        select(ParYieldRecord)
        .where(ParYieldRecord.curve_date >= start)
        .where(ParYieldRecord.curve_date <= end)
        .order_by(ParYieldRecord.curve_date)
    )
    records = result.scalars().all()
    return [
        {"date": r.curve_date, "yields": json.loads(r.yields_json)}
        for r in records
    ]


async def save_spot_curve(
    session: AsyncSession, curve_date: date, rates: dict[str, float]
) -> SpotCurveRecord:
    """Save spot curve for a date. Upserts."""
    existing = await session.execute(
        select(SpotCurveRecord).where(SpotCurveRecord.curve_date == curve_date)
    )
    record = existing.scalar_one_or_none()

    if record:
        record.rates_json = json.dumps(rates)
    else:
        record = SpotCurveRecord(
            curve_date=curve_date, rates_json=json.dumps(rates)
        )
        session.add(record)

    await session.commit()
    return record


async def get_spot_curve_by_date(
    session: AsyncSession, curve_date: date
) -> dict[str, float] | None:
    """Get spot curve for a specific date. Returns None if not found."""
    result = await session.execute(
        select(SpotCurveRecord).where(SpotCurveRecord.curve_date == curve_date)
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None
    return json.loads(record.rates_json)


async def save_bond(
    session: AsyncSession,
    isin: str,
    coupon: float,
    maturity: date,
    face_value: float = 1000.0,
    issue_date: date | None = None,
    frequency: int = 2,
    bond_type: str = "treasury",
    is_callable: bool = False,
) -> BondRecord:
    """Save a bond definition."""
    record = BondRecord(
        isin=isin,
        coupon=coupon,
        maturity=maturity,
        face_value=face_value,
        issue_date=issue_date or date.today(),
        frequency=frequency,
        bond_type=bond_type,
        is_callable=is_callable,
    )
    session.add(record)
    await session.commit()
    return record


async def get_bond_by_isin(
    session: AsyncSession, isin: str
) -> BondRecord | None:
    """Get a bond by ISIN. Returns None if not found."""
    result = await session.execute(
        select(BondRecord).where(BondRecord.isin == isin)
    )
    return result.scalar_one_or_none()
