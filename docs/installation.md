# Installation (Local Development)

## Prerequisites

- Docker + Docker Compose (v2 plugin, or the standalone `docker-compose` binary)
- ~4GB free disk for images/models (the AI service pulls a small text model
  and a pretrained image model)
- Git

Flutter is only needed if you plan to run the mobile app; the web app and
backend do not require it.

## 1. Clone and configure

```bash
git clone <your-fork-url> nellai-green-civic
cd nellai-green-civic
cp .env.example .env
# Generate a real secret instead of the placeholder:
sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$(openssl rand -hex 32)/" .env
```

## 2. (Recommended) Pre-fetch AI model weights on the host

Some networks block the AI model CDNs from inside a Docker container's
default bridge network while allowing the host through. Avoid the problem
entirely by fetching the weights once on the host:

```bash
./scripts/download_ai_models.sh
```

This populates `ai/model_assets/`, which is bind-mounted read-only into the
`ai-service` container. If you skip this step, the container will try to
download the models itself on first request.

## 3. Start everything

```bash
docker compose up -d --build
# or, if you don't have the compose plugin:
docker-compose up -d --build
```

This starts: `db` (PostgreSQL+PostGIS), `redis`, `backend` (FastAPI,
auto-runs Alembic migrations and the seed script on boot), `ai-service`,
and `web` (Vite dev server).

## 4. Seed data

The backend container automatically runs `alembic upgrade head` and
`python -m app.db.seed` on startup. The seed creates:

- All roles (`CITIZEN`, `VOLUNTEER`, `AUTHORITY`, `ADMIN`, `SUPER_ADMIN`,
  `MODULE_DEVELOPER`)
- Every complaint category declared by every module's `module.json`
- A default (and a disaster-specific) escalation rule
- A `SUPER_ADMIN` account: `admin@nellaigreencivic.org` /
  `ChangeMe123!` -- **change this password immediately** after first login.

To re-run manually:

```bash
docker compose run --rm backend python -m app.db.seed
```

## 5. Open it

- Web app: http://localhost:5173
- API docs (Swagger UI): http://localhost:8000/api/v1/docs
- AI service health: http://localhost:8100/health

## 6. Configure GIS data (boundaries, authorities)

Fresh installs have no administrative boundaries or authorities. Nothing
breaks (complaints still get created and reach `AI_ANALYZED`), but automatic
authority assignment needs:

1. `POST /api/v1/boundaries` -- a GeoJSON polygon for your village/town/ward.
2. `POST /api/v1/authorities` -- the office responsible, scoped to that boundary.
3. `POST /api/v1/authorities/responsibility-map` -- map a category code to
   that authority.

Do this from Swagger UI, or from the Admin web UI under **Authorities**.

## Troubleshooting

- **`docker-compose: command not found`** -- either install the Docker
  Compose plugin (`sudo apt install docker-compose-plugin`) or download the
  standalone binary into `~/.local/bin` (no root needed):
  ```bash
  curl -sL "https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-x86_64" -o ~/.local/bin/docker-compose
  chmod +x ~/.local/bin/docker-compose
  ```
- **AI service stuck "loading model"** -- see step 2 above; some sandboxed
  networks intercept the model CDN with a self-signed certificate inside
  Docker's bridge network specifically. Pre-fetching on the host works around it.
- **`npm install` hangs with no output / no error** -- some networks
  terminate TLS with a certificate that your system's CA store trusts (so
  `curl`/`pip` work fine) but that Node.js's own bundled CA list does not,
  causing every HTTPS request npm makes to hang or fail silently. Fix:
  `export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt` before
  running `npm install` (already set as a build-time `ENV` in
  `web/Dockerfile`, so this only matters if you're running npm directly on
  the host outside Docker).
- **Alembic autogenerate diffs `spatial_ref_sys`** -- this is a PostGIS
  system table, not ours; `alembic/env.py` already excludes it via
  `include_object`. Never let a migration drop it.
