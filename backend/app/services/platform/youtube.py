"""YouTube metadata-push adapter (Data API v3, live broadcasts).

Updates the active (or upcoming) live broadcast's title/description/visibility/scheduled start
via ``liveBroadcasts.update`` and, optionally, uploads a thumbnail via ``thumbnails.set``
(scope ``https://www.googleapis.com/auth/youtube``).
"""

from __future__ import annotations

from app.core.errors import ErrorCode
from app.services.platform.base import PlatformAdapter, PushOutcome, map_http_error

_API = "https://www.googleapis.com/youtube/v3"
_UPLOAD = "https://www.googleapis.com/upload/youtube/v3"
_PRIVACY = {"public", "unlisted", "private"}


class YouTubeAdapter(PlatformAdapter):
    provider = "youtube"

    async def _find_broadcast(self, http, headers) -> tuple[dict | None, PushOutcome | None]:
        for status in ("active", "upcoming"):
            r = await http.get(
                f"{_API}/liveBroadcasts", headers=headers,
                params={"part": "id,snippet,status", "broadcastStatus": status, "broadcastType": "all"},
            )
            if r.status_code in (401, 403):
                return None, PushOutcome().fail(ErrorCode.PLATFORM_MISSING_SCOPE, provider="youtube")
            if r.status_code != 200:
                return None, PushOutcome().fail(ErrorCode.PLATFORM_API_ERROR, provider="youtube",
                                                status=r.status_code)
            items = r.json().get("items") or []
            if items:
                return items[0], None
        return None, PushOutcome().fail(ErrorCode.PLATFORM_INVALID_BROADCAST, provider="youtube")

    async def push(self, http, access_token, client_id, meta, *, thumbnail=None) -> PushOutcome:
        out = PushOutcome()
        headers = {"Authorization": f"Bearer {access_token}"}

        broadcast, err = await self._find_broadcast(http, headers)
        if err is not None:
            return err
        assert broadcast is not None
        bid = broadcast["id"]
        snippet = dict(broadcast.get("snippet") or {})
        status = dict(broadcast.get("status") or {})

        if meta.get("title"):
            snippet["title"] = meta["title"]
            out.applied.append("title")
        if meta.get("description") is not None:
            snippet["description"] = meta["description"]
            out.applied.append("description")
        if meta.get("scheduled_start"):
            snippet["scheduledStartTime"] = meta["scheduled_start"]
            out.applied.append("scheduled_start")
        if meta.get("visibility") in _PRIVACY:
            status["privacyStatus"] = meta["visibility"]
            out.applied.append("visibility")

        r = await http.put(
            f"{_API}/liveBroadcasts", headers=headers, params={"part": "id,snippet,status"},
            json={"id": bid, "snippet": snippet, "status": status},
        )
        if r.status_code in (401, 403):
            return out.fail(ErrorCode.PLATFORM_MISSING_SCOPE, provider="youtube")
        if r.status_code == 404:
            return out.fail(ErrorCode.PLATFORM_INVALID_BROADCAST, provider="youtube")
        if r.status_code != 200:
            out.error = map_http_error(r.status_code, provider="youtube")
            return out

        # optional thumbnail upload (a failure here is a warning, not a hard error)
        if thumbnail is not None:
            data, mime = thumbnail
            rt = await http.post(
                f"{_UPLOAD}/thumbnails/set", headers={**headers, "Content-Type": mime},
                params={"videoId": bid}, content=data,
            )
            if rt.status_code == 200:
                out.applied.append("thumbnail")
            else:
                out.warn(ErrorCode.PLATFORM_THUMBNAIL_FAILED, provider="youtube", status=rt.status_code)

        return out
