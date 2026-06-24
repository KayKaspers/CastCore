"""Notification endpoints (admin only). Connection params are encrypted, write-only."""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import DbDep, require_roles
from app.core.errors import CastCoreError, ErrorCode
from app.core.security import encrypt_secret
from app.models.notification import Notification
from app.services import notification_service

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    dependencies=[Depends(require_roles("admin"))],
)


class NotificationIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    channel: str = Field(pattern="^(webhook|discord|slack|gotify|telegram|email)$")
    events: list[str] = Field(default_factory=list)
    secret: dict = Field(default_factory=dict)  # connection params (url/token/…), write-only
    config: dict = Field(default_factory=dict)
    enabled: bool = True


class NotificationOut(BaseModel):
    id: uuid.UUID
    name: str
    channel: str
    events: list[str]
    config: dict
    enabled: bool
    has_secret: bool


class TestResult(BaseModel):
    ok: bool
    detail: str | None = None


def _out(n: Notification) -> NotificationOut:
    return NotificationOut(id=n.id, name=n.name, channel=n.channel, events=n.events,
                           config=n.config, enabled=n.enabled, has_secret=n.secret is not None)


async def _get(db: DbDep, nid: uuid.UUID) -> Notification:
    n = await db.get(Notification, nid)
    if n is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"notification": "not_found"}, http_status=404)
    return n


@router.get("", response_model=list[NotificationOut])
async def list_notifications(db: DbDep) -> list[NotificationOut]:
    res = await db.execute(select(Notification).order_by(Notification.name))
    return [_out(n) for n in res.scalars().all()]


@router.get("/events", response_model=list[str])
async def list_events() -> list[str]:
    return notification_service.EVENTS


@router.post("", response_model=NotificationOut, status_code=201)
async def create_notification(payload: NotificationIn, db: DbDep) -> NotificationOut:
    n = Notification(
        name=payload.name, channel=payload.channel, events=payload.events,
        config=payload.config, enabled=payload.enabled,
        secret=encrypt_secret(json.dumps(payload.secret)) if payload.secret else None,
    )
    db.add(n)
    await db.flush()
    return _out(n)


@router.patch("/{nid}", response_model=NotificationOut)
async def update_notification(nid: uuid.UUID, payload: NotificationIn, db: DbDep) -> NotificationOut:
    n = await _get(db, nid)
    n.name = payload.name
    n.channel = payload.channel
    n.events = payload.events
    n.config = payload.config
    n.enabled = payload.enabled
    if payload.secret:  # only replace when new params provided (write-only)
        n.secret = encrypt_secret(json.dumps(payload.secret))
    await db.flush()
    return _out(n)


@router.post("/{nid}/test", response_model=TestResult)
async def test_notification(nid: uuid.UUID, db: DbDep) -> TestResult:
    n = await _get(db, nid)
    ok, detail = await notification_service.send_one(n, "test", {"name": n.name})
    return TestResult(ok=ok, detail=detail)


@router.delete("/{nid}", status_code=204)
async def delete_notification(nid: uuid.UUID, db: DbDep) -> None:
    n = await db.get(Notification, nid)
    if n is not None:
        await db.delete(n)
