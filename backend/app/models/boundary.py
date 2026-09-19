import uuid

from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import BoundaryLevel


class AdministrativeBoundary(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Configurable admin hierarchy: Village -> Panchayat, Town -> Municipality,
    Urban area -> Corporation, etc. Stored as GIS polygons so complaints can be
    matched to a boundary by point-in-polygon lookup (see gis service)."""

    __tablename__ = "administrative_boundaries"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    level: Mapped[str] = mapped_column(String(30), nullable=False)  # BoundaryLevel
    district: Mapped[str] = mapped_column(String(100), nullable=False, default="Tirunelveli")
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("administrative_boundaries.id"), nullable=True
    )
    geom = mapped_column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True)

    parent: Mapped["AdministrativeBoundary"] = relationship(remote_side="AdministrativeBoundary.id")
