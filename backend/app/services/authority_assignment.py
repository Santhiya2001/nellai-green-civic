"""Authority assignment engine (spec section 12).

Resolution order:
  1. Find the administrative boundary containing the complaint's GPS point.
  2. Look up AuthorityResponsibilityMap rows for the complaint's category,
     preferring a rule scoped to the boundary's level, falling back to a
     category rule with no boundary_level (applies everywhere), ordered by
     priority (desc).
  3. If nothing matches, leave the complaint unassigned for manual triage
     rather than guessing.

Nothing here hard-codes "Collector" or any specific officer -- all of it is
data configured by admins via /api/v1/authorities and
/api/v1/authorities/responsibility-map.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.authority import Authority, AuthorityResponsibilityMap
from app.models.boundary import AdministrativeBoundary
from app.services.gis import find_containing_boundary


async def assign_authority(
    db: AsyncSession, category_code: str, latitude: float, longitude: float
) -> tuple[Authority | None, AdministrativeBoundary | None]:
    boundary = await find_containing_boundary(db, latitude, longitude)

    query = (
        select(AuthorityResponsibilityMap)
        .where(AuthorityResponsibilityMap.category_code == category_code)
        .order_by(AuthorityResponsibilityMap.priority.desc())
    )
    result = await db.execute(query)
    candidates = result.scalars().all()
    if not candidates:
        return None, boundary

    boundary_level = boundary.level if boundary else None
    scoped = [c for c in candidates if c.boundary_level == boundary_level]
    generic = [c for c in candidates if c.boundary_level is None]

    chosen = (scoped or generic or candidates)[0]
    authority_result = await db.execute(select(Authority).where(Authority.id == chosen.authority_id))
    return authority_result.scalar_one_or_none(), boundary
