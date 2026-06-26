"""Setup-wizard logic: step state, admin bootstrap, system checks."""

from __future__ import annotations

import datetime as dt
import os
import shutil

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import ffmpeg_inspect
from app.core.config import get_settings
from app.core.errors import CastCoreError, ErrorCode
from app.models.settings import SetupState
from app.models.user import User
from app.schemas.setup import (
    SETUP_STEPS,
    AdminCreate,
    StepState,
    SetupStatus,
    SystemCheckItem,
    SystemCheckResult,
)
from app.services.auth_service import create_user


async def _ensure_rows(db: AsyncSession) -> dict[str, SetupState]:
    res = await db.execute(select(SetupState))
    existing = {row.step: row for row in res.scalars().all()}
    for step in SETUP_STEPS:
        if step not in existing:
            row = SetupState(step=step, status="pending")
            db.add(row)
            existing[step] = row
    await db.flush()
    return existing


async def get_status(db: AsyncSession) -> SetupStatus:
    rows = await _ensure_rows(db)
    steps = [StepState(step=s, status=rows[s].status) for s in SETUP_STEPS]
    completed = rows["complete"].status == "done"
    current = next((s.step for s in steps if s.status == "pending"), None)
    return SetupStatus(completed=completed, current_step=current, steps=steps)


async def is_setup_complete(db: AsyncSession) -> bool:
    res = await db.execute(
        select(SetupState.status).where(SetupState.step == "complete")
    )
    return res.scalar_one_or_none() == "done"


async def set_step(db: AsyncSession, step: str, status: str) -> SetupStatus:
    if step not in SETUP_STEPS:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"step": step})
    if status not in ("pending", "done", "skipped"):
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"status": status})
    rows = await _ensure_rows(db)
    row = rows[step]
    row.status = status
    row.completed_at = dt.datetime.now(dt.timezone.utc) if status != "pending" else None
    return await get_status(db)


async def create_admin(db: AsyncSession, data: AdminCreate) -> User:
    # Admin bootstrap is only allowed while no users exist.
    count = await db.scalar(select(func.count()).select_from(User))
    if count and count > 0:
        raise CastCoreError(ErrorCode.SETUP_ALREADY_COMPLETED, http_status=409)
    user = await create_user(
        db,
        username=data.username,
        password=data.password,
        email=data.email,
        language=data.language,
        role_names=["admin"],
    )
    await set_step(db, "admin", "done")
    return user


async def run_syscheck() -> SystemCheckResult:
    settings = get_settings()
    items: list[SystemCheckItem] = []

    ffmpeg = shutil.which(settings.ffmpeg_path) or shutil.which("ffmpeg")
    items.append(SystemCheckItem(key="ffmpeg", ok=ffmpeg is not None, detail=ffmpeg))
    ffprobe = shutil.which(settings.ffprobe_path) or shutil.which("ffprobe")
    items.append(SystemCheckItem(key="ffprobe", ok=ffprobe is not None, detail=ffprobe))

    # FFmpeg version vs. the CVE-2026-8461 minimum. A vulnerable build is a warning, not a
    # blocker (CastCore still runs, but the operator should upgrade).
    info = await ffmpeg_inspect.get_info()
    if info["ffmpeg_vulnerable"] is True:
        detail = f"{info['ffmpeg_version']} < {info['min_version']} (vulnerable — upgrade FFmpeg)"
    elif info["ffmpeg_vulnerable"] is None:
        detail = "version unknown — could not verify"
    else:
        detail = f"{info['ffmpeg_version']} (ok)"
    items.append(SystemCheckItem(key="ffmpeg_version", ok=info["ffmpeg_vulnerable"] is False, detail=detail))

    for key, path in (
        ("data_dir", settings.data_dir),
        ("media_dir", settings.media_dir),
        ("log_dir", settings.log_dir),
        ("recordings_dir", settings.recordings_dir),
    ):
        writable = os.path.isdir(path) and os.access(path, os.W_OK)
        items.append(SystemCheckItem(key=key, ok=writable, detail=str(path)))

    try:
        usage = shutil.disk_usage(settings.data_dir if os.path.isdir(settings.data_dir) else "/")
        free_gb = usage.free / (1024**3)
        items.append(
            SystemCheckItem(key="disk_space", ok=free_gb > 5, detail=f"{free_gb:.1f} GB free")
        )
    except OSError:
        items.append(SystemCheckItem(key="disk_space", ok=False, detail="unavailable"))

    blocking = not all(i.ok for i in items if i.key in ("ffmpeg", "ffprobe"))
    warnings = not all(i.ok for i in items)
    level = "red" if blocking else ("yellow" if warnings else "green")
    return SystemCheckResult(level=level, items=items)
