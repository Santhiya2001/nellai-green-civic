import importlib
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User
from app.services.gis import make_point, nearby_filter
from app.services.storage import save_upload

_models = importlib.import_module("nellai_modules.biodiversity.models")
Species = _models.Species
BiodiversityObservation = _models.BiodiversityObservation

router = APIRouter()


@router.post("/species", dependencies=[Depends(require_roles("ADMIN"))])
async def create_species(common_name: str = Form(...), scientific_name: str = Form(default=""), category: str = Form(...), conservation_status: str = Form(default="NOT_EVALUATED"), description: str = Form(default=""), db: AsyncSession = Depends(get_db)):
    species = Species(common_name=common_name, scientific_name=scientific_name, category=category, conservation_status=conservation_status, description=description)
    db.add(species)
    await db.commit()
    await db.refresh(species)
    return {"id": str(species.id), "common_name": species.common_name, "category": species.category}


@router.get("/species")
async def list_species(category: str | None = Query(default=None), db: AsyncSession = Depends(get_db)):
    query = select(Species)
    if category:
        query = query.where(Species.category == category)
    result = await db.execute(query)
    return [{"id": str(s.id), "common_name": s.common_name, "scientific_name": s.scientific_name, "category": s.category, "conservation_status": s.conservation_status} for s in result.scalars().all()]


@router.post("/observations", status_code=status.HTTP_201_CREATED)
async def create_observation(
    species_id: uuid.UUID | None = Form(default=None),
    custom_species_name: str | None = Form(default=None),
    latitude: float = Form(...),
    longitude: float = Form(...),
    notes: str = Form(default=""),
    photo: UploadFile | None = File(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if species_id is None and not custom_species_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide species_id or custom_species_name")
    photo_url = await save_upload(photo, subdirectory="biodiversity") if photo else None
    observation = BiodiversityObservation(
        user_id=current_user.id, species_id=species_id, custom_species_name=custom_species_name,
        location=make_point(latitude, longitude), photo_url=photo_url, notes=notes,
    )
    db.add(observation)
    await db.commit()
    await db.refresh(observation)
    return {"id": str(observation.id), "species_id": str(species_id) if species_id else None, "custom_species_name": custom_species_name}


@router.get("/observations/nearby")
async def nearby_observations(latitude: float = Query(...), longitude: float = Query(...), radius_meters: float = Query(default=5000, le=50000), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BiodiversityObservation).where(nearby_filter(BiodiversityObservation.location, latitude, longitude, radius_meters)))
    out = []
    for o in result.scalars().all():
        p = to_shape(o.location)
        out.append({"id": str(o.id), "species_id": str(o.species_id) if o.species_id else None, "custom_species_name": o.custom_species_name, "latitude": p.y, "longitude": p.x, "verified": o.verified})
    return out


@router.post("/observations/{observation_id}/verify", dependencies=[Depends(require_roles("ADMIN"))])
async def verify_observation(observation_id: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    observation = (await db.execute(select(BiodiversityObservation).where(BiodiversityObservation.id == observation_id))).scalar_one_or_none()
    if observation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found")
    observation.verified = True
    observation.verified_by = current_user.id
    await db.commit()
    return {"id": str(observation.id), "verified": True}
