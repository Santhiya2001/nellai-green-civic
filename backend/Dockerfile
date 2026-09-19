# Build context is the REPO ROOT (see docker-compose.yml's `context: .` /
# `dockerfile: backend/Dockerfile`, and render.yaml), not backend/ --
# because modules/ is a sibling directory that must be baked into the
# image for any deployment that can't bind-mount it at runtime (i.e.
# everywhere except local `docker compose up`, which mounts it live).
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY modules/ /app/modules
COPY scripts/ /app/scripts

EXPOSE 8000

ENV PYTHONPATH=/app
ENV MODULES_ROOT=/app/modules
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
