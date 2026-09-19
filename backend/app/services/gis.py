"""Shared GIS helpers built on PostGIS via GeoAlchemy2."""
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_Contains, ST_DWithin, ST_Distance, ST_SetSRID, ST_MakePoint
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.boundary import AdministrativeBoundary


def make_point(latitude: float, longitude: float):
    return ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)


async def find_containing_boundary(db: AsyncSession, latitude: float, longitude: float) -> AdministrativeBoundary | None:
    """Point-in-polygon lookup used for authority assignment (section 12).
    Returns the smallest (most specific) matching boundary if several nest."""
    point = make_point(latitude, longitude)
    result = await db.execute(
        select(AdministrativeBoundary)
        .where(AdministrativeBoundary.geom.isnot(None))
        .where(ST_Contains(AdministrativeBoundary.geom, point))
    )
    boundaries = result.scalars().all()
    if not boundaries:
        return None
    # Prefer the most specific level (VILLAGE/WARD over DISTRICT) when nested.
    specificity = {"WARD": 0, "VILLAGE": 0, "TOWN": 1, "URBAN_AREA": 1, "BLOCK": 2, "DISTRICT": 3}
    return sorted(boundaries, key=lambda b: specificity.get(b.level, 99))[0]


def nearby_filter(column, latitude: float, longitude: float, radius_meters: float):
    """PostGIS geography cast gives ST_DWithin/ST_Distance results in meters
    directly, avoiding a manual degrees<->meters approximation."""
    point = make_point(latitude, longitude)
    return ST_DWithin(column.cast(Geography), point.cast(Geography), radius_meters)


def distance_expr(column, latitude: float, longitude: float):
    point = make_point(latitude, longitude)
    return ST_Distance(column.cast(Geography), point.cast(Geography))
