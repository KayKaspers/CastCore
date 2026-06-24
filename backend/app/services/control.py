"""Process-control client: publish start/stop commands to the Process Manager.

The backend never spawns FFmpeg itself. It publishes a command (with the already-built,
secret-containing argv) onto the Redis control channel; the Process Manager consumes it
and supervises the actual process. This keeps a single owner of process lifecycle.
"""

from __future__ import annotations

import json

from app.core.redis import CONTROL_CHANNEL, get_redis


async def send_start(output_id: str, argv: list[str], job_id: str) -> None:
    await _publish({"action": "start", "output_id": output_id, "job_id": job_id, "argv": argv})


async def send_stop(output_id: str, job_id: str) -> None:
    await _publish({"action": "stop", "output_id": output_id, "job_id": job_id})


async def send_restart(output_id: str, argv: list[str], job_id: str) -> None:
    await _publish({"action": "restart", "output_id": output_id, "job_id": job_id, "argv": argv})


async def _publish(message: dict) -> None:
    await get_redis().publish(CONTROL_CHANNEL, json.dumps(message))
