"""Duplicate complaint detection (spec section 11).

Flags -- never deletes -- likely duplicates so admins can review and merge.
Signals combined into one score:
  - GPS proximity (PostGIS ST_DWithin, default 75m)
  - same category
  - reported within a time window (default 72h)
  - description text similarity (pg_trgm `similarity()`)

Image similarity is left as a documented extension point: once the AI
service exposes perceptual-hash/embedding comparison, `_image_similarity`
is where it plugs in.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.complaint import Complaint
from app.services.gis import nearby_filter

DUPLICATE_RADIUS_METERS = 75
DUPLICATE_TIME_WINDOW_HOURS = 72
DUPLICATE_SCORE_THRESHOLD = 0.55


async def find_possible_duplicates(
    db: AsyncSession,
    category_id,
    latitude: float,
    longitude: float,
    description: str,
    exclude_complaint_id=None,
) -> list[tuple[Complaint, float]]:
    since = datetime.now(timezone.utc) - timedelta(hours=DUPLICATE_TIME_WINDOW_HOURS)

    query = (
        select(Complaint, func.similarity(Complaint.description, description).label("text_score"))
        .where(Complaint.category_id == category_id)
        .where(Complaint.created_at >= since)
        .where(nearby_filter(Complaint.location, latitude, longitude, DUPLICATE_RADIUS_METERS))
    )
    if exclude_complaint_id:
        query = query.where(Complaint.id != exclude_complaint_id)

    result = await db.execute(query)
    rows = result.all()

    scored: list[tuple[Complaint, float]] = []
    for complaint, text_score in rows:
        text_score = float(text_score or 0.0)
        # Proximity + recency already gated by the query; text similarity
        # nudges the score so near-identical wording ranks first.
        score = min(1.0, 0.6 + 0.4 * text_score)
        if score >= DUPLICATE_SCORE_THRESHOLD:
            scored.append((complaint, round(score, 3)))

    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored


def _image_similarity(image_url_a: str | None, image_url_b: str | None) -> float:
    """Placeholder extension point -- returns 0.0 until the AI service exposes
    an image embedding/perceptual-hash comparison endpoint."""
    return 0.0
