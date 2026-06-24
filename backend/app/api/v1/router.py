"""Aggregate router for API v1.

As modules land (auth, setup, stream-jobs, storage, platforms, …) their routers are
included here. See docs/API.md for the full planned surface.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import ffmpeg_preview, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(ffmpeg_preview.router)

# TODO(Phase 1): include auth, setup, users, settings, stream_jobs,
# ffmpeg_profiles, storage_sources, platforms routers here.
