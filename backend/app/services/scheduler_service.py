"""Scheduler: time-based / recurring actions, evaluated by a backend loop.

Supports three schedule types:
- ``once``     — run a single time at ``run_at``, then disable.
- ``interval`` — every ``interval_minutes``.
- ``daily``    — every day at ``daily_time`` ("HH:MM", interpreted as UTC).

Actions: stream_start, stream_stop, backup, scan. The loop runs in the backend process
(FastAPI lifespan), alongside the status consumer.
"""

from __future__ import annotations

import asyncio
import datetime as dt

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.models.scheduler import SchedulerEntry
from app.models.storage import StorageSource
from app.models.streaming import StreamJob
from app.services import backup_service, media_service, stream_service

ACTIONS = ["stream_start", "stream_stop", "backup", "scan"]
_TICK_SECONDS = 20


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def compute_next(entry: SchedulerEntry, after: dt.datetime) -> dt.datetime | None:
    if entry.schedule_type == "once":
        return entry.run_at if (entry.run_at and entry.run_at > after) else None
    if entry.schedule_type == "interval":
        minutes = max(1, entry.interval_minutes)
        return after + dt.timedelta(minutes=minutes)
    if entry.schedule_type == "daily" and entry.daily_time:
        try:
            hh, mm = (int(x) for x in entry.daily_time.split(":", 1))
        except ValueError:
            return None
        candidate = after.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if candidate <= after:
            candidate += dt.timedelta(days=1)
        return candidate
    return None


def initial_next_run(entry: SchedulerEntry) -> dt.datetime | None:
    now = _utcnow()
    if entry.schedule_type == "once":
        return entry.run_at
    return compute_next(entry, now)


async def execute_entry(db: AsyncSession, entry: SchedulerEntry) -> str:
    try:
        if entry.action == "stream_start":
            job = await db.get(StreamJob, entry.target_id)
            if job is None:
                return "job not found"
            await stream_service.start_job(db, job)
        elif entry.action == "stream_stop":
            job = await db.get(StreamJob, entry.target_id)
            if job is None:
                return "job not found"
            await stream_service.stop_job(db, job)
        elif entry.action == "backup":
            await backup_service.create_backup(db, kind="scheduled")
        elif entry.action == "scan":
            source = await db.get(StorageSource, entry.target_id)
            if source is None:
                return "source not found"
            await media_service.scan_source(db, source)
        else:
            return f"unknown action: {entry.action}"
        return "ok"
    except Exception as exc:  # noqa: BLE001 - record any failure, keep scheduler alive
        return str(exc)[:200]


async def tick(db: AsyncSession) -> int:
    """Run all due entries. Returns the number executed."""
    now = _utcnow()
    res = await db.execute(
        select(SchedulerEntry).where(
            SchedulerEntry.enabled.is_(True),
            SchedulerEntry.next_run_at.is_not(None),
            SchedulerEntry.next_run_at <= now,
        )
    )
    due = list(res.scalars().all())
    for entry in due:
        entry.last_status = await execute_entry(db, entry)
        entry.last_run_at = now
        if entry.schedule_type == "once":
            entry.enabled = False
            entry.next_run_at = None
        else:
            entry.next_run_at = compute_next(entry, now)
    await db.commit()
    return len(due)


async def run_scheduler(stop: asyncio.Event) -> None:
    while not stop.is_set():
        try:
            async with SessionLocal() as db:
                await tick(db)
        except Exception as exc:  # noqa: BLE001 - never let the loop die
            print(f"[scheduler] tick error: {exc}")
        try:
            await asyncio.wait_for(stop.wait(), timeout=_TICK_SECONDS)
        except asyncio.TimeoutError:
            pass
