"""Platform metadata resolution.

Description templates support placeholders that are filled from the stream job, its
source, the server and the current date/time. Resolved metadata is shown (and checked)
before a stream starts.

Supported placeholders:
  {stream_title} {date} {time} {platform} {category} {tags}
  {source_name} {server_name} {channel_name}
"""

from __future__ import annotations

import datetime as dt
import os

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.platform import PlatformMetadata
from app.models.streaming import StreamJob

PLACEHOLDERS = [
    "stream_title", "date", "time", "platform", "category", "tags",
    "source_name", "server_name", "channel_name",
]


def resolve_template(template: str | None, context: dict) -> str:
    if not template:
        return ""
    out = template
    for key in PLACEHOLDERS:
        out = out.replace("{" + key + "}", str(context.get(key, "")))
    return out


async def build_context(db: AsyncSession, job: StreamJob, meta: PlatformMetadata) -> dict:
    now = dt.datetime.now()
    source_name = ""
    if job.inputs:
        source_name = os.path.basename(job.inputs[0].uri) or job.inputs[0].uri
    return {
        # {stream_title} is the job's canonical name; the per-platform title is itself a
        # template that may reference {stream_title}, so they must not be the same value.
        "stream_title": job.name,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "platform": meta.platform,
        "category": meta.category or "",
        "tags": ", ".join(meta.tags or []),
        "source_name": source_name,
        "server_name": os.getenv("DOMAIN") or "castcore",
        "channel_name": "",
    }


async def resolve_metadata(db: AsyncSession, job: StreamJob, meta: PlatformMetadata) -> dict:
    ctx = await build_context(db, job, meta)
    title = resolve_template(meta.title, ctx) if (meta.title and "{" in meta.title) else (meta.title or job.name)
    description = resolve_template(meta.description_template, ctx)
    warnings: list[str] = []
    if not title:
        warnings.append("title.empty")
    if meta.platform in ("youtube",) and not meta.category:
        warnings.append("category.recommended")
    thumb_id = str(meta.thumbnail_asset_id) if meta.thumbnail_asset_id else None
    if not thumb_id:
        warnings.append("thumbnail.missing")
    return {
        "platform": meta.platform,
        "title": title,
        "description": description,
        "category": meta.category,
        "tags": meta.tags or [],
        "language": meta.language,
        "visibility": meta.visibility,
        "scheduled_start": meta.scheduled_start.isoformat() if meta.scheduled_start else None,
        "thumbnail_asset_id": thumb_id,
        "thumbnail_url": f"/api/v1/assets/{thumb_id}/file" if thumb_id else None,
        "warnings": warnings,
    }
