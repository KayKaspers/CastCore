"""Playlist resolution — turn a playlist into an ordered list of playable media.

Used by the UI (preview/total duration) and, in Phase 3, by linear channel playout.
"""

from __future__ import annotations

import random

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import MediaItem
from app.models.playlist import Playlist
from app.models.storage import StorageSource
from app.services import storage_service


async def resolve(db: AsyncSession, playlist: Playlist) -> tuple[list[dict], float]:
    """Return (entries, total_duration_s). Entries carry the absolute media path."""
    source_cache: dict[str, StorageSource] = {}
    entries: list[dict] = []
    total = 0.0

    for item in playlist.items:
        if not item.enabled:
            continue
        media = await db.get(MediaItem, item.media_item_id)
        if media is None:
            continue
        sid = str(media.storage_source_id)
        source = source_cache.get(sid)
        if source is None:
            source = await db.get(StorageSource, media.storage_source_id)
            if source is not None:
                source_cache[sid] = source
        base = storage_service.effective_path(source) if source else None
        abs_path = f"{base.rstrip('/')}/{media.rel_path}" if base else media.rel_path
        duration = media.probe.duration_s if (media.probe and media.probe.duration_s) else None
        entries.append({
            "media_item_id": str(media.id),
            "filename": media.filename,
            "abs_path": abs_path,
            "duration_s": duration,
        })
        if duration:
            total += duration

    if playlist.mode == "shuffle":
        random.shuffle(entries)
    return entries, round(total, 1)
