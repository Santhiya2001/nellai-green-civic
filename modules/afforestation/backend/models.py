"""Green Nellai (afforestation) module models.

Ownership note (spec section 17): PlantationSite.ownership_status defaults to
UNVERIFIED. The system must never claim land is government-owned from
satellite imagery alone -- verified_by/verification_document_url exist
precisely so that only an explicit authority confirmation can move a site to
GOVERNMENT_VERIFIED.
"""
import datetime
import uuid

from geoalchemy2 import Geometry
from sqlalchemy import ARRAY, Date, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PlantationSite(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "plantation_sites"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    geom = mapped_column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=False)
    land_type: Mapped[str] = mapped_column(String(50), default="UNKNOWN")
    ownership_status: Mapped[str] = mapped_column(String(30), default="UNVERIFIED")  # UNVERIFIED/GOVERNMENT_VERIFIED/PRIVATE/COMMUNITY
    verified_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    verification_document_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    estimated_capacity: Mapped[int | None] = mapped_column(nullable=True)
    recommended_species: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    trees: Mapped[list["Tree"]] = relationship(back_populates="plantation_site", lazy="selectin")


class Tree(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "trees"

    tree_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    species: Mapped[str] = mapped_column(String(150), nullable=False)
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    planting_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    organization: Mapped[str] = mapped_column(String(150), default="")
    volunteer_group: Mapped[str] = mapped_column(String(150), default="")
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="PLANTED")  # PLANTED/HEALTHY/NEEDS_MAINTENANCE/DAMAGED/DEAD/REPLACED
    plantation_site_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("plantation_sites.id"), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    plantation_site: Mapped["PlantationSite"] = relationship(back_populates="trees")
    maintenance_logs: Mapped[list["TreeMaintenanceLog"]] = relationship(back_populates="tree", lazy="selectin")


class TreeMaintenanceLog(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "tree_maintenance_logs"

    tree_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trees.id", ondelete="CASCADE"), nullable=False)
    log_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    note: Mapped[str] = mapped_column(Text, default="")
    logged_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    tree: Mapped["Tree"] = relationship(back_populates="maintenance_logs")
