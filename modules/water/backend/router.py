import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape as shapely_shape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User
from app.services.gis import make_point, nearby_filter
from app.services.storage import save_upload

# These modules run inside the backend process, so they can import the
# module's own models.py the same way core code imports app.models.
import importlib
_models = importlib.import_module("nellai_modules.water.models")
WaterBody = _models.WaterBody
WaterObservation = _models.WaterObservation

router = APIRouter()


def _point_latlng(geom):
    if geom is None:
        return None, None
    s = to_shape(geom)
    centroid = s.centroid if s.geom_type != "Point" else s
    return centroid.y, centroid.x


def _water_body_out(wb: WaterBody) -> dict:
    lat, lng = _point_latlng(wb.geom)
    return {
        "id": str(wb.id), "name": wb.name, "type": wb.type,
        "latitude": lat, "longitude": lng,
        "capacity_liters": wb.capacity_liters, "notes": wb.notes,
    }


@router.post("/water-bodies", dependencies=[Depends(require_roles("ADMIN"))])
async def create_water_body(
    name: str = Form(...),
    type: str = Form(...),
    geojson: str = Form(..., description="GeoJSON geometry as a JSON string (Point or Polygon)"),
    capacity_liters: float | None = Form(default=None),
    notes: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
):
    import json
    try:
        geom_shape = shapely_shape(json.loads(geojson))
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid GeoJSON: {exc}") from exc

    water_body = WaterBody(name=name, type=type, geom=from_shape(geom_shape, srid=4326), capacity_liters=capacity_liters, notes=notes)
    db.add(water_body)
    await db.commit()
    await db.refresh(water_body)
    return _water_body_out(water_body)


@router.get("/water-bodies")
async def list_water_bodies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WaterBody))
    return [_water_body_out(wb) for wb in result.scalars().all()]


@router.get("/water-bodies/nearby")
async def nearby_water_bodies(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_meters: float = Query(default=5000, le=50000),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(WaterBody).where(nearby_filter(WaterBody.geom, latitude, longitude, radius_meters)))
    return [_water_body_out(wb) for wb in result.scalars().all()]


@router.post("/observations", status_code=status.HTTP_201_CREATED)
async def create_observation(
    water_body_id: uuid.UUID = Form(...),
    observation_type: str = Form(...),
    description: str = Form(default=""),
    latitude: float | None = Form(default=None),
    longitude: float | None = Form(default=None),
    water_level_meters: float | None = Form(default=None),
    photo: UploadFile | None = File(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    water_body = (await db.execute(select(WaterBody).where(WaterBody.id == water_body_id))).scalar_one_or_none()
    if water_body is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Water body not found")

    photo_url = await save_upload(photo, subdirectory="water") if photo else None
    observation = WaterObservation(
        water_body_id=water_body_id,
        observed_by=current_user.id,
        observation_type=observation_type,
        description=description,
        photo_url=photo_url,
        water_level_meters=water_level_meters,
        location=make_point(latitude, longitude) if latitude is not None and longitude is not None else None,
    )
    db.add(observation)
    await db.commit()
    await db.refresh(observation)
    return {
        "id": str(observation.id), "water_body_id": str(water_body_id),
        "observation_type": observation.observation_type, "description": observation.description,
        "photo_url": observation.photo_url, "created_at": observation.created_at.isoformat(),
    }


@router.get("/water-bodies/{water_body_id}/observations")
async def list_observations(water_body_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WaterObservation).where(WaterObservation.water_body_id == water_body_id).order_by(WaterObservation.created_at.desc()))
    return [
        {"id": str(o.id), "observation_type": o.observation_type, "description": o.description, "photo_url": o.photo_url, "created_at": o.created_at.isoformat()}
        for o in result.scalars().all()
    ]
