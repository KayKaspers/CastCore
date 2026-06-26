"""End-to-end stream-lifecycle test (full stack: backend + Redis + Process Manager).

Exercises the real CastCore lifecycle with safe, local-only media (lavfi `testsrc`, H.264,
no audio, MPEG-TS to a local file — no external services, no risky codecs):

    create job -> command preview -> start -> process status -> receive logs ->
    check output -> stop -> final status

Run it INSIDE the running stack so the real backend (status consumer), Process Manager and
Redis all participate:

    docker compose up -d
    docker compose exec backend python /app/e2e_stream.py

It mints a throwaway admin in the live DB, drives the HTTP API at localhost:8000, subscribes
to the per-job Redis log channel, verifies the output file grows, then cleans everything up.
Exits non-zero on failure. FFmpeg < 8.1.2 (CVE-2026-8461) does NOT fail the test: only the
version *warning* is affected and no risky codec is used.
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
import uuid

import httpx
from sqlalchemy import delete, select

from app.core.redis import LOGS_CHANNEL_PREFIX, get_redis
from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.models.streaming import Destination, FFmpegProfile, StreamJob
from app.models.user import User
from app.services.auth_service import create_user

BASE = "http://localhost:8000/api/v1"
TAG = uuid.uuid4().hex[:8]
JOB_NAME = f"e2e-{TAG}"
OUT_PATH = f"/data/recordings/e2e_{TAG}.ts"
USERNAME = f"_e2e_{TAG}"


def log(msg: str) -> None:
    print(f"[e2e] {msg}", flush=True)


async def _seed_admin() -> tuple[uuid.UUID, str]:
    async with SessionLocal() as db:
        user = await create_user(
            db, username=USERNAME, password="E2e!" + TAG, email=None, language="de",
            role_names=["admin"],
        )
        await db.commit()
        return user.id, create_access_token(str(user.id), extra={"roles": ["admin"]})


async def _collect_logs(job_id: str, sink: list[str], stop: asyncio.Event) -> None:
    redis = get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"{LOGS_CHANNEL_PREFIX}{job_id}")
    try:
        while not stop.is_set():
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if msg and msg.get("data"):
                sink.append(msg["data"])
    finally:
        await pubsub.unsubscribe()
        await pubsub.aclose()


async def _output_state(client: httpx.AsyncClient, headers: dict) -> str | None:
    r = await client.get(f"{BASE}/monitoring/outputs", headers=headers)
    r.raise_for_status()
    for o in r.json():
        if o.get("job_name") == JOB_NAME:
            return o.get("state")
    return None


async def _wait_state(client, headers, target: set[str], timeout: float) -> str | None:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        last = await _output_state(client, headers)
        if last in target:
            return last
        await asyncio.sleep(1.0)
    return last


async def main() -> int:
    user_id, token = await _seed_admin()
    headers = {"authorization": f"Bearer {token}"}
    job_id = profile_id = dest_id = None
    logs: list[str] = []
    stop_logs = asyncio.Event()
    log_task: asyncio.Task | None = None

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            # 1) create profile (H.264, audio disabled) + local recording destination + job
            r = await client.post(f"{BASE}/ffmpeg-profiles", headers=headers, json={
                "name": f"e2e-{TAG}", "copy_mode": False,
                "video": {"codec": "libx264", "preset": "ultrafast", "bitrate": "600k"},
                "audio": {"disabled": True},
            })
            assert r.status_code in (200, 201), r.text
            profile_id = r.json()["id"]

            r = await client.post(f"{BASE}/destinations", headers=headers, json={
                "name": f"e2e-{TAG}", "kind": "recording", "url": OUT_PATH,
            })
            assert r.status_code in (200, 201), r.text
            dest_id = r.json()["id"]

            r = await client.post(f"{BASE}/stream-jobs", headers=headers, json={
                "name": JOB_NAME, "ffmpeg_profile_id": profile_id,
                "inputs": [{"kind": "url", "uri": "testsrc=size=320x240:rate=15", "options": {"f": "lavfi"}}],
                "outputs": [{"format": "mpegts", "destination_id": dest_id}],
            })
            assert r.status_code == 201, r.text
            job_id = r.json()["id"]
            log(f"job created: {job_id}")

            # 2) command preview
            r = await client.post(f"{BASE}/stream-jobs/{job_id}/preview", headers=headers)
            assert r.status_code == 200, r.text
            cmd = next(iter(r.json()["previews"].values()))
            assert "testsrc" in cmd and OUT_PATH in cmd and "ffmpeg" in cmd, cmd
            log("command preview ok")

            # 3) subscribe to logs, then start
            log_task = asyncio.create_task(_collect_logs(job_id, logs, stop_logs))
            await asyncio.sleep(0.5)
            r = await client.post(f"{BASE}/stream-jobs/{job_id}/start", headers=headers)
            assert r.status_code == 200, r.text
            log("start requested")

            # 4) process status -> running
            state = await _wait_state(client, headers, {"running"}, timeout=25)
            assert state == "running", f"expected running, got {state}"
            log("process status: running")

            # 5) receive logs + 6) output file grows
            await asyncio.sleep(3.0)
            assert logs, "no log lines received from the Redis log channel"
            log(f"received {len(logs)} log line(s)")
            assert os.path.isfile(OUT_PATH), f"output file missing: {OUT_PATH}"
            s1 = os.path.getsize(OUT_PATH)
            await asyncio.sleep(2.0)
            s2 = os.path.getsize(OUT_PATH)
            assert s2 > s1 > 0, f"output not growing: {s1} -> {s2}"
            log(f"output file growing: {s1} -> {s2} bytes")

            # 7) stop + 8) final status
            r = await client.post(f"{BASE}/stream-jobs/{job_id}/stop", headers=headers)
            assert r.status_code == 202, r.text
            final = await _wait_state(client, headers, {"stopped", "failed"}, timeout=20)
            assert final == "stopped", f"expected stopped, got {final}"
            log("final status: stopped")

        log("ALL E2E LIFECYCLE STEPS PASSED")
        return 0
    finally:
        stop_logs.set()
        if log_task:
            try:
                await asyncio.wait_for(log_task, timeout=3)
            except asyncio.TimeoutError:
                log_task.cancel()
        # cleanup: job (cascades outputs/status), destination, profile, user, file
        async with SessionLocal() as db:
            if job_id:
                await db.execute(delete(StreamJob).where(StreamJob.id == uuid.UUID(job_id)))
            if dest_id:
                await db.execute(delete(Destination).where(Destination.id == uuid.UUID(dest_id)))
            if profile_id:
                await db.execute(delete(FFmpegProfile).where(FFmpegProfile.id == uuid.UUID(profile_id)))
            res = await db.execute(select(User).where(User.id == user_id))
            u = res.scalar_one_or_none()
            if u:
                await db.delete(u)
            await db.commit()
        try:
            os.remove(OUT_PATH)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
