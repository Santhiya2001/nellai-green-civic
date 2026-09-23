import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import to_shape

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.complaint import Complaint, ComplaintCategory, ComplaintStatusHistory, ResolutionEvidence
from app.models.enums import ComplaintStatus
from app.models.user import User
from app.schemas.complaint import (
    ComplaintListItem,
    ComplaintOut,
    CitizenVerificationRequest,
    RejectionRequest,
    ResolutionCreate,
    ResolutionOut,
    StatusUpdateRequest,
)
from app.services import numbering
from app.services.ai_client import classify_complaint
from app.services.authority_assignment import assign_authority
from app.services.duplicate_detection import find_possible_duplicates
from app.services.escalation_engine import compute_deadline
from app.services.gis import make_point, nearby_filter
from app.services.notification_service import notify_admin_new_complaint, notify_user
from app.services.storage import save_upload

router = APIRouter(prefix="/complaints", tags=["Complaints"])

# Statuses an AUTHORITY may transition a complaint through manually.
ALLOWED_MANUAL_TRANSITIONS = {
    ComplaintStatus.ASSIGNED.value: {ComplaintStatus.ACKNOWLEDGED.value, ComplaintStatus.REJECTED.value},
    ComplaintStatus.ACKNOWLEDGED.value: {ComplaintStatus.IN_PROGRESS.value, ComplaintStatus.REJECTED.value},
    ComplaintStatus.IN_PROGRESS.value: {ComplaintStatus.RESOLVED.value},
    ComplaintStatus.REOPENED.value: {ComplaintStatus.IN_PROGRESS.value},
}


def _point_to_lat_lng(geom) -> tuple[float, float]:
    shape = to_shape(geom)
    return shape.y, shape.x


def _complaint_to_out(complaint: Complaint) -> ComplaintOut:
    lat, lng = _point_to_lat_lng(complaint.location)
    return ComplaintOut(
        id=complaint.id,
        complaint_number=complaint.complaint_number,
        user_id=complaint.user_id,
        category=complaint.category,
        description=complaint.description,
        image_url=complaint.image_url,
        latitude=lat,
        longitude=lng,
        address_text=complaint.address_text,
        severity=complaint.severity,
        ai_category_code=complaint.ai_category_code,
        ai_confidence=complaint.ai_confidence,
        ai_severity=complaint.ai_severity,
        status=complaint.status,
        assigned_authority_id=complaint.assigned_authority_id,
        deadline_at=complaint.deadline_at,
        escalation_level=complaint.escalation_level,
        duplicate_of_id=complaint.duplicate_of_id,
        rejection_reason=complaint.rejection_reason,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
    )


async def _get_complaint_or_404(db: AsyncSession, complaint_id: uuid.UUID) -> Complaint:
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalar_one_or_none()
    if complaint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    return complaint


