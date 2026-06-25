"""Linear channel endpoints.

CRUD + start/stop require operator. HLS/EPG/M3U are exposed on a separate, unauthenticated
router so that media players / IPTV clients can consume them (self-hosted MVP; production
should put these behind signed URLs or the reverse proxy's auth).
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import DbDep, require_roles
from app.core.errors import CastCoreError, ErrorCode
from app.models.channel import Channel
from app.services import channel_service
from app.services.ffmpeg import mask_command

router = APIRouter(
    prefix="/channels",
    tags=["channels"],
    dependencies=[Depends(require_roles("operator"))],
)
public_router = APIRouter(prefix="/channels", tags=["channels"])


class ChannelIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None
    playlist_id: uuid.UUID | None = None
    ffmpeg_profile_id: uuid.UUID | None = None
    fallback_uri: str | None = None
    hls_enabled: bool = True
    epg_enabled: bool = True
    enabled: bool = True


class ChannelOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    playlist_id: uuid.UUID | None
    ffmpeg_profile_id: uuid.UUID | None
    fallback_uri: str | None
    hls_enabled: bool
    epg_enabled: bool
    enabled: bool
    status: str


async def _get(db: DbDep, cid: uuid.UUID) -> Channel:
    ch = await db.get(Channel, cid)
    if ch is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"channel": "not_found"}, http_status=404)
    return ch


@router.get("", response_model=list[ChannelOut])
async def list_channels(db: DbDep) -> list[Channel]:
    res = await db.execute(select(Channel).order_by(Channel.name))
    return list(res.scalars().all())


@router.post("", response_model=ChannelOut, status_code=201)
async def create_channel(payload: ChannelIn, db: DbDep) -> Channel:
    ch = Channel(**payload.model_dump())
    db.add(ch)
    await db.flush()
    return ch


@router.get("/{cid}", response_model=ChannelOut)
async def get_channel(cid: uuid.UUID, db: DbDep) -> Channel:
    return await _get(db, cid)


@router.patch("/{cid}", response_model=ChannelOut)
async def update_channel(cid: uuid.UUID, payload: ChannelIn, db: DbDep) -> Channel:
    ch = await _get(db, cid)
    for key, value in payload.model_dump().items():
        setattr(ch, key, value)
    await db.flush()
    return ch


@router.delete("/{cid}", status_code=204)
async def delete_channel(cid: uuid.UUID, db: DbDep) -> None:
    ch = await db.get(Channel, cid)
    if ch is not None:
        await db.delete(ch)


@router.post("/{cid}/start")
async def start_channel(cid: uuid.UUID, db: DbDep) -> dict:
    ch = await _get(db, cid)
    argv = await channel_service.start_channel(db, ch)
    return {"status": "starting", "preview": mask_command(argv)}


@router.post("/{cid}/stop", status_code=202)
async def stop_channel(cid: uuid.UUID, db: DbDep) -> dict:
    ch = await _get(db, cid)
    await channel_service.stop_channel(db, ch)
    return {"status": "stopping"}


# --- public (no auth): HLS / EPG / M3U for players ---
@public_router.get("/{cid}/hls/{path:path}")
async def serve_hls(cid: uuid.UUID, path: str) -> FileResponse:
    base = channel_service.hls_dir(cid).resolve()
    target = (base / path).resolve()
    if base != target and base not in target.parents:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"path": "denied"}, http_status=404)
    if not target.is_file():
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"hls": "not_ready"}, http_status=404)
    media = "application/vnd.apple.mpegurl" if target.suffix == ".m3u8" else "video/mp2t"
    return FileResponse(target, media_type=media)


@public_router.get("/{cid}/epg.xml")
async def channel_epg(cid: uuid.UUID, db: DbDep) -> Response:
    ch = await db.get(Channel, cid)
    if ch is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"channel": "not_found"}, http_status=404)
    xml = await channel_service.build_epg(db, ch)
    return Response(content=xml, media_type="application/xml")


@public_router.get("/export.m3u")
async def channels_m3u(db: DbDep, request: Request) -> Response:
    res = await db.execute(select(Channel).where(Channel.enabled.is_(True)).order_by(Channel.name))
    m3u = channel_service.build_m3u(list(res.scalars().all()), str(request.base_url))
    return Response(content=m3u, media_type="audio/x-mpegurl")
