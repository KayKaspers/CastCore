---
title: "API: monitoring"
description: "System and output metrics."
lang: en
audience: "Developers / Integrators"
status: stable
lastReviewed: 2026-06-24
---

# API: monitoring

> System and stream metrics. Readable by any authenticated user.

**Audience:** developers / integrators.

## REST

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/monitoring/system` | CPU, RAM, disk, FFmpeg processes |
| `GET` | `/api/v1/monitoring/outputs` | Live metrics per output (fps, bitrate, speed, CPU, RAM) |
| `GET` | `/api/v1/health` · `/api/v1/system/health` | Liveness / readiness |

## WebSocket (live)

| Channel | Content |
| --- | --- |
| `WS /api/v1/ws/logs/{job_id}?token=<access>` | FFmpeg log lines `{line, level, hint}` |
| `WS /api/v1/ws/status?token=<access>` | status changes + per-output metrics |

Browsers can't set headers on WebSockets → pass the token as `?token=`.

## Example: system metrics

```json
{ "cpu_percent": 13.2, "mem_percent": 39.4, "disk_percent": 0.6, "ffmpeg_processes": 2 }
```

## Related pages

- [Monitoring (UI)](/docs/en/user-guide/monitoring.md) · [Performance](/docs/en/troubleshooting/performance.md)

---
_Last reviewed: 2026-06-24 · Status: stable_
