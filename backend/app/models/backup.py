"""Backup artifact model."""

from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, uuid_pk


class Backup(Base, TimestampMixin):
    __tablename__ = "backups"

    id: Mapped[uuid.UUID] = uuid_pk()
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(String(2048), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), default="manual", nullable=False)  # manual|scheduled
    size_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    includes: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="completed", nullable=False)
