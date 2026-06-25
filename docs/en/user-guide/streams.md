---
title: "Stream jobs"
description: "Create, start, stop and monitor stream jobs."
lang: en
audience: "Users / Operators"
status: stable
lastReviewed: 2026-06-24
---

# Stream jobs

> A **stream job** connects one or more sources (inputs) to one or more destinations
> (outputs) and is driven via FFmpeg.

**Audience:** users / operators. UI area: **Stream jobs** (`/streams`).

## What this page does

The list shows all stream jobs with a **status badge** and actions. From here you start,
stop and monitor streams.

## Actions per job

| Action | Effect |
| --- | --- |
| **Start** | Builds the FFmpeg command and starts the process(es). |
| **Stop** | Cleanly terminates the running processes. |
| **Restart** | Stop + start (e.g. after a profile change). |
| **Live logs** | Real-time FFmpeg output incl. plain-language hints. |
| **Meta** | Maintain [platform metadata](/docs/en/user-guide/metadata-thumbnails.md). |
| **Preflight** | [Readiness check](/docs/en/user-guide/preflight-checks.md) (🟢/🟡/🔴). |
| **⌘ (preview)** | Masked FFmpeg command preview (stream keys hidden). |
| **✕** | Delete the job. |

## Status values

- `stopped` – not active
- `starting` – being started
- `running` – live
- `failed` – process failed (see logs)

Status is **reconciled automatically** from the real process state.

## Step by step: start a job

1. Select a job (or create one → [Stream editor](/docs/en/user-guide/stream-editor.md)).
2. Run **Preflight** – proceed if green/yellow.
3. Click **Start**, open **Live logs** and watch progress.

## Self-healing (auto-restart)

If you enable **auto-restart on failure** when creating the job, CastCore automatically
restarts an output after an **unexpected crash** – up to **max. retries** times, with a
short delay. A **deliberate stop** does not trigger a restart; a successful run resets the
counter.

> 💡 Ideal for 24/7 operation. The reconnect count per output is shown in
> [Monitoring](/docs/en/user-guide/monitoring.md).

## Notes

> 💡 With multi-output, **one FFmpeg process per active output** is supervised.

> 🔐 Stream keys are **masked** in the command preview and logs.

## If something fails

- [Stream not starting](/docs/en/troubleshooting/stream-not-starting.md)
- [FFmpeg errors](/docs/en/troubleshooting/ffmpeg-errors.md)

## Related pages

- [Stream editor](/docs/en/user-guide/stream-editor.md)
- [Monitoring](/docs/en/user-guide/monitoring.md)
- [Recordings & replay](/docs/en/user-guide/recordings-replay.md)

---
_Last reviewed: 2026-06-24 · Status: stable_
