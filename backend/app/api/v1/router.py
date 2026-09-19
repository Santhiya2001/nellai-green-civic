from fastapi import APIRouter

from app.api.v1 import analytics, authorities, auth, categories, complaints, escalation, modules, notifications, public, users

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(complaints.router)
api_router.include_router(categories.router)
api_router.include_router(authorities.router)
api_router.include_router(authorities.boundaries_router)
api_router.include_router(escalation.router)
api_router.include_router(notifications.router)
api_router.include_router(modules.router)
api_router.include_router(analytics.router)
api_router.include_router(public.router)
