---
title: "WebSockets / SSE"
description: "Live-Logs und Status über WebSockets."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# WebSockets / SSE

> Live-Logs und Statusupdates laufen über WebSockets.

**Zielgruppe:** Entwickler.

## Kanäle

| Endpoint | Inhalt |
| --- | --- |
| `WS /api/v1/ws/logs/{job_id}` | FFmpeg-Logzeilen `{output_id, line, level, hint, ts}` |
| `WS /api/v1/ws/status` | Statuswechsel + Metriken pro Output |

## Datenfluss

Der **Process Manager** published nach Redis (`castcore:logs:<job>` / `:status`); das
Backend abonniert per Redis-Pub/Sub und reicht die Nachrichten an die WebSocket-Clients
weiter.

## Authentifizierung

Browser können auf WebSockets **keine Header** setzen → der Access-Token wird als
Query-Parameter `?token=` übergeben und beim Connect validiert.

## Implementierung

- Backend: `app/api/v1/endpoints/ws.py` (Relay + Disconnect-Erkennung).
- Frontend: `lib/useLogStream.ts` (Hook) + `components/LogsPanel.tsx`.

## Reverse Proxy

Der Proxy muss Upgrade/Connection-Header durchreichen (Caddy automatisch).

## Verwandte Seiten

- [Process Manager](/docs/de/developer-guide/process-manager.md) · [API: Monitoring](/docs/de/api/monitoring.md)

---
_Stand: 2026-06-24 · Status: Stabil_
