"""Platform-metadata endpoints (operator+): per stream-job, per-platform metadata
with description-template placeholder resolution."""

from __future__ import annotations

import datetime as dt
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import CurrentUser, DbDep, require_roles
from app.core.errors import CastCoreError, ErrorCode
from app.models.platform import PlatformMetadata
from app.models.streaming import StreamJob
from app.services import audit_service, metadata_service, platform_push, platform_readiness

router = APIRouter(prefix="/stream-jobs", tags=["metadata"], dependencies=[Depends(require_roles("operator"))])
generic = APIRouter(prefix="/metadata", tags=["metadata"], dependencies=[Depends(require_roles("operator"))])


class MetadataIn(BaseModel):
    title: str | None = None
    description_template: str | None = None
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    language: str | None = None
    visibility: str = Field(default="public", pattern="^(public|unlisted|private)$")
    scheduled_start: dt.datetime | None = None
    thumbnail_asset_id: uuid.UUID | None = None


class MetadataOut(MetadataIn):
    id: uuid.UUID
    stream_job_id: uuid.UUID
    platform: str


class ResolveIn(BaseModel):
    template: str
    context: dict = Field(default_factory=dict)


class PushResultOut(BaseModel):
    provider: str
    status: str  # success | warning | error
    applied: list[str] = Field(default_factory=list)
    warnings: list[dict] = Field(default_factory=list)
    error: dict | None = None


class ReadinessOut(BaseModel):
    provider: str
    level: str  # green | yellow | red
    checks: list[dict] = Field(default_factory=list)


def _out(m: PlatformMetadata) -> MetadataOut:
    return MetadataOut(
        id=m.id, stream_job_id=m.stream_job_id, platform=m.platform, title=m.title,
        description_template=m.description_template, category=m.category, tags=m.tags,
        language=m.language, visibility=m.visibility, scheduled_start=m.scheduled_start,
        thumbnail_asset_id=m.thumbnail_asset_id,
    )


async def _job(db: DbDep, job_id: uuid.UUID) -> StreamJob:
    job = await db.get(StreamJob, job_id)
    if job is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"job": "not_found"}, http_status=404)
    return job


async def _meta(db: DbDep, job_id: uuid.UUID, platform: str) -> PlatformMetadata | None:
    res = await db.execute(
        select(PlatformMetadata).where(
            PlatformMetadata.stream_job_id == job_id, PlatformMetadata.platform == platform
        )
    )
    return res.scalar_one_or_none()


@router.get("/{job_id}/metadata", response_model=list[MetadataOut])
async def list_metadata(job_id: uuid.UUID, db: DbDep) -> list[MetadataOut]:
    await _job(db, job_id)
    res = await db.execute(select(PlatformMetadata).where(PlatformMetadata.stream_job_id == job_id))
    return [_out(m) for m in res.scalars().all()]


@router.put("/{job_id}/metadata/{platform}", response_model=MetadataOut)
async def upsert_metadata(job_id: uuid.UUID, platform: str, payload: MetadataIn, db: DbDep) -> MetadataOut:
    await _job(db, job_id)
    m = await _meta(db, job_id, platform)
    if m is None:
        m = PlatformMetadata(stream_job_id=job_id, platform=platform)
        db.add(m)
    for key, value in payload.model_dump().items():
        setattr(m, key, value)
    await db.flush()
    return _out(m)


@router.delete("/{job_id}/metadata/{platform}", status_code=204)
async def delete_metadata(job_id: uuid.UUID, platform: str, db: DbDep) -> None:
    m = await _meta(db, job_id, platform)
    if m is not None:
        await db.delete(m)


@router.get("/{job_id}/metadata/{platform}/resolved")
async def resolved_metadata(job_id: uuid.UUID, platform: str, db: DbDep) -> dict:
    job = await _job(db, job_id)
    m = await _meta(db, job_id, platform)
    if m is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"metadata": "not_found"}, http_status=404)
    return await metadata_service.resolve_metadata(db, job, m)


@router.post("/{job_id}/platforms/{provider}/push-metadata", response_model=PushResultOut)
async def push_metadata(job_id: uuid.UUID, provider: str, db: DbDep, user: CurrentUser) -> PushResultOut:
    """Push the job's metadata to a connected platform account (YouTube/Twitch)."""
    job = await _job(db, job_id)
    result = await platform_push.push_metadata(db, job, provider)
    await audit_service.record(
        db, actor_id=user.id, action="platform.metadata_push", target_type="stream_job",
        target_id=str(job.id), meta={"provider": provider, "status": result["status"],
                                     "applied": result["applied"]},
    )
    return PushResultOut(**result)


@router.post("/{job_id}/platforms/{provider}/readiness", response_model=ReadinessOut)
async def platform_readiness_check(job_id: uuid.UUID, provider: str, db: DbDep, user: CurrentUser) -> ReadinessOut:
    """Traffic-light readiness check for a platform (connection, token, scopes, broadcast, …)."""
    job = await _job(db, job_id)
    result = await platform_readiness.check(db, job, provider)
    await audit_service.record(
        db, actor_id=user.id, action="platform.readiness_check", target_type="stream_job",
        target_id=str(job.id), meta={"provider": provider, "level": result["level"]},
    )
    return ReadinessOut(**result)


@generic.get("/placeholders", response_model=list[str])
async def placeholders() -> list[str]:
    return metadata_service.PLACEHOLDERS


@generic.post("/resolve")
async def resolve_preview(payload: ResolveIn) -> dict:
    return {"resolved": metadata_service.resolve_template(payload.template, payload.context)}
