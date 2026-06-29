"""Stream-job CRUD + process control (operator+)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import CurrentUser, DbDep, require_roles
from app.core.config import get_settings
from app.core.errors import CastCoreError, ErrorCode
from app.models.preflight import PreflightReport as PreflightReportModel
from app.models.streaming import Input, Output, StreamJob
from app.schemas.preflight import PreflightReportOut
from app.schemas.streaming import CommandPreviewOut, StreamJobIn, StreamJobOut
from app.services import audit_service, dry_run_service, notification_service, preflight_service, stream_service
from app.services.ffmpeg import mask_command

router = APIRouter(
    prefix="/stream-jobs",
    tags=["streaming"],
    dependencies=[Depends(require_roles("operator"))],
)


async def _get_job(db: DbDep, job_id: uuid.UUID) -> StreamJob:
    job = await db.get(StreamJob, job_id)
    if job is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"job": "not_found"}, http_status=404)
    return job


@router.get("", response_model=list[StreamJobOut])
async def list_jobs(db: DbDep) -> list[StreamJob]:
    res = await db.execute(select(StreamJob).order_by(StreamJob.created_at))
    return list(res.scalars().all())


@router.post("", response_model=StreamJobOut, status_code=201)
async def create_job(payload: StreamJobIn, db: DbDep) -> StreamJob:
    job = StreamJob(
        name=payload.name,
        type=payload.type,
        autostart=payload.autostart,
        enabled=payload.enabled,
        ffmpeg_profile_id=payload.ffmpeg_profile_id,
        fallback_policy=payload.fallback_policy,
        recording_enabled=payload.recording_enabled,
        recording_retention_days=payload.recording_retention_days,
        inputs=[
            Input(kind=i.kind, uri=i.uri, options=i.options, loop=i.loop, reconnect=i.reconnect, order=i.order)
            for i in payload.inputs
        ],
        outputs=[
            Output(destination_id=o.destination_id, format=o.format, output_opts=o.output_opts, enabled=o.enabled)
            for o in payload.outputs
        ],
    )
    db.add(job)
    await db.flush()
    return job


@router.get("/{job_id}", response_model=StreamJobOut)
async def get_job(job_id: uuid.UUID, db: DbDep) -> StreamJob:
    return await _get_job(db, job_id)


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: uuid.UUID, db: DbDep) -> None:
    job = await db.get(StreamJob, job_id)
    if job is not None:
        await db.delete(job)


@router.post("/{job_id}/preview", response_model=CommandPreviewOut)
async def preview_job(job_id: uuid.UUID, db: DbDep) -> CommandPreviewOut:
    job = await _get_job(db, job_id)
    argvs = stream_service.build_output_argvs(job)
    return CommandPreviewOut(previews={oid: mask_command(argv) for oid, argv in argvs.items()})


@router.post("/{job_id}/preflight", response_model=PreflightReportOut)
async def preflight_job(job_id: uuid.UUID, db: DbDep, user: CurrentUser) -> PreflightReportOut:
    job = await _get_job(db, job_id)
    report = await preflight_service.run_preflight(db, job, user_id=user.id)
    await audit_service.record(db, actor_id=user.id, action="stream.preflight", target_type="stream_job",
                               target_id=str(job_id), meta={"level": report.level, "can_start": report.can_start})
    if report.level == "red":
        await notification_service.dispatch(db, "preflight_failed", {"job_name": job.name})
    return PreflightReportOut(**preflight_service.to_out(report))


@router.get("/{job_id}/preflight/latest", response_model=PreflightReportOut | None)
async def preflight_latest(job_id: uuid.UUID, db: DbDep) -> PreflightReportOut | None:
    await _get_job(db, job_id)
    report = await preflight_service.get_latest(db, job_id)
    return PreflightReportOut(**preflight_service.to_out(report)) if report else None


@router.get("/{job_id}/preflight/reports", response_model=list[PreflightReportOut])
async def preflight_reports(job_id: uuid.UUID, db: DbDep) -> list[PreflightReportOut]:
    await _get_job(db, job_id)
    rows = (await db.execute(
        select(PreflightReportModel).where(PreflightReportModel.stream_job_id == job_id)
        .order_by(PreflightReportModel.created_at.desc()).limit(20)
    )).scalars().all()
    return [PreflightReportOut(**preflight_service.to_out(r)) for r in rows]


@router.get("/{job_id}/preflight/reports/{report_id}", response_model=PreflightReportOut)
async def preflight_report(job_id: uuid.UUID, report_id: uuid.UUID, db: DbDep) -> PreflightReportOut:
    report = await db.get(PreflightReportModel, report_id)
    if report is None or report.stream_job_id != job_id:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"report": "not_found"}, http_status=404)
    return PreflightReportOut(**preflight_service.to_out(report))


@router.post("/{job_id}/dry-run")
async def dry_run_job(job_id: uuid.UUID, db: DbDep) -> dict:
    job = await _get_job(db, job_id)
    return await dry_run_service.run_dry_run(job)


@router.post("/{job_id}/start", response_model=CommandPreviewOut)
async def start_job(job_id: uuid.UUID, db: DbDep, user: CurrentUser, override: bool = False) -> CommandPreviewOut:
    job = await _get_job(db, job_id)
    settings = get_settings()
    is_admin = "admin" in user.role_names
    if settings.preflight_required_before_start or settings.preflight_block_on_red:
        latest = await preflight_service.get_latest(db, job_id)
        blocked_required = settings.preflight_required_before_start and (
            latest is None or preflight_service.is_stale(latest)
        )
        blocked_red = settings.preflight_block_on_red and latest is not None and not latest.can_start
        if blocked_required or blocked_red:
            if override and is_admin:
                await audit_service.record(db, actor_id=user.id, action="stream.preflight_override",
                                           target_type="stream_job", target_id=str(job_id),
                                           meta={"reason": "required" if blocked_required else "red"})
            elif blocked_required:
                raise CastCoreError(ErrorCode.PREFLIGHT_REQUIRED, http_status=409, params={"job": job.name})
            else:
                raise CastCoreError(ErrorCode.PREFLIGHT_BLOCKED, http_status=409, params={"job": job.name})

    argvs = await stream_service.start_job(db, job)
    await audit_service.record(db, actor_id=user.id, action="stream.start", target_type="stream_job", target_id=str(job_id))
    return CommandPreviewOut(previews={oid: mask_command(argv) for oid, argv in argvs.items()})


@router.post("/{job_id}/stop", status_code=202)
async def stop_job(job_id: uuid.UUID, db: DbDep, user: CurrentUser) -> dict:
    job = await _get_job(db, job_id)
    await stream_service.stop_job(db, job)
    await audit_service.record(db, actor_id=user.id, action="stream.stop", target_type="stream_job", target_id=str(job_id))
    return {"status": "stopping"}


@router.post("/{job_id}/restart", response_model=CommandPreviewOut)
async def restart_job(job_id: uuid.UUID, db: DbDep, user: CurrentUser) -> CommandPreviewOut:
    job = await _get_job(db, job_id)
    argvs = await stream_service.restart_job(db, job)
    await audit_service.record(db, actor_id=user.id, action="stream.restart", target_type="stream_job", target_id=str(job_id))
    return CommandPreviewOut(previews={oid: mask_command(argv) for oid, argv in argvs.items()})


@router.post("/{job_id}/recording", response_model=StreamJobOut)
async def toggle_recording(job_id: uuid.UUID, db: DbDep, enabled: bool = True, retention_days: int = 0) -> StreamJob:
    job = await _get_job(db, job_id)
    job.recording_enabled = enabled
    job.recording_retention_days = retention_days
    await db.flush()
    return job
