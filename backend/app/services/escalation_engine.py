"""Automatic escalation engine (spec section 14).

`compute_deadline` is called once, when a complaint is assigned, to set
Complaint.deadline_at using the matching EscalationRule and the working-day
calendar (never a naive +72h).

`run_escalation_sweep` is meant to run periodically (see
scripts/run_escalation_sweep.py, intended for cron / a simple loop) and:
  - sends a reminder notification when a complaint is close to its deadline
  - escalates a complaint's authority level when the deadline has passed
    and the complaint is not yet RESOLVED/CLOSED/REJECTED

Escalation targets are computed the same way as the original assignment
(category + boundary + AuthorityResponsibilityMap), but filtered to the
next AuthorityLevel from the rule, so it never hard-codes a specific office.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.authority import Authority, AuthorityResponsibilityMap
from app.models.complaint import Complaint, ComplaintStatusHistory
from app.models.enums import ComplaintStatus
from app.models.escalation import EscalationRule
from app.services.notification_service import notify_user
from app.services.working_calendar import add_working_days

TERMINAL_STATUSES = {
    ComplaintStatus.RESOLVED.value,
    ComplaintStatus.CLOSED.value,
    ComplaintStatus.REJECTED.value,
    ComplaintStatus.VERIFICATION.value,
}


async def get_rule_for_category(db: AsyncSession, category_code: str) -> EscalationRule:
    result = await db.execute(select(EscalationRule).where(EscalationRule.category_code == category_code, EscalationRule.is_active.is_(True)))
    rule = result.scalar_one_or_none()
    if rule is None:
        result = await db.execute(select(EscalationRule).where(EscalationRule.category_code.is_(None), EscalationRule.is_active.is_(True)))
        rule = result.scalar_one_or_none()
    return rule


async def compute_deadline(db: AsyncSession, category_code: str, from_time: datetime | None = None) -> datetime:
    rule = await get_rule_for_category(db, category_code)
    deadline_days = rule.deadline_days if rule else 3
    start = from_time or datetime.now(timezone.utc)
    return await add_working_days(db, start, deadline_days)


async def _next_authority_for_level(db: AsyncSession, category_code: str, boundary_id, level: str) -> Authority | None:
    query = (
        select(AuthorityResponsibilityMap)
        .where(AuthorityResponsibilityMap.category_code == category_code)
        .order_by(AuthorityResponsibilityMap.priority.desc())
    )
    result = await db.execute(query)
    candidates = result.scalars().all()
    for c in candidates:
        authority = (await db.execute(select(Authority).where(Authority.id == c.authority_id))).scalar_one_or_none()
        if authority and authority.level == level:
            return authority
    return None


async def run_escalation_sweep(db: AsyncSession) -> dict:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Complaint).where(Complaint.status.notin_(list(TERMINAL_STATUSES))).where(Complaint.deadline_at.isnot(None))
    )
    complaints = result.scalars().all()

    reminded, escalated = 0, 0

    for complaint in complaints:
        rule = await get_rule_for_category(db, complaint.category.code if complaint.category else None)
        reminder_days = rule.reminder_before_days if rule else 1

        reminder_threshold = complaint.deadline_at - timedelta(days=reminder_days)
        if now >= reminder_threshold and now < complaint.deadline_at:
            await notify_user(
                db,
                complaint.user_id,
                title="Deadline approaching",
                body=f"Your complaint {complaint.complaint_number} is due soon.",
                notif_type="DEADLINE_APPROACHING",
                related_complaint_id=complaint.id,
            )
            reminded += 1

        if now >= complaint.deadline_at:
            levels = ["LOCAL_BODY", "BLOCK_LEVEL", "DISTRICT_LEVEL"]
            current_index = min(complaint.escalation_level, len(levels) - 1)
            next_index = min(current_index + 1, len(levels) - 1)
            if next_index > current_index or complaint.escalation_level == 0:
                next_level = levels[next_index]
                new_authority = await _next_authority_for_level(
                    db, complaint.category.code if complaint.category else None, complaint.boundary_id, next_level
                )
                if new_authority and new_authority.id != complaint.assigned_authority_id:
                    complaint.assigned_authority_id = new_authority.id
                complaint.escalation_level = max(complaint.escalation_level + 1, 1)
                complaint.last_escalated_at = now
                db.add(
                    ComplaintStatusHistory(
                        complaint_id=complaint.id,
                        from_status=complaint.status,
                        to_status=complaint.status,
                        note=f"Auto-escalated to level {complaint.escalation_level}",
                    )
                )
                await notify_user(
                    db,
                    complaint.user_id,
                    title="Complaint escalated",
                    body=f"Your complaint {complaint.complaint_number} has been escalated.",
                    notif_type="COMPLAINT_ESCALATED",
                    related_complaint_id=complaint.id,
                )
                escalated += 1

    await db.commit()
    return {"reminded": reminded, "escalated": escalated, "checked": len(complaints)}
