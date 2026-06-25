"""Linear channel playout: loop a playlist via the FFmpeg concat demuxer into HLS.

A channel is a long-running supervised FFmpeg process (driven through the same control
channel as stream jobs). It reads a generated concat list, loops it forever, re-encodes
to a constant HLS output, and optionally feeds EPG/M3U exports.
"""

from __future__ import annotations

import datetime as dt
import os
import uuid
from pathlib import Path
from xml.sax.saxutils import escape

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import CastCoreError, ErrorCode
from app.models.channel import Channel
from app.models.playlist import Playlist
from app.models.streaming import FFmpegProfile
from app.services import control, playlist_service

_DEFAULT_DURATION = 300.0  # fallback per-item duration for EPG when unknown


def channel_dir(channel_id: uuid.UUID) -> Path:
    return Path(get_settings().data_dir) / "channels" / str(channel_id)


def hls_dir(channel_id: uuid.UUID) -> Path:
    return channel_dir(channel_id) / "hls"


def _write_concat(path: Path, entries: list[dict]) -> None:
    lines = []
    for e in entries:
        # concat demuxer format; escape single quotes in paths.
        safe = e["abs_path"].replace("'", "'\\''")
        lines.append(f"file '{safe}'")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_argv(channel: Channel, profile: FFmpegProfile | None, concat_file: Path, out_dir: Path) -> list[str]:
    settings = get_settings()
    argv = [
        settings.ffmpeg_path, "-hide_banner", "-loglevel", "info",
        "-re", "-stream_loop", "-1",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
    ]
    vcodec = "libx264"
    if profile and not profile.copy_mode and profile.video:
        vcodec = profile.video.get("codec", "libx264")
    argv += ["-c:v", vcodec, "-preset", "veryfast", "-g", "60", "-pix_fmt", "yuv420p"]
    argv += ["-c:a", "aac", "-b:a", "160k"]
    argv += [
        "-f", "hls", "-hls_time", "4", "-hls_list_size", "6",
        "-hls_flags", "delete_segments+append_list+omit_endlist",
        "-hls_segment_filename", str(out_dir / "seg_%05d.ts"),
        str(out_dir / "index.m3u8"),
    ]
    return argv


async def start_channel(db: AsyncSession, channel: Channel) -> list[str]:
    entries: list[dict] = []
    if channel.playlist_id is not None:
        playlist = await db.get(Playlist, channel.playlist_id)
        if playlist is not None:
            entries, _total = await playlist_service.resolve(db, playlist)

    # Drop media that no longer exists on disk so one missing file can't kill the channel.
    entries = [e for e in entries if os.path.isfile(e["abs_path"])]

    # Fallback: loop a configured fallback video when nothing playable remains.
    if not entries:
        if channel.fallback_uri and os.path.isfile(channel.fallback_uri):
            entries = [{"abs_path": channel.fallback_uri, "filename": "fallback", "duration_s": None}]
        else:
            raise CastCoreError(ErrorCode.FFMPEG_NO_INPUT, params={"channel": "no playable media"})

    base = channel_dir(channel.id)
    out_dir = hls_dir(channel.id)
    out_dir.mkdir(parents=True, exist_ok=True)
    concat_file = base / "concat.txt"
    _write_concat(concat_file, entries)

    profile = await db.get(FFmpegProfile, channel.ffmpeg_profile_id) if channel.ffmpeg_profile_id else None
    argv = _build_argv(channel, profile, concat_file, out_dir)

    output_id = uuid.uuid4()
    channel.output_id = output_id
    channel.status = "running"
    await control.send_start(str(output_id), argv, job_id=str(channel.id))
    return argv


async def stop_channel(db: AsyncSession, channel: Channel) -> None:
    if channel.output_id is not None:
        await control.send_stop(str(channel.output_id), job_id=str(channel.id))
    channel.status = "stopped"


# --- exports ---
def _xmltv_time(t: dt.datetime) -> str:
    return t.strftime("%Y%m%d%H%M%S +0000")


async def build_epg(db: AsyncSession, channel: Channel, hours: int = 6) -> str:
    entries: list[dict] = []
    if channel.playlist_id is not None:
        playlist = await db.get(Playlist, channel.playlist_id)
        if playlist is not None:
            entries, _ = await playlist_service.resolve(db, playlist)
    if not entries:
        entries = [{"filename": channel.name, "duration_s": _DEFAULT_DURATION}]

    cid = str(channel.id)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    end = now + dt.timedelta(hours=hours)
    progs: list[str] = []
    t = now
    i = 0
    while t < end:
        e = entries[i % len(entries)]
        dur = e.get("duration_s") or _DEFAULT_DURATION
        stop = t + dt.timedelta(seconds=dur)
        progs.append(
            f'<programme start="{_xmltv_time(t)}" stop="{_xmltv_time(stop)}" channel="{cid}">'
            f'<title lang="de">{escape(e["filename"])}</title></programme>'
        )
        t = stop
        i += 1

    head = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<tv generator-info-name="CastCore">'
        f'<channel id="{cid}"><display-name>{escape(channel.name)}</display-name></channel>'
    )
    return head + "".join(progs) + "</tv>"


def build_m3u(channels: list[Channel], base_url: str) -> str:
    lines = ["#EXTM3U"]
    for ch in channels:
        url = f"{base_url.rstrip('/')}/api/v1/channels/{ch.id}/hls/index.m3u8"
        lines.append(f'#EXTINF:-1 tvg-id="{ch.id}" tvg-name="{escape(ch.name)}",{ch.name}')
        lines.append(url)
    return "\n".join(lines) + "\n"
