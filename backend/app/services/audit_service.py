"""Audit logging — record security-relevant actions to the audit_events table.

Best-effort: failures must never break the action being audited. The session is committed
by the request dependency.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditEvent


async def record(
    db: AsyncSession,
    *,
    actor_id: uuid.UUID | None,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    ip: str | None = None,
    meta: dict[str, Any] | None = None,
) -> None:
    try:
        db.add(AuditEvent(
            actor_id=actor_id, action=action, target_type=target_type,
            target_id=target_id, ip=ip, meta=meta or {},
        ))
        await db.flush()
    except Exception:  # noqa: BLE001 - auditing must not break the main action
        pass
