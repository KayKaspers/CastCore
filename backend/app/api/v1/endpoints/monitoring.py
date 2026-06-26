"""Monitoring endpoints: system metrics + live per-output process metrics.

Readable by any authenticated user (including viewers).
"""

from __future__ import annotations

import datetime as dt
import uuid

import psutil
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import CurrentUser, DbDep, get_current_user
from app.core import ffmpeg_inspect
from app.core.config import get_settings
from app.core.errors import CastCoreError, ErrorCode
from app.models.streaming import Destination, Output, ProcessStatus, StreamJob
from app.services import diagnostics_service, health_service

router = APIRouter(
    prefix="/monitoring",
    tags=["monitoring"],
    dependencies=[Depends(get_current_user)],
)


class SystemMetrics(BaseModel):
    cpu_percent: float
    mem_percent: float
    mem_used_mb: float
    mem_total_mb: float
    disk_percent: float
    disk_free_gb: float
    ffmpeg_processes: int


class OutputMetrics(BaseModel):
    output_id: uuid.UUID
    job_id: uuid.UUID
    job_name: str
    destination: str | None
    state: str
    fps: float | None
    bitrate_kbps: float | None
    speed: float | None
    cpu_pct: float | None
    rss_mb: float | None
    reconnect_count: int
    started_at: dt.datetime | None


@router.get("/system", response_model=SystemMetrics)
async def system_metrics(_user: CurrentUser) -> SystemMetrics:
    settings = get_settings()
    mem = psutil.virtual_memory()
    # Fall back to the filesystem root if the data dir is not present yet (e.g. before the
    # volume is mounted) so the endpoint never 500s on a misconfigured/early environment.
    try:
        disk = psutil.disk_usage(str(settings.data_dir))
    except OSError:
        disk = psutil.disk_usage("/")
    ffmpeg = sum(1 for p in psutil.process_iter(["name"]) if (p.info.get("name") or "").startswith("ffmpeg"))
    return SystemMetrics(
        cpu_percent=psutil.cpu_percent(interval=0.0),
        mem_percent=mem.percent,
        mem_used_mb=round(mem.used / (1024**2), 1),
        mem_total_mb=round(mem.total / (1024**2), 1),
        disk_percent=disk.percent,
        disk_free_gb=round(disk.free / (1024**3), 1),
        ffmpeg_processes=ffmpeg,
    )


@router.get("/ffmpeg")
async def ffmpeg_status(_user: CurrentUser) -> dict:
    """FFmpeg/ffprobe version, vulnerability flag and safe-media settings."""
    return await ffmpeg_inspect.get_info()


class HealthReason(BaseModel):
    code: str
    level: str
    params: dict = {}


class OutputHealth(BaseModel):
    output_id: uuid.UUID | None = None
    score: int | None = None
    status: str
    reasons: list[HealthReason] = []


class JobHealth(BaseModel):
    job_id: uuid.UUID
    name: str
    score: int | None = None
    status: str  # green | yellow | red | gray
    reasons: list[HealthReason] = []
    outputs: list[OutputHealth] = []


class JobHealthSummary(BaseModel):
    job_id: uuid.UUID
    name: str
    score: int | None = None
    status: str


def _metrics(status: ProcessStatus | None) -> dict:
    if status is None:
        return {"state": None}
    return {
        "state": status.state,
        "speed": status.speed,
        "reconnect_count": status.reconnect_count,
        "dropped_frames": status.dropped_frames,
        "fps": status.fps,
        "bitrate_kbps": status.bitrate_kbps,
    }


async def _collect(db: DbDep, job_id: uuid.UUID | None):
    stmt = (
        select(StreamJob, Output, ProcessStatus)
        .outerjoin(Output, (Output.job_id == StreamJob.id) & (Output.enabled.is_(True)))
        .outerjoin(ProcessStatus, ProcessStatus.output_id == Output.id)
        .order_by(StreamJob.name)
    )
    if job_id is not None:
        stmt = stmt.where(StreamJob.id == job_id)
    rows = (await db.execute(stmt)).all()
    jobs: dict = {}
    for job, output, status in rows:
        entry = jobs.setdefault(job.id, {"name": job.name, "outputs": []})
        if output is not None:
            m = _metrics(status)
            m["output_id"] = str(output.id)
            entry["outputs"].append(m)
    return [
        health_service.compute_job_health(str(jid), data["name"], data["outputs"])
        for jid, data in jobs.items()
    ]


