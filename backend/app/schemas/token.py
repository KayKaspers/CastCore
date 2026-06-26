"""Personal access token schemas."""

from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel, ConfigDict, Field


class ApiTokenCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    expires_in_days: int | None = Field(default=None, ge=1, le=3650)


class ApiTokenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    last_used_at: dt.datetime | None = None
    expires_at: dt.datetime | None = None
    created_at: dt.datetime


class ApiTokenCreated(ApiTokenOut):
    """Returned once on creation — carries the plaintext token."""

    token: str
