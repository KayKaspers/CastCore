"""API integration tests: RBAC (admin/operator/viewer) and protected-route access."""

from __future__ import annotations

V1 = "/api/v1"


async def test_protected_route_requires_token(client):
    r = await client.get(f"{V1}/auth/me")
    assert r.status_code == 401


async def test_me_returns_current_user(client, roles_tokens):
    tok = roles_tokens["tokens"]["operator"]
    r = await client.get(f"{V1}/auth/me", headers={"authorization": f"Bearer {tok}"})
    assert r.status_code == 200 and r.json()["username"] == "operator_u"


async def test_stream_jobs_requires_operator_role(client, roles_tokens):
    t = roles_tokens["tokens"]
    # viewer is forbidden on the operator-gated stream-jobs router
    r = await client.get(f"{V1}/stream-jobs", headers={"authorization": f"Bearer {t['viewer']}"})
    assert r.status_code == 403
    # operator and admin are allowed
    for role in ("operator", "admin"):
        r = await client.get(f"{V1}/stream-jobs", headers={"authorization": f"Bearer {t[role]}"})
        assert r.status_code == 200, (role, r.text)


async def test_users_admin_only(client, roles_tokens):
    t = roles_tokens["tokens"]
    r = await client.get(f"{V1}/users", headers={"authorization": f"Bearer {t['operator']}"})
    assert r.status_code == 403
    r = await client.get(f"{V1}/users", headers={"authorization": f"Bearer {t['admin']}"})
    assert r.status_code == 200


async def test_inactive_user_token_rejected(client, user_factory, mint):
    user = await user_factory("frozen", "operator", active=False)
    r = await client.get(f"{V1}/auth/me", headers={"authorization": f"Bearer {mint(user)}"})
    assert r.status_code == 403
