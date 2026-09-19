import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ComplaintCategoryOut(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    module_id: str
    default_severity: str
    icon: str

    model_config = {"from_attributes": True}


class ComplaintCreate(BaseModel):
    category_code: str
    description: str = Field(min_length=5, max_length=3000)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address_text: str | None = None
    extra_data: dict | None = None


class DuplicateHint(BaseModel):
    complaint_id: uuid.UUID
    complaint_number: str
    score: float


class ComplaintOut(BaseModel):
    id: uuid.UUID
    complaint_number: str
    user_id: uuid.UUID
    category: ComplaintCategoryOut
    description: str
    image_url: str | None
    latitude: float
    longitude: float
    address_text: str | None
    severity: str
    ai_category_code: str | None
    ai_confidence: float | None
    ai_severity: str | None
    status: str
    assigned_authority_id: uuid.UUID | None
    deadline_at: datetime | None
    escalation_level: int
    duplicate_of_id: uuid.UUID | None
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ComplaintListItem(BaseModel):
    id: uuid.UUID
    complaint_number: str
    category_code: str
    description: str
    severity: str
    status: str
    latitude: float
    longitude: float
    created_at: datetime
    deadline_at: datetime | None


class StatusUpdateRequest(BaseModel):
    to_status: str
    note: str | None = None


class ResolutionCreate(BaseModel):
    description: str = Field(min_length=5, max_length=2000)
    latitude: float | None = None
    longitude: float | None = None


class ResolutionOut(BaseModel):
    id: uuid.UUID
    complaint_id: uuid.UUID
    description: str
    photo_url: str | None
    resolved_by: uuid.UUID
    resolved_at: datetime
    citizen_verified: bool | None
    citizen_feedback: str | None

    model_config = {"from_attributes": True}


class CitizenVerificationRequest(BaseModel):
    verified: bool
    feedback: str | None = None


class RejectionRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=1000)
