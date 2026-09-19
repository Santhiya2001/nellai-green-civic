FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Prefer the CPU-only PyTorch index (far smaller than the CUDA build); if
# that host is unreachable in this build environment, fall back to the
# default PyPI wheel (larger, bundles CUDA, but still CPU-inference-capable).
RUN pip install --no-cache-dir torch==2.2.2 torchvision==0.17.2 --index-url https://download.pytorch.org/whl/cpu \
    || pip install --no-cache-dir torch==2.2.2 torchvision==0.17.2

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV HF_HOME=/app/model_cache
ENV TRANSFORMERS_CACHE=/app/model_cache
# The accelerated hf-xet downloader talks to an AWS CDN host directly; in
# some sandboxed/proxied network environments that host's TLS cert fails
# verification even though huggingface.co itself is reachable. Force the
# classic HTTP(S) download path instead.
ENV HF_HUB_DISABLE_XET=1

COPY . .

EXPOSE 8100

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100"]
