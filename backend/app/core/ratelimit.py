"""Redis-backed fixed-window rate limiting for sensitive auth endpoints.

A counter per ``(bucket, client)`` is incremented in Redis and expires after the window.
Once the limit is exceeded, a translatable ``auth.rate_limited`` error (HTTP 429) is raised
with a ``retry_after`` (seconds) and a ``Retry-After`` header.

Design choices:
- **Fail-open**: if Redis is unreachable the limiter does not block requests (a Redis hiccup
  must not lock everyone out). The trade-off is documented in the security guide.
- **Client identity**: the first hop of ``X-Forwarded-For`` (set by the reverse proxy) is
  preferred over the immediate peer, so users behind the proxy are not lumped together.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request

from app.core.config import get_settings
from app.core.errors import CastCoreError, ErrorCode
from app.core.redis import get_redis

_KEY_PREFIX = "castcore:rl:"


def client_identity(request: Request) -> str:
    """Best-effort client IP: first X-Forwarded-For hop, else the immediate peer."""
    xff = request.headers.get("x-forwarded-for")
    if xff:
        first = xff.split(",")[0].strip()
        if first:
            return first
    return request.client.host if request.client else "unknown"


async def enforce(bucket: str, identifier: str, *, limit: int, window_seconds: int) -> None:
    """Increment the counter for ``bucket:identifier``; raise 429 when over ``limit``.

    Fails open on any Redis error.
    """
    key = f"{_KEY_PREFIX}{bucket}:{identifier}"
    try:
        redis = get_redis()
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, window_seconds)
        if count > limit:
            ttl = await redis.ttl(key)
            retry_after = ttl if ttl and ttl > 0 else window_seconds
            raise CastCoreError(
                ErrorCode.AUTH_RATE_LIMITED,
                http_status=429,
                params={"retry_after": retry_after},
                headers={"Retry-After": str(retry_after)},
            )
    except CastCoreError:
        raise
    except Exception as exc:  # noqa: BLE001 - never block legitimate users on Redis errors
        print(f"[ratelimit] fail-open ({bucket}): {exc}")


def rate_limit(bucket: str) -> Callable[[Request], Awaitable[None]]:
    """FastAPI dependency factory enforcing the configured auth limit for ``bucket``."""

    async def _dependency(request: Request) -> None:
        settings = get_settings()
        if not settings.rate_limit_enabled:
            return
        await enforce(
            bucket,
            client_identity(request),
            limit=settings.rate_limit_auth_attempts,
            window_seconds=settings.rate_limit_auth_window_seconds,
        )

    return _dependency
