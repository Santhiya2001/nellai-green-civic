from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ModuleRegistryEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Mirrors the module.json of every module found under /modules at
    startup. Lets the admin UI list/enable/disable modules without reading
    the filesystem directly."""

    __tablename__ = "modules_registry"

    module_id: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column(String(500), default="")
    api_version: Mapped[str] = mapped_column(String(10), default="v1")
    author: Mapped[str] = mapped_column(String(150), default="Community")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    manifest: Mapped[dict] = mapped_column(JSONB, default=dict)
