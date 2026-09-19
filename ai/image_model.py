"""Auxiliary image signal using a pretrained MobileNetV3-Small (ImageNet).
See classifier.py docstring for why this is secondary, not primary."""
import logging
import threading
from pathlib import Path

import torch
from PIL import Image
from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small

logger = logging.getLogger("image_model")

_model = None
_weights = None
_preprocess = None
_load_lock = threading.Lock()

UPLOADS_ROOT = Path("/app/uploads")

# Curated: only these ImageNet labels are considered meaningful evidence for
# our civic/environmental categories -- ImageNet was never trained for this
# domain, so we deliberately do not trust its full 1000-class output.
RELEVANT_LABEL_HINTS: dict[str, list[str]] = {
    "DRAIN_BLOCKAGE": ["sewer", "manhole cover", "drain"],
    "WATER_STAGNATION": ["lakeside", "puddle", "swamp"],
    "GARBAGE_DUMPING": ["trash can", "ashcan", "plastic bag", "garbage truck"],
    "ILLEGAL_DUMPING": ["trash can", "ashcan", "plastic bag"],
    "PLASTIC_WASTE": ["plastic bag", "water bottle"],
    "FALLEN_TREE": ["tree", "log"],
    "LAKE_POLLUTION": ["lakeside", "alga"],
    "RIVER_POLLUTION": ["seashore", "alga"],
    "ROAD_DAMAGE": ["pothole", "manhole cover"],
}


_LOCAL_WEIGHTS_PATH = Path("/app/model_assets/torchvision/mobilenet_v3_small-047dcff4.pth")


def load_model() -> None:
    global _model, _weights, _preprocess
    with _load_lock:
        if _model is not None:
            return
        _weights = MobileNet_V3_Small_Weights.IMAGENET1K_V1
        # weights.meta (incl. the 1000 ImageNet category names) is bundled in
        # torchvision itself -- no network call. Only the actual state dict
        # would trigger a download, so build the architecture unweighted and
        # load a pre-fetched local copy (see scripts/download_ai_models.sh).
        _model = mobilenet_v3_small(weights=None)
        if _LOCAL_WEIGHTS_PATH.exists():
            logger.info("Loading MobileNetV3-Small weights from local file %s", _LOCAL_WEIGHTS_PATH)
            state_dict = torch.load(_LOCAL_WEIGHTS_PATH, map_location="cpu")
            _model.load_state_dict(state_dict)
        else:
            logger.warning("No local MobileNetV3-Small weights found; image signal will be untrained/random until scripts/download_ai_models.sh is run.")
        _model.eval()
        _preprocess = _weights.transforms()
        logger.info("Image model ready.")


def _resolve_local_path(image_url: str) -> Path | None:
    if not image_url:
        return None
    # image_url looks like "/uploads/<subdir>/<file>"; the ai-service mounts
    # the same uploads volume read-only at /app/uploads.
    relative = image_url.split("/uploads/", 1)[-1]
    candidate = UPLOADS_ROOT / relative
    return candidate if candidate.exists() else None


def classify_image_labels(image_url: str | None, top_k: int = 5) -> list[str]:
    if _model is None:
        load_model()

    path = _resolve_local_path(image_url) if image_url else None
    if path is None:
        return []

    try:
        img = Image.open(path).convert("RGB")
        batch = _preprocess(img).unsqueeze(0)
        with torch.no_grad():
            logits = _model(batch)
        probs = torch.nn.functional.softmax(logits[0], dim=0)
        top_indices = torch.topk(probs, top_k).indices.tolist()
        categories = _weights.meta["categories"]
        return [categories[i] for i in top_indices]
    except (OSError, ValueError) as exc:
        logger.warning("Could not classify image %s: %s", path, exc)
        return []


def relevant_category_boost(labels: list[str]) -> str | None:
    labels_joined = " ".join(labels).lower()
    for category_code, hints in RELEVANT_LABEL_HINTS.items():
        if any(hint in labels_joined for hint in hints):
            return category_code
    return None
