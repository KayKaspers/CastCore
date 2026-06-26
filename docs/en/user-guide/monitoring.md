---
title: "Monitoring"
description: "Live system and stream metrics: CPU, RAM, FPS, bitrate."
lang: en
audience: "Users / Operators"
status: stable
lastReviewed: 2026-06-25
---

# Monitoring

> Monitoring shows system and stream metrics in real time. It auto-refreshes every 2
> seconds.

**Audience:** users / operators / viewers. UI area: **Monitoring** (`/monitoring`).

## System metrics

| Tile | Meaning |
| --- | --- |
| **CPU** | Overall host CPU usage. |
| **RAM** | Memory usage (used/total). |
| **Disk** | Usage of the data directory, free space. |
| **FFmpeg** | Number of running FFmpeg processes. |

## Output table

Per active output: **status**, **FPS**, **kbit/s**, **speed**, **CPU%**, **RAM**. Values
come from the process manager (psutil + FFmpeg progress) and are reconciled into the
database.

## Important signals

> ⚠️ **Speed < 1.0×** (highlighted yellow) means real-time isn't kept – typically under
> high load. See [Performance](/docs/en/troubleshooting/performance.md).

## Notes

> 💡 FPS/bitrate appear once FFmpeg emits progress lines; CPU/RAM after a few seconds of
> process runtime.

## Ingest (MediaMTX)

When the optional **MediaMTX** integration is enabled, an **Ingest (MediaMTX)** panel
appears below the outputs table. It shows the router's reachability and every active ingest
path (path name, live/ready, source, tracks, received bytes, readers). Setup:
[MediaMTX integration](/docs/en/admin-guide/mediamtx.md).

## Prometheus / Grafana

CastCore exposes a **Prometheus exporter** at `/api/v1/metrics` (standard text format).
Metrics include `castcore_cpu_percent`, `castcore_mem_percent`,
`castcore_disk_free_bytes`, `castcore_ffmpeg_processes`, `castcore_outputs_running` and
per-output `castcore_output_fps|bitrate_kbps|speed|cpu_percent|rss_mb` (label `output_id`).

A preconfigured Prometheus service ships in the **monitoring** compose profile:

```bash
docker compose --profile monitoring up -d
```

> ⚠️ The `/metrics` endpoint is **unauthenticated** (Prometheus convention). Labels only
> contain UUIDs (no job names). Restrict it at the reverse proxy in production.

## Related pages

- [Stream jobs](/docs/en/user-guide/streams.md)
- [Performance](/docs/en/troubleshooting/performance.md)
- [API: monitoring](/docs/en/api/monitoring.md)
- [MediaMTX integration](/docs/en/admin-guide/mediamtx.md)

---
_Last reviewed: 2026-06-25 · Status: stable_
