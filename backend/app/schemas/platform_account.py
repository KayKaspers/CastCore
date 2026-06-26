"""Linked platform account schemas (tokens are never serialized)."""

from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel


class PlatformAccountOut(BaseModel):
    id: uuid.UUID
    provider: str
    account_name: str | None = None
    scope: str | None = None
    token_expires_at: dt.datetime | None = None
    has_refresh: bool = False
    created_at: dt.datetime


def account_to_out(a) -> PlatformAccountOut:
    return PlatformAccountOut(
        id=a.id,
        provider=a.provider,
        account_name=a.account_name,
        scope=a.scope,
        token_expires_at=a.token_expires_at,
        has_refresh=a.refresh_token is not None,
        created_at=a.created_at,
    )


class ProviderInfo(BaseModel):
    provider: str
    enabled: bool


class AuthorizeUrlOut(BaseModel):
    authorize_url: str
