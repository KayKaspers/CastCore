"""Stream Health Assistant — turns raw signals into structured, actionable diagnoses.

Aggregates the health score (``health_service``), FFmpeg version info (``ffmpeg_inspect``),
live process status, and the **cached** last preflight/readiness results into a list of
diagnoses per stream job (optionally per output). Each diagnosis is a translatable ``code``
plus structured metadata (category, severity, confidence, affected component/output, a docs
page and interpolation params). The human-readable title/summary/technical_reason/actions are
resolved in the UI from i18n (``diag.<code>.*``), consistent with CastCore's code-based i18n.

No secrets, tokens or stream keys are ever included.
"""

from __future__ import annotations

import datetime as dt
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import ffmpeg_inspect
from app.models.streaming import Output, ProcessStatus, StreamJob
from app.services import health_service

# ---- preflight / readiness cache (avoids re-calling slow/rate-limited probes per poll) ----

_STALE_AFTER = dt.timedelta(minutes=10)
_preflight_cache: dict[str, dict] = {}
_readiness_cache: dict[str, dict] = {}


def cache_preflight(job_id: str, report: dict) -> None:
    _preflight_cache[job_id] = {"report": report, "at": dt.datetime.now(dt.timezone.utc)}


def cache_readiness(job_id: str, provider: str, result: dict) -> None:
    _readiness_cache[f"{job_id}:{provider}"] = {"result": result, "at": dt.datetime.now(dt.timezone.utc)}


def _is_stale(at: dt.datetime) -> bool:
    return dt.datetime.now(dt.timezone.utc) - at > _STALE_AFTER


# ---- diagnosis catalog: code -> category/severity/component/docs -------------------------

CATALOG: dict[str, dict] = {
    "encoding_speed_critical": {"category": "performance", "severity": "critical", "component": "encoding", "docs": "troubleshooting/performance.md"},
    "encoding_speed_low": {"category": "performance", "severity": "warning", "component": "encoding", "docs": "troubleshooting/performance.md"},
    "dropped_frames": {"category": "performance", "severity": "warning", "component": "encoding", "docs": "troubleshooting/performance.md"},
    "reconnects": {"category": "network", "severity": "warning", "component": "output", "docs": "troubleshooting/stream-not-starting.md"},
    "process_crashed": {"category": "process", "severity": "critical", "component": "process", "docs": "troubleshooting/ffmpeg-errors.md"},
    "no_throughput": {"category": "encoding", "severity": "warning", "component": "encoding", "docs": "troubleshooting/ffmpeg-errors.md"},
    "not_running": {"category": "process", "severity": "info", "component": "process", "docs": "user-guide/streams.md"},
    "ffmpeg_vulnerable": {"category": "security", "severity": "warning", "component": "security", "docs": "admin-guide/ffmpeg-requirements.md"},
    "ffmpeg_version_unknown": {"category": "security", "severity": "info", "component": "security", "docs": "admin-guide/ffmpeg-requirements.md"},
    "input_unreachable": {"category": "input", "severity": "critical", "component": "input", "docs": "troubleshooting/stream-not-starting.md"},
    "no_video": {"category": "input", "severity": "critical", "component": "input", "docs": "troubleshooting/ffmpeg-errors.md"},
    "no_audio": {"category": "input", "severity": "warning", "component": "input", "docs": "troubleshooting/ffmpeg-errors.md"},
    "risky_codec": {"category": "security", "severity": "critical", "component": "input", "docs": "admin-guide/ffmpeg-requirements.md"},
    "stream_key_missing": {"category": "output", "severity": "warning", "component": "output", "docs": "troubleshooting/platform-errors.md"},
    "disk_space_low": {"category": "storage", "severity": "warning", "component": "storage", "docs": "troubleshooting/performance.md"},
    "platform_not_connected": {"category": "platform", "severity": "warning", "component": "platform", "docs": "admin-guide/platform-oauth.md"},
    "platform_token_invalid": {"category": "platform", "severity": "critical", "component": "platform", "docs": "admin-guide/platform-oauth.md"},
    "platform_missing_scope": {"category": "platform", "severity": "critical", "component": "platform", "docs": "admin-guide/platform-oauth.md"},
    "platform_invalid_category": {"category": "platform", "severity": "warning", "component": "platform", "docs": "admin-guide/platform-oauth.md"},
    "platform_no_broadcast": {"category": "platform", "severity": "warning", "component": "platform", "docs": "admin-guide/platform-oauth.md"},
    "platform_api_unreachable": {"category": "platform", "severity": "warning", "component": "platform", "docs": "admin-guide/platform-oauth.md"},
}

# health reason code -> diagnosis code
_HEALTH_TO_DIAG = {
    "encoding_speed_critical": "encoding_speed_critical",
    "encoding_speed_low": "encoding_speed_low",
    "dropped_frames": "dropped_frames",
    "reconnects": "reconnects",
    "output_failed": "process_crashed",
    "no_throughput": "no_throughput",
}


def _diag(code: str, *, params: dict | None = None, output_id: str | None = None,
          confidence: str = "high", detected_at: dt.datetime | None = None,
          stale: bool = False, severity: str | None = None) -> dict:
    meta = CATALOG[code]
    return {
        "code": code,
        "category": meta["category"],
        "severity": severity or meta["severity"],
        "confidence": confidence,
        "affected_component": meta["component"],
        "affected_output_id": output_id,
        "docs_url": meta["docs"],
        "detected_at": (detected_at or dt.datetime.now(dt.timezone.utc)).isoformat(),
        "stale": stale,
        "params": params or {},
    }


