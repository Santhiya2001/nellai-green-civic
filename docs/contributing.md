# Contributing

See also the root [CONTRIBUTING.md](../CONTRIBUTING.md) for the PR process
and [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md).

## Ways to contribute

- **New module** -- see [module-development.md](module-development.md).
  This is the easiest way to add a whole feature area without touching core.
- **Core platform improvement** -- auth, GIS, escalation engine, notification
  fan-out, etc. Anything under `backend/app/core/` or `backend/app/services/`.
  These changes affect every module, so they need a clear "why" and tests.
- **Frontend** -- `web/` (React) or `mobile/` (Flutter). A module can ship
  its own components under `modules/<id>/frontend/`.
- **AI model** -- `ai/` is intentionally decoupled from the backend behind
  one HTTP contract (`POST /classify`). Swap the model, add a new signal,
  or improve severity heuristics without needing backend changes, as long
  as the response shape in `docs/api.md` still holds.
- **Documentation** -- this `docs/` folder, or module `README.md` files.

## Local dev loop

```bash
docker compose up -d --build
# backend auto-reloads on file change (uvicorn --reload)
# web auto-reloads via Vite HMR
```

Run backend tests:

```bash
docker compose run --rm backend pytest
```

## Before opening a PR

- New backend code: add or update tests under `backend/tests/` (core) or
  `modules/<id>/tests/` (module-specific).
- New/changed models: include the Alembic migration, and check it by eye
  (see the autogenerate caveats in `docs/database.md`).
- New API endpoints: they should show up correctly in
  `http://localhost:8000/api/v1/docs` -- if a field is unclear from the
  OpenAPI schema alone, add a docstring.
- Run `docker compose run --rm backend pytest` and, for web changes,
  `docker compose run --rm web npm run lint`.

## Commit / PR conventions

- Keep PRs scoped to one module or one concern -- a new module + an
  unrelated core refactor in the same PR is hard to review.
- Describe *why*, not just *what*, in the PR description -- the diff already
  shows what changed.

## Versioning

The project follows semantic versioning per module (`module.json.version`)
and per API (`/api/v1`, `/api/v2` when a breaking change is needed). A
module bump from `1.0.0` to `1.1.0` should never break another module's
integration with it; a `2.0.0` bump means it might, and should say so in its
`README.md`.
