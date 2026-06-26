"""Tests for the platform readiness check (YouTube/Twitch) with mocked platform APIs."""

from __future__ import annotations

import datetime as dt

import httpx

from app.core.security import encrypt_secret
from app.services import oauth_service, platform_readiness
from app.services.platform.twitch import TwitchAdapter
from app.services.platform.youtube import YouTubeAdapter

V1 = "/api/v1"


def _client(handler):
    return httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://mock")


def _levels(checks: list) -> dict:
    return {c.key: c.level for c in checks}


# ------------------------------------------------------------------- Twitch readiness adapter

def _twitch_handler(*, validate_status=200, scopes=("channel:manage:broadcast",), user_id="123",
                    games=None):
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/validate"):
            if validate_status != 200:
                return httpx.Response(validate_status, json={})
            return httpx.Response(200, json={"scopes": list(scopes), "user_id": user_id, "login": "x"})
        if req.url.path.endswith("/games"):
            return httpx.Response(200, json={"data": games if games is not None else []})
        return httpx.Response(404)
    return handler


async def test_twitch_ready():
    async with _client(_twitch_handler(games=[{"id": "1"}])) as http:
        checks = await TwitchAdapter().check_readiness(http, "AT", "cid", {"category": "Just Chatting"})
    lv = _levels(checks)
    assert lv["api"] == "ok" and lv["token"] == "ok" and lv["scopes"] == "ok"
    assert lv["account_info"] == "ok" and lv["category"] == "ok"


async def test_twitch_missing_scope():
    async with _client(_twitch_handler(scopes=())) as http:
        checks = await TwitchAdapter().check_readiness(http, "AT", "cid", {})
    c = next(c for c in checks if c.key == "scopes")
    assert c.level == "error" and c.code == "platform.missing_scope"


async def test_twitch_invalid_category_warns():
    async with _client(_twitch_handler(games=[])) as http:
        checks = await TwitchAdapter().check_readiness(http, "AT", "cid", {"category": "Nope"})
    c = next(c for c in checks if c.key == "category")
    assert c.level == "warn" and c.code == "platform.invalid_category"


async def test_twitch_token_invalid():
    async with _client(_twitch_handler(validate_status=401)) as http:
        checks = await TwitchAdapter().check_readiness(http, "AT", "cid", {})
    c = next(c for c in checks if c.key == "token")
    assert c.level == "error" and c.code == "platform.token_expired"


# ------------------------------------------------------------------ YouTube readiness adapter

def _youtube_handler(*, tokeninfo_status=200, scope="https://www.googleapis.com/auth/youtube",
                     channels=("c1",), broadcasts_active=("b1",)):
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/tokeninfo"):
            if tokeninfo_status != 200:
                return httpx.Response(tokeninfo_status, json={})
            return httpx.Response(200, json={"scope": scope})
        if req.url.path.endswith("/channels"):
            return httpx.Response(200, json={"items": [{"id": c} for c in channels]})
        if req.url.path.endswith("/liveBroadcasts"):
            status = req.url.params.get("broadcastStatus")
            items = [{"id": b, "snippet": {}, "status": {}} for b in broadcasts_active] if status == "active" else []
            return httpx.Response(200, json={"items": items})
        return httpx.Response(404)
    return handler


async def test_youtube_ready():
    async with _client(_youtube_handler()) as http:
        checks = await YouTubeAdapter().check_readiness(http, "AT", "cid", {})
    lv = _levels(checks)
    assert lv["token"] == "ok" and lv["scopes"] == "ok" and lv["account_info"] == "ok"
    assert lv["broadcast"] == "ok"


async def test_youtube_no_broadcast_warns():
    async with _client(_youtube_handler(broadcasts_active=())) as http:
        checks = await YouTubeAdapter().check_readiness(http, "AT", "cid", {})
    c = next(c for c in checks if c.key == "broadcast")
    assert c.level == "warn" and c.code == "platform.invalid_broadcast"


async def test_youtube_missing_scope():
    async with _client(_youtube_handler(scope="https://www.googleapis.com/auth/other")) as http:
        checks = await YouTubeAdapter().check_readiness(http, "AT", "cid", {})
    c = next(c for c in checks if c.key == "scopes")
    assert c.level == "error" and c.code == "platform.missing_scope"


