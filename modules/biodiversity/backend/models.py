import datetime
import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Species(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "species"

    common_name: Mapped[str] = mapped_column(String(150), nullable=False)
    scientific_name: Mapped[str] = mapped_column(String(150), default="")
    category: Mapped[str] = mapped_column(String(20), nullable=False)  # FLORA/FAUNA/BIRD/INSECT/AQUATIC
    conservation_status: Mapped[str] = mapped_column(String(50), default="NOT_EVALUATED")
    description: Mapped[str] = mapped_column(Text, default="")


class BiodiversityObservation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "biodiversity_observations"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    species_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("species.id"), nullable=True)
    custom_species_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    observed_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default="now()")
    notes: Mapped[str] = mapped_column(Text, default="")
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
