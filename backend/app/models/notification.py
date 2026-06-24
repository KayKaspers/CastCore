"""Notification channel model. Connection secrets are encrypted at rest."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, uuid_pk


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    channel: Mapped[str] = mapped_column(String(16), nullable=False)  # webhook|discord|slack|gotify|telegram|email
    events: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # non-secret display fields
    secret: Mapped[str | None] = mapped_column(String(4096), nullable=True)  # encrypted JSON of connection params
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
