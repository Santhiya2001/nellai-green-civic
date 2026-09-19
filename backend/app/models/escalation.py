import datetime
import uuid

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class EscalationRule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Configurable per-category escalation rule (section 14 of the spec).
    category_code = None means "default rule" applied when no category-specific
    rule exists."""

    __tablename__ = "escalation_rules"

    category_code: Mapped[str | None] = mapped_column(String(60), nullable=True, index=True)
    deadline_days: Mapped[int] = mapped_column(Integer, default=3)
    initial_authority_level: Mapped[str] = mapped_column(String(30), default="LOCAL_BODY")
    escalation_level_1: Mapped[str] = mapped_column(String(30), default="BLOCK_LEVEL")
    escalation_level_2: Mapped[str] = mapped_column(String(30), default="DISTRICT_LEVEL")
    reminder_before_days: Mapped[int] = mapped_column(Integer, default=1)
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class WorkingCalendarEntry(Base, UUIDPrimaryKeyMixin):
    """Holiday calendar used by the working-day deadline calculator so
    deadlines don't naively add 72 hours across weekends/holidays."""

    __tablename__ = "working_calendar"

    entry_date: Mapped[datetime.date] = mapped_column(Date, unique=True, nullable=False)
    is_holiday: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str] = mapped_column(String(255), default="")
