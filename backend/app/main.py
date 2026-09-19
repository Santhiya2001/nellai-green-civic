import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.module_loader import load_module_routers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nellai")

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Open-source modular civic & environmental management platform for Tirunelveli.",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.LOCAL_STORAGE_PATH), name="uploads")

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Plugin/module system: every folder under /modules with a valid module.json
# gets its router mounted here automatically. See docs/module-development.md.
mounted_modules = load_module_routers(app)
logger.info("Loaded %d module(s): %s", len(mounted_modules), [m.module_id for m in mounted_modules])


@app.get("/health")
async def health():
    return {"status": "ok", "modules_loaded": [m.module_id for m in mounted_modules]}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
