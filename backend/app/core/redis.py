"""Shared async Redis client and channel names."""

from __future__ import annotations

from redis.asyncio import Redis

from app.core.config import get_settings

# Control commands: backend -> process manager (start/stop/restart an output).
CONTROL_CHANNEL = "castcore:control"
# Live status/log fan-out: process manager -> backend -> WebSocket clients.
STATUS_CHANNEL = "castcore:status"
LOGS_CHANNEL_PREFIX = "castcore:logs:"  # + job_id

_redis: Redis | None = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(get_settings().redis_url, decode_responses=True)
    return _redis
