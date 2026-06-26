"""Unit tests for preflight risky-codec and FFmpeg-version checks (CVE-2026-8461)."""

from __future__ import annotations

from app.core import ffmpeg_inspect
from app.models.streaming import Destination, Input, Output, StreamJob
from app.services import preflight_service


def _job() -> StreamJob:
    job = StreamJob(name="j", type="single", status="stopped")
    job.profile = None
    job.inputs = [Input(kind="file", uri="/data/media/clip.mkv", options={}, order=0)]
    out = Output(format="flv", output_opts={}, enabled=True)
    out.destination = Destination(name="d", kind="rtmp", url="rtmp://x/app", stream_key=None, enabled=True)
    job.outputs = [out]
    return job


def _streams(video_codec: str):
    return (
        {"streams": [
            {"codec_type": "video", "codec_name": video_codec},
            {"codec_type": "audio", "codec_name": "aac"},
        ], "format": {}},
        None,
    )


async def _safe_info():
    return {"ffmpeg_vulnerable": False, "ffmpeg_version": "8.1.2", "min_version": "8.1.2"}


async def _vuln_info():
    return {"ffmpeg_vulnerable": True, "ffmpeg_version": "7.1.5", "min_version": "8.1.2"}


async def test_preflight_blocks_risky_codec(monkeypatch):
    async def fake_ffprobe(inp):
        return _streams("magicyuv")

    monkeypatch.setattr(preflight_service, "_ffprobe", fake_ffprobe)
    monkeypatch.setattr(ffmpeg_inspect, "get_info", _safe_info)

    report = await preflight_service.run_preflight(_job())
    risky = [c for c in report.checks if c.key == "risky_codec"]
    assert risky and risky[0].level == "error"  # default: block_risky_codecs + safe mode on
    assert report.level == "red"


async def test_preflight_clean_codec_has_no_risky_check(monkeypatch):
    async def fake_ffprobe(inp):
        return _streams("h264")

    monkeypatch.setattr(preflight_service, "_ffprobe", fake_ffprobe)
    monkeypatch.setattr(ffmpeg_inspect, "get_info", _safe_info)

    report = await preflight_service.run_preflight(_job())
    assert not any(c.key == "risky_codec" for c in report.checks)


async def test_preflight_warns_on_vulnerable_ffmpeg(monkeypatch):
    async def fake_ffprobe(inp):
        return _streams("h264")

    monkeypatch.setattr(preflight_service, "_ffprobe", fake_ffprobe)
    monkeypatch.setattr(ffmpeg_inspect, "get_info", _vuln_info)

    report = await preflight_service.run_preflight(_job())
    ver = [c for c in report.checks if c.key == "ffmpeg_version"]
    assert ver and ver[0].level == "warn"
