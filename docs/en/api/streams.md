---
title: "API: streams"
description: "Stream jobs, profiles, start/stop, preflight."
lang: en
audience: "Developers / Integrators"
status: stable
lastReviewed: 2026-06-24
---

# API: streams

> Stream jobs, FFmpeg profiles, destinations and process control. All routes require at
> least **operator**.

**Audience:** developers / integrators.

## Stream jobs

| Method | Path | Purpose |
| --- | --- | --- |
| `GET/POST` | `/api/v1/stream-jobs` | List / create (with inputs/outputs) |
| `GET/DELETE` | `/api/v1/stream-jobs/{id}` | Detail / delete |
| `POST` | `/api/v1/stream-jobs/{id}/preview` | Masked command preview |
| `POST` | `/api/v1/stream-jobs/{id}/preflight` | Readiness check (🟢/🟡/🔴) |
| `POST` | `/api/v1/stream-jobs/{id}/dry-run` | Short test encode (speed/fps) |
| `POST` | `/api/v1/stream-jobs/{id}/start` · `/stop` · `/restart` | Process control |
| `POST` | `/api/v1/stream-jobs/{id}/recording` | Recording on/off |

## Profiles & destinations

| Method | Path | Purpose |
| --- | --- | --- |
| `GET/POST/PATCH/DELETE` | `/api/v1/ffmpeg-profiles[/{id}]` | FFmpeg profiles |
| `GET/POST/PATCH/DELETE` | `/api/v1/destinations[/{id}]` | Destinations (stream key write-only) |
| `POST` | `/api/v1/ffmpeg/preview` | Command from inputs/outputs (masked) |

## Metadata (per job/platform)

| Method | Path | Purpose |
| --- | --- | --- |
| `GET/PUT/DELETE` | `/api/v1/stream-jobs/{id}/metadata/{platform}` | Metadata per platform |
| `GET` | `/api/v1/stream-jobs/{id}/metadata/{platform}/resolved` | Resolved preview |
| `POST` | `/api/v1/metadata/resolve` | Resolve a template generically |

## Live logs

`WS /api/v1/ws/logs/{job_id}?token=<access>` – see [Monitoring](/docs/en/api/monitoring.md).

## Related pages

- [Stream jobs (UI)](/docs/en/user-guide/streams.md) · [FFmpeg profiles](/docs/en/reference/ffmpeg-profiles.md)

---
_Last reviewed: 2026-06-24 · Status: stable_
