"""Playlist endpoints (operator+)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.api.deps import DbDep, require_roles
from app.core.errors import CastCoreError, ErrorCode
from app.models.media import MediaItem
from app.models.playlist import Playlist, PlaylistItem
from app.services import playlist_service

router = APIRouter(
    prefix="/playlists",
    tags=["playlists"],
    dependencies=[Depends(require_roles("operator"))],
)


class PlaylistIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    mode: str = Field(default="sequential", pattern="^(sequential|shuffle|loop)$")
    description: str | None = None


class ItemIn(BaseModel):
    media_item_id: uuid.UUID


class ReorderIn(BaseModel):
    item_ids: list[uuid.UUID]


class ItemOut(BaseModel):
    id: uuid.UUID
    media_item_id: uuid.UUID
    filename: str
    duration_s: float | None
    order: int
    enabled: bool


class PlaylistOut(BaseModel):
    id: uuid.UUID
    name: str
    mode: str
    description: str | None
    item_count: int
    items: list[ItemOut] = []


class ResolveOut(BaseModel):
    mode: str
    total_duration_s: float
    entries: list[dict]


async def _get(db: DbDep, pid: uuid.UUID) -> Playlist:
    p = await db.get(Playlist, pid)
    if p is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"playlist": "not_found"}, http_status=404)
    return p


async def _items_out(db: DbDep, p: Playlist) -> list[ItemOut]:
    out: list[ItemOut] = []
    for it in p.items:
        media = await db.get(MediaItem, it.media_item_id)
        out.append(ItemOut(
            id=it.id, media_item_id=it.media_item_id,
            filename=media.filename if media else "?",
            duration_s=media.probe.duration_s if (media and media.probe) else None,
            order=it.order, enabled=it.enabled,
        ))
    return out


@router.get("", response_model=list[PlaylistOut])
async def list_playlists(db: DbDep) -> list[PlaylistOut]:
    res = await db.execute(select(Playlist).order_by(Playlist.name))
    return [
        PlaylistOut(id=p.id, name=p.name, mode=p.mode, description=p.description, item_count=len(p.items))
        for p in res.scalars().all()
    ]


@router.post("", response_model=PlaylistOut, status_code=201)
async def create_playlist(payload: PlaylistIn, db: DbDep) -> PlaylistOut:
    p = Playlist(name=payload.name, mode=payload.mode, description=payload.description)
    db.add(p)
    await db.flush()
    return PlaylistOut(id=p.id, name=p.name, mode=p.mode, description=p.description, item_count=0)


@router.get("/{pid}", response_model=PlaylistOut)
async def get_playlist(pid: uuid.UUID, db: DbDep) -> PlaylistOut:
    p = await _get(db, pid)
    return PlaylistOut(id=p.id, name=p.name, mode=p.mode, description=p.description,
                       item_count=len(p.items), items=await _items_out(db, p))


@router.patch("/{pid}", response_model=PlaylistOut)
async def update_playlist(pid: uuid.UUID, payload: PlaylistIn, db: DbDep) -> PlaylistOut:
    p = await _get(db, pid)
    p.name, p.mode, p.description = payload.name, payload.mode, payload.description
    await db.flush()
    return PlaylistOut(id=p.id, name=p.name, mode=p.mode, description=p.description, item_count=len(p.items))


@router.delete("/{pid}", status_code=204)
async def delete_playlist(pid: uuid.UUID, db: DbDep) -> None:
    p = await db.get(Playlist, pid)
    if p is not None:
        await db.delete(p)


@router.post("/{pid}/items", response_model=PlaylistOut, status_code=201)
async def add_item(pid: uuid.UUID, payload: ItemIn, db: DbDep) -> PlaylistOut:
    p = await _get(db, pid)
    if await db.get(MediaItem, payload.media_item_id) is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"media": "not_found"}, http_status=404)
    max_order = await db.scalar(
        select(func.coalesce(func.max(PlaylistItem.order), -1)).where(PlaylistItem.playlist_id == pid)
    )
    db.add(PlaylistItem(playlist_id=pid, media_item_id=payload.media_item_id, order=(max_order or -1) + 1))
    await db.flush()
    await db.refresh(p, attribute_names=["items"])
    return PlaylistOut(id=p.id, name=p.name, mode=p.mode, description=p.description,
                       item_count=len(p.items), items=await _items_out(db, p))


@router.delete("/{pid}/items/{item_id}", status_code=204)
async def remove_item(pid: uuid.UUID, item_id: uuid.UUID, db: DbDep) -> None:
    it = await db.get(PlaylistItem, item_id)
    if it is not None and it.playlist_id == pid:
        await db.delete(it)


@router.post("/{pid}/reorder", response_model=PlaylistOut)
async def reorder(pid: uuid.UUID, payload: ReorderIn, db: DbDep) -> PlaylistOut:
    p = await _get(db, pid)
    order_map = {iid: idx for idx, iid in enumerate(payload.item_ids)}
    for it in p.items:
        if it.id in order_map:
            it.order = order_map[it.id]
    await db.flush()
    await db.refresh(p, attribute_names=["items"])
    return PlaylistOut(id=p.id, name=p.name, mode=p.mode, description=p.description,
                       item_count=len(p.items), items=await _items_out(db, p))


@router.get("/{pid}/resolve", response_model=ResolveOut)
async def resolve_playlist(pid: uuid.UUID, db: DbDep) -> ResolveOut:
    p = await _get(db, pid)
    entries, total = await playlist_service.resolve(db, p)
    return ResolveOut(mode=p.mode, total_duration_s=total, entries=entries)
