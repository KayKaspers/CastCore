"""Platform OAuth: authorization-URL building, code exchange, token refresh.

Provider-agnostic with a small registry (YouTube/Twitch). Client credentials come from the
environment; a provider is "enabled" only when its client id is configured. The OAuth
``state`` is a short-lived signed token carrying the initiating user — the callback is a
browser redirect without an auth header, so state must be self-describing.

All outbound provider HTTP goes through :func:`_post_token` / :func:`fetch_account_name`,
which are deliberately thin so tests can stub the external boundary.
"""

from __future__ import annotations

import datetime as dt
import uuid
from urllib.parse import urlencode

import httpx
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import CastCoreError, ErrorCode
from app.core.security import decrypt_secret, encrypt_secret
from app.models.platform_account import PlatformAccount

_TIMEOUT = 10.0
_STATE_TTL_MINUTES = 10


# Static per-provider endpoints, default scopes and extra authorize params.
PROVIDERS: dict[str, dict] = {
    "youtube": {
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": ["https://www.googleapis.com/auth/youtube"],
        "authorize_params": {"access_type": "offline", "prompt": "consent"},
    },
    "twitch": {
        "authorize_url": "https://id.twitch.tv/oauth2/authorize",
        "token_url": "https://id.twitch.tv/oauth2/token",
        "scopes": ["channel:manage:broadcast"],
        "authorize_params": {},
    },
}


def _require_provider(provider: str) -> dict:
    cfg = PROVIDERS.get(provider)
    if cfg is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"provider": "unknown"}, http_status=404)
    return cfg


def provider_credentials(provider: str) -> tuple[str, str]:
    s = get_settings()
    return {
        "youtube": (s.youtube_client_id, s.youtube_client_secret),
        "twitch": (s.twitch_client_id, s.twitch_client_secret),
    }[provider]


def is_enabled(provider: str) -> bool:
    if provider not in PROVIDERS or not get_settings().public_base_url:
        return False
    return bool(provider_credentials(provider)[0])


def enabled_providers() -> list[str]:
    return [p for p in PROVIDERS if is_enabled(p)]


def redirect_uri(provider: str) -> str:
    base = get_settings().public_base_url.rstrip("/")
    return f"{base}/api/v1/oauth/{provider}/callback"


def build_state(user_id: uuid.UUID, provider: str) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": str(user_id),
        "provider": provider,
        "type": "oauth_state",
        "nonce": uuid.uuid4().hex,
        "iat": now,
        "exp": now + dt.timedelta(minutes=_STATE_TTL_MINUTES),
    }
    return jwt.encode(payload, get_settings().secret_key, algorithm="HS256")


def verify_state(state: str, provider: str) -> uuid.UUID:
    try:
        payload = jwt.decode(state, get_settings().secret_key, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise CastCoreError(ErrorCode.AUTH_FORBIDDEN, http_status=400) from exc
    if payload.get("type") != "oauth_state" or payload.get("provider") != provider:
        raise CastCoreError(ErrorCode.AUTH_FORBIDDEN, http_status=400)
    try:
        return uuid.UUID(str(payload.get("sub")))
    except (ValueError, TypeError) as exc:
        raise CastCoreError(ErrorCode.AUTH_FORBIDDEN, http_status=400) from exc


def build_authorize_url(provider: str, state: str) -> str:
    cfg = _require_provider(provider)
    if not is_enabled(provider):
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"provider": "disabled"}, http_status=400)
    client_id, _ = provider_credentials(provider)
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri(provider),
        "response_type": "code",
        "scope": " ".join(cfg["scopes"]),
        "state": state,
        **cfg["authorize_params"],
    }
    return f"{cfg['authorize_url']}?{urlencode(params)}"


async def _post_token(token_url: str, data: dict) -> dict:
    """POST to a provider token endpoint. Isolated so tests can stub the boundary."""
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        res = await client.post(token_url, data=data)
        res.raise_for_status()
        return res.json()


async def fetch_account_name(provider: str, access_token: str) -> str | None:
    """Best-effort display name for the linked account; None on any failure."""
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            if provider == "twitch":
                client_id, _ = provider_credentials("twitch")
                res = await client.get(
                    "https://api.twitch.tv/helix/users",
                    headers={"Authorization": f"Bearer {access_token}", "Client-Id": client_id},
                )
                res.raise_for_status()
                items = res.json().get("data") or []
                return items[0].get("display_name") if items else None
            if provider == "youtube":
                res = await client.get(
                    "https://www.googleapis.com/youtube/v3/channels",
                    params={"part": "snippet", "mine": "true"},
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                res.raise_for_status()
                items = res.json().get("items") or []
                return items[0]["snippet"]["title"] if items else None
    except (httpx.HTTPError, KeyError, IndexError, ValueError):
        return None
    return None


def _expires_at(token: dict) -> dt.datetime | None:
    secs = token.get("expires_in")
    if not secs:
        return None
    return dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=int(secs))


async def exchange_code(db: AsyncSession, provider: str, code: str, user_id: uuid.UUID) -> PlatformAccount:
    """Exchange an authorization code for tokens and persist a linked account."""
    cfg = _require_provider(provider)
    client_id, client_secret = provider_credentials(provider)
    token = await _post_token(cfg["token_url"], {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri(provider),
    })
    access = token["access_token"]
    name = await fetch_account_name(provider, access)
    account = PlatformAccount(
        provider=provider,
        account_name=name,
        scope=token.get("scope") if isinstance(token.get("scope"), str) else " ".join(token.get("scope") or []),
        access_token=encrypt_secret(access),
        refresh_token=encrypt_secret(token["refresh_token"]) if token.get("refresh_token") else None,
        token_expires_at=_expires_at(token),
        created_by=user_id,
    )
    db.add(account)
    await db.flush()
    return account


async def refresh_account(db: AsyncSession, account: PlatformAccount) -> PlatformAccount:
    """Use the stored refresh token to obtain a fresh access token."""
    cfg = _require_provider(account.provider)
    if not account.refresh_token:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"refresh_token": "missing"}, http_status=400)
    client_id, client_secret = provider_credentials(account.provider)
    token = await _post_token(cfg["token_url"], {
        "grant_type": "refresh_token",
        "refresh_token": decrypt_secret(account.refresh_token),
        "client_id": client_id,
        "client_secret": client_secret,
    })
    account.access_token = encrypt_secret(token["access_token"])
    if token.get("refresh_token"):
        account.refresh_token = encrypt_secret(token["refresh_token"])
    account.token_expires_at = _expires_at(token)
    await db.flush()
    return account
