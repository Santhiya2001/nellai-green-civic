import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.escalation import EscalationRule
from app.schemas.escalation import EscalationRuleCreate, EscalationRuleOut, SweepResult
from app.services.escalation_engine import run_escalation_sweep

router = APIRouter(prefix="/escalation", tags=["Escalation"])


@router.post("/rules", response_model=EscalationRuleOut, dependencies=[Depends(require_roles("ADMIN"))])
async def create_rule(payload: EscalationRuleCreate, db: AsyncSession = Depends(get_db)):
    rule = EscalationRule(**payload.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.get("/rules", response_model=list[EscalationRuleOut])
async def list_rules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EscalationRule))
    return result.scalars().all()


@router.put("/rules/{rule_id}", response_model=EscalationRuleOut, dependencies=[Depends(require_roles("ADMIN"))])
async def update_rule(rule_id: uuid.UUID, payload: EscalationRuleCreate, db: AsyncSession = Depends(get_db)):
    rule = (await db.execute(select(EscalationRule).where(EscalationRule.id == rule_id))).scalar_one_or_none()
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    for field, value in payload.model_dump().items():
        setattr(rule, field, value)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.post("/sweep", response_model=SweepResult, dependencies=[Depends(require_roles("ADMIN"))])
async def trigger_sweep(db: AsyncSession = Depends(get_db)):
    """Manually trigger the escalation sweep (also runnable unattended via
    scripts/run_escalation_sweep.py on a schedule)."""
    return await run_escalation_sweep(db)
