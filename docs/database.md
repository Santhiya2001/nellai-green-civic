# Database Schema

PostgreSQL 15 + PostGIS 3.4. Managed entirely through SQLAlchemy models +
Alembic migrations (`backend/alembic/`) -- there is no hand-maintained SQL
schema file to keep in sync. Every geometry column is `SRID 4326` (WGS84).

## Core tables (`backend/app/models/`)

| Table | Purpose |
|---|---|
| `roles`, `users`, `user_roles`, `refresh_tokens` | Auth & RBAC |
| `administrative_boundaries` | GIS polygons for village/town/ward/district, self-referencing `parent_id` for the hierarchy |
| `authorities` | Responsible offices, scoped to a boundary + level |
| `authority_responsibility_map` | Configurable `category_code (+ boundary_level) -> authority_id`, the thing that replaces hard-coded "send it to the Collector" logic |
| `complaint_categories` | Every category any module has registered (`code`, `module_id`, `default_severity`) |
| `complaints` | The generic complaint/issue record -- category, location, AI + human classification, status, assignment, deadline, escalation level, duplicate link, `extra_data` JSONB for module-specific fields |
| `complaint_status_history` | Append-only audit trail of every status transition |
| `resolution_evidence` | Authority's resolution description/photo + citizen verification outcome |
| `escalation_rules` | Per-category (or default, `category_code IS NULL`) deadline + escalation levels |
| `working_calendar` | Admin-configurable holiday list used by the working-day deadline calculator |
| `notifications` | In-app notifications (email/push are pluggable fan-outs from the same call site) |
| `audit_logs` | Generic audit trail for sensitive actions |
| `modules_registry` | Mirrors every discovered `module.json`, plus an `enabled` flag |

## Module tables

| Module | Tables |
|---|---|
| water | `water_bodies`, `water_observations` |
| afforestation | `plantation_sites`, `trees`, `tree_maintenance_logs` |
| volunteer | `volunteer_profiles`, `volunteer_events`, `volunteer_event_registrations` |
| agriculture | `farm_advisories`, `crop_reports` |
| biodiversity | `species`, `biodiversity_observations` |
| disaster | `disaster_alerts`, `disaster_reports` |
| civic / drainage / waste | none -- use `complaints` + `complaint_categories` only |

## Migrations

```bash
# After changing/adding SQLAlchemy models (core or module):
docker compose run --rm backend alembic revision --autogenerate -m "describe the change"
# Review the generated file under backend/alembic/versions/ -- autogenerate
# is a draft, not ground truth (see the spatial_ref_sys caveat below).
docker compose run --rm backend alembic upgrade head
```

**Known autogenerate quirks, already handled but worth knowing:**

- `spatial_ref_sys` is a PostGIS system table. `alembic/env.py` registers an
  `include_object` filter so autogenerate never proposes dropping it. If you
  see it in a diff, something reintroduced the omission -- don't apply it.
- GeoAlchemy2 automatically creates the `GIST` spatial index on a `Geometry`
  column as a DDL event on `CREATE TABLE`. Autogenerate doesn't know this and
  will propose a duplicate `CREATE INDEX ... USING gist`, which fails with
  "already exists" on `upgrade`. Delete those specific `op.create_index(...,
  postgresql_using='gist')` / matching `op.drop_index` lines from a freshly
  generated migration for any *new* geometry column before applying it.

## Seed data

`backend/app/db/seed.py` (idempotent, safe to re-run) creates: all roles,
every category declared by every module's `module.json`, a default
escalation rule (+ a tighter one for `FLOOD_REPORT`), the module registry
rows, and a `SUPER_ADMIN` bootstrap account.
