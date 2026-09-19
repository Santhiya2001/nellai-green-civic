import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Authority(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "authorities"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    department: Mapped[str] = mapped_column(String(150), nullable=False)
    level: Mapped[str] = mapped_column(String(30), nullable=False)  # AuthorityLevel
    boundary_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("administrative_boundaries.id"), nullable=True
    )
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    boundary: Mapped["AdministrativeBoundary"] = relationship(lazy="selectin")


class AuthorityResponsibilityMap(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Configurable mapping: complaint category (+ optional boundary level) ->
    responsible authority. Admins edit this via API instead of it being
    hard-coded, per the project's 'no hard-coded Collector' requirement."""

    __tablename__ = "authority_responsibility_map"

    category_code: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    boundary_level: Mapped[str | None] = mapped_column(String(30), nullable=True)  # None = applies to all levels
    authority_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("authorities.id"), nullable=False)
    priority: Mapped[int] = mapped_column(default=0)  # higher priority wins when multiple rules match

    authority: Mapped["Authority"] = relationship(lazy="selectin")
