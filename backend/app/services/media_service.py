"""Media library: scan a storage source and index files + ffprobe metadata.

Reusable by both the API (synchronous scan for small libraries) and, later, the arq
worker (background scans for large libraries).
"""

from __future__ import annotations

import asyncio
import datetime as dt
import json
import os
import shutil

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.media import MediaItem, MediaProbe
from app.models.storage import StorageSource
from app.services import storage_service

_VIDEO = {".mp4", ".mkv", ".mov", ".avi", ".ts", ".m2ts", ".flv", ".webm", ".mpg", ".mpeg", ".m4v"}
_AUDIO = {".mp3", ".aac", ".wav", ".m4a", ".flac", ".ogg", ".opus"}
_IMAGE = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
_SCAN_LIMIT = 5000
_PROBE_TIMEOUT_S = 12


def _kind(ext: str) -> str:
    ext = ext.lower()
    if ext in _VIDEO:
        return "video"
    if ext in _AUDIO:
        return "audio"
    if ext in _IMAGE:
        return "image"
    return "other"


def _fps(rate: str | None) -> float | None:
    if not rate or "/" not in rate:
        return None
    num, den = rate.split("/", 1)
    try:
        d = float(den)
        return round(float(num) / d, 3) if d else None
    except ValueError:
        return None


async def _ffprobe(abspath: str) -> dict | None:
    settings = get_settings()
    ffprobe = shutil.which(settings.ffprobe_path) or shutil.which("ffprobe")
    if not ffprobe:
        return None
    args = [ffprobe, "-v", "error", "-print_format", "json", "-show_streams", "-show_format", abspath]
    try:
        proc = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=_PROBE_TIMEOUT_S)
    except (OSError, asyncio.TimeoutError):
        return None
    if proc.returncode != 0:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def _build_probe(data: dict) -> dict:
    fmt = data.get("format", {})
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)

    def _int(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    return {
        "container": fmt.get("format_name"),
        "duration_s": float(fmt["duration"]) if fmt.get("duration") else None,
        "video_codec": video.get("codec_name") if video else None,
        "audio_codec": audio.get("codec_name") if audio else None,
        "width": _int(video.get("width")) if video else None,
        "height": _int(video.get("height")) if video else None,
        "fps": _fps(video.get("r_frame_rate")) if video else None,
        "video_bitrate": _int(video.get("bit_rate")) if video else None,
        "audio_bitrate": _int(audio.get("bit_rate")) if audio else None,
        "has_video": video is not None,
        "has_audio": audio is not None,
    }


async def scan_source(db: AsyncSession, source: StorageSource) -> dict:
    base = storage_service.effective_path(source)
    if not base or not os.path.isdir(base):
        raise ValueError("source path not available")

    res = await db.execute(select(MediaItem).where(MediaItem.storage_source_id == source.id))
    existing = {m.rel_path: m for m in res.scalars().all()}

    files = 0
    indexed = 0
    probed = 0
    for root, _dirs, names in os.walk(base):
        for name in names:
            if files >= _SCAN_LIMIT:
                break
            files += 1
            abspath = os.path.join(root, name)
            rel = os.path.relpath(abspath, base)
            ext = os.path.splitext(name)[1]
            kind = _kind(ext)
            try:
                st = os.stat(abspath)
            except OSError:
                continue

            item = existing.get(rel)
            unchanged = item is not None and item.size_bytes == st.st_size and abs(item.mtime - st.st_mtime) < 1
            if unchanged:
                continue

            if item is None:
                item = MediaItem(storage_source_id=source.id, rel_path=rel, filename=name)
                item.probe = None
                db.add(item)
            item.filename = name
            item.kind = kind
            item.size_bytes = st.st_size
            item.mtime = st.st_mtime
            indexed += 1

            if kind in ("video", "audio"):
                data = await _ffprobe(abspath)
                if data is not None:
                    p = _build_probe(data)
                    item.streamable = bool(p["has_video"] or p["has_audio"])
                    item.problem_flags = {} if item.streamable else {"unreadable": False, "no_av": True}
                    if item.probe is None:
                        item.probe = MediaProbe(media_item_id=item.id)
                    item.probe.container = p["container"]
                    item.probe.duration_s = p["duration_s"]
                    item.probe.video_codec = p["video_codec"]
                    item.probe.audio_codec = p["audio_codec"]
                    item.probe.width = p["width"]
                    item.probe.height = p["height"]
                    item.probe.fps = p["fps"]
                    item.probe.video_bitrate = p["video_bitrate"]
                    item.probe.audio_bitrate = p["audio_bitrate"]
                    item.probe.raw_ffprobe = data
                    item.probe.probed_at = dt.datetime.now(dt.timezone.utc)
                    probed += 1
                else:
                    item.streamable = False
                    item.problem_flags = {"unreadable": True}

    source.last_scan_at = dt.datetime.now(dt.timezone.utc)
    await db.flush()
    return {"files": files, "indexed": indexed, "probed": probed}
