"""Platform readiness check: a traffic-light status per provider before going live.

Composes generic checks (account connected, token valid/refreshable, metadata complete,
output configured) with provider-specific probes (API reachable, scopes, account info,
category, broadcast) from the platform adapters. Reuses ``oauth_service.ensure_access_token``
and never logs or returns token material.
"""

from __future__ import annotations

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import CastCoreError, ErrorCode
from app.models.platform import PlatformMetadata
from app.models.streaming import Output, StreamJob
from app.services import metadata_service, oauth_service
from app.services.platform import ADAPTERS
from app.services.platform.base import Check
from app.services.platform_push import _connected_account

_TIMEOUT = 12.0


def _client() -> httpx.AsyncClient:
    """HTTP client for readiness probes (overridden in tests with a MockTransport)."""
    return httpx.AsyncClient(timeout=_TIMEOUT)


def _level(checks: list[Check]) -> str:
    if any(c.level == "error" for c in checks):
        return "red"
    if any(c.level == "warn" for c in checks):
        return "yellow"
    return "green"


async def check(db: AsyncSession, job: StreamJob, provider: str) -> dict:
    """Return ``{provider, level, checks}`` where level is green/yellow/red."""
    if provider not in ADAPTERS:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"provider": "unknown"}, http_status=404)

    checks: list[Check] = []

    account = await _connected_account(db, provider)
    if account is None:
        checks.append(Check("account_connected", "error", ErrorCode.PLATFORM_NOT_CONNECTED, {"provider": provider}))
        return {"provider": provider, "level": "red", "checks": [c.as_dict() for c in checks]}
    checks.append(Check("account_connected", "ok"))

    try:
        access = await oauth_service.ensure_access_token(db, account)
    except CastCoreError as exc:
        checks.append(Check("token", "error", exc.code, exc.params))
        return {"provider": provider, "level": "red", "checks": [c.as_dict() for c in checks]}

    # metadata completeness
    res = await db.execute(
        select(PlatformMetadata).where(
            PlatformMetadata.stream_job_id == job.id, PlatformMetadata.platform == provider
        )
    )
    meta_row = res.scalar_one_or_none() or PlatformMetadata(stream_job_id=job.id, platform=provider)
    resolved = await metadata_service.resolve_metadata(db, job, meta_row)
    checks.append(
        Check("metadata", "ok") if resolved.get("title")
        else Check("metadata", "warn", ErrorCode.PLATFORM_METADATA_INCOMPLETE, {"provider": provider})
    )

    # output / stream-key configured (at least one enabled output with a destination URL).
    # Query explicitly so we don't trigger a lazy load on job.outputs in async context.
    ores = await db.execute(select(Output).where(Output.job_id == job.id, Output.enabled.is_(True)))
    has_output = any(o.destination is not None and o.destination.url for o in ores.scalars().all())
    checks.append(
        Check("output", "ok") if has_output
        else Check("output", "warn", ErrorCode.PLATFORM_OUTPUT_MISSING, {"provider": provider})
    )

    # provider-specific probes
    client_id = oauth_service.provider_credentials(provider)[0]
    try:
        async with _client() as http:
            checks += await ADAPTERS[provider].check_readiness(http, access, client_id, resolved)
    except httpx.HTTPError:
        checks.append(Check("api", "error", ErrorCode.PLATFORM_API_ERROR, {"provider": provider}))

    return {"provider": provider, "level": _level(checks), "checks": [c.as_dict() for c in checks]}
