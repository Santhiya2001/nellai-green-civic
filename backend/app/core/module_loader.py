"""
Module discovery and loading.

This is what makes the architecture "modular": every subdirectory under
MODULES_ROOT that contains a valid module.json is a self-contained feature
module. The core never imports a module by name — it discovers modules at
runtime, so `modules/flood-monitoring/` can be dropped in without touching
this file or any other core file.

Expected module layout:

    modules/<module_id>/
        module.json          -- manifest (see docs/module-development.md)
        backend/
            __init__.py
            models.py         -- optional: SQLAlchemy models on the shared Base
            router.py         -- optional: FastAPI APIRouter named `router`
        frontend/             -- optional React components consumed by web/
        database/             -- optional raw SQL seed/reference data
        tests/
        README.md
"""
from __future__ import annotations

import importlib.util
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger("module_loader")

MODULES_ROOT = Path(os.environ.get("MODULES_ROOT", Path(__file__).resolve().parents[2] / "modules"))


@dataclass
class ModuleManifest:
    module_id: str
    name: str
    version: str
    description: str
    api_version: str
    author: str
    permissions: list
    dependencies: list
    path: Path
    raw: dict


def discover_modules() -> list[ModuleManifest]:
    manifests: list[ModuleManifest] = []
    if not MODULES_ROOT.exists():
        logger.warning("Modules root %s does not exist; running with core only.", MODULES_ROOT)
        return manifests

    for entry in sorted(MODULES_ROOT.iterdir()):
        manifest_path = entry / "module.json"
        if not entry.is_dir() or not manifest_path.exists():
            continue
        try:
            raw = json.loads(manifest_path.read_text())
            manifests.append(
                ModuleManifest(
                    module_id=raw["id"],
                    name=raw.get("name", raw["id"]),
                    version=raw.get("version", "0.0.0"),
                    description=raw.get("description", ""),
                    api_version=raw.get("api_version", "v1"),
                    author=raw.get("author", "Community"),
                    permissions=raw.get("permissions", []),
                    dependencies=raw.get("dependencies", []),
                    path=entry,
                    raw=raw,
                )
            )
        except (json.JSONDecodeError, KeyError) as exc:
            logger.error("Skipping invalid module manifest at %s: %s", manifest_path, exc)
    return manifests


def _import_module_file(module_id: str, file_path: Path, submodule_name: str):
    if not file_path.exists():
        return None
    qualified_name = f"nellai_modules.{module_id}.{submodule_name}"
    if qualified_name in sys.modules:
        return sys.modules[qualified_name]
    spec = importlib.util.spec_from_file_location(qualified_name, file_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[qualified_name] = module
    spec.loader.exec_module(module)
    return module


def import_all_module_models() -> None:
    """Import every module's backend/models.py so its tables join the shared
    Base.metadata before Alembic/init_db runs."""
    for manifest in discover_modules():
        models_path = manifest.path / "backend" / "models.py"
        try:
            _import_module_file(manifest.module_id, models_path, "models")
        except Exception:
            logger.exception("Failed to import models for module '%s'", manifest.module_id)


def load_module_routers(app) -> list[ModuleManifest]:
    """Import every module's backend/router.py and mount its APIRouter under
    /api/v1/modules/<module_id>. Returns the manifests that were mounted."""
    from app.core.config import settings

    mounted: list[ModuleManifest] = []
    for manifest in discover_modules():
        router_path = manifest.path / "backend" / "router.py"
        try:
            mod = _import_module_file(manifest.module_id, router_path, "router")
            router = getattr(mod, "router", None) if mod else None
            if router is not None:
                app.include_router(
                    router,
                    prefix=f"{settings.API_V1_PREFIX}/modules/{manifest.module_id}",
                    tags=[manifest.name],
                )
                logger.info("Mounted module '%s' v%s", manifest.module_id, manifest.version)
            mounted.append(manifest)
        except Exception:
            logger.exception("Failed to load router for module '%s'", manifest.module_id)
    return mounted


def get_manifest(module_id: str) -> Optional[ModuleManifest]:
    for m in discover_modules():
        if m.module_id == module_id:
            return m
    return None
