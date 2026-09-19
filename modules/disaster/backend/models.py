import datetime
import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DisasterAlert(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "disaster_alerts"

    type: Mapped[str] = mapped_column(String(30), nullable=False)  # FLOOD/CYCLONE/HEAVY_RAIN/DROUGHT/OTHER
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    affected_boundary_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("administrative_boundaries.id"), nullable=True)
    geom = mapped_column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    issued_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    issued_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default="now()")
    expires_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class DisasterReport(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "disaster_reports"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    alert_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("disaster_alerts.id"), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    casualties_reported: Mapped[bool] = mapped_column(Boolean, default=False)
    needs_rescue: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="REPORTED")
    complaint_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=True)
