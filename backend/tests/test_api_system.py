"""API integration tests: health, readiness and monitoring endpoints."""

from __future__ import annotations

V1 = "/api/v1"


async def test_health_liveness(client):
    r = await client.get(f"{V1}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok" and "version" in r.json()


async def test_system_health_readiness(client):
    r = await client.get(f"{V1}/system/health")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "ok"
    assert "ffmpeg_available" in body and "ffprobe_available" in body


async def test_monitoring_system_requires_auth(client):
    r = await client.get(f"{V1}/monitoring/system")
    assert r.status_code == 401


async def test_monitoring_system_metrics(client, roles_tokens):
    tok = roles_tokens["tokens"]["viewer"]
    r = await client.get(f"{V1}/monitoring/system", headers={"authorization": f"Bearer {tok}"})
    assert r.status_code == 200, r.text
    body = r.json()
    for key in ("cpu_percent", "mem_percent", "disk_percent", "ffmpeg_processes"):
        assert key in body
