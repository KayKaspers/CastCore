"""Stream-job logic: assemble FFmpeg argv from stored job/profile/destinations and
drive the Process Manager via the control channel.

One supervised FFmpeg process is created per enabled output (multi-destination =
multiple processes), which matches the Process Manager's supervision model.
"""

from __future__ import annotations

from app.core.config import get_settings
from app.core.errors import CastCoreError, ErrorCode
from app.core.security import decrypt_secret
from app.models.streaming import FFmpegProfile, Output, StreamJob
from app.services import control
from app.services.ffmpeg import (
    AudioSettings,
    CommandBuildError,
    FFmpegCommand,
    Input as FFInput,
    Output as FFOutput,
    OutputFormat,
    VideoSettings,
)

_FORMAT_MAP = {
    "flv": OutputFormat.FLV,
    "hls": OutputFormat.HLS,
    "mpegts": OutputFormat.MPEGTS,
    "mp4": OutputFormat.MP4,
}

_VIDEO_KEYS = {"codec", "bitrate", "width", "height", "fps", "preset", "tune", "gop", "pixel_format"}
_AUDIO_KEYS = {"codec", "bitrate", "disabled"}


def _video_settings(profile: FFmpegProfile | None) -> VideoSettings | None:
    if profile is None:
        return VideoSettings(codec="copy")
    if profile.copy_mode:
        return VideoSettings(codec="copy")
    data = {k: v for k, v in (profile.video or {}).items() if k in _VIDEO_KEYS}
    return VideoSettings(**data) if data else VideoSettings()


def _audio_settings(profile: FFmpegProfile | None) -> AudioSettings | None:
    if profile is None or profile.copy_mode:
        return AudioSettings(codec="copy")
    data = {k: v for k, v in (profile.audio or {}).items() if k in _AUDIO_KEYS}
    return AudioSettings(**data) if data else AudioSettings()


def _destination_uri(output: Output) -> str:
    """Resolve the final output URI, appending a decrypted stream key for RTMP."""
    dest = output.destination
    if dest is None:
        raise CastCoreError(ErrorCode.FFMPEG_NO_OUTPUT, params={"output": str(output.id)})
    uri = dest.url
    if dest.stream_key:
        key = decrypt_secret(dest.stream_key)
        if dest.kind in ("rtmp", "platform"):
            uri = uri.rstrip("/") + "/" + key
    return uri


def build_output_command(job: StreamJob, output: Output) -> FFmpegCommand:
    if not job.inputs:
        raise CastCoreError(ErrorCode.FFMPEG_NO_INPUT, params={"job": str(job.id)})
    fmt = _FORMAT_MAP.get(output.format)
    if fmt is None:
        raise CastCoreError(ErrorCode.FFMPEG_INVALID_PARAMETER, params={"format": output.format})

    settings = get_settings()
    ff_inputs = [
        FFInput(uri=i.uri, options=dict(i.options or {}), loop=i.loop, reconnect=i.reconnect)
        for i in job.inputs
    ]
    ff_output = FFOutput(
        uri=_destination_uri(output),
        fmt=fmt,
        video=_video_settings(job.profile),
        audio=_audio_settings(job.profile),
        extra_options=dict(output.output_opts or {}),
    )
    return FFmpegCommand(
        inputs=ff_inputs,
        outputs=[ff_output],
        filter_complex=(job.profile.filters or {}).get("complex") if job.profile else None,
        expert_args=list(job.profile.expert_args or []) if job.profile else [],
        ffmpeg_path=settings.ffmpeg_path,
    )


def build_output_argvs(job: StreamJob) -> dict[str, list[str]]:
    """Return {output_id: argv} for every enabled output. Raises CastCoreError on bad config."""
    result: dict[str, list[str]] = {}
    enabled = [o for o in job.outputs if o.enabled]
    if not enabled:
        raise CastCoreError(ErrorCode.FFMPEG_NO_OUTPUT, params={"job": str(job.id)})
    for output in enabled:
        try:
            result[str(output.id)] = build_output_command(job, output).build()
        except CommandBuildError as exc:
            raise CastCoreError(exc.code, params={"output": str(output.id), "detail": str(exc)}) from exc
    return result


async def start_job(job: StreamJob) -> dict[str, list[str]]:
    argvs = build_output_argvs(job)
    for output_id, argv in argvs.items():
        await control.send_start(output_id, argv, job_id=str(job.id))
    job.status = "starting"
    return argvs


async def stop_job(job: StreamJob) -> None:
    for output in job.outputs:
        await control.send_stop(str(output.id), job_id=str(job.id))
    job.status = "stopped"


async def restart_job(job: StreamJob) -> dict[str, list[str]]:
    argvs = build_output_argvs(job)
    for output_id, argv in argvs.items():
        await control.send_restart(output_id, argv, job_id=str(job.id))
    job.status = "starting"
    return argvs
