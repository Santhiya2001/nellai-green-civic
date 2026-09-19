# Security

This document describes the current implementation, not aspirational
policy -- if something below stops being true, fix the code or fix this
file, not just one of them.

## Authentication & authorization

- Passwords hashed with bcrypt (`passlib`), never stored or logged in plain text.
- JWT access tokens (short-lived, default 30 min) + refresh tokens (default
  14 days), signed with `JWT_SECRET_KEY` (`HS256`). **Generate a real secret**
  for any non-local deployment: `openssl rand -hex 32`.
- Refresh tokens are hashed with SHA-256 before storage (not bcrypt --
  bcrypt silently truncates input over 72 bytes, which a JWT-length token
  exceeds; SHA-256 is correct for an opaque-token lookup hash).
- Role-based access control via `app/core/deps.py:require_roles(...)`.
  `SUPER_ADMIN` bypasses role checks; every other role is checked explicitly
  per-endpoint, never inferred.

## Input validation

- Every request body is a Pydantic model (`app/schemas/`) -- FastAPI rejects
  malformed input before it reaches business logic.
- File uploads (`app/services/storage.py`) validate MIME type against an
  allowlist (`ALLOWED_IMAGE_MIME_TYPES`) and enforce `MAX_UPLOAD_SIZE_MB`
  before writing to disk.
- GeoJSON geometry input is parsed with `shapely` inside a `try/except`,
  never passed to the database unvalidated.

## Injection / XSS

- All database access goes through SQLAlchemy's parameterized query builder
  -- no raw string-interpolated SQL anywhere in the codebase.
- The web app is React (auto-escapes rendered content) and does not use
  `dangerouslySetInnerHTML`.

## Rate limiting

- `slowapi` enforces `RATE_LIMIT_PER_MINUTE` (default 60/min) per client IP
  on every endpoint via `app.state.limiter`.

## CORS

- `BACKEND_CORS_ORIGINS` in `.env` is an explicit allowlist (JSON array),
  not a wildcard. Add your production web app's origin before deploying.

## Secrets

- Nothing sensitive is committed: `.env` is gitignored, `.env.example` ships
  placeholders only. `docker-compose.yml` reads all secrets from `.env`.
- The seed script's bootstrap `SUPER_ADMIN` password (`ChangeMe123!`) is
  intentionally obvious and must be rotated immediately in any shared
  environment -- it exists only so a fresh install has *a* way in.

## Audit trail

- `complaint_status_history` records every workflow transition with actor,
  timestamp and note.
- `audit_logs` is available for broader sensitive-action logging as the
  platform grows (not yet wired into every mutation -- see
  `docs/contributing.md` if you want to help close that gap).

## Reporting a vulnerability

See [SECURITY.md](../SECURITY.md) at the repo root.

## Known gaps (tracked, not hidden)

- CSRF protection is not yet implemented; the API is token-bearer-auth only
  (no cookies), which sidesteps classic CSRF, but this should be revisited
  if cookie-based sessions are ever added.
- The AI service has no auth of its own (it trusts the backend network); it
  should not be exposed directly to the public internet in production --
  put it behind the same network boundary as the backend, not in front of it.
- File storage's local backend (`STORAGE_BACKEND=local`) is fine for a
  single-host demo; production deployments should use the S3-compatible
  backend so uploads survive container recreation and scale horizontally.
