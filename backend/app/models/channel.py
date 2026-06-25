"""Linear channel model — 24/7 playout from a playlist (Phase 3)."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, uuid_pk


class Channel(Base, TimestampMixin):
    __tablename__ = "channels"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    playlist_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("playlists.id", ondelete="SET NULL"), nullable=True
    )
    ffmpeg_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ffmpeg_profiles.id", ondelete="SET NULL"), nullable=True
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    hls_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    epg_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="stopped", nullable=False)
    output_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)  # current playout process id
