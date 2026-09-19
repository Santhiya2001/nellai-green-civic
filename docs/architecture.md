# Architecture

Nellai Green & Civic is a modular monorepo. The core platform provides
generic services (auth, RBAC, the complaint/workflow engine, GIS, escalation,
notifications, the module loader); everything domain-specific is a module.

```
CORE PLATFORM (backend/)
  |
  +-- Auth & RBAC
  +-- Generic Complaint Engine (categories, workflow, status history)
  +-- Escalation Engine (working-day deadlines, configurable rules)
  +-- Authority Assignment (GIS boundary + responsibility map, no hard-coding)
  +-- GIS services (PostGIS point-in-polygon, nearby search)
  +-- Notification service
  +-- Module Loader (discovers /modules/*/module.json at startup)
  |
  +---- modules/civic         (categories only, uses the core engine directly)
  +---- modules/drainage      (categories only)
  +---- modules/waste         (categories only)
  +---- modules/water         (categories + WaterBody/WaterObservation entities)
  +---- modules/afforestation (categories + PlantationSite/Tree entities)
  +---- modules/volunteer     (VolunteerProfile/Event/Registration entities)
  +---- modules/agriculture   (categories + FarmAdvisory/CropReport entities)
  +---- modules/biodiversity  (categories + Species/Observation entities)
  +---- modules/disaster      (categories + DisasterAlert/Report entities)
```

## Why a generic complaint engine

Most "modules" in the spec (civic, drainage, waste, most of water, most of
disaster) are really just **categories of the same underlying workflow**:
citizen reports GPS + photo + description -> AI-assisted classification ->
authority assignment -> deadline -> escalation -> resolution -> citizen
verification. Building this once in `backend/app/api/v1/complaints.py` and
`backend/app/services/` means:

- A new "flood monitoring" category is a `module.json` + a few rows in
  `complaint_categories` -- no new backend code required.
- A module that needs its own domain entities (trees, water bodies,
  volunteer events) adds `backend/models.py` + `backend/router.py`, which
  bind to the *same* shared SQLAlchemy `Base` and get mounted under
  `/api/v1/modules/<module_id>/...` automatically.

## Module loading mechanism

`backend/app/core/module_loader.py`:

1. `discover_modules()` scans `MODULES_ROOT` (defaults to `../modules`,
   `/app/modules` in Docker) for any folder with a `module.json`.
2. `import_all_module_models()` is called once, from `app/models/__init__.py`,
   before Alembic or the app starts -- it imports every module's
   `backend/models.py` so their tables join `Base.metadata`.
3. `load_module_routers(app)` is called once from `app/main.py` -- it imports
   every module's `backend/router.py` and mounts its `router` under
   `/api/v1/modules/<module_id>`.

No core file lists module names. Dropping a new folder under `/modules` with
a valid `module.json` is enough for the backend to pick it up on next
restart. See [module-development.md](module-development.md) for the full
walkthrough.

## Request flow: filing a complaint

```
Citizen (web/mobile)
   |  POST /api/v1/complaints (category_code, description, lat/lng, image)
   v
FastAPI backend
   |-- save image (services/storage.py)
   |-- call AI service for category/severity suggestion (services/ai_client.py)
   |-- check for likely duplicates (services/duplicate_detection.py)
   |-- find containing administrative boundary (services/gis.py)
   |-- resolve responsible authority (services/authority_assignment.py)
   |-- compute working-day deadline (services/escalation_engine.py)
   |-- create Notification
   v
PostgreSQL + PostGIS
```

A background sweep (`scripts/run_escalation_sweep.py`, or
`POST /api/v1/escalation/sweep`) reminds citizens/authorities before a
deadline and escalates the authority level after it, using the same
category -> boundary -> AuthorityResponsibilityMap resolution as initial
assignment -- so escalation targets are configured data, never a hard-coded
office.

## Why a separate AI microservice

`ai/` is a standalone FastAPI service, not an in-process model. The backend
only depends on its HTTP contract (`POST /classify`), so the model can be
retrained, swapped for a different architecture, or scaled independently
without touching the backend. If the AI service is down or slow, complaint
creation still succeeds -- AI output is advisory, never blocking (see
`app/services/ai_client.py`).

## Data model

See [database.md](database.md) for the full schema. Every geometry column
uses PostGIS `SRID 4326` (WGS84 lat/lng), matching GPS coordinates directly.

## Frontends

- `web/` -- React + TypeScript, three role-based views (citizen, admin,
  authority) behind one login, talking to the same REST API.
- `mobile/` -- Flutter, citizen-focused (report/track complaints, volunteer
  activities), same REST API.

Both are thin clients: all business logic (assignment, escalation, workflow
validity) lives in the backend so a third-party client only has to call the
documented API.
