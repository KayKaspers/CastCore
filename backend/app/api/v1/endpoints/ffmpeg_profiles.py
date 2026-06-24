"""FFmpeg profile CRUD (operator+)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import DbDep, require_roles
from app.core.errors import CastCoreError, ErrorCode
from app.models.streaming import FFmpegProfile
from app.schemas.streaming import FFmpegProfileIn, FFmpegProfileOut

router = APIRouter(
    prefix="/ffmpeg-profiles",
    tags=["ffmpeg"],
    dependencies=[Depends(require_roles("operator"))],
)


@router.get("", response_model=list[FFmpegProfileOut])
async def list_profiles(db: DbDep) -> list[FFmpegProfile]:
    res = await db.execute(select(FFmpegProfile).order_by(FFmpegProfile.name))
    return list(res.scalars().all())


@router.post("", response_model=FFmpegProfileOut, status_code=201)
async def create_profile(payload: FFmpegProfileIn, db: DbDep) -> FFmpegProfile:
    profile = FFmpegProfile(**payload.model_dump())
    db.add(profile)
    await db.flush()
    return profile


@router.get("/{profile_id}", response_model=FFmpegProfileOut)
async def get_profile(profile_id: uuid.UUID, db: DbDep) -> FFmpegProfile:
    profile = await db.get(FFmpegProfile, profile_id)
    if profile is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"profile": "not_found"}, http_status=404)
    return profile


@router.patch("/{profile_id}", response_model=FFmpegProfileOut)
async def update_profile(profile_id: uuid.UUID, payload: FFmpegProfileIn, db: DbDep) -> FFmpegProfile:
    profile = await db.get(FFmpegProfile, profile_id)
    if profile is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"profile": "not_found"}, http_status=404)
    for key, value in payload.model_dump().items():
        setattr(profile, key, value)
    await db.flush()
    return profile


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(profile_id: uuid.UUID, db: DbDep) -> None:
    profile = await db.get(FFmpegProfile, profile_id)
    if profile is not None:
        await db.delete(profile)
