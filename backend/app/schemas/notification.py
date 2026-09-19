import uuid
from datetime import datetime

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: uuid.UUID
    title: str
    body: str
    type: str
    is_read: bool
    related_complaint_id: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
