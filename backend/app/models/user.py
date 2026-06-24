"""User, role, session and API-token models (security core)."""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Table, Column, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, uuid_pk

# Many-to-many: users <-> roles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)  # admin/operator/viewer
    permissions: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    users: Mapped[list["User"]] = relationship(
        secondary=user_roles, back_populates="roles"
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = uuid_pk()
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(5), default="de", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    totp_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)  # encrypted
    last_login_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    roles: Mapped[list[Role]] = relationship(
        secondary=user_roles, back_populates="users", lazy="selectin"
    )
    sessions: Mapped[list["Session"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def role_names(self) -> list[str]:
        return [r.name for r in self.roles]


class Session(Base, TimestampMixin):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    expires_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="sessions")


class ApiToken(Base, TimestampMixin):
    __tablename__ = "api_tokens"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    scopes: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    last_used_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
