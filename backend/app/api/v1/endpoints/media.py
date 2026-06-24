"""Media library endpoints (operator+): scan sources, browse/search indexed media."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.api.deps import DbDep, require_roles
from app.core.errors import CastCoreError, ErrorCode
from app.models.media import MediaItem
from app.models.storage import StorageSource
from app.schemas.media import MediaItemOut, ScanResult, media_to_out
from app.services import media_service

router = APIRouter(
    prefix="/media",
    tags=["media"],
    dependencies=[Depends(require_roles("operator"))],
)


@router.post("/scan/{source_id}", response_model=ScanResult)
async def scan(source_id: uuid.UUID, db: DbDep) -> ScanResult:
    source = await db.get(StorageSource, source_id)
    if source is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"source": "not_found"}, http_status=404)
    try:
        result = await media_service.scan_source(db, source)
    except ValueError as exc:
        raise CastCoreError(ErrorCode.STORAGE_TEST_FAILED, params={"detail": str(exc)}) from exc
    return ScanResult(**result)


@router.get("", response_model=list[MediaItemOut])
async def list_media(
    db: DbDep,
    source_id: uuid.UUID | None = None,
    kind: str | None = None,
    streamable: bool | None = None,
    q: str | None = None,
    limit: int = Query(default=200, le=1000),
    offset: int = 0,
) -> list[MediaItemOut]:
    stmt = select(MediaItem)
    if source_id is not None:
        stmt = stmt.where(MediaItem.storage_source_id == source_id)
    if kind is not None:
        stmt = stmt.where(MediaItem.kind == kind)
    if streamable is not None:
        stmt = stmt.where(MediaItem.streamable == streamable)
    if q:
        stmt = stmt.where(MediaItem.filename.ilike(f"%{q}%"))
    stmt = stmt.order_by(MediaItem.filename).limit(limit).offset(offset)
    res = await db.execute(stmt)
    return [media_to_out(m) for m in res.scalars().all()]


@router.get("/{item_id}", response_model=MediaItemOut)
async def get_media(item_id: uuid.UUID, db: DbDep) -> MediaItemOut:
    item = await db.get(MediaItem, item_id)
    if item is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"item": "not_found"}, http_status=404)
    return media_to_out(item)


@router.delete("/{item_id}", status_code=204)
async def delete_media(item_id: uuid.UUID, db: DbDep) -> None:
    item = await db.get(MediaItem, item_id)
    if item is not None:
        await db.delete(item)
