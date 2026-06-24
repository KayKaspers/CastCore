"""Tests for stream-job argv assembly (no DB required — in-memory ORM objects)."""

from __future__ import annotations

from app.core.security import encrypt_secret
from app.models.streaming import Destination, FFmpegProfile, Input, Output, StreamJob
from app.services import stream_service
from app.services.ffmpeg import mask_command


def _job(copy_mode: bool = True) -> StreamJob:
    profile = FFmpegProfile(
        name="p", global_opts={"hide_banner": ""}, video={}, audio={},
        filters={}, copy_mode=copy_mode, expert_args=[],
    )
    dest = Destination(
        name="Twitch", kind="rtmp",
        url="rtmp://live.twitch.tv/app",
        stream_key=encrypt_secret("live_SECRET_KEY_42"),
        enabled=True,
    )
    job = StreamJob(name="j", type="single", status="stopped")
    job.profile = profile
    job.inputs = [Input(kind="file", uri="/data/media/clip.mp4", options={}, loop=True, reconnect=False, order=0)]
    out = Output(format="flv", output_opts={}, enabled=True)
    out.destination = dest
    job.outputs = [out]
    return job


def test_build_output_argvs_appends_stream_key():
    job = _job(copy_mode=True)
    argvs = stream_service.build_output_argvs(job)
    assert len(argvs) == 1
    argv = next(iter(argvs.values()))
    # Final RTMP URI must include the decrypted key.
    assert argv[-1] == "rtmp://live.twitch.tv/app/live_SECRET_KEY_42"
    assert "-stream_loop" in argv  # loop input
    assert "copy" in argv  # copy_mode profile


def test_preview_masks_stream_key():
    job = _job(copy_mode=True)
    argvs = stream_service.build_output_argvs(job)
    preview = mask_command(next(iter(argvs.values())))
    assert "live_SECRET_KEY_42" not in preview
    assert "••••" in preview


def test_disabled_output_excluded():
    job = _job()
    job.outputs[0].enabled = False
    try:
        stream_service.build_output_argvs(job)
        assert False, "expected error when no enabled outputs"
    except Exception as exc:  # CastCoreError
        assert getattr(exc, "code", "") == "ffmpeg.no_output"
