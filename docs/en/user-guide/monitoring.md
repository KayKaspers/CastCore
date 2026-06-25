---
title: "Monitoring"
description: "Live system and stream metrics: CPU, RAM, FPS, bitrate."
lang: en
audience: "Users / Operators"
status: stable
lastReviewed: 2026-06-24
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

## Related pages

- [Stream jobs](/docs/en/user-guide/streams.md)
- [Performance](/docs/en/troubleshooting/performance.md)
- [API: monitoring](/docs/en/api/monitoring.md)

---
_Last reviewed: 2026-06-24 · Status: stable_
