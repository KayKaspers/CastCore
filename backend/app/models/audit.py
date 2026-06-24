"""Audit-event model for security-relevant actions."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, uuid_pk


class AuditEvent(Base, TimestampMixin):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = uuid_pk()
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    meta: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
