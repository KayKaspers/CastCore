"""CastCore Process Manager — supervises long-running FFmpeg stream processes.

This is the heart of safe streaming control:

- Spawns FFmpeg with ``asyncio.create_subprocess_exec`` (``shell=False``) from an
  argv produced by the backend's Command Builder — never a shell string.
- Pumps FFmpeg stderr/stdout line by line, publishing each line to a per-job Redis
  channel (``castcore:logs:<job_id>``) and parsing progress (fps/bitrate/speed/frame)
  into status updates on ``castcore:status``.
- Recognises common failure patterns and attaches a translatable ``hint`` code so the
  UI can show a plain-language explanation next to the raw log (Stream Health Assistant).

Control commands arrive on ``castcore:control``.

Run: ``python -m app.main``
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import signal
import time
from dataclasses import dataclass, field

from redis.asyncio import Redis

CONTROL_CHANNEL = "castcore:control"
STATUS_CHANNEL = "castcore:status"
LOGS_CHANNEL_PREFIX = "castcore:logs:"

# FFmpeg progress line, e.g.:
# frame=  120 fps= 30 q=28.0 size=  256kB time=00:00:04.00 bitrate= 524.3kbits/s speed=1.0x
_PROGRESS = re.compile(
    r"(?=.*\bfps=\s*(?P<fps>[\d.]+))?"
    r"(?=.*\bbitrate=\s*(?P<bitrate>[\d.]+)\s*kbits/s)?"
    r"(?=.*\bspeed=\s*(?P<speed>[\d.]+)x)?"
    r"(?=.*\bdrop=\s*(?P<drop>\d+))?"
    r".*\bframe=",
)

# Failure pattern -> translatable hint code (see frontend i18n "loghint.*").
_HINTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"no such file or directory", re.I), "source_missing"),
    (re.compile(r"connection refused|failed to connect|connection timed out|network is unreachable", re.I), "network_unreachable"),
    (re.compile(r"401 unauthorized|403 forbidden|auth", re.I), "auth_failed"),
    (re.compile(r"rtmp.*(refused|eof|broken pipe)|broken pipe", re.I), "rtmp_rejected"),
    (re.compile(r"no space left", re.I), "disk_full"),
    (re.compile(r"invalid data found|could not find codec", re.I), "bad_media"),
]
_ERROR_RE = re.compile(r"\b(error|failed|fatal|unable|invalid|refused)\b", re.I)


def _classify(line: str) -> tuple[str, str | None]:
    """Return (level, hint_code|None) for a log line."""
    for pattern, code in _HINTS:
        if pattern.search(line):
            return "error", code
    return ("error" if _ERROR_RE.search(line) else "info"), None


@dataclass
class ManagedProcess:
    output_id: str
    job_id: str
    argv: list[str]
    proc: asyncio.subprocess.Process | None = None
    tasks: list[asyncio.Task] = field(default_factory=list)

    async def start(self) -> None:
        # shell=False: argv is a list; nothing is interpreted by a shell.
        self.proc = await asyncio.create_subprocess_exec(
            *self.argv,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    async def stop(self) -> None:
        for task in self.tasks:
            task.cancel()
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

    # --- publishing helpers ---
    async def _publish_status(self, output_id: str, job_id: str, state: str, **extra) -> None:
        if self.redis is None:
            return
        payload = {"output_id": output_id, "job_id": job_id, "state": state, **extra}
        await self.redis.publish(STATUS_CHANNEL, json.dumps(payload))

    async def _publish_log(self, job_id: str, output_id: str, line: str) -> None:
        if self.redis is None:
            return
        level, hint = _classify(line)
        payload = {
            "output_id": output_id,
            "job_id": job_id,
            "ts": time.time(),
            "line": line,
            "level": level,
            "hint": hint,
        }
        await self.redis.publish(f"{LOGS_CHANNEL_PREFIX}{job_id}", json.dumps(payload))

    async def _maybe_status(self, line: str, output_id: str, job_id: str) -> None:
        m = _PROGRESS.search(line)
        if not m:
            return
        extra = {k: float(v) for k, v in m.groupdict().items() if v is not None}
        if extra:
            await self._publish_status(output_id, job_id, "running", **extra)

    # --- stream pumping ---
    async def _pump(self, stream: asyncio.StreamReader, output_id: str, job_id: str) -> None:
        buf = b""
        while True:
            chunk = await stream.read(1024)
            if not chunk:
                break
            buf += chunk
            parts = re.split(rb"[\r\n]", buf)
            buf = parts.pop()
            for raw in parts:
                text = raw.decode("utf-8", "replace").strip()
                if not text:
                    continue
                await self._publish_log(job_id, output_id, text)
                await self._maybe_status(text, output_id, job_id)
        if buf.strip():
            await self._publish_log(job_id, output_id, buf.decode("utf-8", "replace").strip())

    async def _watch_exit(self, mp: ManagedProcess) -> None:
        assert mp.proc is not None
        rc = await mp.proc.wait()
        state = "stopped" if rc == 0 else "failed"
        await self._publish_log(mp.job_id, mp.output_id, f"[castcore] process exited with code {rc}")
        await self._publish_status(mp.output_id, mp.job_id, state, returncode=rc)
        self.processes.pop(mp.output_id, None)

    # --- command handlers ---
    async def handle_start(self, output_id: str, argv: list[str], job_id: str = "") -> None:
        if output_id in self.processes:
            await self.handle_stop(output_id, job_id)
        mp = ManagedProcess(output_id=output_id, job_id=job_id, argv=argv)
        await mp.start()
        self.processes[output_id] = mp
        assert mp.proc is not None
        mp.tasks = [
            asyncio.create_task(self._pump(mp.proc.stderr, output_id, job_id)),
            asyncio.create_task(self._pump(mp.proc.stdout, output_id, job_id)),
            asyncio.create_task(self._watch_exit(mp)),
        ]
        await self._publish_status(output_id, job_id, "running")
        await self._publish_log(job_id, output_id, "[castcore] stream started")

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

    # --- main loop ---
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

        listener = asyncio.create_task(self._listen(pubsub))
        await self._stop.wait()
        listener.cancel()

        print("[process-manager] shutting down; stopping all processes…")
        await asyncio.gather(*(mp.stop() for mp in self.processes.values()), return_exceptions=True)
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
