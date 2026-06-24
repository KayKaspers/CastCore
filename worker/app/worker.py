"""CastCore worker (arq) — bounded async jobs.

Handles media scanning, ffprobe analysis, thumbnail generation, backups and other
short-lived tasks. Long-running FFmpeg *streams* are NOT handled here — those are
supervised by the Process Manager. See docs/ARCHITECTURE.md.
"""

from __future__ import annotations

import os

from arq.connections import RedisSettings


async def scan_source(ctx: dict, source_id: str) -> dict:
    """Index a storage source: walk files, record media_library_items (Phase 2)."""
    # TODO(Phase 2): walk the mounted path, upsert media_library_items.
    return {"source_id": source_id, "indexed": 0}


async def probe_media(ctx: dict, media_item_id: str) -> dict:
    """Run ffprobe on a media item and store media_probe_data (Phase 2)."""
    # TODO(Phase 2): subprocess_exec(ffprobe, -v quiet -print_format json -show_streams ...)
    return {"media_item_id": media_item_id, "probed": False}


async def generate_thumbnail(ctx: dict, media_item_id: str) -> dict:
    """Generate a thumbnail via FFmpeg (Phase 2)."""
    return {"media_item_id": media_item_id, "thumbnail": None}


async def run_backup(ctx: dict, reason: str = "manual") -> dict:
    """Create a backup archive of DB + config + profiles (Phase 1 basic)."""
    return {"reason": reason, "status": "todo"}


class WorkerSettings:
    """arq entrypoint: `arq app.worker.WorkerSettings`."""

    functions = [scan_source, probe_media, generate_thumbnail, run_backup]
    redis_settings = RedisSettings(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        password=os.getenv("REDIS_PASSWORD") or None,
    )
