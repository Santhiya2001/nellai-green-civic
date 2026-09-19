# API Reference

Full interactive docs (generated from the FastAPI OpenAPI schema, always
in sync with the code) are at `http://localhost:8000/api/v1/docs` when
running locally. This page is a map of what's where.

Base URL: `/api/v1`. All endpoints below are relative to that prefix.
Authenticated endpoints expect `Authorization: Bearer <access_token>`.

## Auth (`auth.py`)

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/auth/register` | none | Creates a CITIZEN account |
| POST | `/auth/login` | none | Returns access + refresh JWTs |
| POST | `/auth/refresh` | none | Exchanges a refresh token for a new pair |
| GET | `/auth/me` | any | Current user profile + roles |

## Users (`users.py`)

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/users` | ADMIN | List users |
| POST | `/users/{id}/roles/{role_name}` | SUPER_ADMIN | Grant a role |
| POST | `/users/{id}/deactivate` | ADMIN | Deactivate an account |
| DELETE | `/users/me` | any | Self-service account deletion |

## Categories (`categories.py`)

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/categories` | none | Every active category from every module |

## Complaints -- the generic engine (`complaints.py`)

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/complaints` | any | multipart/form-data: category_code, description, latitude, longitude, address_text?, extra_data?, image? |
| GET | `/complaints` | any | `mine`, `status`, `category_code`, `authority_id`, `limit`, `offset` |
| GET | `/complaints/nearby` | any | `latitude`, `longitude`, `radius_meters` |
| GET | `/complaints/{id}` | any | Full detail (citizen can only see their own) |
| POST | `/complaints/{id}/status` | AUTHORITY, ADMIN | `{to_status, note?}`, validated against the workflow graph |
| POST | `/complaints/{id}/resolve` | AUTHORITY, ADMIN | multipart: description, photo?, latitude?, longitude? |
| POST | `/complaints/{id}/verify` | citizen who filed it | `{verified, feedback?}` -- CLOSED or REOPENED |
| POST | `/complaints/{id}/reject` | AUTHORITY, ADMIN | `{reason}` |
| POST | `/complaints/{id}/merge/{duplicate_target_id}` | ADMIN | Confirm a duplicate merge |

Workflow: `REPORTED -> AI_ANALYZED -> ASSIGNED -> ACKNOWLEDGED -> IN_PROGRESS
-> RESOLVED -> VERIFICATION -> CLOSED` (or `REJECTED` at any point before
`CLOSED`; `VERIFICATION` can bounce to `REOPENED -> IN_PROGRESS` if the
citizen rejects the resolution).

## Authorities & boundaries (`authorities.py`)

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST/GET | `/authorities` | ADMIN write, any read | |
| POST/GET | `/authorities/responsibility-map` | ADMIN write, any read | category_code (+ optional boundary_level) -> authority_id |
| DELETE | `/authorities/responsibility-map/{id}` | ADMIN | |
| POST/GET | `/boundaries` | ADMIN write, any read | GeoJSON polygon in, GeoJSON out via `/boundaries/{id}/geojson` |

## Escalation (`escalation.py`)

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST/GET/PUT | `/escalation/rules` | ADMIN write, any read | Per-category (or default) deadline + escalation levels |
| POST | `/escalation/sweep` | ADMIN | Manually trigger reminders/escalations (also runnable via `scripts/run_escalation_sweep.py`) |

## Notifications (`notifications.py`)

| Method | Path | Auth |
|---|---|---|
| GET | `/notifications` | any |
| POST | `/notifications/{id}/read` | any |

## Modules registry (`modules.py`)

| Method | Path | Auth |
|---|---|---|
| GET | `/modules` | any |
| POST | `/modules/{id}/enable` \| `/disable` | SUPER_ADMIN |

## Analytics (`analytics.py`)

| Method | Path | Auth |
|---|---|---|
| GET | `/analytics/dashboard` | ADMIN, AUTHORITY |
| GET | `/analytics/by-category` | ADMIN, AUTHORITY |
| GET | `/analytics/by-status` | ADMIN, AUTHORITY |
| GET | `/analytics/monthly-trend` | ADMIN, AUTHORITY |

## Module APIs

Every module is mounted at `/api/v1/modules/<module_id>/...`:

- **water**: `/water-bodies` (+`/nearby`), `/observations`,
  `/water-bodies/{id}/observations`
- **afforestation**: `/species-recommendations`, `/plantation-sites`
  (+`/{id}/verify-ownership`), `/trees` (+`/nearby`),
  `/trees/{id}/maintenance`, `/stats/survival-rate`
- **volunteer**: `/profile`, `/events` (+`/recommended`, `/nearby`),
  `/events/{id}/register`
- **agriculture**: `/advisories`, `/crop-reports`
- **biodiversity**: `/species`, `/observations` (+`/nearby`),
  `/observations/{id}/verify`
- **disaster**: `/alerts`, `/reports` (+`/nearby`), `/reports/{id}/status`

See each module's `README.md` for full request/response shapes, or the
Swagger UI (every module route is tagged with the module's display name).

## AI service (separate process, `ai/main.py`)

| Method | Path | Notes |
|---|---|---|
| POST | `/classify` | `{description, image_url?}` -> `{category_code, confidence, severity, top_matches, image_labels, image_agreement, model}` |
| GET | `/health` | |

The backend is the only intended caller (`app/services/ai_client.py`), but
the contract is stable and documented so the model can be swapped or called
directly for experimentation.
