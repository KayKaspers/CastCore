"""Tests for platform metadata push (YouTube/Twitch) with mocked platform APIs."""

from __future__ import annotations

import datetime as dt

import httpx

from app.core.security import decrypt_secret, encrypt_secret
from app.services import oauth_service
from app.services.platform.twitch import TwitchAdapter
from app.services.platform.youtube import YouTubeAdapter

V1 = "/api/v1"


def _client(handler):
    return httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://mock")


# --------------------------------------------------------------------------- Twitch adapter

async def test_twitch_push_success():
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/users"):
            return httpx.Response(200, json={"data": [{"id": "123", "display_name": "Streamer"}]})
        if req.url.path.endswith("/games"):
            return httpx.Response(200, json={"data": [{"id": "33214"}]})
        if req.url.path.endswith("/channels"):
            assert req.method == "PATCH"
            return httpx.Response(204)
        return httpx.Response(404)

    async with _client(handler) as http:
        out = await TwitchAdapter().push(
            http, "AT", "cid",
            {"title": "Live now", "category": "Just Chatting", "language": "de", "tags": ["x"]},
        )
    assert out.status == "success"
    assert set(out.applied) >= {"title", "category", "language", "tags"}


async def test_twitch_invalid_category_is_warning():
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/users"):
            return httpx.Response(200, json={"data": [{"id": "123"}]})
        if req.url.path.endswith("/games"):
            return httpx.Response(200, json={"data": []})  # unknown category
        if req.url.path.endswith("/channels"):
            return httpx.Response(204)
        return httpx.Response(404)

    async with _client(handler) as http:
        out = await TwitchAdapter().push(http, "AT", "cid", {"title": "T", "category": "Nope"})
    assert out.status == "warning"
    assert out.warnings[0].code == "platform.invalid_category"
    assert "title" in out.applied and "category" not in out.applied


async def test_twitch_api_error():
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/users"):
            return httpx.Response(200, json={"data": [{"id": "123"}]})
        if req.url.path.endswith("/channels"):
            return httpx.Response(500, json={"error": "boom"})
        return httpx.Response(404)

    async with _client(handler) as http:
        out = await TwitchAdapter().push(http, "AT", "cid", {"title": "T"})
    assert out.status == "error" and out.error.code == "platform.api_error"


async def test_twitch_missing_scope():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "Unauthorized"})

    async with _client(handler) as http:
        out = await TwitchAdapter().push(http, "AT", "cid", {"title": "T"})
    assert out.status == "error" and out.error.code == "platform.missing_scope"


# --------------------------------------------------------------------------- YouTube adapter

def _yt_handler(*, list_status=200, items=None, update_status=200, thumb_status=200):
    def handler(req: httpx.Request) -> httpx.Response:
        if "/upload/" in req.url.path:
            return httpx.Response(thumb_status, json={})
        if req.url.path.endswith("/liveBroadcasts") and req.method == "GET":
            status = req.url.params.get("broadcastStatus")
            data = items if (status == "active" and items is not None) else []
            return httpx.Response(list_status, json={"items": data})
        if req.url.path.endswith("/liveBroadcasts") and req.method == "PUT":
            return httpx.Response(update_status, json={"id": "vid1"})
        return httpx.Response(404)
    return handler


async def test_youtube_push_success():
    items = [{"id": "vid1", "snippet": {"title": "old"}, "status": {"privacyStatus": "private"}}]
    async with _client(_yt_handler(items=items)) as http:
        out = await YouTubeAdapter().push(
            http, "AT", "cid",
            {"title": "New", "description": "Desc", "visibility": "unlisted"},
        )
    assert out.status == "success"
    assert set(out.applied) >= {"title", "description", "visibility"}


async def test_youtube_thumbnail_upload():
    items = [{"id": "vid1", "snippet": {}, "status": {}}]
    async with _client(_yt_handler(items=items, thumb_status=200)) as http:
        out = await YouTubeAdapter().push(
            http, "AT", "cid", {"title": "New"}, thumbnail=(b"\x89PNG", "image/png"),
        )
    assert "thumbnail" in out.applied and out.status == "success"


async def test_youtube_thumbnail_failure_is_warning():
    items = [{"id": "vid1", "snippet": {}, "status": {}}]
    async with _client(_yt_handler(items=items, thumb_status=400)) as http:
        out = await YouTubeAdapter().push(
            http, "AT", "cid", {"title": "New"}, thumbnail=(b"\x89PNG", "image/png"),
        )
    assert out.status == "warning"
    assert out.warnings[0].code == "platform.thumbnail_failed"


