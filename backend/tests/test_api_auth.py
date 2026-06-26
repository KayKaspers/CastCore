"""API integration tests: setup, login/refresh/logout, 2FA, API tokens."""

from __future__ import annotations

from app.core import totp

V1 = "/api/v1"


async def test_setup_state(client):
    r = await client.get(f"{V1}/setup/state")
    assert r.status_code == 200, r.text
    body = r.json()
    assert "completed" in body and isinstance(body["steps"], list)
    assert any(s["step"] == "admin" for s in body["steps"])


async def test_setup_admin_bootstrap_then_conflict(client):
    payload = {"username": "rootadmin", "password": "Sup3r!Secret", "language": "de"}
    r = await client.post(f"{V1}/setup/admin", json=payload)
    assert r.status_code == 201, r.text
    assert r.json()["username"] == "rootadmin"
    # a second bootstrap is rejected once a user exists
    r2 = await client.post(f"{V1}/setup/admin", json=payload)
    assert r2.status_code == 409


async def test_login_refresh_logout(client, user_factory):
    await user_factory("alice", "operator", password="Pa55!word")

    r = await client.post(f"{V1}/auth/login", json={"username": "alice", "password": "Pa55!word"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["access_token"] and data["refresh_token"]
    assert data["user"]["username"] == "alice"

    r = await client.post(f"{V1}/auth/refresh", json={"refresh_token": data["refresh_token"]})
    assert r.status_code == 200, r.text
    assert r.json()["access_token"]

    access = data["access_token"]
    r = await client.post(f"{V1}/auth/logout", headers={"authorization": f"Bearer {access}"})
    assert r.status_code == 204


async def test_login_wrong_password(client, user_factory):
    await user_factory("bob", "viewer", password="Right!1234")
    r = await client.post(f"{V1}/auth/login", json={"username": "bob", "password": "wrong"})
    assert r.status_code == 401
    assert r.json()["detail"]["error"]["code"] == "auth.invalid_credentials"


async def test_refresh_with_bogus_token_rejected(client):
    r = await client.post(f"{V1}/auth/refresh", json={"refresh_token": "not-a-real-token"})
    assert r.status_code == 401


async def test_2fa_setup_verify_and_login_gate(client, user_factory, mint):
    user = await user_factory("carol", "operator", password="Pa55!word")
    headers = {"authorization": f"Bearer {mint(user)}"}

    r = await client.post(f"{V1}/auth/2fa/setup", headers=headers)
    assert r.status_code == 200, r.text
    secret = r.json()["secret"]
    assert r.json()["otpauth_uri"].startswith("otpauth://totp/CastCore:")

    # wrong code rejected
    r = await client.post(f"{V1}/auth/2fa/verify", headers=headers, json={"code": "000000"})
    assert r.status_code == 400 and r.json()["detail"]["error"]["code"] == "auth.totp_invalid"

    # correct code enables 2FA
    r = await client.post(f"{V1}/auth/2fa/verify", headers=headers, json={"code": totp.now_code(secret)})
    assert r.status_code == 200 and r.json()["enabled"] is True

    # login now requires the code
    r = await client.post(f"{V1}/auth/login", json={"username": "carol", "password": "Pa55!word"})
    assert r.status_code == 401 and r.json()["detail"]["error"]["code"] == "auth.totp_required"

    r = await client.post(
        f"{V1}/auth/login",
        json={"username": "carol", "password": "Pa55!word", "totp_code": totp.now_code(secret)},
    )
    assert r.status_code == 200 and r.json()["user"]["totp_enabled"] is True


async def test_api_token_lifecycle(client, user_factory, mint):
    user = await user_factory("dave", "operator")
    headers = {"authorization": f"Bearer {mint(user)}"}

    r = await client.post(f"{V1}/tokens", headers=headers, json={"name": "ci-bot"})
    assert r.status_code == 201, r.text
    raw = r.json()["token"]
    tok_id = r.json()["id"]
    assert raw.startswith("cc_")

    # list omits the plaintext
    r = await client.get(f"{V1}/tokens", headers=headers)
    assert r.status_code == 200 and "token" not in r.json()[0]

    # the token authenticates as its owner
    r = await client.get(f"{V1}/auth/me", headers={"authorization": f"Bearer {raw}"})
    assert r.status_code == 200 and r.json()["username"] == "dave"

    # revoke -> token stops working
    r = await client.delete(f"{V1}/tokens/{tok_id}", headers=headers)
    assert r.status_code == 204
    r = await client.get(f"{V1}/auth/me", headers={"authorization": f"Bearer {raw}"})
    assert r.status_code == 401
