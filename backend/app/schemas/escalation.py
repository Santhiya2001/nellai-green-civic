import uuid


from pydantic import BaseModel


class EscalationRuleCreate(BaseModel):
    category_code: str | None = None
    deadline_days: int = 3
    initial_authority_level: str = "LOCAL_BODY"
    escalation_level_1: str = "BLOCK_LEVEL"
    escalation_level_2: str = "DISTRICT_LEVEL"
    reminder_before_days: int = 1
    config: dict | None = None


class EscalationRuleOut(EscalationRuleCreate):
    id: uuid.UUID
    is_active: bool

    model_config = {"from_attributes": True}


class SweepResult(BaseModel):
    reminded: int
    escalated: int
    checked: int
