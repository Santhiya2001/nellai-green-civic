"""
Import every core model AND every installed module's models here so that
Base.metadata is fully populated before Alembic autogenerate/upgrade runs.

Module models are discovered dynamically by app.core.module_loader at import
time of this package, so a new module under /modules/<id>/backend/models.py
is picked up automatically without editing this file.
"""

from app.models.user import User, Role, UserRole, RefreshToken  # noqa: F401
from app.models.boundary import AdministrativeBoundary  # noqa: F401
from app.models.authority import Authority, AuthorityResponsibilityMap  # noqa: F401
from app.models.complaint import (  # noqa: F401
    ComplaintCategory,
    Complaint,
    ComplaintStatusHistory,
    ResolutionEvidence,
)
from app.models.escalation import EscalationRule, WorkingCalendarEntry  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401
from app.models.module_registry import ModuleRegistryEntry  # noqa: F401

from app.core.module_loader import import_all_module_models  # noqa: E402

import_all_module_models()
