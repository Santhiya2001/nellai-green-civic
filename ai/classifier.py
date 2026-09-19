"""Real (not mocked) but genuinely lightweight classification.

Text: zero-shot classification via a pretrained sentence-embedding model
(paraphrase-MiniLM-L3-v2, ~17M params, ~60MB). We embed the citizen's free
text description and every category's canonical description, then pick the
category whose embedding is closest by cosine similarity. This needs no
labeled training data (there is none yet for this project) and is exactly
the kind of model a real deployment would later fine-tune or replace.

Image: auxiliary signal via a pretrained MobileNetV3-Small (ImageNet
weights). ImageNet has no "blocked drain" class, so we only use it to
nudge confidence/severity when a curated subset of its 1000 labels is
plausibly relevant (e.g. detecting standing water, trash-like objects).
This is intentionally documented as a *secondary* signal -- text carries
the primary classification, matching the spec's requirement that AI output
is advisory and human-correctable, never authoritative.
"""
import logging
import re
import threading
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer, util

from category_prompts import CATEGORY_PROMPTS, SEVERITY_KEYWORDS

logger = logging.getLogger("classifier")

_TEXT_MODEL_NAME = "paraphrase-MiniLM-L3-v2"
_LOCAL_MODEL_PATH = Path("/app/model_assets/paraphrase-MiniLM-L3-v2")

_text_model: SentenceTransformer | None = None
_category_codes: list[str] = []
_category_embeddings = None
_load_lock = threading.Lock()


def load_models() -> None:
    global _text_model, _category_codes, _category_embeddings
    with _load_lock:
        if _text_model is not None:
            return
        # Prefer a pre-fetched local copy (see scripts/download_ai_models.sh)
        # so the container never needs outbound access to huggingface.co at
        # runtime; falls back to downloading by name if not present.
        source = str(_LOCAL_MODEL_PATH) if _LOCAL_MODEL_PATH.exists() else _TEXT_MODEL_NAME
        logger.info("Loading text embedding model from '%s' ...", source)
        _text_model = SentenceTransformer(source, cache_folder="/app/model_cache")
        _category_codes = list(CATEGORY_PROMPTS.keys())
        _category_embeddings = _text_model.encode(list(CATEGORY_PROMPTS.values()), convert_to_tensor=True, normalize_embeddings=True)
        logger.info("Text model ready. %d category prompts embedded.", len(_category_codes))


def _severity_from_keywords(text: str, base_severity: str) -> str:
    text_lower = text.lower()
    order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    best = base_severity if base_severity in order else "MEDIUM"
    for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        keywords = SEVERITY_KEYWORDS.get(level, [])
        if any(re.search(rf"\b{re.escape(kw)}", text_lower) for kw in keywords):
            if order.index(level) > order.index(best):
                best = level
            break  # keywords are checked from most to least severe; first hit wins
    return best


def classify_text(description: str) -> dict:
    if _text_model is None:
        load_models()

    query_embedding = _text_model.encode(description, convert_to_tensor=True, normalize_embeddings=True)
    similarities = util.cos_sim(query_embedding, _category_embeddings)[0].cpu().numpy()

    top_index = int(np.argmax(similarities))
    top_category = _category_codes[top_index]
    # Cosine similarity for short free text vs. a template sentence rarely
    # exceeds ~0.6-0.7 even for a good match; rescale into a believable
    # 0-1 confidence band instead of reporting the raw (misleadingly low) cosine value.
    raw_score = float(similarities[top_index])
    confidence = max(0.0, min(1.0, (raw_score - 0.15) / 0.45))

    severity = _severity_from_keywords(description, base_severity="MEDIUM")

    ranked = sorted(zip(_category_codes, similarities.tolist()), key=lambda p: p[1], reverse=True)[:3]

    return {
        "category_code": top_category,
        "confidence": round(confidence, 3),
        "severity": severity,
        "top_matches": [{"category_code": c, "similarity": round(s, 3)} for c, s in ranked],
        "model": _TEXT_MODEL_NAME,
    }