@router.post("", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    category_code: str = Form(...),
    description: str = Form(..., min_length=5, max_length=3000),
    latitude: float = Form(..., ge=-90, le=90),
    longitude: float = Form(..., ge=-180, le=180),
    address_text: Optional[str] = Form(default=None),
    extra_data: Optional[str] = Form(default=None),
    image: Optional[UploadFile] = File(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    category = (await db.execute(select(ComplaintCategory).where(ComplaintCategory.code == category_code, ComplaintCategory.is_active.is_(True)))).scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown or inactive category '{category_code}'")

    image_url = None
    if image is not None:
        image_url = await save_upload(image, subdirectory=category.module_id)

    parsed_extra_data = {}
    if extra_data:
        try:
            parsed_extra_data = json.loads(extra_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="extra_data must be valid JSON")

    ai_result = await classify_complaint(description, image_url)

    complaint = Complaint(
        complaint_number=numbering.generate_complaint_number(category_code),
        user_id=current_user.id,
        category_id=category.id,
        description=description,
        image_url=image_url,
        location=make_point(latitude, longitude),
        address_text=address_text,
        severity=ai_result.severity or category.default_severity,
        ai_category_code=ai_result.category_code,
        ai_confidence=ai_result.confidence,
        ai_severity=ai_result.severity,
        ai_raw_response=ai_result.raw,
        status=ComplaintStatus.AI_ANALYZED.value if ai_result.category_code else ComplaintStatus.REPORTED.value,
        extra_data=parsed_extra_data,
    )
    db.add(complaint)
    await db.flush()

    db.add(ComplaintStatusHistory(complaint_id=complaint.id, from_status=None, to_status=complaint.status, changed_by=current_user.id, note="Complaint reported"))

    duplicates = await find_possible_duplicates(db, category.id, latitude, longitude, description, exclude_complaint_id=complaint.id)
    if duplicates:
        best_match, score = duplicates[0]
        complaint.duplicate_of_id = best_match.id
        complaint.possible_duplicate_score = score

    authority, boundary = await assign_authority(db, category_code, latitude, longitude)
    if authority:
        complaint.assigned_authority_id = authority.id
        complaint.boundary_id = boundary.id if boundary else None
        complaint.status = ComplaintStatus.ASSIGNED.value
        complaint.deadline_at = await compute_deadline(db, category_code)
        db.add(ComplaintStatusHistory(complaint_id=complaint.id, from_status=ComplaintStatus.AI_ANALYZED.value, to_status=ComplaintStatus.ASSIGNED.value, note=f"Auto-assigned to {authority.name}"))
        await notify_user(db, current_user.id, "Complaint assigned", f"Your complaint {complaint.complaint_number} was assigned to {authority.name}.", "COMPLAINT_ASSIGNED", complaint.id)

    await db.commit()
    await db.refresh(complaint)

    # Runs after commit so a slow/unreachable SMTP server never delays or
    # risks the complaint-creation transaction itself.
    await notify_admin_new_complaint(
        complaint_number=complaint.complaint_number,
        category_name=category.name,
        description=description,
        severity=complaint.severity,
        latitude=latitude,
        longitude=longitude,
        reporter_email=current_user.email,
    )

    return _complaint_to_out(complaint)


@router.get("", response_model=list[ComplaintListItem])
async def list_complaints(
    mine: bool = Query(default=False),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    category_code: Optional[str] = Query(default=None),
    authority_id: Optional[uuid.UUID] = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Complaint)
    roles = set(current_user.role_names())

    if mine or roles == {"CITIZEN"}:
        query = query.where(Complaint.user_id == current_user.id)
    if status_filter:
        query = query.where(Complaint.status == status_filter)
    if authority_id:
        query = query.where(Complaint.assigned_authority_id == authority_id)

    query = query.order_by(Complaint.created_at.desc()).limit(limit).offset(offset)
    complaints = (await db.execute(query)).scalars().all()

    items = []
    for c in complaints:
        if category_code and c.category.code != category_code:
            continue
        lat, lng = _point_to_lat_lng(c.location)
        items.append(
            ComplaintListItem(
                id=c.id, complaint_number=c.complaint_number, category_code=c.category.code,
                description=c.description, severity=c.severity, status=c.status,
                latitude=lat, longitude=lng, created_at=c.created_at, deadline_at=c.deadline_at,
            )
        )
    return items


@router.get("/nearby", response_model=list[ComplaintListItem])
async def nearby_complaints(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_meters: float = Query(default=2000, le=20000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Complaint).where(nearby_filter(Complaint.location, latitude, longitude, radius_meters)).order_by(Complaint.created_at.desc()).limit(200)
    complaints = (await db.execute(query)).scalars().all()
    items = []
    for c in complaints:
        lat, lng = _point_to_lat_lng(c.location)
        items.append(ComplaintListItem(id=c.id, complaint_number=c.complaint_number, category_code=c.category.code, description=c.description, severity=c.severity, status=c.status, latitude=lat, longitude=lng, created_at=c.created_at, deadline_at=c.deadline_at))
    return items


@router.get("/{complaint_id}", response_model=ComplaintOut)
async def get_complaint(complaint_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    complaint = await _get_complaint_or_404(db, complaint_id)
    roles = set(current_user.role_names())
    if "CITIZEN" in roles and "ADMIN" not in roles and "SUPER_ADMIN" not in roles and complaint.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your complaint")
    return _complaint_to_out(complaint)


@router.post("/{complaint_id}/status", response_model=ComplaintOut)
async def update_status(
    complaint_id: uuid.UUID,
    payload: StatusUpdateRequest,
    current_user: User = Depends(require_roles("AUTHORITY", "ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    complaint = await _get_complaint_or_404(db, complaint_id)
    allowed_next = ALLOWED_MANUAL_TRANSITIONS.get(complaint.status, set())
    if payload.to_status not in allowed_next and "ADMIN" not in current_user.role_names():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot move from {complaint.status} to {payload.to_status}")

    db.add(ComplaintStatusHistory(complaint_id=complaint.id, from_status=complaint.status, to_status=payload.to_status, changed_by=current_user.id, note=payload.note))
    complaint.status = payload.to_status
    await db.commit()
    await db.refresh(complaint)
    return _complaint_to_out(complaint)


@router.post("/{complaint_id}/resolve", response_model=ResolutionOut)
async def resolve_complaint(
    complaint_id: uuid.UUID,
    description: str = Form(..., min_length=5),
    latitude: Optional[float] = Form(default=None),
    longitude: Optional[float] = Form(default=None),
    photo: Optional[UploadFile] = File(default=None),
    current_user: User = Depends(require_roles("AUTHORITY", "ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    complaint = await _get_complaint_or_404(db, complaint_id)
    if complaint.status not in {ComplaintStatus.IN_PROGRESS.value, ComplaintStatus.ACKNOWLEDGED.value}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Complaint must be in progress before it can be resolved")

    photo_url = await save_upload(photo, subdirectory="resolutions") if photo else None
    resolution = ResolutionEvidence(
        complaint_id=complaint.id,
        description=description,
        photo_url=photo_url,
        location=make_point(latitude, longitude) if latitude is not None and longitude is not None else None,
        resolved_by=current_user.id,
    )
    db.add(resolution)

    db.add(ComplaintStatusHistory(complaint_id=complaint.id, from_status=complaint.status, to_status=ComplaintStatus.VERIFICATION.value, changed_by=current_user.id, note="Marked resolved, pending citizen verification"))
    complaint.status = ComplaintStatus.VERIFICATION.value
    await notify_user(db, complaint.user_id, "Complaint resolved", f"Your complaint {complaint.complaint_number} was marked resolved. Please verify.", "COMPLAINT_RESOLVED", complaint.id)

    await db.commit()
    await db.refresh(resolution)
    return resolution


@router.post("/{complaint_id}/verify", response_model=ComplaintOut)
async def verify_resolution(
    complaint_id: uuid.UUID,
    payload: CitizenVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    complaint = await _get_complaint_or_404(db, complaint_id)
    if complaint.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the reporting citizen can verify resolution")
    if complaint.status != ComplaintStatus.VERIFICATION.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Complaint is not awaiting verification")

    result = await db.execute(select(ResolutionEvidence).where(ResolutionEvidence.complaint_id == complaint.id))
    resolution = result.scalar_one_or_none()
    if resolution is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No resolution evidence recorded")

    resolution.citizen_verified = payload.verified
    resolution.citizen_verified_at = datetime.now(timezone.utc)
    resolution.citizen_feedback = payload.feedback

    if payload.verified:
        complaint.status = ComplaintStatus.CLOSED.value
        note = "Citizen confirmed resolution"
    else:
        complaint.status = ComplaintStatus.REOPENED.value
        note = "Citizen rejected resolution; complaint reopened"
        await notify_user(db, complaint.assigned_authority_id, "Complaint reopened", f"{complaint.complaint_number} was reopened by the citizen.", "COMPLAINT_REOPENED", complaint.id) if complaint.assigned_authority_id else None

    db.add(ComplaintStatusHistory(complaint_id=complaint.id, from_status=ComplaintStatus.VERIFICATION.value, to_status=complaint.status, changed_by=current_user.id, note=note))
    await db.commit()
    await db.refresh(complaint)
    return _complaint_to_out(complaint)


@router.post("/{complaint_id}/reject", response_model=ComplaintOut)
async def reject_complaint(
    complaint_id: uuid.UUID,
    payload: RejectionRequest,
    current_user: User = Depends(require_roles("AUTHORITY", "ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    complaint = await _get_complaint_or_404(db, complaint_id)
    complaint.status = ComplaintStatus.REJECTED.value
    complaint.rejection_reason = payload.reason
    db.add(ComplaintStatusHistory(complaint_id=complaint.id, from_status=complaint.status, to_status=ComplaintStatus.REJECTED.value, changed_by=current_user.id, note=payload.reason))
    await notify_user(db, complaint.user_id, "Complaint rejected", f"{complaint.complaint_number}: {payload.reason}", "COMPLAINT_REJECTED", complaint.id)
    await db.commit()
    await db.refresh(complaint)
    return _complaint_to_out(complaint)


@router.post("/{complaint_id}/merge/{duplicate_target_id}", response_model=ComplaintOut, dependencies=[Depends(require_roles("ADMIN"))])
async def merge_duplicate(complaint_id: uuid.UUID, duplicate_target_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Admin-confirmed merge (spec section 11: never auto-delete, admin decides)."""
    complaint = await _get_complaint_or_404(db, complaint_id)
    target = await _get_complaint_or_404(db, duplicate_target_id)
    complaint.duplicate_of_id = target.id
    complaint.status = ComplaintStatus.CLOSED.value
    db.add(ComplaintStatusHistory(complaint_id=complaint.id, from_status=complaint.status, to_status=ComplaintStatus.CLOSED.value, note=f"Merged into {target.complaint_number}"))
    await db.commit()
    await db.refresh(complaint)
    return _complaint_to_out(complaint)
