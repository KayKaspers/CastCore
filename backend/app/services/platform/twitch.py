"""Twitch metadata-push adapter (Helix API).

Sets channel title, category (game), language and tags via
``PATCH /helix/channels`` (scope ``channel:manage:broadcast``). The category name is resolved
to a game id via ``GET /helix/games``; the broadcaster id via ``GET /helix/users``.
"""

from __future__ import annotations

from app.core.errors import ErrorCode
from app.services.platform.base import PlatformAdapter, PushOutcome, map_http_error

_API = "https://api.twitch.tv/helix"


class TwitchAdapter(PlatformAdapter):
    provider = "twitch"

    async def push(self, http, access_token, client_id, meta, *, thumbnail=None) -> PushOutcome:
        out = PushOutcome()
        headers = {"Authorization": f"Bearer {access_token}", "Client-Id": client_id}

        # 1) broadcaster id
        r = await http.get(f"{_API}/users", headers=headers)
        if r.status_code in (401, 403):
            return out.fail(ErrorCode.PLATFORM_MISSING_SCOPE, provider="twitch")
        if r.status_code != 200:
            return out.fail(ErrorCode.PLATFORM_API_ERROR, provider="twitch", status=r.status_code)
        users = r.json().get("data") or []
        if not users:
            return out.fail(ErrorCode.PLATFORM_API_ERROR, provider="twitch", status=r.status_code)
        broadcaster_id = users[0]["id"]

        body: dict = {}
        if meta.get("title"):
            body["title"] = meta["title"]
            out.applied.append("title")
        if meta.get("language"):
            body["broadcaster_language"] = meta["language"]
            out.applied.append("language")
        if meta.get("tags"):
            body["tags"] = list(meta["tags"])
            out.applied.append("tags")

        # 2) resolve category -> game_id (a typo is a warning, not a hard failure)
        if meta.get("category"):
            rg = await http.get(f"{_API}/games", headers=headers, params={"name": meta["category"]})
            games = rg.json().get("data") or [] if rg.status_code == 200 else []
            if games:
                body["game_id"] = games[0]["id"]
                out.applied.append("category")
            else:
                out.warn(ErrorCode.PLATFORM_INVALID_CATEGORY, provider="twitch", category=meta["category"])

        if not body:
            return out  # nothing to apply

        # 3) update channel
        r = await http.patch(
            f"{_API}/channels", headers=headers,
            params={"broadcaster_id": broadcaster_id}, json=body,
        )
        if r.status_code in (200, 204):
            return out
        if r.status_code in (401, 403):
            return out.fail(ErrorCode.PLATFORM_MISSING_SCOPE, provider="twitch")
        out.error = map_http_error(r.status_code, provider="twitch")
        return out
