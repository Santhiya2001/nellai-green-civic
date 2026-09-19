import importlib
import uuid
from datetime import date

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

_models = importlib.import_module("nellai_modules.afforestation.models")
PlantationSite = _models.PlantationSite
Tree = _models.Tree
TreeMaintenanceLog = _models.TreeMaintenanceLog

router = APIRouter()

NATIVE_SPECIES_GUIDE = {
    "default": ["Neem", "Tamarind", "Banyan", "Peepal", "Pungai (Indian Beech)", "Vaagai (Albizia lebbeck)"],
    "coastal": ["Casuarina", "Screwpine", "Coconut"],
    "riverbank": ["Arjuna", "Bamboo", "Portia Tree"],
}


@router.get("/species-recommendations")
async def recommend_species(land_type: str = Query(default="default")):
    return {"land_type": land_type, "recommended_species": NATIVE_SPECIES_GUIDE.get(land_type, NATIVE_SPECIES_GUIDE["default"])}


@router.post("/plantation-sites", dependencies=[Depends(require_roles("ADMIN", "VOLUNTEER"))])
async def create_plantation_site(
    name: str = Form(...),
    geojson: str = Form(...),
    land_type: str = Form(default="UNKNOWN"),
    estimated_capacity: int | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    import json
    try:
        geom_shape = shapely_shape(json.loads(geojson))
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid GeoJSON: {exc}") from exc

    site = PlantationSite(
        name=name,
        geom=from_shape(geom_shape, srid=4326),
        land_type=land_type,
        ownership_status="UNVERIFIED",  # never auto-claim government ownership -- see models.py docstring
        estimated_capacity=estimated_capacity,
        recommended_species=NATIVE_SPECIES_GUIDE.get(land_type, NATIVE_SPECIES_GUIDE["default"]),
        created_by=current_user.id,
    )
    db.add(site)
    await db.commit()
    await db.refresh(site)
    return {"id": str(site.id), "name": site.name, "ownership_status": site.ownership_status, "recommended_species": site.recommended_species}


@router.post("/plantation-sites/{site_id}/verify-ownership", dependencies=[Depends(require_roles("ADMIN"))])
async def verify_ownership(
    site_id: uuid.UUID,
    ownership_status: str = Form(...),
    verification_document_url: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if ownership_status not in {"GOVERNMENT_VERIFIED", "PRIVATE", "COMMUNITY", "UNVERIFIED"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ownership_status")
    site = (await db.execute(select(PlantationSite).where(PlantationSite.id == site_id))).scalar_one_or_none()
    if site is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plantation site not found")
    site.ownership_status = ownership_status
    site.verified_by = current_user.id
    site.verification_document_url = verification_document_url
    await db.commit()
    return {"id": str(site.id), "ownership_status": site.ownership_status}


@router.get("/plantation-sites")
async def list_plantation_sites(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PlantationSite))
    return [
        {"id": str(s.id), "name": s.name, "land_type": s.land_type, "ownership_status": s.ownership_status, "estimated_capacity": s.estimated_capacity, "recommended_species": s.recommended_species}
        for s in result.scalars().all()
    ]


@router.post("/trees", status_code=status.HTTP_201_CREATED)
async def register_tree(
    species: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    planting_date: date = Form(...),
    organization: str = Form(default=""),
    volunteer_group: str = Form(default=""),
    plantation_site_id: uuid.UUID | None = Form(default=None),
    photo: UploadFile | None = File(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    photo_url = await save_upload(photo, subdirectory="trees") if photo else None
    tree = Tree(
        tree_code=f"TREE-{uuid.uuid4().hex[:8].upper()}",
        species=species,
        location=make_point(latitude, longitude),
        planting_date=planting_date,
        organization=organization,
        volunteer_group=volunteer_group,
        photo_url=photo_url,
        status="PLANTED",
        plantation_site_id=plantation_site_id,
        created_by=current_user.id,
    )
    db.add(tree)
    await db.commit()
    await db.refresh(tree)
    return {"id": str(tree.id), "tree_code": tree.tree_code, "species": tree.species, "status": tree.status}


@router.get("/trees")
async def list_trees(status_filter: str | None = Query(default=None, alias="status"), db: AsyncSession = Depends(get_db)):
    query = select(Tree)
    if status_filter:
        query = query.where(Tree.status == status_filter)
    result = await db.execute(query)
    trees = result.scalars().all()
    out = []
    for t in trees:
        p = to_shape(t.location)
        out.append({"id": str(t.id), "tree_code": t.tree_code, "species": t.species, "status": t.status, "latitude": p.y, "longitude": p.x, "planting_date": t.planting_date.isoformat()})
    return out


@router.get("/trees/nearby")
async def nearby_trees(latitude: float = Query(...), longitude: float = Query(...), radius_meters: float = Query(default=2000, le=20000), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tree).where(nearby_filter(Tree.location, latitude, longitude, radius_meters)))
    trees = result.scalars().all()
    out = []
    for t in trees:
        p = to_shape(t.location)
        out.append({"id": str(t.id), "tree_code": t.tree_code, "species": t.species, "status": t.status, "latitude": p.y, "longitude": p.x})
    return out


@router.post("/trees/{tree_id}/maintenance", dependencies=[Depends(require_roles("VOLUNTEER", "ADMIN"))])
async def log_maintenance(
    tree_id: uuid.UUID,
    status_value: str = Form(..., alias="status"),
    log_date: date = Form(...),
    note: str = Form(default=""),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tree = (await db.execute(select(Tree).where(Tree.id == tree_id))).scalar_one_or_none()
    if tree is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tree not found")
    log = TreeMaintenanceLog(tree_id=tree_id, log_date=log_date, status=status_value, note=note, logged_by=current_user.id)
    db.add(log)
    tree.status = status_value
    await db.commit()
    return {"tree_id": str(tree_id), "status": status_value, "log_date": log_date.isoformat()}


@router.get("/stats/survival-rate")
async def survival_rate(db: AsyncSession = Depends(get_db)):
    all_trees = (await db.execute(select(Tree))).scalars().all()
    total = len(all_trees)
    dead = len([t for t in all_trees if t.status in {"DEAD"}])
    survival_pct = round(((total - dead) / total) * 100, 1) if total else 0.0
    return {"total_trees": total, "dead_or_removed": dead, "survival_rate_percent": survival_pct}
