from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_roles
from app.core.module_loader import discover_modules
from app.db.session import get_db
from app.models.module_registry import ModuleRegistryEntry

router = APIRouter(prefix="/modules", tags=["Module Registry"])


@router.get("")
async def list_modules(db: AsyncSession = Depends(get_db)):
    """Lists modules discovered on disk, cross-referenced with their enabled
    state stored in the DB registry (seeded by scripts/sync_module_registry.py)."""
    manifests = discover_modules()
    registry_rows = {r.module_id: r for r in (await db.execute(select(ModuleRegistryEntry))).scalars().all()}

    response = []
    for m in manifests:
        registry_entry = registry_rows.get(m.module_id)
        response.append(
            {
                "id": m.module_id,
                "name": m.name,
                "version": m.version,
                "description": m.description,
                "api_version": m.api_version,
                "author": m.author,
                "enabled": registry_entry.enabled if registry_entry else True,
            }
        )
    return response


@router.post("/{module_id}/enable", dependencies=[Depends(require_roles("SUPER_ADMIN"))])
async def enable_module(module_id: str, db: AsyncSession = Depends(get_db)):
    entry = (await db.execute(select(ModuleRegistryEntry).where(ModuleRegistryEntry.module_id == module_id))).scalar_one_or_none()
    if entry:
        entry.enabled = True
        await db.commit()
    return {"module_id": module_id, "enabled": True}


@router.post("/{module_id}/disable", dependencies=[Depends(require_roles("SUPER_ADMIN"))])
async def disable_module(module_id: str, db: AsyncSession = Depends(get_db)):
    entry = (await db.execute(select(ModuleRegistryEntry).where(ModuleRegistryEntry.module_id == module_id))).scalar_one_or_none()
    if entry:
        entry.enabled = False
        await db.commit()
    return {"module_id": module_id, "enabled": False}
