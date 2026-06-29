"""Tests for Preflight 2.0: structured checks, persistence, start gate, integration."""

from __future__ import annotations

import datetime as dt

import pytest

from app.core.config import get_settings
from app.core.security import encrypt_secret

V1 = "/api/v1"


async def _job(db, *, with_input=True, uri="/data/media/clip.mp4", with_output=True,
               dest_kind="rtmp", dest_url="rtmp://live/app", key="STREAMKEY_SECRET",
               recording=False):
    from app.models.streaming import Destination, Input, Output, StreamJob
    job = StreamJob(name="pf-job", type="single", status="stopped", recording_enabled=recording)
    job.inputs = [Input(kind="url", uri=uri, options={"f": "lavfi"}, order=0)] if with_input else []
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

async def test_preflight_green_with_lavfi_input(db):
    from app.services import preflight_service
    # lavfi testsrc is a real, readable source with video; rtmp output with a key
    job = await _job(db, uri="testsrc=size=320x240:rate=15")
    report = await preflight_service.run_preflight(db, job)
    out = preflight_service.to_out(report)
    codes = _codes(out)
    assert codes.get("source_readable") == "ok" and codes.get("has_video") == "ok"
    assert out["level"] in ("green", "yellow")  # yellow only from a vulnerable-FFmpeg warning
    assert out["can_start"] is True


async def test_preflight_red_missing_source(db):
    from app.services import preflight_service
    job = await _job(db, uri="/data/media/does-not-exist.mp4")
    out = preflight_service.to_out(await preflight_service.run_preflight(db, job))
    assert out["level"] == "red" and out["can_start"] is False
    assert any(c["code"] == "source_readable" and c["level"] == "error" and c["blocking"]
               for c in out["blocking_errors"])


async def test_preflight_no_output(db):
    from app.services import preflight_service
    job = await _job(db, uri="testsrc=size=320x240:rate=15", with_output=False)
    out = preflight_service.to_out(await preflight_service.run_preflight(db, job))
    assert any(c["code"] == "output_enabled" and c["level"] == "error" for c in out["checks"])
    assert out["can_start"] is False


async def test_preflight_unwritable_output_path(db):
    from app.services import preflight_service
    job = await _job(db, uri="testsrc=size=320x240:rate=15", dest_kind="recording",
                     dest_url="/nonexistent-dir-xyz/out.ts", key=None)
    out = preflight_service.to_out(await preflight_service.run_preflight(db, job))
    assert any(c["code"] == "output_writable" and c["level"] == "error" for c in out["checks"])


async def test_preflight_never_leaks_stream_key(db):
    from app.services import preflight_service
    job = await _job(db, uri="testsrc=size=320x240:rate=15", key="TOP_SECRET_KEY_9")
    report = await preflight_service.run_preflight(db, job)
    import json
    blob = json.dumps(preflight_service.to_out(report), default=str).lower()
    assert "top_secret_key_9" not in blob and "stream_key" not in blob


async def test_persisted_report_and_stale(db, monkeypatch):
    from app.services import preflight_service
    job = await _job(db, uri="testsrc=size=320x240:rate=15")
    await preflight_service.run_preflight(db, job)
    latest = await preflight_service.get_latest(db, job.id)
    assert latest is not None
    # force a 0s TTL -> the report is stale
    monkeypatch.setattr(get_settings(), "preflight_report_ttl_seconds", 0, raising=False)
    # is_stale reads settings fresh; emulate by checking with an old created_at
    latest.created_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
    assert preflight_service.is_stale(latest) is True


# ---- start gate -------------------------------------------------------------------------

@pytest.fixture
def op_headers(roles_tokens):
    return {"authorization": f"Bearer {roles_tokens['tokens']['operator']}"}


async def _api_job(client, headers, *, bad_source=False):
    r = await client.post(f"{V1}/ffmpeg-profiles", headers=headers, json={"name": "p", "copy_mode": True})
    profile_id = r.json()["id"]
    r = await client.post(f"{V1}/destinations", headers=headers,
                          json={"name": "d", "kind": "rtmp", "url": "rtmp://x/app", "stream_key": "k"})
    dest_id = r.json()["id"]
    uri = "/data/media/missing.mp4" if bad_source else "testsrc=size=320x240:rate=15"
    opts = {} if bad_source else {"f": "lavfi"}
    r = await client.post(f"{V1}/stream-jobs", headers=headers, json={
        "name": "gate-job", "ffmpeg_profile_id": profile_id,
        "inputs": [{"kind": "url" if not bad_source else "file", "uri": uri, "options": opts}],
        "outputs": [{"format": "flv", "destination_id": dest_id}],
    })
    return r.json()["id"]


async def test_start_blocked_on_red_preflight(client, op_headers, monkeypatch):
    from app.core import config
    job_id = await _api_job(client, op_headers, bad_source=True)
    # run preflight -> red, can_start False
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
