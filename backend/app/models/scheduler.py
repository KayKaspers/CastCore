"""Scheduler entry model — time-based / recurring actions."""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, uuid_pk


class SchedulerEntry(Base, TimestampMixin):
    __tablename__ = "scheduler_entries"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(24), nullable=False)  # stream_start|stream_stop|backup|scan
    target_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)  # job id / source id (action-specific)
    schedule_type: Mapped[str] = mapped_column(String(12), default="interval", nullable=False)  # once|interval|daily
    run_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    interval_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    daily_time: Mapped[str | None] = mapped_column(String(5), nullable=True)  # "HH:MM" (UTC)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    next_run_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    last_run_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_status: Mapped[str | None] = mapped_column(String(256), nullable=True)
