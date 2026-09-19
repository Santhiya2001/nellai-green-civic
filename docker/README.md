# docker/

Each service keeps its own `Dockerfile` next to its source
(`backend/Dockerfile`, `ai/Dockerfile`, `web/Dockerfile`) so it stays in
sync with that service's dependency files. This directory is reserved for
shared/cross-service assets (e.g. an Nginx reverse-proxy config for a
single-VM production deployment) as the project grows — see
[docs/deployment.md](../docs/deployment.md).
