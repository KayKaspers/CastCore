"""Storage-source endpoints (operator+): local folders + SMB shares."""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import DbDep, require_roles
from app.core.config import get_settings
from app.core.errors import CastCoreError, ErrorCode
from app.core.security import encrypt_secret
from app.models.storage import SmbSource, StorageSource
from app.schemas.storage import (
    BrowseResult,
    LocalSourceIn,
    SmbOut,
    SmbSourceIn,
    StorageSourceOut,
    TestResult,
)
from app.services import storage_service

router = APIRouter(
    prefix="/storage-sources",
    tags=["storage"],
    dependencies=[Depends(require_roles("operator"))],
)


def _to_out(s: StorageSource) -> StorageSourceOut:
    smb = None
    if s.smb is not None:
        smb = SmbOut(
            server=s.smb.server, share=s.smb.share, domain=s.smb.domain,
            username=s.smb.username, smb_version=s.smb.smb_version,
            mount_path=s.smb.mount_path, has_password=s.smb.password is not None,
        )
    return StorageSourceOut(
        id=s.id, name=s.name, source_class=s.source_class, type=s.type, path=s.path,
        effective_path=storage_service.effective_path(s), read_only=s.read_only,
        automount=s.automount, status=s.status, last_error=s.last_error,
        last_scan_at=s.last_scan_at, smb=smb,
    )


async def _get(db: DbDep, source_id: uuid.UUID) -> StorageSource:
    s = await db.get(StorageSource, source_id)
    if s is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"source": "not_found"}, http_status=404)
    return s


@router.get("", response_model=list[StorageSourceOut])
async def list_sources(db: DbDep) -> list[StorageSourceOut]:
    res = await db.execute(select(StorageSource).order_by(StorageSource.name))
    return [_to_out(s) for s in res.scalars().all()]


@router.post("/local", response_model=StorageSourceOut, status_code=201)
async def create_local(payload: LocalSourceIn, db: DbDep) -> StorageSourceOut:
    s = StorageSource(
        name=payload.name, source_class="local", type="folder",
        path=payload.path, read_only=payload.read_only,
    )
    s.smb = None  # mark relationship loaded (avoids async lazy-load on serialize)
    ok, detail = await storage_service.test_source(s)
    s.status = "online" if ok else "error"
    s.last_error = detail
    db.add(s)
    await db.flush()
    return _to_out(s)


@router.post("/smb", response_model=StorageSourceOut, status_code=201)
async def create_smb(payload: SmbSourceIn, db: DbDep) -> StorageSourceOut:
    settings = get_settings()
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", payload.name).strip("_") or "smb"
    s = StorageSource(
        name=payload.name, source_class="network", type="smb",
        read_only=payload.read_only, automount=payload.automount,
    )
    s.smb = SmbSource(
        server=payload.server, share=payload.share, domain=payload.domain,
        username=payload.username,
        password=encrypt_secret(payload.password) if payload.password else None,
        smb_version=payload.smb_version,
        mount_path=payload.mount_path or str(Path(settings.mount_dir) / safe),
    )
    db.add(s)
    await db.flush()
    return _to_out(s)


@router.get("/{source_id}", response_model=StorageSourceOut)
async def get_source(source_id: uuid.UUID, db: DbDep) -> StorageSourceOut:
    return _to_out(await _get(db, source_id))


@router.delete("/{source_id}", status_code=204)
async def delete_source(source_id: uuid.UUID, db: DbDep) -> None:
    s = await db.get(StorageSource, source_id)
    if s is not None:
        await db.delete(s)


@router.post("/{source_id}/test", response_model=TestResult)
async def test_source(source_id: uuid.UUID, db: DbDep) -> TestResult:
    s = await _get(db, source_id)
    ok, detail = await storage_service.test_source(s)
    s.status = "online" if ok else "error"
    s.last_error = detail
    return TestResult(ok=ok, detail=detail)


@router.post("/{source_id}/mount", response_model=TestResult)
async def mount_source(source_id: uuid.UUID, db: DbDep) -> TestResult:
    s = await _get(db, source_id)
    if s.type != "smb":
        return TestResult(ok=True, detail="local source — no mount needed")
    ok, detail = await storage_service.mount_smb(s)
    s.status = "online" if ok else "error"
    s.last_error = detail
    return TestResult(ok=ok, detail=detail)


@router.post("/{source_id}/unmount", response_model=TestResult)
async def unmount_source(source_id: uuid.UUID, db: DbDep) -> TestResult:
    s = await _get(db, source_id)
    ok, detail = await storage_service.unmount(s)
    if ok:
        s.status = "offline"
    return TestResult(ok=ok, detail=detail)


@router.get("/{source_id}/browse", response_model=BrowseResult)
async def browse_source(source_id: uuid.UUID, db: DbDep, subpath: str = "") -> BrowseResult:
    s = await _get(db, source_id)
    try:
        entries = storage_service.browse(s, subpath)
    except ValueError as exc:
        raise CastCoreError(ErrorCode.STORAGE_TEST_FAILED, params={"detail": str(exc)}) from exc
    return BrowseResult(base=storage_service.effective_path(s) or "", subpath=subpath, entries=entries)  # type: ignore[arg-type]
