# Production Deployment

The stack has no hard dependency on a specific cloud provider -- everything
is a standard Docker container plus PostgreSQL+PostGIS. This describes the
shape of a production deployment; adapt the specific commands to whichever
of the options below you pick.

## What needs to run

| Component | What it is | Notes |
|---|---|---|
| `db` | PostgreSQL 15 + PostGIS | Use a managed Postgres with the PostGIS extension available (RDS, Cloud SQL, Azure Database for PostgreSQL all support it), or self-host with persistent volumes + backups |
| `backend` | FastAPI (Uvicorn) | Stateless -- scale horizontally behind a load balancer |
| `ai-service` | FastAPI + sentence-transformers/torchvision | CPU-only is fine; keep it on the same private network as the backend, never expose it publicly |
| `web` | Static build (`npm run build`) | Serve via any static host/CDN (Nginx, Cloudflare Pages, S3+CloudFront, etc.) -- it's just files |
| `redis` | Rate limiting / future caching | Managed Redis or self-hosted |
| File storage | Local disk (dev) or S3-compatible | Switch `STORAGE_BACKEND=s3` for anything beyond a single-host demo, so uploads survive container replacement |

## Quick path: Netlify (web) + Render (everything else)

The repo ships ready-to-use config for exactly this split:

- **`netlify.toml`** builds and deploys `web/` as a static site.
- **`render.yaml`** is a Render Blueprint for `backend`, `ai-service`, and a database.

Steps:

1. Push this repo to GitHub (Netlify and Render both deploy from a connected Git repo).
2. **Render**: dashboard -> New -> Blueprint -> select the repo. Render reads
   `render.yaml` and provisions `nellai-backend`, `nellai-ai`, and `nellai-db`.
   Read the comments at the top of `render.yaml` first -- two values need
   manual attention after first deploy (the AI service's internal URL, and
   confirming the managed Postgres supports the `postgis` extension).
3. **Netlify**: dashboard -> Add new site -> Import from Git -> select the
   repo. Netlify reads `netlify.toml` automatically (base `web/`, build
   `npm run build`, publish `web/dist`). After Render gives you the
   backend's public URL, set `VITE_API_BASE_URL` in Netlify's Site settings
   -> Environment variables to `https://<your-backend>.onrender.com/api/v1`,
   then trigger a redeploy.
4. Back in Render, update `nellai-backend`'s `BACKEND_CORS_ORIGINS` env var
   to your real Netlify URL (`["https://<your-site>.netlify.app"]`) and
   redeploy -- otherwise the browser will block the API calls as
   cross-origin.
5. Run the one-time seed if `preDeployCommand` didn't already
   (`python -m app.db.seed`, from Render's shell) and change the seeded
   `SUPER_ADMIN` password immediately.

Neither file has been tested against a live Render account from this
session -- the field names follow Render's documented Blueprint spec, but
verify them against Render's current docs if a deploy fails on a field
Render no longer recognizes.

## Steps

1. **Provision Postgres+PostGIS.** Enable the `postgis`, `uuid-ossp` and
   `pg_trgm` extensions (see `database/init/001_extensions.sql`).
2. **Set real environment variables** (never reuse `.env.example` values):
   `JWT_SECRET_KEY`, `POSTGRES_*`/`DATABASE_URL`, `BACKEND_CORS_ORIGINS`
   (your real web origin), SMTP/FCM credentials if you want real
   notifications, S3 credentials if using S3 storage.
3. **Build and push images**:
   ```bash
   docker build -t your-registry/nellai-backend backend/
   docker build -t your-registry/nellai-ai ai/
   docker build -t your-registry/nellai-web web/ --build-arg VITE_API_BASE_URL=https://api.yourdomain.org/api/v1
   ```
4. **Run migrations + seed once** against the production database:
   ```bash
   docker run --rm --env-file .env your-registry/nellai-backend alembic upgrade head
   docker run --rm --env-file .env your-registry/nellai-backend python -m app.db.seed
   ```
   Immediately log in as the seeded `SUPER_ADMIN` and change the password.
5. **Deploy** the three images to your platform of choice:
   - **Single VM**: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d` (write a prod override that drops the `--reload` dev command and bind-mounts).
   - **Cloud Run / ECS / Container Apps**: deploy `backend` and `ai-service` as separate services; `web`'s build output is static, so it doesn't need a container runtime at all -- host it on any static/CDN service.
   - **Kubernetes**: standard Deployments for `backend`/`ai-service`, a Service+Ingress, a StatefulSet or managed DB for Postgres.
6. **Schedule the escalation sweep.** `scripts/run_escalation_sweep.py` needs
   to run periodically (every 15-60 min is reasonable): a cron job, a
   Kubernetes CronJob, or a scheduled Cloud Run job all work -- it's a plain
   script with no daemon requirements.
7. **Point DNS** at the web static host and the backend API, and set
   `VITE_API_BASE_URL` / `BACKEND_CORS_ORIGINS` accordingly.

## AI model weights in production

Run `scripts/download_ai_models.sh` as part of your image build (or at
deploy time before first traffic) so `ai-service` never needs outbound
network access at runtime -- smaller attack surface and faster cold starts.

## Health checks

- `GET /health` (backend) -- returns loaded module ids, useful to confirm a
  new module actually mounted after deploy.
- `GET /health` (ai-service).
- `pg_isready` for the database (already used in `docker-compose.yml`'s
  healthcheck).
