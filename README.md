# Nellai Green & Civic

An open-source, modular civic and environmental management platform for
Tirunelveli (Nellai), Tamil Nadu — built so it can grow into a reusable
framework for other districts and cities.

Citizens report civic and environmental issues (drainage, waste, water
pollution, fallen trees, disasters, crop damage, wildlife sightings...);
authorities track, resolve and get automatically escalated when they miss
a deadline; volunteers organize plantation drives, cleanups and surveys;
everyone sees it on a shared GIS map.

## Why it's built this way

The core platform (auth, RBAC, a generic complaint/workflow engine, GIS,
escalation, notifications) never needs to change when a new feature area is
added. Every domain feature — civic issues, drainage, waste, water bodies,
afforestation, volunteering, agriculture, biodiversity, disaster response —
is an independent **module** under `/modules`, discovered automatically at
backend startup. See [docs/architecture.md](docs/architecture.md).

```
CORE PLATFORM
  |
  +---- civic          +---- afforestation   +---- agriculture
  +---- drainage        +---- volunteer       +---- biodiversity
  +---- waste            +---- water            +---- disaster
```

## Quick start

```bash
git clone <this-repo>
cd nellai-green-civic
cp .env.example .env
sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$(openssl rand -hex 32)/" .env
./scripts/download_ai_models.sh   # optional but recommended, see docs/installation.md
docker compose up -d --build
```

- Web app: http://localhost:5173
- API docs: http://localhost:8000/api/v1/docs
- Login as `admin@nellaigreencivic.org` / `ChangeMe123!` (change immediately)

Full setup, troubleshooting, and first-run GIS configuration:
[docs/installation.md](docs/installation.md).

## Testing the project

**Automated tests:**

```bash
# Backend (auth, complaint creation, GIS authority assignment, escalation deadlines)
docker compose run --rm -e AI_SERVICE_ENABLED=false -e TESTING=true backend pytest -v

# Every module.json manifest validates against the required schema
python3 scripts/validate_modules.py

# Mobile app: static analysis + widget test
cd mobile && flutter pub get && flutter analyze && flutter test

# Web app: TypeScript compiles clean
cd web && npm install && npx tsc -b
```

**Manual end-to-end walkthrough** (once `docker compose up -d --build` is running):

1. Open http://localhost:5173, log in as `admin@nellaigreencivic.org` /
   `ChangeMe123!`.
2. Go to **Authorities** → create a boundary (any polygon over your test
   area), an authority scoped to it, and a responsibility-map rule mapping
   a category (e.g. `DRAIN_BLOCKAGE`) to that authority.
3. Log out, register a new citizen account.
4. Go to **Report Issue** → pick that category, allow location access,
   submit. You should immediately see `status: ASSIGNED`, a
   `deadline_at` a few working days out, and (if the AI service finished
   loading its model — first request after a fresh start takes ~20s) an
   `ai_category_code` suggestion.
5. Log back in as admin/an authority account → the complaint appears
   under **Complaints** / **Assigned Complaints**, movable through
   Acknowledged → In Progress → Resolved.
6. Back as the citizen, confirm or reject the resolution from **My
   Complaints**.
7. Check **GIS Map** to see it plotted, and **Admin → Dashboard** for the
   analytics it feeds.

Or drive the same flow directly against the API docs at
http://localhost:8000/api/v1/docs (Swagger UI — every endpoint is there
with a "Try it out" button).

## Presentation

A ready-to-present slide deck for demos is at
[`presentation/Nellai_Green_Civic.pptx`](presentation/Nellai_Green_Civic.pptx)
— architecture, workflow, GIS assignment, escalation engine, AI
classification, all 9 modules, and verified test results. Fill in the
presenter name/guide/department placeholders on the title slide before use.

## What's in the repo

| Path | What |
|---|---|
| `backend/` | FastAPI + SQLAlchemy + Alembic + PostGIS. The core platform and generic complaint engine. |
| `ai/` | Standalone AI classification microservice (sentence-embedding zero-shot text classification + pretrained image signal). |
| `modules/` | Nine feature modules — civic, drainage, waste, water, afforestation, volunteer, agriculture, biodiversity, disaster. |
| `web/` | React + TypeScript web app (citizen, admin, authority views). |
| `mobile/` | Flutter mobile app (citizen-focused). |
| `database/` | PostGIS extension bootstrap SQL. |
| `docs/` | Architecture, API, database, module-development, deployment, security docs. |
| `scripts/` | Setup/ops scripts (AI model prefetch, escalation sweep). |
| `.github/workflows/` | CI: lint, tests, module manifest validation. |

## Tech stack

Backend: Python 3.11, FastAPI, SQLAlchemy 2 (async), Alembic, PostgreSQL 15 +
PostGIS. AI: sentence-transformers, torchvision (CPU inference). Web: React
18, TypeScript, Vite, Leaflet, Recharts. Mobile: Flutter/Dart. Everything
runs via Docker Compose for local dev; see
[docs/deployment.md](docs/deployment.md) for production, which has no
single-cloud-provider dependency.

## Contributing

Adding your own module — e.g. flood monitoring, a school environmental
program, a temple water-tank tracker — doesn't require touching the core.
See [docs/module-development.md](docs/module-development.md), then
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache License 2.0 — see [LICENSE](LICENSE).

## Security & Privacy

See [SECURITY.md](SECURITY.md) / [docs/security.md](docs/security.md) for
the security model, and [docs/privacy-policy.md](docs/privacy-policy.md)
for the data handling policy (citizen photos, GPS and account data).
