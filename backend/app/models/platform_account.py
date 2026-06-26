"""Linked platform account — OAuth tokens for a streaming platform (YouTube/Twitch/…).

Access and refresh tokens are stored **encrypted at rest** (Fernet) and never returned by
the API. One row per connected account; CastCore uses the tokens to read/write platform
metadata on the user's behalf.
"""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, uuid_pk


class PlatformAccount(Base, TimestampMixin):
    __tablename__ = "platform_accounts"

    id: Mapped[uuid.UUID] = uuid_pk()
    provider: Mapped[str] = mapped_column(String(24), nullable=False, index=True)  # youtube|twitch
    account_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    scope: Mapped[str | None] = mapped_column(String(512), nullable=True)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)  # encrypted
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)  # encrypted
    token_expires_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
