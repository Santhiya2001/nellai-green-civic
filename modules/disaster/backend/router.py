import importlib
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User
from app.services.gis import make_point, nearby_filter
from app.services.notification_service import notify_user
from app.services.storage import save_upload

_models = importlib.import_module("nellai_modules.disaster.models")
DisasterAlert = _models.DisasterAlert
DisasterReport = _models.DisasterReport

router = APIRouter()


@router.post("/alerts", dependencies=[Depends(require_roles("ADMIN", "AUTHORITY"))])
async def issue_alert(
    type: str = Form(...),
    severity: str = Form(default="MEDIUM"),
    description: str = Form(default=""),
    expires_at: datetime | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    alert = DisasterAlert(type=type, severity=severity, description=description, issued_by=current_user.id, expires_at=expires_at)
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return {"id": str(alert.id), "type": alert.type, "severity": alert.severity, "is_active": alert.is_active}


@router.get("/alerts")
async def list_alerts(active_only: bool = Query(default=True), db: AsyncSession = Depends(get_db)):
    query = select(DisasterAlert).order_by(DisasterAlert.issued_at.desc())
    if active_only:
        query = query.where(DisasterAlert.is_active.is_(True))
    result = await db.execute(query)
    return [{"id": str(a.id), "type": a.type, "severity": a.severity, "description": a.description, "issued_at": a.issued_at.isoformat(), "is_active": a.is_active} for a in result.scalars().all()]


@router.post("/reports", status_code=status.HTTP_201_CREATED)
async def create_report(
    alert_id: uuid.UUID | None = Form(default=None),
    description: str = Form(default=""),
    latitude: float = Form(...),
    longitude: float = Form(...),
    casualties_reported: bool = Form(default=False),
    needs_rescue: bool = Form(default=False),
    photo: UploadFile | None = File(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    photo_url = await save_upload(photo, subdirectory="disaster") if photo else None
    report = DisasterReport(
        user_id=current_user.id, alert_id=alert_id, description=description, photo_url=photo_url,
        location=make_point(latitude, longitude), casualties_reported=casualties_reported, needs_rescue=needs_rescue,
    )
    db.add(report)
    await db.flush()

    if needs_rescue or casualties_reported:
        all_users = (await db.execute(select(User))).scalars().all()
        # Filter in Python since role membership is a many-to-many collection.
        for admin_user in [u for u in all_users if {"ADMIN", "AUTHORITY", "SUPER_ADMIN"} & set(u.role_names())]:
            await notify_user(db, admin_user.id, "URGENT: Disaster report needs response", f"Rescue/casualty report near ({latitude}, {longitude}).", "GENERAL", None)

    await db.commit()
    await db.refresh(report)
    return {"id": str(report.id), "needs_rescue": report.needs_rescue, "status": report.status}


@router.get("/reports/nearby")
async def nearby_reports(latitude: float = Query(...), longitude: float = Query(...), radius_meters: float = Query(default=10000, le=100000), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DisasterReport).where(nearby_filter(DisasterReport.location, latitude, longitude, radius_meters)))
    out = []
    for r in result.scalars().all():
        p = to_shape(r.location)
        out.append({"id": str(r.id), "description": r.description, "needs_rescue": r.needs_rescue, "status": r.status, "latitude": p.y, "longitude": p.x})
    return out


@router.post("/reports/{report_id}/status", dependencies=[Depends(require_roles("ADMIN", "AUTHORITY"))])
async def update_report_status(report_id: uuid.UUID, status_value: str = Form(..., alias="status"), db: AsyncSession = Depends(get_db)):
    report = (await db.execute(select(DisasterReport).where(DisasterReport.id == report_id))).scalar_one_or_none()
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    report.status = status_value
    await db.commit()
    return {"id": str(report.id), "status": report.status}
