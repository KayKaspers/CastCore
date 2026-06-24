"""Storage-source models: local folders and SMB/CIFS network shares.

Secrets (SMB password) are encrypted at rest (Fernet). The polymorphic root is
``StorageSource``; ``SmbSource`` holds SMB-specific detail. Cloud sources arrive later.
"""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, uuid_pk


class StorageSource(Base, TimestampMixin):
    __tablename__ = "storage_sources"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    source_class: Mapped[str] = mapped_column(String(16), default="local", nullable=False)  # local|network
    type: Mapped[str] = mapped_column(String(16), default="folder", nullable=False)  # folder|smb
    path: Mapped[str | None] = mapped_column(String(2048), nullable=True)  # local base path
    read_only: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    automount: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="offline", nullable=False)  # online|offline|error
    last_error: Mapped[str | None] = mapped_column(String(512), nullable=True)
    last_scan_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    smb: Mapped["SmbSource | None"] = relationship(
        back_populates="storage_source", cascade="all, delete-orphan", uselist=False, lazy="selectin"
    )


class SmbSource(Base, TimestampMixin):
    __tablename__ = "smb_sources"

    id: Mapped[uuid.UUID] = uuid_pk()
    storage_source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("storage_sources.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    server: Mapped[str] = mapped_column(String(255), nullable=False)
    share: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str | None] = mapped_column(String(128), nullable=True)
    username: Mapped[str | None] = mapped_column(String(128), nullable=True)
    password: Mapped[str | None] = mapped_column(String(1024), nullable=True)  # encrypted at rest
    smb_version: Mapped[str | None] = mapped_column(String(8), nullable=True)  # e.g. 3.0
    mount_path: Mapped[str] = mapped_column(String(2048), nullable=False)

    storage_source: Mapped[StorageSource] = relationship(back_populates="smb")
