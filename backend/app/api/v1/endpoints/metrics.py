"""Prometheus metrics exporter (`/api/v1/metrics`).

Plain-text exposition format (no external client dependency). Exposes system metrics and
per-output stream metrics. Labels use UUIDs only (no job names) to avoid leaking names;
the endpoint is unauthenticated by convention — restrict it at the reverse proxy if needed.
"""

from __future__ import annotations

import psutil
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from sqlalchemy import func, select

from app.api.deps import DbDep
from app.core.config import get_settings
from app.models.streaming import ProcessStatus, StreamJob

router = APIRouter(tags=["metrics"])

_PROM = "text/plain; version=0.0.4; charset=utf-8"


def _line(name: str, value: float | int, labels: dict | None = None) -> str:
    if labels:
        lbl = ",".join(f'{k}="{v}"' for k, v in labels.items())
        return f"{name}{{{lbl}}} {value}"
    return f"{name} {value}"


@router.get("/metrics", response_class=PlainTextResponse)
async def metrics(db: DbDep) -> PlainTextResponse:
    settings = get_settings()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(str(settings.data_dir))
    ffmpeg = sum(1 for p in psutil.process_iter(["name"]) if (p.info.get("name") or "").startswith("ffmpeg"))
    jobs = await db.scalar(select(func.count()).select_from(StreamJob)) or 0

    out: list[str] = [
        "# HELP castcore_up CastCore backend is up.",
        "# TYPE castcore_up gauge",
        _line("castcore_up", 1),
        "# TYPE castcore_cpu_percent gauge",
        _line("castcore_cpu_percent", psutil.cpu_percent(interval=0.0)),
        "# TYPE castcore_mem_percent gauge",
        _line("castcore_mem_percent", mem.percent),
        _line("castcore_mem_used_bytes", mem.used),
        _line("castcore_mem_total_bytes", mem.total),
        "# TYPE castcore_disk_percent gauge",
        _line("castcore_disk_percent", disk.percent),
        _line("castcore_disk_free_bytes", disk.free),
        "# TYPE castcore_ffmpeg_processes gauge",
        _line("castcore_ffmpeg_processes", ffmpeg),
        "# TYPE castcore_stream_jobs_total gauge",
        _line("castcore_stream_jobs_total", jobs),
    ]

    rows = (await db.execute(select(ProcessStatus))).scalars().all()
    out.append("# TYPE castcore_outputs_running gauge")
    out.append(_line("castcore_outputs_running", sum(1 for r in rows if r.state == "running")))
    out.append("# TYPE castcore_output_fps gauge")
    out.append("# TYPE castcore_output_speed gauge")
    for r in rows:
        labels = {"output_id": str(r.output_id), "state": r.state}
        if r.fps is not None:
            out.append(_line("castcore_output_fps", r.fps, labels))
        if r.bitrate_kbps is not None:
            out.append(_line("castcore_output_bitrate_kbps", r.bitrate_kbps, labels))
        if r.speed is not None:
            out.append(_line("castcore_output_speed", r.speed, labels))
        if r.cpu_pct is not None:
            out.append(_line("castcore_output_cpu_percent", r.cpu_pct, labels))
        if r.rss_mb is not None:
            out.append(_line("castcore_output_rss_mb", r.rss_mb, labels))

    return PlainTextResponse("\n".join(out) + "\n", media_type=_PROM)
