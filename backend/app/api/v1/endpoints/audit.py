"""Audit-log endpoint (admin only)."""

from __future__ import annotations

import datetime as dt
import uuid

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import DbDep, require_roles
from app.models.audit import AuditEvent
from app.models.user import User

router = APIRouter(prefix="/audit", tags=["audit"], dependencies=[Depends(require_roles("admin"))])


class AuditOut(BaseModel):
    id: uuid.UUID
    actor: str | None
    action: str
    target_type: str | None
    target_id: str | None
    ip: str | None
    meta: dict
    at: dt.datetime


@router.get("", response_model=list[AuditOut])
async def list_audit(
    db: DbDep,
    action: str | None = None,
    limit: int = Query(default=100, le=500),
    offset: int = 0,
) -> list[AuditOut]:
    stmt = (
        select(AuditEvent, User.username)
        .outerjoin(User, AuditEvent.actor_id == User.id)
        .order_by(AuditEvent.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if action:
        stmt = stmt.where(AuditEvent.action == action)
    rows = (await db.execute(stmt)).all()
    return [
        AuditOut(
            id=e.id, actor=username, action=e.action, target_type=e.target_type,
            target_id=e.target_id, ip=e.ip, meta=e.meta, at=e.created_at,
        )
        for e, username in rows
    ]
