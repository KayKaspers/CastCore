"""WebSocket endpoints for live logs and status.

Browsers cannot set an Authorization header on a WebSocket, so the access token is
passed as a ``?token=`` query parameter and validated on connect.

The backend subscribes to the Redis channels populated by the Process Manager and
fans messages out to the connected client.
"""

from __future__ import annotations

import asyncio

import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.redis import LOGS_CHANNEL_PREFIX, STATUS_CHANNEL, get_redis
from app.core.security import decode_token

router = APIRouter(tags=["ws"])


def _authorized(token: str | None) -> bool:
    if not token:
        return False
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        return False
    return payload.get("type") == "access"


async def _forward(ws: WebSocket, pubsub) -> None:
    async for message in pubsub.listen():
        if message.get("type") == "message":
            await ws.send_text(message["data"])


async def _drain(ws: WebSocket) -> None:
    """Consume client frames so a disconnect is detected even when idle."""
    while True:
        await ws.receive_text()


async def _relay(ws: WebSocket, channel: str) -> None:
    """Subscribe to a Redis channel and forward every message to the WebSocket."""
    redis = get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)
    forward = asyncio.create_task(_forward(ws, pubsub))
    drain = asyncio.create_task(_drain(ws))
    try:
        await asyncio.wait({forward, drain}, return_when=asyncio.FIRST_COMPLETED)
    except WebSocketDisconnect:
        pass
    finally:
        forward.cancel()
        drain.cancel()
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()


@router.websocket("/ws/logs/{job_id}")
async def ws_logs(ws: WebSocket, job_id: str) -> None:
    if not _authorized(ws.query_params.get("token")):
        await ws.close(code=1008)
        return
    await ws.accept()
    await _relay(ws, f"{LOGS_CHANNEL_PREFIX}{job_id}")


@router.websocket("/ws/status")
async def ws_status(ws: WebSocket) -> None:
    if not _authorized(ws.query_params.get("token")):
        await ws.close(code=1008)
        return
    await ws.accept()
    await _relay(ws, STATUS_CHANNEL)
