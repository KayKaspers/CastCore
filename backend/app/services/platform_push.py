"""Orchestrates platform metadata push: account lookup, token refresh, adapter call.

Keeps platform logic OUT of the stream service. Selects the connected ``PlatformAccount`` for
a provider, ensures a valid (refreshed) access token, resolves the job's metadata, then hands
off to the provider adapter. Returns a uniform, translatable result. Tokens are never logged
or returned.
"""

from __future__ import annotations

from pathlib import Path

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import CastCoreError, ErrorCode
from app.models.asset import Asset
from app.models.platform import PlatformMetadata
from app.models.platform_account import PlatformAccount
from app.models.streaming import StreamJob
from app.services import metadata_service, oauth_service
from app.services.platform import ADAPTERS

_TIMEOUT = 15.0


def _client() -> httpx.AsyncClient:
    """HTTP client used for platform API calls (overridden in tests with a MockTransport)."""
    return httpx.AsyncClient(timeout=_TIMEOUT)


async def _connected_account(db: AsyncSession, provider: str) -> PlatformAccount | None:
    res = await db.execute(
        select(PlatformAccount).where(PlatformAccount.provider == provider)
        .order_by(PlatformAccount.created_at.desc())
    )
    return res.scalars().first()


async def _thumbnail(db: AsyncSession, meta: PlatformMetadata) -> tuple[bytes, str] | None:
    if not meta.thumbnail_asset_id:
        return None
    asset = await db.get(Asset, meta.thumbnail_asset_id)
    if asset is None:
        return None
    try:
        return Path(asset.path).read_bytes(), asset.mime
    except OSError:
        return None


async def push_metadata(db: AsyncSession, job: StreamJob, provider: str) -> dict:
    """Push the job's metadata for ``provider`` to the platform. Returns a structured result."""
    if provider not in ADAPTERS:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"provider": "unknown"}, http_status=404)

    def result(status: str, applied=None, warnings=None, error=None) -> dict:
        return {"provider": provider, "status": status, "applied": applied or [],
                "warnings": warnings or [], "error": error}

    account = await _connected_account(db, provider)
    if account is None:
        return result("error", error={"code": ErrorCode.PLATFORM_NOT_CONNECTED, "params": {"provider": provider}})

    try:
        access = await oauth_service.ensure_access_token(db, account)
    except CastCoreError as exc:
        return result("error", error={"code": exc.code, "params": exc.params})

    # resolve metadata (use a stored row if present, else a transient title=job.name)
    res = await db.execute(
        select(PlatformMetadata).where(
            PlatformMetadata.stream_job_id == job.id, PlatformMetadata.platform == provider
        )
    )
    meta_row = res.scalar_one_or_none() or PlatformMetadata(stream_job_id=job.id, platform=provider)
    resolved = await metadata_service.resolve_metadata(db, job, meta_row)
    thumb = await _thumbnail(db, meta_row)
    client_id = oauth_service.provider_credentials(provider)[0]

    adapter = ADAPTERS[provider]
    try:
        async with _client() as http:
            outcome = await adapter.push(http, access, client_id, resolved, thumbnail=thumb)
    except httpx.HTTPError:
        return result("error", error={"code": ErrorCode.PLATFORM_API_ERROR, "params": {"provider": provider}})

    return result(
        outcome.status,
        applied=outcome.applied,
        warnings=[w.as_dict() for w in outcome.warnings],
        error=outcome.error.as_dict() if outcome.error else None,
    )
