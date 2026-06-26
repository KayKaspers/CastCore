"""Tests for the Redis-backed auth rate limiter (no real Redis required)."""

from __future__ import annotations

import pytest

from app.core import ratelimit
from app.core.errors import CastCoreError


class _FakeRedis:
    """Minimal async stand-in for the bits of redis.asyncio the limiter uses."""

    def __init__(self, *, broken: bool = False) -> None:
        self.store: dict[str, int] = {}
        self.ttls: dict[str, int] = {}
        self.broken = broken

    async def incr(self, key: str) -> int:
        if self.broken:
            raise RuntimeError("redis down")
        self.store[key] = self.store.get(key, 0) + 1
        return self.store[key]

    async def expire(self, key: str, seconds: int) -> None:
        self.ttls[key] = seconds

    async def ttl(self, key: str) -> int:
        return self.ttls.get(key, -1)


class _FakeRequest:
    def __init__(self, headers: dict[str, str] | None = None, host: str = "10.0.0.5") -> None:
        self.headers = headers or {}
        self.client = type("C", (), {"host": host})()


def _patch_redis(monkeypatch, fake: _FakeRedis) -> None:
    monkeypatch.setattr(ratelimit, "get_redis", lambda: fake)


async def test_enforce_allows_up_to_limit_then_blocks(monkeypatch):
    _patch_redis(monkeypatch, _FakeRedis())
    # limit=3: first three pass, fourth raises 429
    for _ in range(3):
        await ratelimit.enforce("login", "1.2.3.4", limit=3, window_seconds=60)
    with pytest.raises(CastCoreError) as exc:
        await ratelimit.enforce("login", "1.2.3.4", limit=3, window_seconds=60)
    assert exc.value.status_code == 429
    assert exc.value.code == "auth.rate_limited"
    assert exc.value.params["retry_after"] > 0


async def test_enforce_separates_buckets_and_identities(monkeypatch):
    _patch_redis(monkeypatch, _FakeRedis())
    # different identity and different bucket share no counter
    for _ in range(3):
        await ratelimit.enforce("login", "ip-a", limit=3, window_seconds=60)
    await ratelimit.enforce("login", "ip-b", limit=3, window_seconds=60)  # other IP: fine
    await ratelimit.enforce("refresh", "ip-a", limit=3, window_seconds=60)  # other bucket: fine


async def test_enforce_fails_open_on_redis_error(monkeypatch):
    _patch_redis(monkeypatch, _FakeRedis(broken=True))
    # Redis broken -> must not raise (fail-open), legitimate users keep working
    for _ in range(50):
        await ratelimit.enforce("login", "1.2.3.4", limit=3, window_seconds=60)


async def test_dependency_disabled_by_settings(monkeypatch):
    fake = _FakeRedis()
    _patch_redis(monkeypatch, fake)

    class _S:
        rate_limit_enabled = False
        rate_limit_auth_attempts = 1
        rate_limit_auth_window_seconds = 60

    monkeypatch.setattr(ratelimit, "get_settings", lambda: _S())
    dep = ratelimit.rate_limit("login")
    # disabled -> never touches Redis, never raises
    for _ in range(10):
        await dep(_FakeRequest())
    assert fake.store == {}


async def test_dependency_enforces_when_enabled(monkeypatch):
    fake = _FakeRedis()
    _patch_redis(monkeypatch, fake)

    class _S:
        rate_limit_enabled = True
        rate_limit_auth_attempts = 2
        rate_limit_auth_window_seconds = 60

    monkeypatch.setattr(ratelimit, "get_settings", lambda: _S())
    dep = ratelimit.rate_limit("login")
    req = _FakeRequest(headers={"x-forwarded-for": "9.9.9.9, 10.0.0.1"})
    await dep(req)
    await dep(req)
    with pytest.raises(CastCoreError):
        await dep(req)  # third hit over limit=2


def test_client_identity_prefers_forwarded_for():
    req = _FakeRequest(headers={"x-forwarded-for": "203.0.113.7, 10.0.0.1"}, host="10.0.0.1")
    assert ratelimit.client_identity(req) == "203.0.113.7"
    assert ratelimit.client_identity(_FakeRequest(host="198.51.100.2")) == "198.51.100.2"
