"""Settings and setup-state models."""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import DateTime, ForeignKey, String, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, uuid_pk


class Setting(Base, TimestampMixin):
    __tablename__ = "settings"
    __table_args__ = (UniqueConstraint("key", "user_id", name="uq_setting_key_user"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    scope: Mapped[str] = mapped_column(String(16), default="global", nullable=False)  # global|user
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )


class SetupState(Base, TimestampMixin):
    __tablename__ = "setup_state"

    id: Mapped[uuid.UUID] = uuid_pk()
    step: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)  # pending|done|skipped
    data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    completed_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
