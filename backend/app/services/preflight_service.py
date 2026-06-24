"""Preflight checks: validate a stream job is ready to start (🟢/🟡/🔴).

Runs ffprobe against the job's first input, checks streams/outputs/destinations and
basic system resources. Returns a structured report; the UI renders it before start.
"""

from __future__ import annotations

import asyncio
import json
import shutil

from app.core.config import get_settings
from app.models.streaming import Input, StreamJob
from app.schemas.streaming import PreflightCheck, PreflightReport

_TIMEOUT_S = 12


async def _ffprobe(inp: Input) -> tuple[dict | None, str | None]:
    """Probe an input. Returns (parsed_json, error_detail)."""
    settings = get_settings()
    ffprobe = shutil.which(settings.ffprobe_path) or shutil.which("ffprobe")
    if not ffprobe:
        return None, "ffprobe not found"
    args = [ffprobe, "-v", "error", "-print_format", "json", "-show_streams", "-show_format"]
    for key, val in (inp.options or {}).items():
        args.append(f"-{key}")
        if val != "":
            args.append(str(val))
    args.append(inp.uri)
    try:
        proc = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=_TIMEOUT_S)
    except asyncio.TimeoutError:
        return None, "timeout"
    except OSError as exc:
        return None, str(exc)
    if proc.returncode != 0:
        return None, (err.decode("utf-8", "replace").strip()[:200] or "ffprobe failed")
    try:
        return json.loads(out), None
    except json.JSONDecodeError:
        return None, "unparseable ffprobe output"


def _level(checks: list[PreflightCheck]) -> str:
    if any(c.level == "error" for c in checks):
        return "red"
    if any(c.level == "warn" for c in checks):
        return "yellow"
    return "green"


async def run_preflight(job: StreamJob) -> PreflightReport:
    checks: list[PreflightCheck] = []

    # --- inputs ---
    if not job.inputs:
        checks.append(PreflightCheck(key="inputs", level="error", detail="no input defined"))
    else:
        inp = job.inputs[0]
        data, err = await _ffprobe(inp)
        if data is None:
            checks.append(PreflightCheck(key="source_readable", level="error", detail=err))
        else:
            checks.append(PreflightCheck(key="source_readable", level="ok", detail=inp.uri))
            streams = data.get("streams", [])
            has_video = any(s.get("codec_type") == "video" for s in streams)
            has_audio = any(s.get("codec_type") == "audio" for s in streams)
            checks.append(
                PreflightCheck(key="has_video", level="ok" if has_video else "error",
                               detail=None if has_video else "input has no video stream")
            )
            checks.append(
                PreflightCheck(key="has_audio", level="ok" if has_audio else "warn",
                               detail=None if has_audio else "input has no audio stream")
            )

    # --- outputs & destinations ---
    enabled = [o for o in job.outputs if o.enabled]
    if not enabled:
        checks.append(PreflightCheck(key="outputs", level="error", detail="no enabled output"))
    for out in enabled:
        dest = out.destination
        if dest is None:
            checks.append(PreflightCheck(key="destination", level="error", detail="output has no destination"))
            continue
        if not dest.url:
            checks.append(PreflightCheck(key="output_url", level="error", detail="destination URL missing"))
        if dest.kind in ("platform", "rtmp") and not dest.stream_key:
            checks.append(
                PreflightCheck(key="stream_key", level="warn",
                               detail=f"no stream key for '{dest.name}' (ok if embedded in URL)")
            )

    # --- recording disk space / writability ---
    settings = get_settings()
    if any((o.destination and o.destination.kind == "recording") for o in enabled):
        try:
            usage = shutil.disk_usage(str(settings.recordings_dir))
            free_gb = usage.free / (1024**3)
            checks.append(
                PreflightCheck(key="disk_space", level="ok" if free_gb > 2 else "warn",
                               detail=f"{free_gb:.1f} GB free")
            )
        except OSError:
            checks.append(PreflightCheck(key="disk_space", level="warn", detail="unavailable"))

    return PreflightReport(level=_level(checks), checks=checks)
