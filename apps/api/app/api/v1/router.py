from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, users, brands, uploads, jobs, profiles,
    generate, outputs, references, themes, theme_generate, theme_export
)

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
api_router.include_router(themes.router)
api_router.include_router(theme_generate.router)
api_router.include_router(theme_export.router)
