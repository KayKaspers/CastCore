"""Platform metadata model — per stream-job, per-platform titles/description templates."""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import DateTime, ForeignKey, String, Text, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, uuid_pk


class PlatformMetadata(Base, TimestampMixin):
    __tablename__ = "platform_metadata"
    __table_args__ = (UniqueConstraint("stream_job_id", "platform", name="uq_meta_job_platform"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    stream_job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("stream_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    platform: Mapped[str] = mapped_column(String(24), nullable=False)  # twitch|youtube|kick|facebook|custom
    title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    description_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    language: Mapped[str | None] = mapped_column(String(8), nullable=True)
    visibility: Mapped[str] = mapped_column(String(16), default="public", nullable=False)  # public|unlisted|private
    scheduled_start: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    thumbnail_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("assets.id", ondelete="SET NULL"), nullable=True
    )
