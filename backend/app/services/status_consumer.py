"""Background consumer of the Process Manager status channel.

Subscribes to ``castcore:status``, reconciles DB state (per-output ProcessStatus +
StreamJob.status) and fires notifications on state transitions. Runs for the lifetime
of the backend process (started/stopped via the FastAPI lifespan).
"""

from __future__ import annotations

import asyncio
import datetime as dt
import json
import os
import uuid

from sqlalchemy import select

from app.core.redis import STATUS_CHANNEL, get_redis
from app.db.session import SessionLocal
from app.models.recording import Recording
from app.models.streaming import Output, ProcessStatus, StreamJob
from app.services import notification_service

# state -> event on transition
_EVENT = {"running": "stream_started", "failed": "stream_failed", "stopped": "stream_stopped"}
_JOB_STATUS = {"running": "running", "starting": "running", "failed": "failed", "stopped": "stopped"}

_prev: dict[str, str] = {}


async def _handle(message: dict) -> None:
    try:
        output_id = uuid.UUID(message["output_id"])
        job_id = uuid.UUID(message["job_id"]) if message.get("job_id") else None
    except (KeyError, ValueError, TypeError):
        return
    state = message.get("state", "")

    async with SessionLocal() as db:
        # Recording outputs are synthetic (no Output row) — finalize them separately.
        rec = (await db.execute(
            select(Recording).where(Recording.output_id == output_id, Recording.state == "recording")
        )).scalar_one_or_none()
        if rec is not None:
            if state in ("stopped", "failed"):
                rec.state = "completed" if state == "stopped" else "failed"
                rec.ended_at = dt.datetime.now(dt.timezone.utc)
                try:
                    rec.size_bytes = os.path.getsize(rec.path)
                except OSError:
                    pass
                await db.commit()
            return

        # Upsert per-output process status (+ live metrics if present).
        existing = (await db.execute(
            select(ProcessStatus).where(ProcessStatus.output_id == output_id)
        )).scalar_one_or_none()
        if existing is None:
            # only create if the output actually exists
            if await db.get(Output, output_id) is None:
                return
            existing = ProcessStatus(output_id=output_id, state=state)
            db.add(existing)
        existing.state = state
        _FIELD = {
            "fps": "fps", "bitrate": "bitrate_kbps", "speed": "speed",
            "drop": "dropped_frames", "cpu": "cpu_pct", "rss": "rss_mb", "pid": "pid",
        }
        for key, col in _FIELD.items():
            if key in message and message[key] is not None:
                setattr(existing, col, message[key])
        if state == "running" and existing.started_at is None:
            existing.started_at = dt.datetime.now(dt.timezone.utc)
        elif state in ("stopped", "failed"):
            existing.started_at = None

        # Reconcile job status.
        if job_id is not None:
            job = await db.get(StreamJob, job_id)
            if job is not None and state in _JOB_STATUS:
                job.status = _JOB_STATUS[state]

        await db.commit()

        # Fire notifications on transition.
        prev = _prev.get(str(output_id))
        if prev != state and state in _EVENT:
            if not (state == "stopped" and prev not in ("running", "starting")):
                ctx = {"job_id": str(job_id) if job_id else "", "detail": message.get("line", "")}
                if job_id is not None:
                    job = await db.get(StreamJob, job_id)
                    if job is not None:
                        ctx["job_name"] = job.name
                await notification_service.dispatch(db, _EVENT[state], ctx)
        _prev[str(output_id)] = state


async def run_status_consumer(stop: asyncio.Event) -> None:
    while not stop.is_set():
        try:
            redis = get_redis()
            pubsub = redis.pubsub()
            await pubsub.subscribe(STATUS_CHANNEL)
            async for message in pubsub.listen():
                if stop.is_set():
                    break
                if message.get("type") == "message":
                    try:
                        await _handle(json.loads(message["data"]))
                    except Exception as exc:  # noqa: BLE001 - never let the loop die
                        print(f"[status-consumer] error: {exc}")
            await pubsub.unsubscribe(STATUS_CHANNEL)
            await pubsub.aclose()
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 - reconnect on redis errors
            print(f"[status-consumer] reconnecting after: {exc}")
            await asyncio.sleep(2)
