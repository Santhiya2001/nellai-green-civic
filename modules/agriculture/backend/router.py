import importlib
import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User
from app.services.ai_client import classify_complaint
from app.services.gis import make_point
from app.services.storage import save_upload

_models = importlib.import_module("nellai_modules.agriculture.models")
FarmAdvisory = _models.FarmAdvisory
CropReport = _models.CropReport

router = APIRouter()


@router.post("/advisories", dependencies=[Depends(require_roles("ADMIN", "AUTHORITY"))])
async def create_advisory(title: str = Form(...), crop: str = Form(...), content: str = Form(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    advisory = FarmAdvisory(title=title, crop=crop, content=content, published_by=current_user.id)
    db.add(advisory)
    await db.commit()
    await db.refresh(advisory)
    return {"id": str(advisory.id), "title": advisory.title, "crop": advisory.crop}


@router.get("/advisories")
async def list_advisories(crop: str | None = Query(default=None), db: AsyncSession = Depends(get_db)):
    query = select(FarmAdvisory).order_by(FarmAdvisory.created_at.desc())
    if crop:
        query = query.where(FarmAdvisory.crop == crop)
    result = await db.execute(query)
    return [{"id": str(a.id), "title": a.title, "crop": a.crop, "content": a.content, "created_at": a.created_at.isoformat()} for a in result.scalars().all()]


@router.post("/crop-reports", status_code=status.HTTP_201_CREATED)
async def create_crop_report(
    crop: str = Form(...),
    issue_type: str = Form(...),
    description: str = Form(default=""),
    latitude: float = Form(...),
    longitude: float = Form(...),
    photo: UploadFile | None = File(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    photo_url = await save_upload(photo, subdirectory="agriculture") if photo else None
    ai_result = await classify_complaint(f"{crop} {issue_type} {description}", photo_url)

    report = CropReport(
        user_id=current_user.id, crop=crop, issue_type=issue_type, description=description,
        photo_url=photo_url, location=make_point(latitude, longitude),
        ai_diagnosis=ai_result.category_code, ai_confidence=ai_result.confidence,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return {"id": str(report.id), "crop": report.crop, "issue_type": report.issue_type, "ai_diagnosis": report.ai_diagnosis, "ai_confidence": report.ai_confidence}


@router.get("/crop-reports")
async def list_crop_reports(mine: bool = Query(default=False), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = select(CropReport).order_by(CropReport.created_at.desc())
    if mine:
        query = query.where(CropReport.user_id == current_user.id)
    result = await db.execute(query)
    out = []
    for r in result.scalars().all():
        p = to_shape(r.location)
        out.append({"id": str(r.id), "crop": r.crop, "issue_type": r.issue_type, "status": r.status, "latitude": p.y, "longitude": p.x, "ai_diagnosis": r.ai_diagnosis})
    return out
