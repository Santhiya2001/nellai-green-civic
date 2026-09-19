"""Thin HTTP client to the ai/ microservice (spec section 10).

Kept as a separate service (not an in-process import) so the AI model can be
swapped, scaled, or replaced by a third party without touching the backend --
only this client's contract (POST /classify) needs to keep working.
"""
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger("ai_client")


class AIClassificationResult:
    def __init__(self, category_code: str | None, confidence: float | None, severity: str | None, raw: dict | None):
        self.category_code = category_code
        self.confidence = confidence
        self.severity = severity
        self.raw = raw


async def classify_complaint(description: str, image_url: str | None) -> AIClassificationResult:
    if not settings.AI_SERVICE_ENABLED:
        return AIClassificationResult(None, None, None, None)

    payload = {"description": description, "image_url": image_url}
    try:
        async with httpx.AsyncClient(timeout=settings.AI_SERVICE_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{settings.AI_SERVICE_URL}/classify", json=payload)
            response.raise_for_status()
            data = response.json()
            return AIClassificationResult(
                category_code=data.get("category_code"),
                confidence=data.get("confidence"),
                severity=data.get("severity"),
                raw=data,
            )
    except (httpx.HTTPError, ValueError) as exc:
        # AI is advisory, never blocking: a down/slow AI service must not
        # prevent citizens from filing complaints (human review still happens).
        logger.warning("AI classification unavailable: %s", exc)
        return AIClassificationResult(None, None, None, {"error": str(exc)})
