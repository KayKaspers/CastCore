"""Provider-specific platform adapters for pushing stream metadata.

The metadata push is **not** hard-wired into the stream service: each provider implements a
small adapter (``push``) that takes a validated access token + resolved metadata and calls the
real platform API. The orchestration (account lookup, token refresh, error shaping) lives in
``app.services.platform_push``.
"""

from __future__ import annotations

from app.services.platform.base import FieldRef, PlatformAdapter, PushOutcome
from app.services.platform.twitch import TwitchAdapter
from app.services.platform.youtube import YouTubeAdapter

ADAPTERS: dict[str, PlatformAdapter] = {
    "twitch": TwitchAdapter(),
    "youtube": YouTubeAdapter(),
}

__all__ = ["ADAPTERS", "FieldRef", "PushOutcome", "PlatformAdapter"]
