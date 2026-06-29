"""Preflight 2.0 — a structured, persisted readiness check before a stream starts.

Runs ffprobe against the input, validates outputs/destinations/paths, FFmpeg safety, and (from
cached results) platform readiness, then persists a structured report. The report feeds the
health score and diagnostics engine. **No secrets, tokens or stream keys** are ever included.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import json
import os
import shutil
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import ffmpeg_inspect
from app.core.config import get_settings
from app.models.platform import PlatformMetadata
from app.models.platform_account import PlatformAccount
from app.models.preflight import PreflightReport
from app.models.streaming import Input, Output, StreamJob

_TIMEOUT_S = 12

# code -> category, affected_component, docs page, default "blocking" (only meaningful at error)
CATALOG: dict[str, dict] = {
    "input_defined": {"cat": "input", "comp": "input", "docs": "troubleshooting/stream-not-starting.md", "blocking": True},
    "source_readable": {"cat": "input", "comp": "input", "docs": "troubleshooting/stream-not-starting.md", "blocking": True},
    "has_video": {"cat": "input", "comp": "input", "docs": "troubleshooting/ffmpeg-errors.md", "blocking": True},
    "has_audio": {"cat": "input", "comp": "input", "docs": "troubleshooting/ffmpeg-errors.md", "blocking": False},
    "risky_codec": {"cat": "security", "comp": "input", "docs": "admin-guide/ffmpeg-requirements.md", "blocking": True},
    "ffmpeg_version": {"cat": "security", "comp": "security", "docs": "admin-guide/ffmpeg-requirements.md", "blocking": False},
    "output_enabled": {"cat": "output", "comp": "output", "docs": "user-guide/streams.md", "blocking": True},
    "destination_set": {"cat": "output", "comp": "output", "docs": "user-guide/streams.md", "blocking": True},
    "stream_key": {"cat": "output", "comp": "output", "docs": "troubleshooting/platform-errors.md", "blocking": False},
    "output_writable": {"cat": "output", "comp": "output", "docs": "troubleshooting/performance.md", "blocking": True},
    "recording_path": {"cat": "storage", "comp": "storage", "docs": "troubleshooting/performance.md", "blocking": True},
    "disk_space": {"cat": "storage", "comp": "storage", "docs": "troubleshooting/performance.md", "blocking": False},
    "platform_connected": {"cat": "platform", "comp": "platform", "docs": "admin-guide/platform-oauth.md", "blocking": False},
    "platform_ready": {"cat": "platform", "comp": "platform", "docs": "admin-guide/platform-oauth.md", "blocking": False},
    "metadata_complete": {"cat": "platform", "comp": "platform", "docs": "user-guide/platforms.md", "blocking": False},
}


def _check(code: str, level: str, *, output_id: str | None = None, blocking: bool | None = None,
           **params) -> dict:
    meta = CATALOG[code]
    return {
        "code": code,
        "category": meta["cat"],
        "level": level,
        "blocking": (meta["blocking"] if blocking is None else blocking) if level == "error" else False,
        "affected_component": meta["comp"],
        "affected_output_id": output_id,
        "docs_url": meta["docs"],
        "params": params,
    }


async def _ffprobe(inp: Input) -> tuple[dict | None, str | None]:
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


def _writable_dir(path: str) -> bool:
    d = os.path.dirname(path) or path
    return os.path.isdir(d) and os.access(d, os.W_OK)


def _level(checks: list[dict]) -> str:
    if not checks:
        return "gray"
    if any(c["level"] == "error" for c in checks):
        return "red"
    if any(c["level"] == "warn" for c in checks):
        return "yellow"
    return "green"


async def _build_checks(db: AsyncSession, job: StreamJob) -> list[dict]:
    settings = get_settings()
    checks: list[dict] = []

    # --- input ---
    inputs = (await db.execute(select(Input).where(Input.job_id == job.id).order_by(Input.order))).scalars().all()
    if not inputs:
        checks.append(_check("input_defined", "error"))
    else:
        inp = inputs[0]
        data, err = await _ffprobe(inp)
        if data is None:
            checks.append(_check("source_readable", "error", detail=err))
        else:
            checks.append(_check("source_readable", "ok"))
            streams = data.get("streams", [])
            has_video = any(s.get("codec_type") == "video" for s in streams)
            has_audio = any(s.get("codec_type") == "audio" for s in streams)
            checks.append(_check("has_video", "ok" if has_video else "error"))
            checks.append(_check("has_audio", "ok" if has_audio else "warn"))
            risky = sorted({s.get("codec_name") for s in streams if ffmpeg_inspect.is_risky_codec(s.get("codec_name"))})
            if risky:
                block = settings.block_risky_codecs and settings.safe_media_processing_enabled
                checks.append(_check("risky_codec", "error" if block else "warn", codecs=", ".join(risky)))

    # --- FFmpeg version ---
    info = await ffmpeg_inspect.get_info()
    if info["ffmpeg_vulnerable"] is True:
        checks.append(_check("ffmpeg_version", "warn", version=info["ffmpeg_version"], min=info["min_version"]))
    elif info["ffmpeg_vulnerable"] is None:
        checks.append(_check("ffmpeg_version", "warn", version="unknown", min=info["min_version"]))

    # --- outputs ---
    outputs = (await db.execute(select(Output).where(Output.job_id == job.id, Output.enabled.is_(True)))).scalars().all()
    if not outputs:
        checks.append(_check("output_enabled", "error"))
    for out in outputs:
        oid = str(out.id)
        dest = out.destination
        if dest is None or not dest.url:
            checks.append(_check("destination_set", "error", output_id=oid))
            continue
        if dest.kind in ("platform", "rtmp") and not dest.stream_key:
            checks.append(_check("stream_key", "warn", output_id=oid, destination=dest.name))
        # local output paths must be writable (never echo the URL/key)
        if dest.kind == "recording" or dest.url.startswith("/"):
            checks.append(_check("output_writable", "ok" if _writable_dir(dest.url) else "error", output_id=oid))

    # --- recording storage ---
    if job.recording_enabled or any((o.destination and o.destination.kind == "recording") for o in outputs):
        rec = str(settings.recordings_dir)
        checks.append(_check("recording_path", "ok" if os.path.isdir(rec) and os.access(rec, os.W_OK) else "error"))
        try:
            free_gb = shutil.disk_usage(rec if os.path.isdir(rec) else "/").free / (1024**3)
            checks.append(_check("disk_space", "ok" if free_gb > 2 else "warn", free_gb=round(free_gb, 1)))
        except OSError:
            checks.append(_check("disk_space", "warn", free_gb=None))

    # --- platform (intended platforms = configured metadata rows) ---
    from app.services import diagnostics_service  # lazy import to avoid cycles

    metas = (await db.execute(select(PlatformMetadata).where(PlatformMetadata.stream_job_id == job.id))).scalars().all()
    for meta in metas:
        provider = meta.platform
        acc = (await db.execute(select(PlatformAccount).where(PlatformAccount.provider == provider))).scalars().first()
        if provider in ("twitch", "youtube"):
            checks.append(_check("platform_connected", "ok" if acc else "warn", provider=provider))
        checks.append(_check("metadata_complete", "ok" if meta.title else "warn", provider=provider))
        # cached readiness, if available and fresh (no live API call here)
        cached = diagnostics_service._readiness_cache.get(f"{job.id}:{provider}")
        if cached and not diagnostics_service._is_stale(cached["at"]):
            lvl = cached["result"].get("level")
            checks.append(_check("platform_ready", {"red": "error", "yellow": "warn"}.get(lvl, "ok"),
                                 blocking=False, provider=provider))

    return checks


async def run_preflight(db: AsyncSession, job: StreamJob, *, user_id: uuid.UUID | None = None) -> PreflightReport:
    """Run preflight, persist the structured report, and return the ORM row."""
    checks = await _build_checks(db, job)
    can_start = not any(c["level"] == "error" and c["blocking"] for c in checks)
    report = PreflightReport(
        stream_job_id=job.id, level=_level(checks), can_start=can_start,
        checks=checks, started_by_user_id=user_id,
    )
    db.add(report)
    await db.flush()
    return report


async def get_latest(db: AsyncSession, job_id: uuid.UUID) -> PreflightReport | None:
    res = await db.execute(
        select(PreflightReport).where(PreflightReport.stream_job_id == job_id)
        .order_by(PreflightReport.created_at.desc()).limit(1)
    )
    return res.scalar_one_or_none()


def is_stale(report: PreflightReport) -> bool:
    ttl = get_settings().preflight_report_ttl_seconds
    return dt.datetime.now(dt.timezone.utc) - report.created_at > dt.timedelta(seconds=ttl)


def to_out(report: PreflightReport) -> dict:
    """Serialize a persisted report (computing stale, blocking_errors, warnings, summary)."""
    checks = report.checks or []
    blocking = [c for c in checks if c["level"] == "error" and c.get("blocking")]
    warnings = [c for c in checks if c["level"] == "warn"]
    summary = {
        "critical": sum(1 for c in checks if c["level"] == "error"),
        "warning": len(warnings),
        "ok": sum(1 for c in checks if c["level"] == "ok"),
    }
    return {
        "id": report.id,
        "stream_job_id": report.stream_job_id,
        "level": report.level,
        "can_start": report.can_start,
        "created_at": report.created_at,
        "ttl_seconds": get_settings().preflight_report_ttl_seconds,
        "stale": is_stale(report),
        "started_by_user_id": report.started_by_user_id,
        "checks": checks,
        "blocking_errors": blocking,
        "warnings": warnings,
        "summary": summary,
    }
