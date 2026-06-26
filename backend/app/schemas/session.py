"""Auth session (login) schemas."""

from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel, ConfigDict


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_agent: str | None = None
    ip: str | None = None
    created_at: dt.datetime
    expires_at: dt.datetime
    current: bool = False
