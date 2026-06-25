"""Aggregate router for API v1.

As modules land (auth, setup, stream-jobs, storage, platforms, …) their routers are
included here. See docs/API.md for the full planned surface.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    app_settings,
    assets,
    audit,
    auth,
    backups,
    channels,
    destinations,
    ffmpeg_preview,
    ffmpeg_profiles,
    health,
    media,
    metadata,
    monitoring,
    notifications,
    playlists,
    recordings,
    scheduler,
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
api_router.include_router(app_settings.router)
api_router.include_router(users.router)
api_router.include_router(ffmpeg_profiles.router)
api_router.include_router(destinations.router)
api_router.include_router(storage_sources.router)
api_router.include_router(media.router)
api_router.include_router(stream_jobs.router)
api_router.include_router(metadata.router)
api_router.include_router(metadata.generic)
api_router.include_router(assets.router)
api_router.include_router(backups.router)
api_router.include_router(audit.router)
api_router.include_router(notifications.router)
api_router.include_router(monitoring.router)
api_router.include_router(recordings.router)
api_router.include_router(scheduler.router)
api_router.include_router(playlists.router)
# public channel routes (HLS/EPG/M3U) must be registered before the authed channel router
api_router.include_router(channels.public_router)
api_router.include_router(channels.router)
api_router.include_router(ws.router)
api_router.include_router(ffmpeg_preview.router)

# TODO(Phase 1): include settings, storage_sources, platforms routers here.
