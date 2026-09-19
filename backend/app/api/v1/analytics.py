from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.complaint import Complaint, ComplaintCategory
from app.models.enums import ComplaintStatus

router = APIRouter(prefix="/analytics", tags=["Analytics"], dependencies=[Depends(require_roles("ADMIN", "AUTHORITY"))])

OPEN_STATUSES = [s.value for s in ComplaintStatus if s.value not in {"CLOSED", "REJECTED"}]


@router.get("/dashboard")
async def dashboard_summary(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(Complaint.id)))).scalar_one()
    open_count = (await db.execute(select(func.count(Complaint.id)).where(Complaint.status.in_(OPEN_STATUSES)))).scalar_one()
    resolved = (await db.execute(select(func.count(Complaint.id)).where(Complaint.status.in_(["RESOLVED", "CLOSED"])))).scalar_one()
    overdue = (
        await db.execute(
            select(func.count(Complaint.id))
            .where(Complaint.status.in_(OPEN_STATUSES))
            .where(Complaint.deadline_at.isnot(None))
            .where(Complaint.deadline_at < datetime.now(timezone.utc))
        )
    ).scalar_one()
    escalated = (await db.execute(select(func.count(Complaint.id)).where(Complaint.escalation_level > 0))).scalar_one()
    high_severity = (await db.execute(select(func.count(Complaint.id)).where(Complaint.severity.in_(["HIGH", "CRITICAL"])).where(Complaint.status.in_(OPEN_STATUSES)))).scalar_one()

    return {
        "total_complaints": total,
        "open_complaints": open_count,
        "resolved_complaints": resolved,
        "overdue_complaints": overdue,
        "escalated_complaints": escalated,
        "high_severity_open": high_severity,
    }


@router.get("/by-category")
async def complaints_by_category(db: AsyncSession = Depends(get_db)):
    query = (
        select(ComplaintCategory.name, func.count(Complaint.id))
        .join(Complaint, Complaint.category_id == ComplaintCategory.id)
        .group_by(ComplaintCategory.name)
        .order_by(func.count(Complaint.id).desc())
    )
    rows = (await db.execute(query)).all()
    return [{"category": name, "count": count} for name, count in rows]


@router.get("/by-status")
async def complaints_by_status(db: AsyncSession = Depends(get_db)):
    query = select(Complaint.status, func.count(Complaint.id)).group_by(Complaint.status)
    rows = (await db.execute(query)).all()
    return [{"status": status_value, "count": count} for status_value, count in rows]


@router.get("/monthly-trend")
async def monthly_trend(db: AsyncSession = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(days=365)
    query = (
        select(func.date_trunc("month", Complaint.created_at).label("month"), func.count(Complaint.id))
        .where(Complaint.created_at >= since)
        .group_by("month")
        .order_by("month")
    )
    rows = (await db.execute(query)).all()
    return [{"month": month.strftime("%Y-%m"), "count": count} for month, count in rows]
