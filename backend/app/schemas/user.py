"""User / role schemas."""

from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr | None = None
    language: str = Field(default="de", pattern="^(de|en)$")


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    roles: list[str] = Field(default_factory=lambda: ["operator"])


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    language: str | None = Field(default=None, pattern="^(de|en)$")
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    roles: list[str] | None = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    roles: list[str] = Field(default_factory=list)
    last_login_at: dt.datetime | None = None
    created_at: dt.datetime


def user_to_out(user) -> UserOut:
    """Serialize an ORM User (mapping Role objects to their names)."""
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        language=user.language,
        is_active=user.is_active,
        roles=user.role_names,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    )
