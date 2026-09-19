#!/usr/bin/env bash
# Pre-fetches the AI service's pretrained model weights to ai/model_assets/
# so the ai-service container never needs outbound network access at
# runtime (useful on networks/firewalls that block huggingface.co's or
# download.pytorch.org's CDN redirects but allow the host machine through).
#
# Run this on the HOST (not inside Docker) before `docker compose up`.
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p ai/model_assets/torchvision

echo "Downloading sentence-transformer text model..."
pip install --quiet --user huggingface_hub
python3 - <<'PY'
import os
os.environ["HF_HUB_DISABLE_XET"] = "1"
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="sentence-transformers/paraphrase-MiniLM-L3-v2",
    local_dir="ai/model_assets/paraphrase-MiniLM-L3-v2",
)
PY

echo "Downloading MobileNetV3-Small (ImageNet) weights..."
curl -sL -o ai/model_assets/torchvision/mobilenet_v3_small-047dcff4.pth \
  "https://download.pytorch.org/models/mobilenet_v3_small-047dcff4.pth"

echo "Done. ai/model_assets/ is ready to be mounted into the ai-service container."
