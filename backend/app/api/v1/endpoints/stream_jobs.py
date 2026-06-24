"""Stream-job CRUD + process control (operator+)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import DbDep, require_roles
from app.core.errors import CastCoreError, ErrorCode
from app.models.streaming import Input, Output, StreamJob
from app.schemas.streaming import CommandPreviewOut, PreflightReport, StreamJobIn, StreamJobOut
from app.services import preflight_service, stream_service
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


@router.post("/{job_id}/preflight", response_model=PreflightReport)
async def preflight_job(job_id: uuid.UUID, db: DbDep) -> PreflightReport:
    job = await _get_job(db, job_id)
    return await preflight_service.run_preflight(job)


@router.post("/{job_id}/start", response_model=CommandPreviewOut)
async def start_job(job_id: uuid.UUID, db: DbDep) -> CommandPreviewOut:
    job = await _get_job(db, job_id)
    argvs = await stream_service.start_job(job)
    return CommandPreviewOut(previews={oid: mask_command(argv) for oid, argv in argvs.items()})


@router.post("/{job_id}/stop", status_code=202)
async def stop_job(job_id: uuid.UUID, db: DbDep) -> dict:
    job = await _get_job(db, job_id)
    await stream_service.stop_job(job)
    return {"status": "stopping"}


@router.post("/{job_id}/restart", response_model=CommandPreviewOut)
async def restart_job(job_id: uuid.UUID, db: DbDep) -> CommandPreviewOut:
    job = await _get_job(db, job_id)
    argvs = await stream_service.restart_job(job)
    return CommandPreviewOut(previews={oid: mask_command(argv) for oid, argv in argvs.items()})
