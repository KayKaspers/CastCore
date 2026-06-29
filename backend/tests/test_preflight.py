"""Tests for Preflight 2.0: structured checks, persistence, start gate, integration.

ffprobe and the FFmpeg version probe are mocked so the suite is hermetic and does not depend
on an ffmpeg binary being present in the CI runner (matching the project's testing convention).
"""

from __future__ import annotations

import datetime as dt

import pytest

from app.core import ffmpeg_inspect
from app.core.security import encrypt_secret
from app.services import preflight_service

V1 = "/api/v1"


def _probe_data(*, video=True, audio=True, codec="h264"):
    streams = []
    if video:
        streams.append({"codec_type": "video", "codec_name": codec})
    if audio:
        streams.append({"codec_type": "audio", "codec_name": "aac"})
    return {"streams": streams, "format": {}}


@pytest.fixture(autouse=True)
def _safe_ffmpeg(monkeypatch):
    """Default: a healthy, non-vulnerable FFmpeg and a readable A/V source."""
    async def safe_info():
        return {"ffmpeg_vulnerable": False, "ffmpeg_version": "8.1.2", "min_version": "8.1.2"}

    async def ok_probe(inp):
        return _probe_data(), None

    monkeypatch.setattr(ffmpeg_inspect, "get_info", safe_info)
    monkeypatch.setattr(preflight_service, "_ffprobe", ok_probe)


def _set_probe(monkeypatch, *, data=None, err=None):
    async def fake(inp):
        return data, err
    monkeypatch.setattr(preflight_service, "_ffprobe", fake)


async def _job(db, *, with_input=True, with_output=True, dest_kind="rtmp",
               dest_url="rtmp://live/app", key="STREAMKEY_SECRET", recording=False):
    from app.models.streaming import Destination, Input, Output, StreamJob
    job = StreamJob(name="pf-job", type="single", status="stopped", recording_enabled=recording)
    job.inputs = [Input(kind="url", uri="srt://src", options={}, order=0)] if with_input else []
    outs = []
    if with_output:
        out = Output(format="flv", output_opts={}, enabled=True)
        out.destination = Destination(name="d", kind=dest_kind, url=dest_url,
                                      stream_key=encrypt_secret(key) if key else None, enabled=True)
        outs.append(out)
    job.outputs = outs
    db.add(job)
    await db.commit()
    return job


def _codes(report):
    return {c["code"]: c["level"] for c in report["checks"]}


# ---- service-level ----------------------------------------------------------------------

async def test_preflight_green_with_readable_source(db):
    job = await _job(db)
    report = await preflight_service.run_preflight(db, job)
    out = preflight_service.to_out(report)
    codes = _codes(out)
    assert codes.get("source_readable") == "ok" and codes.get("has_video") == "ok"
    assert out["level"] == "green"
    assert out["can_start"] is True


async def test_preflight_red_missing_source(db, monkeypatch):
    _set_probe(monkeypatch, data=None, err="ffprobe failed")
    job = await _job(db)
    out = preflight_service.to_out(await preflight_service.run_preflight(db, job))
    assert out["level"] == "red" and out["can_start"] is False
    assert any(c["code"] == "source_readable" and c["level"] == "error" and c["blocking"]
               for c in out["blocking_errors"])


async def test_preflight_no_video_is_blocking(db, monkeypatch):
    _set_probe(monkeypatch, data=_probe_data(video=False), err=None)
    job = await _job(db)
    out = preflight_service.to_out(await preflight_service.run_preflight(db, job))
    assert _codes(out).get("has_video") == "error" and out["can_start"] is False


async def test_preflight_no_output(db):
    job = await _job(db, with_output=False)
    out = preflight_service.to_out(await preflight_service.run_preflight(db, job))
    assert any(c["code"] == "output_enabled" and c["level"] == "error" for c in out["checks"])
    assert out["can_start"] is False


async def test_preflight_unwritable_output_path(db):
    job = await _job(db, dest_kind="recording", dest_url="/nonexistent-dir-xyz/out.ts", key=None)
    out = preflight_service.to_out(await preflight_service.run_preflight(db, job))
    assert any(c["code"] == "output_writable" and c["level"] == "error" for c in out["checks"])


async def test_preflight_never_leaks_stream_key(db):
    job = await _job(db, key="TOP_SECRET_KEY_9")
    report = await preflight_service.run_preflight(db, job)
    import json
    blob = json.dumps(preflight_service.to_out(report), default=str).lower()
    assert "top_secret_key_9" not in blob and "stream_key" not in blob


async def test_persisted_report_and_stale(db):
    job = await _job(db)
    await preflight_service.run_preflight(db, job)
    latest = await preflight_service.get_latest(db, job.id)
    assert latest is not None
    # an old report is stale (is_stale reads the TTL from settings, default 600s)
    latest.created_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
    assert preflight_service.is_stale(latest) is True


# ---- start gate -------------------------------------------------------------------------

@pytest.fixture
def op_headers(roles_tokens):
    return {"authorization": f"Bearer {roles_tokens['tokens']['operator']}"}


async def _api_job(client, headers):
    r = await client.post(f"{V1}/ffmpeg-profiles", headers=headers, json={"name": "p", "copy_mode": True})
    profile_id = r.json()["id"]
    r = await client.post(f"{V1}/destinations", headers=headers,
                          json={"name": "d", "kind": "rtmp", "url": "rtmp://x/app", "stream_key": "k"})
    dest_id = r.json()["id"]
    r = await client.post(f"{V1}/stream-jobs", headers=headers, json={
        "name": "gate-job", "ffmpeg_profile_id": profile_id,
        "inputs": [{"kind": "url", "uri": "srt://src", "options": {}}],
        "outputs": [{"format": "flv", "destination_id": dest_id}],
    })
    return r.json()["id"]


async def test_start_blocked_on_red_preflight(client, op_headers, monkeypatch):
    from app.core import config
    _set_probe(monkeypatch, data=None, err="ffprobe failed")  # -> red, can_start False
    job_id = await _api_job(client, op_headers)
    r = await client.post(f"{V1}/stream-jobs/{job_id}/preflight", headers=op_headers)
    assert r.json()["level"] == "red" and r.json()["can_start"] is False

    s = config.get_settings()
    monkeypatch.setattr(s, "preflight_block_on_red", True, raising=False)
    r = await client.post(f"{V1}/stream-jobs/{job_id}/start", headers=op_headers)
    assert r.status_code == 409 and r.json()["detail"]["error"]["code"] == "preflight.blocked"


async def test_start_required_without_report(client, op_headers, monkeypatch):
    from app.core import config
    job_id = await _api_job(client, op_headers)
    s = config.get_settings()
    monkeypatch.setattr(s, "preflight_required_before_start", True, raising=False)
    r = await client.post(f"{V1}/stream-jobs/{job_id}/start", headers=op_headers)
    assert r.status_code == 409 and r.json()["detail"]["error"]["code"] == "preflight.required"


async def test_preflight_latest_endpoint(client, op_headers):
    job_id = await _api_job(client, op_headers)
    await client.post(f"{V1}/stream-jobs/{job_id}/preflight", headers=op_headers)
    r = await client.get(f"{V1}/stream-jobs/{job_id}/preflight/latest", headers=op_headers)
    assert r.status_code == 200 and r.json()["stream_job_id"] == job_id
    r = await client.get(f"{V1}/stream-jobs/{job_id}/preflight/reports", headers=op_headers)
    assert r.status_code == 200 and len(r.json()) >= 1
