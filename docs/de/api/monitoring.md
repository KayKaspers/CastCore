---
title: "API: Monitoring"
description: "System- und Output-Metriken."
lang: de
audience: "Entwickler / Integratoren"
status: stable
lastReviewed: 2026-06-24
---

# API: Monitoring

> System- und Stream-Metriken. Für jeden angemeldeten Nutzer lesbar.

**Zielgruppe:** Entwickler / Integratoren.

## REST

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET` | `/api/v1/monitoring/system` | CPU, RAM, Disk, FFmpeg-Prozesse |
| `GET` | `/api/v1/monitoring/outputs` | Live-Metriken pro Output (fps, bitrate, speed, CPU, RAM) |
| `GET` | `/api/v1/health` · `/api/v1/system/health` | Liveness / Readiness |

## WebSocket (Live)

| Kanal | Inhalt |
| --- | --- |
| `WS /api/v1/ws/logs/{job_id}?token=<access>` | FFmpeg-Logzeilen `{line, level, hint}` |
| `WS /api/v1/ws/status?token=<access>` | Statuswechsel + Metriken pro Output |

Browser können keine Header auf WebSockets setzen → Token als `?token=` übergeben.

## Beispiel: System-Metriken

```json
{ "cpu_percent": 13.2, "mem_percent": 39.4, "disk_percent": 0.6, "ffmpeg_processes": 2 }
```

## Verwandte Seiten

- [Monitoring (UI)](/docs/de/user-guide/monitoring.md) · [Performance](/docs/de/troubleshooting/performance.md)

---
_Stand: 2026-06-24 · Status: Stabil_
