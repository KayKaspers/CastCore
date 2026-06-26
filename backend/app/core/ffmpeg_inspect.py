"""FFmpeg/ffprobe version detection and codec-risk helpers.

Background: CVE-2026-8461 ("PixelSmash") affects FFmpeg's MagicYUV decoder in libavcodec
in versions **before 8.1.2**; a crafted media file can trigger it during decoding. CastCore
therefore detects the installed FFmpeg/ffprobe version, flags vulnerable builds, and treats
risky codecs (MagicYUV) specially. See docs/admin-guide/ffmpeg-requirements.

Advisory details (affected versions, codec) are operator-provided parameters here — verify
against authoritative sources (NVD) for your environment.
"""

from __future__ import annotations

import asyncio
import re
import shutil

from app.core.config import get_settings

# Minimum non-vulnerable FFmpeg version per the advisory.
MIN_FFMPEG_VERSION: tuple[int, int, int] = (8, 1, 2)

# Codecs known to be risky to decode from untrusted input (extend via BLOCK_RISKY_CODECS /
# RISKY_CODECS_BLOCKLIST). MagicYUV is the CVE-2026-8461 vector.
DEFAULT_RISKY_CODECS = frozenset({"magicyuv"})

_VERSION_RE = re.compile(r"version\s+n?(\d+)\.(\d+)(?:\.(\d+))?")
_PROBE_TIMEOUT_S = 5

_cache: dict | None = None


def parse_version(output: str) -> tuple[int, int, int] | None:
    """Parse a major.minor.patch tuple from `ffmpeg -version` output, or None if unknown."""
    m = _VERSION_RE.search(output or "")
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3) or 0))


def is_vulnerable(version: tuple[int, int, int] | None) -> bool | None:
    """True if below the minimum, False if at/above, None if version is unknown."""
    if version is None:
        return None
    return version < MIN_FFMPEG_VERSION


def version_str(version: tuple[int, int, int] | None) -> str | None:
    return ".".join(str(p) for p in version) if version else None


def risky_codecs() -> frozenset[str]:
    """Configured codec blocklist (lower-cased), seeded with the defaults."""
    settings = get_settings()
    extra = {c.strip().lower() for c in (settings.risky_codecs_blocklist or "").split(",") if c.strip()}
    return frozenset(DEFAULT_RISKY_CODECS | extra)


def is_risky_codec(codec_name: str | None) -> bool:
    if not codec_name:
        return False
    return codec_name.strip().lower() in risky_codecs()


async def _run_version(binary_path: str, fallback: str) -> tuple[int, int, int] | None:
    exe = shutil.which(binary_path) or shutil.which(fallback)
    if not exe:
        return None
    try:
        proc = await asyncio.create_subprocess_exec(
            exe, "-version",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
        )
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=_PROBE_TIMEOUT_S)
    except (OSError, asyncio.TimeoutError):
        return None
    return parse_version(out.decode("utf-8", "replace"))


async def get_info(refresh: bool = False) -> dict:
    """Return FFmpeg/ffprobe version & vulnerability info (cached for the process lifetime)."""
    global _cache
    if _cache is not None and not refresh:
        return _cache
    settings = get_settings()
    ff = await _run_version(settings.ffmpeg_path, "ffmpeg")
    fp = await _run_version(settings.ffprobe_path, "ffprobe")
    _cache = {
        "ffmpeg_version": version_str(ff),
        "ffprobe_version": version_str(fp),
        "ffmpeg_available": ff is not None,
        "ffprobe_available": fp is not None,
        "min_version": version_str(MIN_FFMPEG_VERSION),
        # True = vulnerable, False = safe, None = unknown (could not determine version)
        "ffmpeg_vulnerable": is_vulnerable(ff),
        "ffprobe_vulnerable": is_vulnerable(fp),
        "risky_codecs": sorted(risky_codecs()),
        "safe_media_processing_enabled": settings.safe_media_processing_enabled,
        "media_autothumbnails_enabled": settings.media_autothumbnails_enabled,
        "block_risky_codecs": settings.block_risky_codecs,
    }
    return _cache
