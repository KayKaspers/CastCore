"""Asset endpoints (operator+): secure image upload, list, serve, delete."""

from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import DbDep, require_roles
from app.core.errors import CastCoreError, ErrorCode
from app.models.asset import Asset
from app.services import asset_service

router = APIRouter(prefix="/assets", tags=["assets"], dependencies=[Depends(require_roles("operator"))])


class AssetOut(BaseModel):
    id: uuid.UUID
    filename: str
    original_name: str | None
    kind: str
    mime: str
    size_bytes: int
    width: int | None
    height: int | None
    used: bool


def _out(a: Asset) -> AssetOut:
    return AssetOut(
        id=a.id, filename=a.filename, original_name=a.original_name, kind=a.kind,
        mime=a.mime, size_bytes=a.size_bytes, width=a.width, height=a.height, used=a.used,
    )


@router.get("", response_model=list[AssetOut])
async def list_assets(db: DbDep) -> list[AssetOut]:
    res = await db.execute(select(Asset).order_by(Asset.created_at.desc()))
    return [_out(a) for a in res.scalars().all()]


@router.post("", response_model=AssetOut, status_code=201)
async def upload_asset(db: DbDep, file: UploadFile) -> AssetOut:
    content = await file.read()
    data = asset_service.validate_and_store(content, file.filename)
    # de-duplicate by content hash
    existing = (await db.execute(select(Asset).where(Asset.sha256 == data["sha256"]))).scalar_one_or_none()
    if existing is not None:
        return _out(existing)
    asset = Asset(**data)
    db.add(asset)
    await db.flush()
    return _out(asset)


async def _get(db: DbDep, asset_id: uuid.UUID) -> Asset:
    a = await db.get(Asset, asset_id)
    if a is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"asset": "not_found"}, http_status=404)
    return a


@router.get("/{asset_id}/file")
async def serve_asset(asset_id: uuid.UUID, db: DbDep) -> FileResponse:
    a = await _get(db, asset_id)
    if not os.path.exists(a.path):
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"asset": "file_missing"}, http_status=404)
    # Served with a fixed, validated content type; never as an executable/inline HTML.
    return FileResponse(a.path, media_type=a.mime)


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(asset_id: uuid.UUID, db: DbDep) -> None:
    a = await db.get(Asset, asset_id)
    if a is not None:
        try:
            os.remove(a.path)
        except OSError:
            pass
        await db.delete(a)
