"""Health & readiness endpoints (used by Docker healthchecks and monitoring)."""

from __future__ import annotations

import shutil

from fastapi import APIRouter

from app import __version__
from app.core.config import get_settings

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict:
    """Liveness probe."""
    return {"status": "ok", "version": __version__}


@router.get("/system/health")
async def system_health() -> dict:
    """Lightweight readiness/capability snapshot (expanded in Phase 1/2)."""
    settings = get_settings()
    return {
        "status": "ok",
        "version": __version__,
        "environment": settings.castcore_env,
        "ffmpeg_available": shutil.which(settings.ffmpeg_path) is not None
        or shutil.which("ffmpeg") is not None,
        "ffprobe_available": shutil.which(settings.ffprobe_path) is not None
        or shutil.which("ffprobe") is not None,
    }
