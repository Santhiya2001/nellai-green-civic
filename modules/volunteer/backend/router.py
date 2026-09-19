import importlib
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from geoalchemy2.shape import to_shape
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User
from app.services.gis import make_point, nearby_filter
from app.services.notification_service import notify_user

_models = importlib.import_module("nellai_modules.volunteer.models")
VolunteerProfile = _models.VolunteerProfile
VolunteerEvent = _models.VolunteerEvent
VolunteerEventRegistration = _models.VolunteerEventRegistration

router = APIRouter()


class ProfileUpdate(BaseModel):
    skills: list[str] = []
    interests: list[str] = []
    preferred_activities: list[str] = []
    latitude: float | None = None
    longitude: float | None = None
    availability: str = ""


class EventCreate(BaseModel):
    title: str
    description: str = ""
    activity_type: str
    latitude: float
    longitude: float
    address_text: str = ""
    start_at: datetime
    end_at: datetime | None = None
    capacity: int | None = None


@router.put("/profile")
async def upsert_profile(payload: ProfileUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    profile = (await db.execute(select(VolunteerProfile).where(VolunteerProfile.user_id == current_user.id))).scalar_one_or_none()
    location = make_point(payload.latitude, payload.longitude) if payload.latitude is not None and payload.longitude is not None else None
    if profile is None:
        profile = VolunteerProfile(user_id=current_user.id, skills=payload.skills, interests=payload.interests, preferred_activities=payload.preferred_activities, location=location, availability=payload.availability)
        db.add(profile)
    else:
        profile.skills = payload.skills
        profile.interests = payload.interests
        profile.preferred_activities = payload.preferred_activities
        profile.location = location
        profile.availability = payload.availability
    await db.commit()
    return {"user_id": str(current_user.id), "skills": profile.skills, "interests": profile.interests}


@router.post("/events", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("VOLUNTEER", "ADMIN"))])
async def create_event(payload: EventCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    event = VolunteerEvent(
        title=payload.title, description=payload.description, activity_type=payload.activity_type,
        location=make_point(payload.latitude, payload.longitude), address_text=payload.address_text,
        start_at=payload.start_at, end_at=payload.end_at, capacity=payload.capacity, organizer_id=current_user.id,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return {"id": str(event.id), "title": event.title, "activity_type": event.activity_type, "start_at": event.start_at.isoformat()}


@router.get("/events")
async def list_events(activity_type: str | None = Query(default=None), db: AsyncSession = Depends(get_db)):
    query = select(VolunteerEvent).where(VolunteerEvent.status == "SCHEDULED").order_by(VolunteerEvent.start_at)
    if activity_type:
        query = query.where(VolunteerEvent.activity_type == activity_type)
    result = await db.execute(query)
    events = result.scalars().all()
    out = []
    for e in events:
        p = to_shape(e.location)
        out.append({
            "id": str(e.id), "title": e.title, "activity_type": e.activity_type,
            "latitude": p.y, "longitude": p.x, "start_at": e.start_at.isoformat(),
            "capacity": e.capacity, "registered_count": len([r for r in e.registrations if r.status != "CANCELLED"]),
        })
    return out


@router.get("/events/recommended")
async def recommended_events(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Simple content-based recommendation: matches the volunteer's
    preferred_activities against upcoming event activity_type."""
    profile = (await db.execute(select(VolunteerProfile).where(VolunteerProfile.user_id == current_user.id))).scalar_one_or_none()
    query = select(VolunteerEvent).where(VolunteerEvent.status == "SCHEDULED").order_by(VolunteerEvent.start_at)
    events = (await db.execute(query)).scalars().all()
    preferred = set(profile.preferred_activities) if profile else set()
    ranked = sorted(events, key=lambda e: 0 if e.activity_type in preferred else 1)
    out = []
    for e in ranked[:20]:
        p = to_shape(e.location)
        out.append({"id": str(e.id), "title": e.title, "activity_type": e.activity_type, "latitude": p.y, "longitude": p.x, "start_at": e.start_at.isoformat(), "matches_preference": e.activity_type in preferred})
    return out


@router.post("/events/{event_id}/register", status_code=status.HTTP_201_CREATED)
async def register_for_event(event_id: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    event = (await db.execute(select(VolunteerEvent).where(VolunteerEvent.id == event_id))).scalar_one_or_none()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    existing = (await db.execute(select(VolunteerEventRegistration).where(VolunteerEventRegistration.event_id == event_id, VolunteerEventRegistration.user_id == current_user.id))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already registered")

    active_count = len([r for r in event.registrations if r.status != "CANCELLED"])
    if event.capacity and active_count >= event.capacity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event is at capacity")

    registration = VolunteerEventRegistration(event_id=event_id, user_id=current_user.id)
    db.add(registration)
    await db.commit()
    return {"event_id": str(event_id), "status": "REGISTERED"}


@router.get("/events/nearby")
async def nearby_events(latitude: float = Query(...), longitude: float = Query(...), radius_meters: float = Query(default=10000, le=50000), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VolunteerEvent).where(VolunteerEvent.status == "SCHEDULED").where(nearby_filter(VolunteerEvent.location, latitude, longitude, radius_meters)))
    events = result.scalars().all()
    out = []
    for e in events:
        p = to_shape(e.location)
        out.append({"id": str(e.id), "title": e.title, "activity_type": e.activity_type, "latitude": p.y, "longitude": p.x, "start_at": e.start_at.isoformat()})
    return out
