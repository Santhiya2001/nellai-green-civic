import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.user import Role, User
from app.schemas.auth import UserOut

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserOut], dependencies=[Depends(require_roles("ADMIN"))])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [UserOut(id=u.id, full_name=u.full_name, email=u.email, phone=u.phone, roles=u.role_names(), is_active=u.is_active, is_verified=u.is_verified) for u in users]


@router.post("/{user_id}/roles/{role_name}", response_model=UserOut, dependencies=[Depends(require_roles("SUPER_ADMIN"))])
async def assign_role(user_id: uuid.UUID, role_name: str, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    role = (await db.execute(select(Role).where(Role.name == role_name))).scalar_one_or_none()
    if role is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown role '{role_name}'")
    if role not in user.roles:
        user.roles.append(role)
    await db.commit()
    await db.refresh(user)
    return UserOut(id=user.id, full_name=user.full_name, email=user.email, phone=user.phone, roles=user.role_names(), is_active=user.is_active, is_verified=user.is_verified)


@router.post("/{user_id}/deactivate", response_model=UserOut, dependencies=[Depends(require_roles("ADMIN"))])
async def deactivate_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return UserOut(id=user.id, full_name=user.full_name, email=user.email, phone=user.phone, roles=user.role_names(), is_active=user.is_active, is_verified=user.is_verified)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(current_user: User = Depends(require_roles("CITIZEN", "VOLUNTEER", "AUTHORITY", "ADMIN", "SUPER_ADMIN")), db: AsyncSession = Depends(get_db)):
    """Self-service account deletion (spec section 29: data deletion mechanism)."""
    current_user.is_active = False
    current_user.full_name = "Deleted User"
    current_user.email = f"deleted-{current_user.id}@nellaigreencivic.org"
    current_user.phone = None
    await db.commit()
