---
title: "WebSockets / SSE"
description: "Live logs and status over WebSockets."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# WebSockets / SSE

> Live logs and status updates run over WebSockets.

**Audience:** developers.

## Channels

| Endpoint | Content |
| --- | --- |
| `WS /api/v1/ws/logs/{job_id}` | FFmpeg log lines `{output_id, line, level, hint, ts}` |
| `WS /api/v1/ws/status` | status changes + per-output metrics |

## Data flow

The **process manager** publishes to Redis (`castcore:logs:<job>` / `:status`); the
backend subscribes via Redis pub/sub and forwards the messages to the WebSocket clients.

## Authentication

Browsers cannot set **headers** on WebSockets → the access token is passed as the
`?token=` query parameter and validated on connect.

## Implementation

- Backend: `app/api/v1/endpoints/ws.py` (relay + disconnect detection).
- Frontend: `lib/useLogStream.ts` (hook) + `components/LogsPanel.tsx`.

## Reverse proxy

The proxy must forward Upgrade/Connection headers (Caddy does this automatically).

## Related pages

- [Process manager](/docs/en/developer-guide/process-manager.md) · [API: monitoring](/docs/en/api/monitoring.md)

---
_Last reviewed: 2026-06-24 · Status: stable_
