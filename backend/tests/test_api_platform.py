"""API integration tests: OAuth providers and linked platform-account status.

The external provider HTTP boundary is mocked; everything CastCore-side (token exchange,
encryption, account status over the API) is exercised for real.
"""

from __future__ import annotations

import pytest

from app.services import oauth_service

V1 = "/api/v1"


@pytest.fixture
def op_headers(roles_tokens):
    return {"authorization": f"Bearer {roles_tokens['tokens']['operator']}"}


async def test_oauth_providers_listed_and_disabled_without_creds(client, op_headers):
    r = await client.get(f"{V1}/oauth/providers", headers=op_headers)
    assert r.status_code == 200, r.text
    providers = {p["provider"]: p["enabled"] for p in r.json()}
    assert set(providers) == {"youtube", "twitch"}
    # no client id / PUBLIC_BASE_URL configured in tests -> all disabled
    assert providers["youtube"] is False and providers["twitch"] is False


async def test_authorize_rejected_when_provider_disabled(client, op_headers):
    r = await client.post(f"{V1}/oauth/twitch/authorize", headers=op_headers)
    assert r.status_code == 400  # disabled (no creds)
    r = await client.post(f"{V1}/oauth/unknownprovider/authorize", headers=op_headers)
    assert r.status_code == 404


async def test_platform_accounts_empty_then_linked(client, op_headers, db, roles_tokens, monkeypatch):
    # initially none
    r = await client.get(f"{V1}/platform-accounts", headers=op_headers)
    assert r.status_code == 200 and r.json() == []

    # mock the provider boundary and exchange a code as the operator user
    async def fake_post_token(token_url, data):
        return {"access_token": "AT-1", "refresh_token": "RT-1", "expires_in": 3600,
                "scope": "channel:manage:broadcast"}

    async def fake_name(provider, access_token):
        return "CoolStreamer"

    monkeypatch.setattr(oauth_service, "_post_token", fake_post_token)
    monkeypatch.setattr(oauth_service, "fetch_account_name", fake_name)

    user_id = roles_tokens["users"]["operator"].id
    account = await oauth_service.exchange_code(db, "twitch", "auth-code", user_id)
    await db.commit()

    # status is visible over the API, tokens are never serialized
    r = await client.get(f"{V1}/platform-accounts", headers=op_headers)
    assert r.status_code == 200, r.text
    items = r.json()
    assert len(items) == 1
    item = items[0]
    assert item["provider"] == "twitch" and item["account_name"] == "CoolStreamer"
    assert item["has_refresh"] is True
    assert "access_token" not in item and "refresh_token" not in item

    # stored tokens are encrypted at rest (not the plaintext)
    assert account.access_token != "AT-1"

    # disconnect
    r = await client.delete(f"{V1}/platform-accounts/{item['id']}", headers=op_headers)
    assert r.status_code == 204
    r = await client.get(f"{V1}/platform-accounts", headers=op_headers)
    assert r.json() == []
