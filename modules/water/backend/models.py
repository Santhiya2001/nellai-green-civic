"""Neervalam (water resources) module models -- bind to the core shared
Base so Alembic manages them alongside core tables."""
import uuid

from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class WaterBody(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "water_bodies"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # RIVER/LAKE/POND/CANAL/WELL/TANK/WETLAND
    geom = mapped_column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=False)  # Point or Polygon
    boundary_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("administrative_boundaries.id"), nullable=True)
    capacity_liters: Mapped[float | None] = mapped_column(nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    observations: Mapped[list["WaterObservation"]] = relationship(back_populates="water_body", lazy="selectin")


class WaterObservation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "water_observations"

    water_body_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("water_bodies.id", ondelete="CASCADE"), nullable=False)
    observed_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    observation_type: Mapped[str] = mapped_column(String(30), nullable=False)  # POLLUTION/GARBAGE/ENCROACHMENT/BLOCKAGE/ILLEGAL_DUMPING/WATER_LEVEL_LOW/DAMAGE/NORMAL
    description: Mapped[str] = mapped_column(Text, default="")
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    water_level_meters: Mapped[float | None] = mapped_column(nullable=True)
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    complaint_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=True)

    water_body: Mapped["WaterBody"] = relationship(back_populates="observations")
