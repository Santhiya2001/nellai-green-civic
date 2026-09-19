import logging
import threading

from fastapi import FastAPI
from pydantic import BaseModel

from classifier import classify_text, load_models
from image_model import classify_image_labels, load_model, relevant_category_boost

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-service")

app = FastAPI(
    title="Nellai Green & Civic - AI Classification Service",
    description=(
        "Standalone microservice implementing spec section 10 (AI complaint "
        "classification). Kept separate from the backend so the model can be "
        "swapped/scaled independently -- only the /classify contract needs "
        "to keep working. Predictions are advisory: the backend always "
        "stores them alongside the human-corrected final classification, "
        "never as ground truth."
    ),
    version="0.1.0",
)


class ClassifyRequest(BaseModel):
    description: str
    image_url: str | None = None


class ClassifyResponse(BaseModel):
    category_code: str
    confidence: float
    severity: str
    top_matches: list[dict]
    image_labels: list[str] = []
    image_agreement: bool | None = None
    model: str


_load_lock = threading.Lock()


@app.on_event("startup")
def _startup() -> None:
    # Load synchronously but under a lock so a slow first /classify request
    # can't race a concurrent one into double-loading both models.
    def _load_all():
        with _load_lock:
            load_models()
            load_model()

    threading.Thread(target=_load_all, daemon=True).start()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/classify", response_model=ClassifyResponse)
def classify(payload: ClassifyRequest):
    text_result = classify_text(payload.description)

    image_labels: list[str] = []
    image_agreement = None
    if payload.image_url:
        image_labels = classify_image_labels(payload.image_url)
        boosted_category = relevant_category_boost(image_labels)
        if boosted_category:
            image_agreement = boosted_category == text_result["category_code"]
            if image_agreement:
                text_result["confidence"] = round(min(1.0, text_result["confidence"] + 0.15), 3)

    return ClassifyResponse(
        category_code=text_result["category_code"],
        confidence=text_result["confidence"],
        severity=text_result["severity"],
        top_matches=text_result["top_matches"],
        image_labels=image_labels,
        image_agreement=image_agreement,
        model=text_result["model"],
    )
