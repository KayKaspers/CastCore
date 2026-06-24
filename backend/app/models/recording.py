"""Recording model — captured stream output files for replay."""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, uuid_pk


class Recording(Base, TimestampMixin):
    __tablename__ = "recordings"

    id: Mapped[uuid.UUID] = uuid_pk()
    stream_job_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("stream_jobs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    output_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)  # synthetic recording output id
    path: Mapped[str] = mapped_column(String(2048), nullable=False)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    state: Mapped[str] = mapped_column(String(16), default="recording", nullable=False)  # recording|completed|failed
    started_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    retention_until: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
