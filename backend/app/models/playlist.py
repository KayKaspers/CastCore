"""Playlist models — ordered lists of media items (basis for linear channels)."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, uuid_pk


class Playlist(Base, TimestampMixin):
    __tablename__ = "playlists"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    mode: Mapped[str] = mapped_column(String(16), default="sequential", nullable=False)  # sequential|shuffle|loop
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)

    items: Mapped[list["PlaylistItem"]] = relationship(
        back_populates="playlist", cascade="all, delete-orphan",
        lazy="selectin", order_by="PlaylistItem.order",
    )


class PlaylistItem(Base, TimestampMixin):
    __tablename__ = "playlist_items"

    id: Mapped[uuid.UUID] = uuid_pk()
    playlist_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    media_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("media_library_items.id", ondelete="CASCADE"), nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    playlist: Mapped[Playlist] = relationship(back_populates="items")
