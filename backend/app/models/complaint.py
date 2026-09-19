import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ComplaintStatus, Severity


class ComplaintCategory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Generic category catalog shared by every reporting module (civic,
    drainage, waste, water, disaster, ...). A module registers its categories
    here at install time instead of the core hard-coding them."""

    __tablename__ = "complaint_categories"

    code: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)  # e.g. DRAIN_BLOCKAGE
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    module_id: Mapped[str] = mapped_column(String(60), nullable=False)  # e.g. "drainage"
    description: Mapped[str] = mapped_column(Text, default="")
    default_severity: Mapped[str] = mapped_column(String(20), default=Severity.MEDIUM.value)
    icon: Mapped[str] = mapped_column(String(60), default="alert-circle")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Complaint(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "complaints"

    complaint_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("complaint_categories.id"), nullable=False)
    final_category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("complaint_categories.id"), nullable=True
    )

    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    location = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    address_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    boundary_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("administrative_boundaries.id"), nullable=True
    )

    severity: Mapped[str] = mapped_column(String(20), default=Severity.MEDIUM.value)

    ai_category_code: Mapped[str | None] = mapped_column(String(60), nullable=True)
    ai_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_severity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ai_raw_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    status: Mapped[str] = mapped_column(String(20), default=ComplaintStatus.REPORTED.value, index=True)
    assigned_authority_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("authorities.id"), nullable=True
    )

    deadline_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=True)
    escalation_level: Mapped[int] = mapped_column(Integer, default=0)
    last_escalated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=True)

    duplicate_of_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=True)
    possible_duplicate_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # extra_data lets a module attach category-specific fields (e.g. water body id,
    # crop name) without altering the shared complaints table.
    extra_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)

    category: Mapped["ComplaintCategory"] = relationship(foreign_keys=[category_id], lazy="selectin")
    status_history: Mapped[list["ComplaintStatusHistory"]] = relationship(
        back_populates="complaint", order_by="ComplaintStatusHistory.created_at", lazy="selectin"
    )
    resolution: Mapped["ResolutionEvidence"] = relationship(back_populates="complaint", uselist=False, lazy="selectin")


class ComplaintStatusHistory(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "complaint_status_history"

    complaint_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    to_status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default="now()")

    complaint: Mapped["Complaint"] = relationship(back_populates="status_history")


class ResolutionEvidence(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "resolution_evidence"

    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("complaints.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    resolved_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    resolved_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default="now()")

    citizen_verified: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    citizen_verified_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=True)
    citizen_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    complaint: Mapped["Complaint"] = relationship(back_populates="resolution")
