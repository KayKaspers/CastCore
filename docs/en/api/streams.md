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
| `POST` | `/api/v1/stream-jobs/{id}/preflight` | Run readiness check (🟢/🟡/🔴/⚪), persists a report |
| `GET` | `/api/v1/stream-jobs/{id}/preflight/latest` | Latest persisted report (or `null`) |
| `GET` | `/api/v1/stream-jobs/{id}/preflight/reports` | Report history (newest first) |
| `GET` | `/api/v1/stream-jobs/{id}/preflight/reports/{report_id}` | Single report |
| `POST` | `/api/v1/stream-jobs/{id}/dry-run` | Short test encode (speed/fps) |
| `POST` | `/api/v1/stream-jobs/{id}/start` · `/stop` · `/restart` | Process control (`start?override=true`: admin bypass of the preflight gate) |
| `POST` | `/api/v1/stream-jobs/{id}/recording` | Recording on/off |

> When the preflight gate is enabled (`PREFLIGHT_REQUIRED_BEFORE_START` /
> `PREFLIGHT_BLOCK_ON_RED`), `start` returns `409` with code `preflight.required` or
> `preflight.blocked`. Admins may pass `?override=true` (audited). See
> [Preflight checks](/docs/en/user-guide/preflight-checks.md).

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
