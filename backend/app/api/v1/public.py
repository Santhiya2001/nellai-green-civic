"""Unauthenticated, public-facing endpoints -- aggregate counts only, no PII.
Powers the marketing/landing page's stats section with real numbers instead
of hard-coded placeholders."""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.complaint import Complaint
from app.models.user import User

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/stats")
async def public_stats(db: AsyncSession = Depends(get_db)):
    total_complaints = (await db.execute(select(func.count(Complaint.id)))).scalar_one()
    resolved_complaints = (await db.execute(select(func.count(Complaint.id)).where(Complaint.status.in_(["RESOLVED", "CLOSED"])))).scalar_one()

    # Registered users (citizens + volunteers + authorities), active only.
    total_users = (await db.execute(select(func.count(User.id)).where(User.is_active.is_(True)))).scalar_one()

    trees_registered = 0
    volunteer_events = 0
    try:
        import importlib
        tree_model = importlib.import_module("nellai_modules.afforestation.models").Tree
        trees_registered = (await db.execute(select(func.count(tree_model.id)))).scalar_one()
    except Exception:
        pass
    try:
        import importlib
        event_model = importlib.import_module("nellai_modules.volunteer.models").VolunteerEvent
        volunteer_events = (await db.execute(select(func.count(event_model.id)))).scalar_one()
    except Exception:
        pass

    return {
        "total_complaints": total_complaints,
        "resolved_complaints": resolved_complaints,
        "registered_users": total_users,
        "trees_registered": trees_registered,
        "volunteer_events": volunteer_events,
    }
