"""Dry-run / test stream — a short, safe test encode.

Runs the job's source through its FFmpeg profile for a few seconds into a throwaway file
(never the real destination, no network), then reports success, encoding speed, fps and
any FFmpeg error. Used to validate a profile and estimate load before going live.
"""

from __future__ import annotations

import asyncio
import os
import re
import uuid
from pathlib import Path

from app.core.config import get_settings
from app.core.errors import CastCoreError, ErrorCode
from app.models.streaming import StreamJob
from app.services.ffmpeg import CommandBuildError, FFmpegCommand, Input as FFInput, Output as FFOutput, OutputFormat
from app.services.stream_service import _audio_settings, _video_settings

_TEST_SECONDS = 5
_TIMEOUT_S = 40
_SPEED = re.compile(r"speed=\s*([\d.]+)x")
_FPS = re.compile(r"\bfps=\s*([\d.]+)")
_ERROR_LINE = re.compile(r"(error|failed|invalid|no such file|not found|unable)", re.I)


def _build_argv(job: StreamJob, out_path: str) -> list[str]:
    settings = get_settings()
    inputs = [
        FFInput(uri=i.uri, options=dict(i.options or {}), loop=False, reconnect=False)
        for i in job.inputs
    ]
    output = FFOutput(
        uri=out_path,
        fmt=OutputFormat.MP4,
        video=_video_settings(job.profile),
        audio=_audio_settings(job.profile),
        extra_options={"t": str(_TEST_SECONDS)},  # limit to a few seconds
    )
    return FFmpegCommand(
        inputs=inputs,
        outputs=[output],
        filter_complex=(job.profile.filters or {}).get("complex") if job.profile else None,
        expert_args=list(job.profile.expert_args or []) if job.profile else [],
        ffmpeg_path=settings.ffmpeg_path,
    ).build()


async def run_dry_run(job: StreamJob) -> dict:
    if not job.inputs:
        raise CastCoreError(ErrorCode.FFMPEG_NO_INPUT, params={"job": str(job.id)})

    settings = get_settings()
    tmp_dir = Path(settings.data_dir) / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    out_path = str(tmp_dir / f"dryrun-{uuid.uuid4().hex}.mp4")

    try:
        argv = _build_argv(job, out_path)
    except CommandBuildError as exc:
        raise CastCoreError(exc.code, params={"detail": str(exc)}) from exc

    try:
        proc = await asyncio.create_subprocess_exec(
            *argv, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        _, err = await asyncio.wait_for(proc.communicate(), timeout=_TIMEOUT_S)
        rc = proc.returncode
        timed_out = False
    except asyncio.TimeoutError:
        proc.kill()
        err, rc, timed_out = b"", -1, True
    except OSError as exc:
        return {"ok": False, "speed": None, "fps": None, "message": str(exc), "log_tail": []}
    finally:
        try:
            os.remove(out_path)
        except OSError:
            pass

    text = err.decode("utf-8", "replace")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    speeds = _SPEED.findall(text)
    fpss = _FPS.findall(text)
    ok = rc == 0 and not timed_out
    if timed_out:
        message = "Timeout – Test hat zu lange gedauert."
    elif ok:
        message = "Test-Encode erfolgreich."
    else:
        err_lines = [ln for ln in lines if _ERROR_LINE.search(ln)]
        message = (err_lines[-1] if err_lines else (lines[-1] if lines else "Test fehlgeschlagen."))[:300]

    return {
        "ok": ok,
        "returncode": rc,
        "speed": float(speeds[-1]) if speeds else None,
        "fps": float(fpss[-1]) if fpss else None,
        "message": message,
        "log_tail": lines[-15:],
    }