async def test_youtube_missing_scope():
    async with _client(_yt_handler(list_status=403)) as http:
        out = await YouTubeAdapter().push(http, "AT", "cid", {"title": "New"})
    assert out.status == "error" and out.error.code == "platform.missing_scope"


async def test_youtube_invalid_broadcast_when_none_live():
    async with _client(_yt_handler(items=[])) as http:
        out = await YouTubeAdapter().push(http, "AT", "cid", {"title": "New"})
    assert out.status == "error" and out.error.code == "platform.invalid_broadcast"


# --------------------------------------------------------------------------- token refresh (DB)

async def test_ensure_access_token_refreshes_when_expired(db, monkeypatch):
    from app.models.platform_account import PlatformAccount

    account = PlatformAccount(
        provider="twitch", account_name="x",
        access_token=encrypt_secret("AT-old"), refresh_token=encrypt_secret("RT-old"),
        token_expires_at=dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=5),
    )
    db.add(account)
    await db.commit()

    async def fake_post_token(token_url, data):
        assert data["grant_type"] == "refresh_token"
        return {"access_token": "AT-new", "refresh_token": "RT-new", "expires_in": 3600}

    monkeypatch.setattr(oauth_service, "_post_token", fake_post_token)
    token = await oauth_service.ensure_access_token(db, account)
    assert token == "AT-new"
    assert decrypt_secret(account.access_token) == "AT-new"


async def test_ensure_access_token_no_refresh_token_raises(db):
    from app.core.errors import CastCoreError
    from app.models.platform_account import PlatformAccount

    account = PlatformAccount(
        provider="twitch", access_token=encrypt_secret("AT"), refresh_token=None,
        token_expires_at=dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=1),
    )
    db.add(account)
    await db.commit()
    try:
        await oauth_service.ensure_access_token(db, account)
        raise AssertionError("expected token_expired")
    except CastCoreError as exc:
        assert exc.code == "platform.token_expired"


# --------------------------------------------------------------------------- API endpoint (no token leak)

async def test_push_endpoint_structured_result_no_token_leak(client, db, roles_tokens, monkeypatch):
    from app.models.platform_account import PlatformAccount
    from app.services import platform_push

    # connected Twitch account with a non-expiring token
    db.add(PlatformAccount(
        provider="twitch", account_name="x",
        access_token=encrypt_secret("AT-secret"), refresh_token=encrypt_secret("RT"),
        token_expires_at=None,
    ))
    await db.commit()

    # a stream job
    op = {"authorization": f"Bearer {roles_tokens['tokens']['operator']}"}
    r = await client.post(f"{V1}/stream-jobs", headers=op, json={
        "name": "push-job",
        "inputs": [{"kind": "file", "uri": "/data/media/clip.mp4"}],
        "outputs": [{"format": "flv"}],
    })
    assert r.status_code == 201, r.text
    job_id = r.json()["id"]

    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/users"):
            return httpx.Response(200, json={"data": [{"id": "123"}]})
        if req.url.path.endswith("/channels"):
            return httpx.Response(204)
        return httpx.Response(404)

    monkeypatch.setattr(platform_push, "_client", lambda: _client(handler))

    r = await client.post(f"{V1}/stream-jobs/{job_id}/platforms/twitch/push-metadata", headers=op)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["provider"] == "twitch" and body["status"] == "success"
    assert "title" in body["applied"]
    # no token material anywhere in the response
    blob = r.text.lower()
    assert "at-secret" not in blob and "access_token" not in blob and "refresh_token" not in blob


async def test_push_endpoint_not_connected(client, roles_tokens):
    op = {"authorization": f"Bearer {roles_tokens['tokens']['operator']}"}
    r = await client.post(f"{V1}/stream-jobs", headers=op, json={
        "name": "nc-job",
        "inputs": [{"kind": "file", "uri": "/x.mp4"}],
        "outputs": [{"format": "flv"}],
    })
    job_id = r.json()["id"]
    r = await client.post(f"{V1}/stream-jobs/{job_id}/platforms/youtube/push-metadata", headers=op)
    assert r.status_code == 200
    assert r.json()["status"] == "error"
    assert r.json()["error"]["code"] == "platform.not_connected"
