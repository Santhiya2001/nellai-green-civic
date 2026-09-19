"""Working-day deadline calculator (spec section 15).

Deadlines must skip weekends and configured public holidays instead of
naively adding N*24 hours. Holidays come from the working_calendar table,
falling back to the `holidays` PyPI package (India, Tamil Nadu) as a seed
when no admin-configured entries exist yet for a given year.
"""
from datetime import date, datetime, timedelta

import holidays as holidays_lib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.escalation import WorkingCalendarEntry


async def _configured_holidays(db: AsyncSession, year: int) -> set[date]:
    result = await db.execute(
        select(WorkingCalendarEntry.entry_date).where(
            WorkingCalendarEntry.is_holiday.is_(True),
        )
    )
    configured = {row[0] for row in result.all() if row[0].year == year}
    if configured:
        return configured
    # Fallback seed so the system is usable before an admin configures the calendar.
    india_holidays = holidays_lib.India(years=year, subdiv="TN")
    return set(india_holidays.keys())


def _is_weekend(d: date) -> bool:
    return d.weekday() >= 5  # Saturday=5, Sunday=6


async def add_working_days(db: AsyncSession, start: datetime, working_days: int) -> datetime:
    """Return `start` advanced by `working_days` working days, skipping
    weekends and configured holidays."""
    current = start
    years_needed = {start.year, (start + timedelta(days=working_days * 2 + 10)).year}
    holiday_set: set[date] = set()
    for y in years_needed:
        holiday_set |= await _configured_holidays(db, y)

    remaining = working_days
    while remaining > 0:
        current += timedelta(days=1)
        if _is_weekend(current.date()) or current.date() in holiday_set:
            continue
        remaining -= 1
    return current