@router.get("/jobs/{job_id}/health", response_model=JobHealth)
async def job_health(job_id: uuid.UUID, db: DbDep, _user: CurrentUser) -> JobHealth:
    """Health score (0–100) + traffic-light status + reasons for one stream job."""
    healths = await _collect(db, job_id)
    if not healths:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"job": "not_found"}, http_status=404)
    return JobHealth(**healths[0])


@router.get("/health", response_model=list[JobHealthSummary])
async def all_job_health(db: DbDep, _user: CurrentUser) -> list[JobHealthSummary]:
    """Per-job health summary for the dashboard overview."""
    return [JobHealthSummary(job_id=h["job_id"], name=h["name"], score=h["score"], status=h["status"])
            for h in await _collect(db, None)]


class Diagnosis(BaseModel):
    code: str
    category: str
    severity: str  # info | warning | critical
    confidence: str  # high | medium | low
    affected_component: str
    affected_output_id: str | None = None
    docs_url: str
    detected_at: str
    stale: bool = False
    params: dict = {}


class JobDiagnostics(BaseModel):
    job_id: uuid.UUID
    name: str
    score: int | None = None
    status: str
    diagnoses: list[Diagnosis] = []


class JobDiagnosticsSummary(BaseModel):
    job_id: uuid.UUID
    name: str
    status: str
    critical: int = 0
    warning: int = 0
    info: int = 0


@router.get("/jobs/{job_id}/diagnostics", response_model=JobDiagnostics)
async def job_diagnostics(job_id: uuid.UUID, db: DbDep, _user: CurrentUser) -> JobDiagnostics:
    """Structured diagnoses (Stream Health Assistant) for one job. No secrets are returned."""
    job = await db.get(StreamJob, job_id)
    if job is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"job": "not_found"}, http_status=404)
    return JobDiagnostics(**await diagnostics_service.diagnose_job(db, job))


@router.get("/diagnostics", response_model=list[JobDiagnosticsSummary])
async def all_diagnostics(db: DbDep, _user: CurrentUser) -> list[JobDiagnosticsSummary]:
    """Per-job diagnosis counts (worst-first) for the dashboard overview."""
    jobs = (await db.execute(select(StreamJob).order_by(StreamJob.name))).scalars().all()
    out = []
    for job in jobs:
        d = await diagnostics_service.diagnose_job(db, job)
        s = diagnostics_service.summarise(d["diagnoses"])
        out.append(JobDiagnosticsSummary(job_id=job.id, name=job.name, status=d["status"], **s))
    return out


@router.get("/outputs", response_model=list[OutputMetrics])
async def output_metrics(db: DbDep, _user: CurrentUser) -> list[OutputMetrics]:
    stmt = (
        select(ProcessStatus, Output, StreamJob, Destination)
        .join(Output, ProcessStatus.output_id == Output.id)
        .join(StreamJob, Output.job_id == StreamJob.id)
        .outerjoin(Destination, Output.destination_id == Destination.id)
        .order_by(StreamJob.name)
    )
    rows = (await db.execute(stmt)).all()
    return [
        OutputMetrics(
            output_id=ps.output_id, job_id=job.id, job_name=job.name,
            destination=dest.name if dest else None, state=ps.state,
            fps=ps.fps, bitrate_kbps=ps.bitrate_kbps, speed=ps.speed,
            cpu_pct=ps.cpu_pct, rss_mb=ps.rss_mb, reconnect_count=ps.reconnect_count,
            started_at=ps.started_at,
        )
        for ps, _out, job, dest in rows
    ]
