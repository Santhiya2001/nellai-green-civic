import datetime
import uuid

from geoalchemy2 import Geometry
from sqlalchemy import ARRAY, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class VolunteerProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "volunteer_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    interests: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    preferred_activities: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    availability: Mapped[str] = mapped_column(String(255), default="")


class VolunteerEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "volunteer_events"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    activity_type: Mapped[str] = mapped_column(String(40), nullable=False)  # tree_planting/drain_cleaning/lake_restoration/waste_cleanup/awareness/biodiversity_survey/other
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    address_text: Mapped[str] = mapped_column(String(500), default="")
    start_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    organizer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="SCHEDULED")  # SCHEDULED/CANCELLED/COMPLETED

    registrations: Mapped[list["VolunteerEventRegistration"]] = relationship(back_populates="event", lazy="selectin")


class VolunteerEventRegistration(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "volunteer_event_registrations"

    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("volunteer_events.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="REGISTERED")  # REGISTERED/ATTENDED/CANCELLED
    registered_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    event: Mapped["VolunteerEvent"] = relationship(back_populates="registrations")
