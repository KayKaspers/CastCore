"""Aggregate router for API v1.

As modules land (auth, setup, stream-jobs, storage, platforms, …) their routers are
included here. See docs/API.md for the full planned surface.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    backups,
    destinations,
    ffmpeg_preview,
    ffmpeg_profiles,
    health,
    media,
    monitoring,
    notifications,
    setup,
    storage_sources,
    stream_jobs,
    users,
    ws,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(setup.router)
api_router.include_router(users.router)
api_router.include_router(ffmpeg_profiles.router)
api_router.include_router(destinations.router)
api_router.include_router(storage_sources.router)
api_router.include_router(media.router)
api_router.include_router(stream_jobs.router)
api_router.include_router(backups.router)
api_router.include_router(notifications.router)
api_router.include_router(monitoring.router)
api_router.include_router(ws.router)
api_router.include_router(ffmpeg_preview.router)

# TODO(Phase 1): include settings, storage_sources, platforms routers here.
