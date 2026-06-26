"""Unit tests for FFmpeg version detection and risky-codec helpers (CVE-2026-8461)."""

from __future__ import annotations

import pytest

from app.core import ffmpeg_inspect as fi


@pytest.mark.parametrize(
    "text,expected",
    [
        ("ffmpeg version 7.1.5-0+deb13u1 Copyright", (7, 1, 5)),
        ("ffmpeg version n8.1.2 Copyright", (8, 1, 2)),
        ("ffmpeg version 8.1 Copyright", (8, 1, 0)),
        ("ffmpeg version 2026-01-01-git-abcdef Copyright", None),
        ("", None),
    ],
)
def test_parse_version(text, expected):
    assert fi.parse_version(text) == expected


@pytest.mark.parametrize(
    "version,expected",
    [
        ((7, 1, 5), True),   # below 8.1.2 -> vulnerable
        ((8, 1, 1), True),
        ((8, 1, 2), False),  # exactly the minimum -> safe
        ((8, 2, 0), False),
        ((9, 0, 0), False),
        (None, None),        # unknown -> None
    ],
)
def test_is_vulnerable(version, expected):
    assert fi.is_vulnerable(version) is expected


def test_is_risky_codec_detects_magicyuv_case_insensitive():
    assert fi.is_risky_codec("magicyuv") is True
    assert fi.is_risky_codec("MagicYUV") is True
    assert fi.is_risky_codec("h264") is False
    assert fi.is_risky_codec(None) is False


async def test_get_info_reports_vulnerable(monkeypatch):
    async def fake_run(path, fallback):
        return (7, 1, 5)

    monkeypatch.setattr(fi, "_run_version", fake_run)
    info = await fi.get_info(refresh=True)
    assert info["ffmpeg_version"] == "7.1.5"
    assert info["ffmpeg_vulnerable"] is True
    assert info["min_version"] == "8.1.2"
    assert "magicyuv" in info["risky_codecs"]


async def test_get_info_reports_safe(monkeypatch):
    async def fake_run(path, fallback):
        return (8, 1, 2)

    monkeypatch.setattr(fi, "_run_version", fake_run)
    info = await fi.get_info(refresh=True)
    assert info["ffmpeg_vulnerable"] is False
    assert info["ffmpeg_available"] is True


async def test_get_info_unknown_when_unparseable(monkeypatch):
    async def fake_run(path, fallback):
        return None

    monkeypatch.setattr(fi, "_run_version", fake_run)
    info = await fi.get_info(refresh=True)
    assert info["ffmpeg_vulnerable"] is None
    assert info["ffmpeg_available"] is False
