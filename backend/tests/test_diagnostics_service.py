"""Tests for the diagnostics engine (Stream Health Assistant)."""

from __future__ import annotations

import json

import pytest

from app.core import ffmpeg_inspect
from app.core.security import encrypt_secret
from app.services import diagnostics_service as ds

V1 = "/api/v1"


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    ds._preflight_cache.clear()
    ds._readiness_cache.clear()

    async def safe_info():
        return {"ffmpeg_vulnerable": False, "ffmpeg_version": "8.1.2", "min_version": "8.1.2"}

    monkeypatch.setattr(ffmpeg_inspect, "get_info", safe_info)


async def _job(db, *, state="running", speed=1.0, reconnects=0, dropped=0, key="SECRET_KEY_321"):
    from app.models.streaming import Destination, Output, ProcessStatus, StreamJob
    job = StreamJob(name="diag-job", type="single", status="running")
    out = Output(format="flv", output_opts={}, enabled=True)
    out.destination = Destination(name="d", kind="rtmp", url="rtmp://x/app",
                                  stream_key=encrypt_secret(key), enabled=True)
    out.status = ProcessStatus(state=state, speed=speed, fps=30.0, bitrate_kbps=6000.0,
                               reconnect_count=reconnects, dropped_frames=dropped)
    job.outputs = [out]
    db.add(job)
    await db.commit()
    return job


def _codes(result):
    return [d["code"] for d in result["diagnoses"]]


async def test_healthy_stream_has_no_critical(db):
    job = await _job(db, state="running", speed=1.0)
    result = await ds.diagnose_job(db, job)
    assert not any(d["severity"] == "critical" for d in result["diagnoses"])


async def test_encoding_speed_critical_diagnosis(db):
    job = await _job(db, speed=0.7)
    result = await ds.diagnose_job(db, job)
    d = next(d for d in result["diagnoses"] if d["code"] == "encoding_speed_critical")
    assert d["category"] == "performance" and d["severity"] == "critical"
    assert d["docs_url"].endswith("performance.md")


async def test_reconnects_diagnosis_network(db):
    job = await _job(db, reconnects=2)
    d = next(d for d in (await ds.diagnose_job(db, job))["diagnoses"] if d["code"] == "reconnects")
    assert d["category"] == "network"


async def test_failed_output_process_crashed(db):
    job = await _job(db, state="failed")
    result = await ds.diagnose_job(db, job)
    d = next(d for d in result["diagnoses"] if d["code"] == "process_crashed")
    assert d["severity"] == "critical" and d["affected_output_id"]


async def test_vulnerable_ffmpeg_security_diagnosis(db, monkeypatch):
    async def vuln():
        return {"ffmpeg_vulnerable": True, "ffmpeg_version": "7.1.5", "min_version": "8.1.2"}
    monkeypatch.setattr(ffmpeg_inspect, "get_info", vuln)
    job = await _job(db)
    d = next(d for d in (await ds.diagnose_job(db, job))["diagnoses"] if d["code"] == "ffmpeg_vulnerable")
    assert d["category"] == "security"


async def test_risky_codec_from_cached_preflight(db):
    job = await _job(db)
    ds.cache_preflight(str(job.id), {"level": "red", "checks": [
        {"key": "risky_codec", "level": "error", "detail": "magicyuv"}]})
    d = next(d for d in (await ds.diagnose_job(db, job))["diagnoses"] if d["code"] == "risky_codec")
    assert d["category"] == "security" and d["confidence"] == "medium"


async def test_missing_input_from_cached_preflight(db):
    job = await _job(db)
    ds.cache_preflight(str(job.id), {"level": "red", "checks": [
        {"key": "source_readable", "level": "error", "detail": "ffprobe failed"}]})
    assert "input_unreachable" in _codes(await ds.diagnose_job(db, job))


async def test_platform_token_and_scope_from_cached_readiness(db):
    job = await _job(db)
    ds.cache_readiness(str(job.id), "twitch", {"provider": "twitch", "level": "red", "checks": [
        {"key": "token", "level": "error", "code": "platform.token_expired"},
        {"key": "scopes", "level": "error", "code": "platform.missing_scope"}]})
    codes = _codes(await ds.diagnose_job(db, job))
    assert "platform_token_invalid" in codes and "platform_missing_scope" in codes


async def test_youtube_no_broadcast_from_cached_readiness(db):
    job = await _job(db)
    ds.cache_readiness(str(job.id), "youtube", {"provider": "youtube", "level": "yellow", "checks": [
        {"key": "broadcast", "level": "warn", "code": "platform.invalid_broadcast"}]})
    assert "platform_no_broadcast" in _codes(await ds.diagnose_job(db, job))


async def test_no_secret_or_token_leak(db):
    job = await _job(db, key="SUPER_SECRET_42")
    ds.cache_readiness(str(job.id), "twitch", {"provider": "twitch", "level": "red", "checks": [
        {"key": "token", "level": "error", "code": "platform.token_expired"}]})
    result = await ds.diagnose_job(db, job)
    blob = json.dumps(result).lower()
    assert "super_secret_42" not in blob and "stream_key" not in blob and "access_token" not in blob


async def test_diagnostics_endpoint(client, db, roles_tokens):
    job = await _job(db, speed=0.7, key="LEAK_TEST_KEY")
    headers = {"authorization": f"Bearer {roles_tokens['tokens']['viewer']}"}
    r = await client.get(f"{V1}/monitoring/jobs/{job.id}/diagnostics", headers=headers)
    assert r.status_code == 200, r.text
    assert any(d["code"] == "encoding_speed_critical" for d in r.json()["diagnoses"])
    assert "leak_test_key" not in r.text.lower() and "stream_key" not in r.text


async def test_diagnostics_summary_endpoint(client, db, roles_tokens):
    await _job(db, state="failed")
    headers = {"authorization": f"Bearer {roles_tokens['tokens']['viewer']}"}
    r = await client.get(f"{V1}/monitoring/diagnostics", headers=headers)
    assert r.status_code == 200 and any(j["critical"] >= 1 for j in r.json())