async def test_youtube_token_invalid():
    async with _client(_youtube_handler(tokeninfo_status=400)) as http:
        checks = await YouTubeAdapter().check_readiness(http, "AT", "cid", {})
    c = next(c for c in checks if c.key == "token")
    assert c.level == "error" and c.code == "platform.token_expired"


# --------------------------------------------------------------------- orchestration (DB)

async def _make_job(db, name="ready-job"):
    from app.models.streaming import StreamJob
    job = StreamJob(name=name, type="single", status="stopped")
    # Set relationships explicitly so resolve_metadata does not trigger an async lazy load
    # (a bare added-then-committed object is not selectin-loaded like a queried one).
    job.inputs = []
    job.outputs = []
    job.profile = None
    db.add(job)
    await db.commit()
    return job


async def test_readiness_not_connected(db):
    job = await _make_job(db, "nc")
    result = await platform_readiness.check(db, job, "twitch")
    assert result["level"] == "red"
    c = result["checks"][0]
    assert c["key"] == "account_connected" and c["code"] == "platform.not_connected"


async def test_readiness_youtube_token_refresh(db, monkeypatch):
    from app.models.platform_account import PlatformAccount

    db.add(PlatformAccount(
        provider="youtube", account_name="x",
        access_token=encrypt_secret("AT-old"), refresh_token=encrypt_secret("RT"),
        token_expires_at=dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=5),
    ))
    await db.commit()

    async def fake_post_token(token_url, data):
        return {"access_token": "AT-new", "refresh_token": "RT2", "expires_in": 3600}

    monkeypatch.setattr(oauth_service, "_post_token", fake_post_token)
    monkeypatch.setattr(platform_readiness, "_client", lambda: _client(_youtube_handler()))

    job = await _make_job(db, "yt")
    result = await platform_readiness.check(db, job, "youtube")
    by_key = {c["key"]: c for c in result["checks"]}
    assert by_key["token"]["level"] == "ok"          # token was refreshed successfully
    assert by_key["scopes"]["level"] == "ok"
    assert result["level"] in ("green", "yellow")     # yellow only because the job has no output


async def test_readiness_api_error(db, monkeypatch):
    from app.models.platform_account import PlatformAccount

    db.add(PlatformAccount(
        provider="twitch", access_token=encrypt_secret("AT"), refresh_token=None,
        token_expires_at=None,
    ))
    await db.commit()

    def boom(req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=req)

    monkeypatch.setattr(platform_readiness, "_client", lambda: _client(boom))
    job = await _make_job(db, "err")
    result = await platform_readiness.check(db, job, "twitch")
    assert any(c["key"] == "api" and c["level"] == "error" for c in result["checks"])
    assert result["level"] == "red"


async def test_readiness_endpoint_no_token_leak(client, db, roles_tokens, monkeypatch):
    from app.models.platform_account import PlatformAccount

    db.add(PlatformAccount(
        provider="twitch", account_name="x",
        access_token=encrypt_secret("AT-secret-xyz"), refresh_token=encrypt_secret("RT"),
        token_expires_at=None,
    ))
    await db.commit()

    op = {"authorization": f"Bearer {roles_tokens['tokens']['operator']}"}
    r = await client.post(f"{V1}/stream-jobs", headers=op, json={
        "name": "rdy", "inputs": [{"kind": "file", "uri": "/x.mp4"}], "outputs": [{"format": "flv"}],
    })
    job_id = r.json()["id"]

    monkeypatch.setattr(platform_readiness, "_client", lambda: _client(_twitch_handler(games=[{"id": "1"}])))
    r = await client.post(f"{V1}/stream-jobs/{job_id}/platforms/twitch/readiness", headers=op)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["provider"] == "twitch" and body["level"] in ("green", "yellow", "red")
    assert {c["key"] for c in body["checks"]} >= {"account_connected", "token", "scopes"}
    blob = r.text.lower()
    assert "at-secret-xyz" not in blob and "access_token" not in blob and "refresh_token" not in blob
