"""Backup / restore endpoints (admin only)."""

from __future__ import annotations

import datetime as dt
import os
import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import CurrentUser, DbDep, require_roles
from app.core.errors import CastCoreError, ErrorCode
from app.models.backup import Backup
from app.services import audit_service, backup_service

router = APIRouter(
    prefix="/backups",
    tags=["backup"],
    dependencies=[Depends(require_roles("admin"))],
)


class BackupOut(BaseModel):
    id: uuid.UUID
    filename: str
    kind: str
    size_bytes: int
    status: str
    created_at: dt.datetime


class RestoreResult(BaseModel):
    restored: dict[str, int]


def _out(b: Backup) -> BackupOut:
    return BackupOut(id=b.id, filename=b.filename, kind=b.kind,
                     size_bytes=b.size_bytes, status=b.status, created_at=b.created_at)


@router.get("", response_model=list[BackupOut])
async def list_backups(db: DbDep) -> list[BackupOut]:
    res = await db.execute(select(Backup).order_by(Backup.created_at.desc()))
    return [_out(b) for b in res.scalars().all()]


@router.post("", response_model=BackupOut, status_code=201)
async def create_backup(db: DbDep, user: CurrentUser) -> BackupOut:
    backup = await backup_service.create_backup(db, kind="manual")
    await audit_service.record(db, actor_id=user.id, action="backup.create", target_type="backup", target_id=str(backup.id))
    return _out(backup)


async def _get(db: DbDep, backup_id: uuid.UUID) -> Backup:
    b = await db.get(Backup, backup_id)
    if b is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"backup": "not_found"}, http_status=404)
    return b


@router.get("/{backup_id}/download")
async def download_backup(backup_id: uuid.UUID, db: DbDep) -> FileResponse:
    b = await _get(db, backup_id)
    if not os.path.exists(b.path):
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"backup": "file_missing"}, http_status=404)
    return FileResponse(b.path, filename=b.filename, media_type="application/gzip")


@router.post("/{backup_id}/restore", response_model=RestoreResult)
async def restore_backup(
    backup_id: uuid.UUID,
    db: DbDep,
    user: CurrentUser,
    confirm: bool = Query(default=False, description="must be true — restore overwrites all data"),
) -> RestoreResult:
    if not confirm:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"confirm": "required"})
    b = await _get(db, backup_id)
    # audit_events are excluded from restore, so this survives the wipe.
    await audit_service.record(db, actor_id=user.id, action="backup.restore", target_type="backup", target_id=str(backup_id))
    try:
        counts = await backup_service.restore_backup(db, b)
    except FileNotFoundError as exc:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"backup": "file_missing"}, http_status=404) from exc
    return RestoreResult(restored=counts)


@router.delete("/{backup_id}", status_code=204)
async def delete_backup(backup_id: uuid.UUID, db: DbDep) -> None:
    b = await db.get(Backup, backup_id)
    if b is not None:
        try:
            os.remove(b.path)
        except OSError:
            pass
        await db.delete(b)
