"""Persisted preflight reports.

A report captures the structured result of a preflight run so it survives restarts and can
feed the health score and diagnostics engine (without re-running slow probes). Checks are
stored as JSON; **no secrets, tokens or stream keys** are ever written into a report.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, uuid_pk


class PreflightReport(Base, TimestampMixin):
    __tablename__ = "preflight_reports"

    id: Mapped[uuid.UUID] = uuid_pk()
    stream_job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("stream_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    level: Mapped[str] = mapped_column(String(8), nullable=False)  # green | yellow | red | gray
    can_start: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    checks: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    started_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
