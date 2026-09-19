# Disaster Management

Disaster alerts (flood, cyclone, heavy rain, drought) issued by authorities,
and citizen disaster reports with urgent rescue/casualty flags.

Categories: `FLOOD_REPORT`, `DISASTER_DAMAGE` (routed through the core
complaint engine; `FLOOD_REPORT` also has a tighter 1-day default
escalation rule seeded in `backend/app/db/seed.py`).

## Own entities

- `DisasterAlert` -- an authority-issued alert with type, severity, and
  optional expiry
- `DisasterReport` -- a citizen's report, with `needs_rescue` /
  `casualties_reported` flags that trigger an immediate notification to
  every ADMIN/AUTHORITY/SUPER_ADMIN user (see `backend/router.py`)

## API (`/api/v1/modules/disaster/...`)

- `POST/GET /alerts`
- `POST /reports`, `GET /reports/nearby`, `POST /reports/{id}/status`

This module keeps disaster reports as its own record type (rather than
routing urgent reports through the standard complaint workflow) so the
rescue/casualty fields and immediate broadcast notification aren't forced
into the generic engine's shape. A future version could link a
`DisasterReport` to a `Complaint` via `complaint_id` for unified tracking
without changing this module's urgent-path behavior.
