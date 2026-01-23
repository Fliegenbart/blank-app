from fastapi import APIRouter
import structlog
import traceback

logger = structlog.get_logger()

from app.api.v1.endpoints import (
    auth, users, brands, uploads, jobs, profiles,
    generate, outputs, references
)

# Try to import theme endpoints with detailed error logging
try:
    from app.api.v1.endpoints import themes
    from app.api.v1.endpoints import theme_generate
    from app.api.v1.endpoints import theme_export
    THEMES_AVAILABLE = True
    logger.info("Theme endpoints loaded successfully")
except Exception as e:
    THEMES_AVAILABLE = False
    logger.error("Failed to import theme endpoints", error=str(e))
    print(f"THEME IMPORT ERROR: {e}")
    print(traceback.format_exc())

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(brands.router)
api_router.include_router(uploads.router)
api_router.include_router(jobs.router)
api_router.include_router(profiles.router)
api_router.include_router(generate.router)
api_router.include_router(outputs.router)
api_router.include_router(references.router)

if THEMES_AVAILABLE:
    api_router.include_router(themes.router)
    api_router.include_router(theme_generate.router)
    api_router.include_router(theme_export.router)
    logger.info("Theme routers registered")
else:
    logger.warning("Theme routers NOT registered due to import error")
