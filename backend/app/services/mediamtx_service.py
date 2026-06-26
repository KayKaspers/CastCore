"""Read-only MediaMTX integration.

MediaMTX is an optional media router (RTSP/RTMP/SRT/WebRTC/HLS). When enabled, CastCore
queries its v3 HTTP API to surface live ingest status — which paths exist and whether a
publisher is currently connected. This module never mutates MediaMTX state.
"""

from __future__ import annotations

import httpx

from app.core.config import get_settings

_TIMEOUT = 5.0


class IngestPath:
    """A normalized view of one MediaMTX path."""

    def __init__(self, raw: dict) -> None:
        self.name: str = raw.get("name", "")
        self.ready: bool = bool(raw.get("ready"))
        # source is null when nobody is publishing
        source = raw.get("source") or {}
        self.source_type: str | None = source.get("type") if isinstance(source, dict) else None
        self.tracks: list[str] = list(raw.get("tracks") or [])
        self.bytes_received: int = int(raw.get("bytesReceived") or 0)
        self.bytes_sent: int = int(raw.get("bytesSent") or 0)
        self.readers: int = len(raw.get("readers") or [])
        self.ready_time: str | None = raw.get("readyTime")

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "ready": self.ready,
            "source_type": self.source_type,
            "tracks": self.tracks,
            "bytes_received": self.bytes_received,
            "bytes_sent": self.bytes_sent,
            "readers": self.readers,
            "ready_time": self.ready_time,
        }


async def get_status() -> dict:
    """Return ``{enabled, reachable, paths}``.

    ``reachable`` is False (and ``paths`` empty) if MediaMTX is disabled or the API call
    fails — callers should render that as an offline hint, not an error.
    """
    settings = get_settings()
    if not settings.mediamtx_enabled:
        return {"enabled": False, "reachable": False, "paths": []}

    url = settings.mediamtx_api_url.rstrip("/") + "/v3/paths/list"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            res = await client.get(url)
            res.raise_for_status()
            data = res.json()
    except (httpx.HTTPError, ValueError):
        return {"enabled": True, "reachable": False, "paths": []}

    items = data.get("items") if isinstance(data, dict) else None
    paths = [IngestPath(item).as_dict() for item in (items or [])]
    return {"enabled": True, "reachable": True, "paths": paths}
