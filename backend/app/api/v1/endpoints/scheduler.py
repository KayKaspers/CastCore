"""Scheduler endpoints (operator+)."""

from __future__ import annotations

import datetime as dt
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import DbDep, require_roles
from app.core.errors import CastCoreError, ErrorCode
from app.models.scheduler import SchedulerEntry
from app.services import scheduler_service

router = APIRouter(
    prefix="/scheduler",
    tags=["scheduler"],
    dependencies=[Depends(require_roles("operator"))],
)


class SchedulerIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    action: str = Field(pattern="^(stream_start|stream_stop|backup|scan)$")
    target_id: uuid.UUID | None = None
    schedule_type: str = Field(default="interval", pattern="^(once|interval|daily)$")
    run_at: dt.datetime | None = None
    interval_minutes: int = 0
    daily_time: str | None = Field(default=None, pattern="^([01]\\d|2[0-3]):[0-5]\\d$")
    enabled: bool = True


class SchedulerOut(BaseModel):
    id: uuid.UUID
    name: str
    action: str
    target_id: uuid.UUID | None
    schedule_type: str
    run_at: dt.datetime | None
    interval_minutes: int
    daily_time: str | None
    enabled: bool
    next_run_at: dt.datetime | None
    last_run_at: dt.datetime | None
    last_status: str | None


def _apply(entry: SchedulerEntry, payload: SchedulerIn) -> None:
    entry.name = payload.name
    entry.action = payload.action
    entry.target_id = payload.target_id
    entry.schedule_type = payload.schedule_type
    entry.run_at = payload.run_at
    entry.interval_minutes = payload.interval_minutes
    entry.daily_time = payload.daily_time
    entry.enabled = payload.enabled
    entry.next_run_at = scheduler_service.initial_next_run(entry) if payload.enabled else None


@router.get("", response_model=list[SchedulerOut])
async def list_entries(db: DbDep) -> list[SchedulerEntry]:
    res = await db.execute(select(SchedulerEntry).order_by(SchedulerEntry.name))
    return list(res.scalars().all())


@router.post("", response_model=SchedulerOut, status_code=201)
async def create_entry(payload: SchedulerIn, db: DbDep) -> SchedulerEntry:
    entry = SchedulerEntry()
    _apply(entry, payload)
    db.add(entry)
    await db.flush()
    return entry


async def _get(db: DbDep, eid: uuid.UUID) -> SchedulerEntry:
    e = await db.get(SchedulerEntry, eid)
    if e is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"entry": "not_found"}, http_status=404)
    return e


@router.patch("/{eid}", response_model=SchedulerOut)
async def update_entry(eid: uuid.UUID, payload: SchedulerIn, db: DbDep) -> SchedulerEntry:
    entry = await _get(db, eid)
    _apply(entry, payload)
    await db.flush()
    return entry


@router.post("/{eid}/run", response_model=SchedulerOut)
async def run_now(eid: uuid.UUID, db: DbDep) -> SchedulerEntry:
    entry = await _get(db, eid)
    entry.last_status = await scheduler_service.execute_entry(db, entry)
    entry.last_run_at = dt.datetime.now(dt.timezone.utc)
    await db.flush()
    return entry


@router.delete("/{eid}", status_code=204)
async def delete_entry(eid: uuid.UUID, db: DbDep) -> None:
    e = await db.get(SchedulerEntry, eid)
    if e is not None:
        await db.delete(e)
