"""Tests for the stream health score service + endpoint."""

from __future__ import annotations

from app.services import health_service as hs

V1 = "/api/v1"


def _running(**kw):
    base = {"state": "running", "speed": 1.0, "reconnect_count": 0, "dropped_frames": 0,
            "fps": 30.0, "bitrate_kbps": 6000.0}
    base.update(kw)
    return base


# ----------------------------------------------------------------- output / job scoring

def test_healthy_stream_scores_green():
    h = hs.output_health(_running())
    assert h["score"] == 100 and h["status"] == "green"
    assert h["reasons"][0]["code"] == "healthy"


def test_encoding_speed_below_one_penalised():
    low = hs.output_health(_running(speed=0.96))
    assert low["status"] in ("green", "yellow") and any(r["code"] == "encoding_speed_low" for r in low["reasons"])
    crit = hs.output_health(_running(speed=0.7))
    assert crit["score"] < low["score"]
    assert any(r["code"] == "encoding_speed_critical" and r["level"] == "error" for r in crit["reasons"])


def test_reconnects_penalised():
    h = hs.output_health(_running(reconnect_count=2))
    r = next(r for r in h["reasons"] if r["code"] == "reconnects")
    assert r["params"]["count"] == 2 and h["score"] < 100
    assert next(r for r in hs.output_health(_running(reconnect_count=4))["reasons"]
                if r["code"] == "reconnects")["level"] == "error"


def test_failed_output_is_red_zero():
    h = hs.output_health({"state": "failed"})
    assert h["score"] == 0 and h["status"] == "red"
    assert h["reasons"][0]["code"] == "output_failed"


def test_stopped_output_is_gray_unknown():
    h = hs.output_health({"state": "stopped"})
    assert h["score"] is None and h["status"] == "gray"


def test_job_health_weakest_output_drives_score():
    # one healthy output + one failed output -> the failed one drags the job to red/0
    job = hs.compute_job_health("j1", "Job", [_running(output_id="a"), {"state": "failed", "output_id": "b"}])
    assert job["status"] == "red"
    assert job["score"] == min(o["score"] for o in job["outputs"] if o["score"] is not None) == 0
    assert len(job["outputs"]) == 2


def test_job_health_speed_warning_is_yellow():
    job = hs.compute_job_health("j1", "Job", [_running(speed=0.7, output_id="a")])
    assert job["status"] == "yellow"  # 100-40=60 -> yellow, not red


def test_job_health_no_outputs_is_gray():
    job = hs.compute_job_health("j1", "Job", [])
    assert job["score"] is None and job["status"] == "gray"
    assert job["reasons"][0]["code"] == "not_running"


def test_missing_preflight_readiness_does_not_penalise():
    job = hs.compute_job_health("j1", "Job", [_running()], preflight_level=None, readiness_level=None)
    assert job["status"] == "green"
    assert not any(r["code"].endswith("_failed") for r in job["reasons"])


def test_preflight_red_forces_red():
    job = hs.compute_job_health("j1", "Job", [_running()], preflight_level="red")
    assert job["status"] == "red"
    assert any(r["code"] == "preflight_failed" for r in job["reasons"])


def test_readiness_yellow_downgrades_green():
    job = hs.compute_job_health("j1", "Job", [_running()], readiness_level="yellow")
    assert job["status"] == "yellow"
    assert any(r["code"] == "readiness_warning" for r in job["reasons"])


# ----------------------------------------------------------------- endpoint (DB)

async def _job_with_status(db, *, state="running", speed=1.0, reconnects=0):
    from app.models.streaming import Destination, Output, ProcessStatus, StreamJob
    from app.core.security import encrypt_secret

    job = StreamJob(name="health-job", type="single", status="running")
    job.inputs = []
    dest = Destination(name="d", kind="rtmp", url="rtmp://x/app",
                       stream_key=encrypt_secret("SECRET_KEY_99"), enabled=True)
    out = Output(format="flv", output_opts={}, enabled=True)
    out.destination = dest
    out.status = ProcessStatus(state=state, speed=speed, fps=30.0, bitrate_kbps=6000.0,
                               reconnect_count=reconnects, dropped_frames=0)
    job.outputs = [out]
    db.add(job)
    await db.commit()
    return job


async def test_job_health_endpoint_running(client, db, roles_tokens):
    job = await _job_with_status(db, state="running", speed=1.0)
    headers = {"authorization": f"Bearer {roles_tokens['tokens']['viewer']}"}
    r = await client.get(f"{V1}/monitoring/jobs/{job.id}/health", headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "green" and body["score"] == 100
    assert len(body["outputs"]) == 1
    # no secret/stream-key leakage anywhere in the payload
    assert "SECRET_KEY_99" not in r.text and "stream_key" not in r.text


async def test_job_health_endpoint_failed_output_red(client, db, roles_tokens):
    job = await _job_with_status(db, state="failed")
    headers = {"authorization": f"Bearer {roles_tokens['tokens']['viewer']}"}
    r = await client.get(f"{V1}/monitoring/jobs/{job.id}/health", headers=headers)
    assert r.status_code == 200 and r.json()["status"] == "red"


async def test_job_health_endpoint_404(client, roles_tokens):
    headers = {"authorization": f"Bearer {roles_tokens['tokens']['viewer']}"}
    r = await client.get(f"{V1}/monitoring/jobs/00000000-0000-0000-0000-000000000000/health", headers=headers)
    assert r.status_code == 404


async def test_all_health_summary(client, db, roles_tokens):
    await _job_with_status(db, state="running")
    headers = {"authorization": f"Bearer {roles_tokens['tokens']['viewer']}"}
    r = await client.get(f"{V1}/monitoring/health", headers=headers)
    assert r.status_code == 200
    assert any(j["status"] == "green" for j in r.json())
