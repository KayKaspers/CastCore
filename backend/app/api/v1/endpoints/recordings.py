"""Recording / replay endpoints (operator+)."""

from __future__ import annotations

import datetime as dt
import os
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import DbDep, require_roles
from app.core.errors import CastCoreError, ErrorCode
from app.models.recording import Recording

router = APIRouter(
    prefix="/recordings",
    tags=["recording"],
    dependencies=[Depends(require_roles("operator"))],
)


class RecordingOut(BaseModel):
    id: uuid.UUID
    stream_job_id: uuid.UUID | None
    filename: str
    state: str
    size_bytes: int
    duration_s: float | None
    started_at: dt.datetime | None
    ended_at: dt.datetime | None
    retention_until: dt.datetime | None


def _out(r: Recording) -> RecordingOut:
    duration = (r.ended_at - r.started_at).total_seconds() if (r.started_at and r.ended_at) else None
    return RecordingOut(
        id=r.id, stream_job_id=r.stream_job_id, filename=r.filename, state=r.state,
        size_bytes=r.size_bytes, duration_s=duration, started_at=r.started_at,
        ended_at=r.ended_at, retention_until=r.retention_until,
    )


@router.get("", response_model=list[RecordingOut])
async def list_recordings(db: DbDep, job_id: uuid.UUID | None = None) -> list[RecordingOut]:
    stmt = select(Recording).order_by(Recording.created_at.desc())
    if job_id is not None:
        stmt = stmt.where(Recording.stream_job_id == job_id)
    res = await db.execute(stmt)
    return [_out(r) for r in res.scalars().all()]


async def _get(db: DbDep, rid: uuid.UUID) -> Recording:
    r = await db.get(Recording, rid)
    if r is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"recording": "not_found"}, http_status=404)
    return r


@router.get("/{rid}/download")
async def download_recording(rid: uuid.UUID, db: DbDep) -> FileResponse:
    r = await _get(db, rid)
    if not os.path.exists(r.path):
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"recording": "file_missing"}, http_status=404)
    return FileResponse(r.path, filename=r.filename, media_type="video/mp4")


@router.delete("/{rid}", status_code=204)
async def delete_recording(rid: uuid.UUID, db: DbDep) -> None:
    r = await db.get(Recording, rid)
    if r is not None:
        try:
            os.remove(r.path)
        except OSError:
            pass
        await db.delete(r)
