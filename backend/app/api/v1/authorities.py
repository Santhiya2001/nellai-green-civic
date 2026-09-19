import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape as shapely_shape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.authority import Authority, AuthorityResponsibilityMap
from app.models.boundary import AdministrativeBoundary
from app.schemas.authority import (
    AuthorityCreate,
    AuthorityOut,
    BoundaryCreate,
    BoundaryOut,
    ResponsibilityMapCreate,
    ResponsibilityMapOut,
)

router = APIRouter(prefix="/authorities", tags=["Authorities"])
boundaries_router = APIRouter(prefix="/boundaries", tags=["Administrative Boundaries"])


@router.post("", response_model=AuthorityOut, dependencies=[Depends(require_roles("ADMIN"))])
async def create_authority(payload: AuthorityCreate, db: AsyncSession = Depends(get_db)):
    authority = Authority(**payload.model_dump())
    db.add(authority)
    await db.commit()
    await db.refresh(authority)
    return authority


@router.get("", response_model=list[AuthorityOut])
async def list_authorities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Authority).where(Authority.is_active.is_(True)))
    return result.scalars().all()


@router.get("/{authority_id}", response_model=AuthorityOut)
async def get_authority(authority_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    authority = (await db.execute(select(Authority).where(Authority.id == authority_id))).scalar_one_or_none()
    if authority is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Authority not found")
    return authority


@router.post("/responsibility-map", response_model=ResponsibilityMapOut, dependencies=[Depends(require_roles("ADMIN"))])
async def create_responsibility_rule(payload: ResponsibilityMapCreate, db: AsyncSession = Depends(get_db)):
    rule = AuthorityResponsibilityMap(**payload.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.get("/responsibility-map", response_model=list[ResponsibilityMapOut])
async def list_responsibility_rules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuthorityResponsibilityMap))
    return result.scalars().all()


@router.delete("/responsibility-map/{rule_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles("ADMIN"))])
async def delete_responsibility_rule(rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    rule = (await db.execute(select(AuthorityResponsibilityMap).where(AuthorityResponsibilityMap.id == rule_id))).scalar_one_or_none()
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    await db.delete(rule)
    await db.commit()


@boundaries_router.post("", response_model=BoundaryOut, dependencies=[Depends(require_roles("ADMIN"))])
async def create_boundary(payload: BoundaryCreate, db: AsyncSession = Depends(get_db)):
    try:
        geom_shape = shapely_shape(payload.geojson)
        if geom_shape.geom_type == "Polygon":
            from shapely.geometry import MultiPolygon
            geom_shape = MultiPolygon([geom_shape])
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid GeoJSON geometry: {exc}") from exc

    boundary = AdministrativeBoundary(
        name=payload.name,
        level=payload.level,
        district=payload.district,
        parent_id=payload.parent_id,
        geom=from_shape(geom_shape, srid=4326),
    )
    db.add(boundary)
    await db.commit()
    await db.refresh(boundary)
    return boundary


@boundaries_router.get("", response_model=list[BoundaryOut])
async def list_boundaries(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AdministrativeBoundary))
    return result.scalars().all()


@boundaries_router.get("/{boundary_id}/geojson")
async def get_boundary_geojson(boundary_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    boundary = (await db.execute(select(AdministrativeBoundary).where(AdministrativeBoundary.id == boundary_id))).scalar_one_or_none()
    if boundary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boundary not found")
    geom = to_shape(boundary.geom) if boundary.geom is not None else None
    return {"id": str(boundary.id), "name": boundary.name, "level": boundary.level, "geometry": geom.__geo_interface__ if geom else None}
