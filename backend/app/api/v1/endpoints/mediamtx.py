"""MediaMTX ingest status (read-only)."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.services import mediamtx_service

router = APIRouter(prefix="/mediamtx", tags=["mediamtx"])


@router.get("/status")
async def mediamtx_status(user: CurrentUser) -> dict:
    """Reachability and live ingest paths of the optional MediaMTX router."""
    return await mediamtx_service.get_status()
