from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.complaint import ComplaintCategory
from app.schemas.complaint import ComplaintCategoryOut

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[ComplaintCategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ComplaintCategory).where(ComplaintCategory.is_active.is_(True)).order_by(ComplaintCategory.module_id, ComplaintCategory.name))
    return result.scalars().all()
