"""CastCore Process Manager — supervises long-running FFmpeg stream processes.

This is the heart of safe streaming control:

- Spawns FFmpeg with ``asyncio.create_subprocess_exec`` (``shell=False``) from an
  argv produced by the backend's Command Builder — never a shell string.
- Parses FFmpeg ``-progress``/stderr for fps, bitrate, speed, dropped frames and
  publishes them to Redis (the backend fans these out to WebSocket clients).
- Reconciles actual process state toward the desired state stored in PostgreSQL,
  applying reconnect / restart / fallback policy.

Phase 1 ships this as a runnable skeleton: a supervisor that listens for control
commands on Redis and can spawn/stop a process. Health parsing & DB reconciliation
land alongside the Stream Job API.

Run: ``python -m app.main``
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
from dataclasses import dataclass, field

from redis.asyncio import Redis

CONTROL_CHANNEL = "castcore:control"
STATUS_CHANNEL = "castcore:status"


@dataclass
class ManagedProcess:
    output_id: str
    argv: list[str]
    proc: asyncio.subprocess.Process | None = None
    reconnect_count: int = 0
    max_retries: int = 5

    async def start(self) -> None:
        # shell=False: argv is a list; nothing is interpreted by a shell.
        self.proc = await asyncio.create_subprocess_exec(
            *self.argv,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    async def stop(self) -> None:
        if self.proc and self.proc.returncode is None:
            self.proc.terminate()
            try:
                await asyncio.wait_for(self.proc.wait(), timeout=10)
            except asyncio.TimeoutError:
                self.proc.kill()


@dataclass
class Supervisor:
    processes: dict[str, ManagedProcess] = field(default_factory=dict)
    redis: Redis | None = None
    _stop: asyncio.Event = field(default_factory=asyncio.Event)

    async def _publish_status(self, output_id: str, job_id: str, state: str) -> None:
        if self.redis is not None:
            await self.redis.publish(
                STATUS_CHANNEL,
                json.dumps({"output_id": output_id, "job_id": job_id, "state": state}),
            )

    async def handle_start(self, output_id: str, argv: list[str], job_id: str = "") -> None:
        if output_id in self.processes:
            await self.handle_stop(output_id, job_id)
        mp = ManagedProcess(output_id=output_id, argv=argv)
        await mp.start()
        self.processes[output_id] = mp
        await self._publish_status(output_id, job_id, "running")
        # TODO: spawn a reader task to parse FFmpeg -progress and publish fps/bitrate/
        #   speed/dropped to STATUS_CHANNEL; apply reconnect/restart policy on exit.

    async def handle_stop(self, output_id: str, job_id: str = "") -> None:
        mp = self.processes.pop(output_id, None)
        if mp:
            await mp.stop()
        await self._publish_status(output_id, job_id, "stopped")

    async def _dispatch(self, message: dict) -> None:
        action = message.get("action")
        output_id = message.get("output_id", "")
        job_id = message.get("job_id", "")
        if action in ("start", "restart"):
            await self.handle_start(output_id, message.get("argv", []), job_id)
        elif action == "stop":
            await self.handle_stop(output_id, job_id)

    async def run(self) -> None:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, self._stop.set)
            except NotImplementedError:  # pragma: no cover - non-POSIX
                pass

        redis_url = _redis_dsn()
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(CONTROL_CHANNEL)
        print(f"[process-manager] up. Redis={redis_url}. Listening on {CONTROL_CHANNEL}…")
        # TODO(Phase 1): on startup, reconcile against desired state in PostgreSQL.

        listener = asyncio.create_task(self._listen(pubsub))
        await self._stop.wait()
        listener.cancel()

        print("[process-manager] shutting down; stopping all processes…")
        await asyncio.gather(*(mp.stop() for mp in self.processes.values()))
        await pubsub.unsubscribe(CONTROL_CHANNEL)
        await self.redis.aclose()

    async def _listen(self, pubsub) -> None:
        async for message in pubsub.listen():
            if message.get("type") != "message":
                continue
            try:
                await self._dispatch(json.loads(message["data"]))
            except (json.JSONDecodeError, KeyError) as exc:
                print(f"[process-manager] bad control message: {exc}")


def _redis_dsn() -> str:
    host = os.getenv("REDIS_HOST", "redis")
    port = os.getenv("REDIS_PORT", "6379")
    pw = os.getenv("REDIS_PASSWORD", "")
    auth = f":{pw}@" if pw else ""
    return f"redis://{auth}{host}:{port}/0"


def main() -> None:
    asyncio.run(Supervisor().run())


if __name__ == "__main__":
    main()
