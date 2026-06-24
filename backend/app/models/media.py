"""Media library models: indexed files and their ffprobe metadata."""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, uuid_pk


class MediaItem(Base, TimestampMixin):
    __tablename__ = "media_library_items"

    id: Mapped[uuid.UUID] = uuid_pk()
    storage_source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("storage_sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rel_path: Mapped[str] = mapped_column(String(2048), nullable=False)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), default="other", nullable=False)  # video|audio|image|other
    size_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    mtime: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    streamable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    problem_flags: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    probe: Mapped["MediaProbe | None"] = relationship(
        back_populates="item", cascade="all, delete-orphan", uselist=False, lazy="selectin"
    )


class MediaProbe(Base, TimestampMixin):
    __tablename__ = "media_probe_data"

    id: Mapped[uuid.UUID] = uuid_pk()
    media_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("media_library_items.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    container: Mapped[str | None] = mapped_column(String(64), nullable=True)
    duration_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    video_codec: Mapped[str | None] = mapped_column(String(32), nullable=True)
    audio_codec: Mapped[str | None] = mapped_column(String(32), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fps: Mapped[float | None] = mapped_column(Float, nullable=True)
    video_bitrate: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    audio_bitrate: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    raw_ffprobe: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    probed_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    item: Mapped[MediaItem] = relationship(back_populates="probe")
