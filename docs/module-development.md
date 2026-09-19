# Writing a Module

This walks through adding a new module -- e.g. a community-contributed
**flood-monitoring** module -- without changing any core file.

## 1. Layout

```
modules/flood-monitoring/
  module.json
  README.md
  backend/
    __init__.py
    models.py      # optional
    router.py      # optional
  frontend/         # optional React components for web/
  database/         # optional raw SQL seed/reference data
  tests/
```

Only `module.json` is required. A module with no `backend/models.py` or
`backend/router.py` still works -- it can register categories onto the core
complaint engine and rely entirely on the existing `/api/v1/complaints`
endpoints (this is exactly what the `civic`, `drainage` and `waste` modules
do).

## 2. `module.json`

```json
{
  "id": "flood-monitoring",
  "name": "Flood Monitoring",
  "version": "1.0.0",
  "description": "Real-time flood risk zones and citizen flood reports.",
  "api_version": "v1",
  "author": "Your Name or Org",
  "permissions": [],
  "dependencies": [],
  "categories": ["FLASH_FLOOD_RISK"],
  "backend_entry": "backend/router.py"
}
```

- `id` must be unique and match the folder name.
- `categories` are complaint category codes this module owns; the seed
  script (`backend/app/db/seed.py`) registers them into
  `complaint_categories` on next `python -m app.db.seed` run (add a
  human-readable name/severity/icon to `CATEGORY_METADATA` in that file, or
  it falls back to a title-cased default).
- `backend_entry` is informational for now (module_loader always looks for
  `backend/router.py`); keep it accurate for documentation/tooling.

## 3. (Optional) `backend/models.py`

If your module needs its own tables, define SQLAlchemy models against the
**shared** `Base` so Alembic manages them alongside core tables:

```python
import uuid
from geoalchemy2 import Geometry
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class FloodRiskZone(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "flood_risk_zones"
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    geom = mapped_column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=False)
```

After adding models, generate and apply a migration:

```bash
docker compose run --rm backend alembic revision --autogenerate -m "add flood-monitoring tables"
docker compose run --rm backend alembic upgrade head
```

Check the generated migration file before applying it -- autogenerate is a
starting point, not a guarantee (see the note about `spatial_ref_sys` in
`alembic/env.py` for a real example of a false positive to watch for).

## 4. (Optional) `backend/router.py`

```python
import importlib
from fastapi import APIRouter, Depends
from app.core.deps import get_current_user, require_roles
from app.db.session import get_db

_models = importlib.import_module("nellai_modules.flood-monitoring.models")
# note: module ids with hyphens need bracket access, e.g.
# import sys; _models = sys.modules["nellai_modules.flood_monitoring.models"]
# (prefer underscore-only module ids to avoid this)

router = APIRouter()

@router.get("/risk-zones")
async def list_risk_zones(db = Depends(get_db)):
    ...
```

`module_loader.py` mounts this router under
`/api/v1/modules/flood-monitoring/...` automatically -- every route you
define here is relative to that prefix. Reuse `app.core.deps`,
`app.services.gis`, `app.services.storage`, etc. exactly like core code does;
see any of the existing modules (`modules/water/backend/router.py` is a good
template) for the pattern used to import your own `models.py` by its
synthetic module name.

**Module id naming**: stick to lowercase letters, digits and underscores
(no hyphens) so the synthetic `nellai_modules.<id>.*` import path stays a
valid Python identifier.

## 5. (Optional) `frontend/`

Drop React components here; a citizen/admin page in `web/src/pages/` can
import them, or your module can ship a fully standalone page. There is no
enforced contract yet beyond "valid React talking to the module's own API
prefix" -- keep it that way unless you're proposing a change to this doc.

## 6. Tests

Add `modules/<id>/tests/` with pytest tests that hit your module's router
the same way `backend/tests/` does for core endpoints.

## 7. Submit

Open a PR against this repository. CI (`.github/workflows/ci.yml`) runs
lint, backend tests, and validates every `module.json` against the schema
described above. See [contributing.md](../CONTRIBUTING.md).