async def _job_metrics(db: AsyncSession, job_id) -> list[dict]:
    rows = (await db.execute(
        select(Output, ProcessStatus)
        .outerjoin(ProcessStatus, ProcessStatus.output_id == Output.id)
        .where(Output.job_id == job_id, Output.enabled.is_(True))
    )).all()
    metrics = []
    for output, status in rows:
        m = {"output_id": str(output.id),
             "state": status.state if status else None,
             "speed": status.speed if status else None,
             "reconnect_count": status.reconnect_count if status else 0,
             "dropped_frames": status.dropped_frames if status else 0,
             "fps": status.fps if status else None,
             "bitrate_kbps": status.bitrate_kbps if status else None}
        metrics.append(m)
    return metrics


def _from_preflight(report: dict, stale: bool, at: dt.datetime) -> list[dict]:
    out: list[dict] = []
    conf = "low" if stale else "medium"
    for c in report.get("checks", []):
        key, level, detail = c.get("key"), c.get("level"), c.get("detail")
        if level == "ok":
            continue
        params = {"detail": detail} if detail else {}
        if key == "source_readable":
            out.append(_diag("input_unreachable", params=params, confidence=conf, detected_at=at, stale=stale))
        elif key == "has_video":
            out.append(_diag("no_video", confidence=conf, detected_at=at, stale=stale))
        elif key == "has_audio":
            out.append(_diag("no_audio", confidence=conf, detected_at=at, stale=stale))
        elif key == "risky_codec":
            out.append(_diag("risky_codec", params=params, confidence=conf, detected_at=at, stale=stale))
        elif key == "stream_key":
            out.append(_diag("stream_key_missing", confidence=conf, detected_at=at, stale=stale))
        elif key == "disk_space":
            out.append(_diag("disk_space_low", params=params, confidence=conf, detected_at=at, stale=stale))
    return out


_READINESS_TO_DIAG = {
    "token": "platform_token_invalid",
    "scopes": "platform_missing_scope",
    "account_connected": "platform_not_connected",
    "category": "platform_invalid_category",
    "broadcast": "platform_no_broadcast",
    "api": "platform_api_unreachable",
}


def _from_readiness(result: dict, stale: bool, at: dt.datetime) -> list[dict]:
    out: list[dict] = []
    conf = "low" if stale else "medium"
    provider = result.get("provider")
    for c in result.get("checks", []):
        if c.get("level") == "ok":
            continue
        diag = _READINESS_TO_DIAG.get(c.get("key"))
        if diag:
            out.append(_diag(diag, params={"provider": provider, **(c.get("params") or {})},
                             confidence=conf, detected_at=at, stale=stale))
    return out


async def diagnose_job(db: AsyncSession, job: StreamJob, *, providers: list[str] | None = None) -> dict:
    """Return ``{job_id, name, score, status, diagnoses[]}`` for one job."""
    metrics = await _job_metrics(db, job.id)
    health = health_service.compute_job_health(str(job.id), job.name, metrics)

    diagnoses: list[dict] = []

    # process state (crash / not running)
    states = [m["state"] for m in metrics]
    if any(s == "failed" for s in states):
        for m in metrics:
            if m["state"] == "failed":
                diagnoses.append(_diag("process_crashed", output_id=m["output_id"]))
    elif metrics and all(s in (None, "stopped") for s in states):
        diagnoses.append(_diag("not_running", confidence="medium"))

    # per-output health reasons
    for o in health["outputs"]:
        for r in o["reasons"]:
            code = _HEALTH_TO_DIAG.get(r["code"])
            if code and not any(d["code"] == code and d["affected_output_id"] == o["output_id"] for d in diagnoses):
                diagnoses.append(_diag(code, params=r.get("params") or {}, output_id=o["output_id"]))

    # FFmpeg version (security)
    info = await ffmpeg_inspect.get_info()
    if info["ffmpeg_vulnerable"] is True:
        diagnoses.append(_diag("ffmpeg_vulnerable",
                               params={"version": info["ffmpeg_version"], "min": info["min_version"]}))
    elif info["ffmpeg_vulnerable"] is None:
        diagnoses.append(_diag("ffmpeg_version_unknown"))

    # cached preflight
    pf = _preflight_cache.get(str(job.id))
    if pf:
        diagnoses += _from_preflight(pf["report"], _is_stale(pf["at"]), pf["at"])

    # cached readiness (any provider)
    for key, entry in _readiness_cache.items():
        if key.startswith(f"{job.id}:"):
            diagnoses += _from_readiness(entry["result"], _is_stale(entry["at"]), entry["at"])

    _SEV_ORDER = {"critical": 0, "warning": 1, "info": 2}
    diagnoses.sort(key=lambda d: _SEV_ORDER.get(d["severity"], 3))

    return {
        "job_id": str(job.id),
        "name": job.name,
        "score": health["score"],
        "status": health["status"],
        "diagnoses": diagnoses,
    }


def summarise(diagnoses: list[dict]) -> dict[str, Any]:
    return {
        "critical": sum(1 for d in diagnoses if d["severity"] == "critical"),
        "warning": sum(1 for d in diagnoses if d["severity"] == "warning"),
        "info": sum(1 for d in diagnoses if d["severity"] == "info"),
    }
