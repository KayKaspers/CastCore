---
title: "Preflight checks"
description: "Check before start whether a job is ready (traffic light), persisted as a report."
lang: en
audience: "Users / Operators"
status: stable
lastReviewed: 2026-06-29
---

# Preflight checks

> The preflight check verifies **before** stream start whether a job is ready, returns a
> traffic-light result, and **persists a structured report** so the result survives restarts
> and feeds the health score and diagnostics engine.

**Audience:** users / operators. Invoke: **Stream jobs → Preflight**.

## Result traffic light

- 🟢 **Green** – ready to start.
- 🟡 **Yellow** – warnings (e.g. no audio), start still possible.
- 🔴 **Red** – blocking errors, start not advisable.
- ⚪ **Gray** – no checks ran yet (no report).

A report also carries a separate **`can_start`** flag: it is `false` only when a **blocking
error** is present. A red report without blocking errors can still allow start.

## Checked items

Each check has a stable `code`, a `category`, a level (`ok` / `warn` / `error`) and — for
errors — a `blocking` flag. Checks reference a docs page and never include secrets.

| Check | Category | Meaning |
| --- | --- | --- |
| **input_defined** | input | At least one input source is defined. |
| **source_readable** | input | Source is readable with ffprobe. |
| **has_video / has_audio** | input | Input contains a video / audio track. |
| **risky_codec** | security | Input uses a risky codec (e.g. MagicYUV → CVE-2026-8461). |
| **ffmpeg_version** | security | FFmpeg version is known and not flagged vulnerable. |
| **output_enabled** | output | At least one enabled output exists. |
| **destination_set** | output | The output has a destination assigned. |
| **stream_key** | output | Stream key present (platform/RTMP destinations). |
| **output_writable** | output | Local/recording output path is writable. |
| **recording_path** | storage | Recording directory exists and is writable. |
| **disk_space** | storage | Enough free space for recordings. |
| **platform_connected** | platform | A connected account exists (Twitch/YouTube). |
| **platform_ready** | platform | Cached platform readiness (no live API call here). |
| **metadata_complete** | platform | Platform metadata (e.g. title) is filled in. |

## Persisted reports

Every preflight run is stored. You can review history without re-probing the source:

- **Latest report:** the most recent result for a job.
- **History:** the last reports (newest first).
- **Stale:** a report older than `PREFLIGHT_REPORT_TTL_SECONDS` (default 600 s) is marked
  `stale`. The health score and the start gate only trust **non-stale** reports.

> 🔒 Reports **never** contain secrets, tokens or stream keys.

## Start gate (optional)

Admins can require preflight before a stream may start (off by default):

| Setting | Effect |
| --- | --- |
| `PREFLIGHT_REQUIRED_BEFORE_START` | Start is refused unless a **fresh** (non-stale) report exists. |
| `PREFLIGHT_BLOCK_ON_RED` | Start is refused while the latest report has `can_start = false`. |
| `PREFLIGHT_REPORT_TTL_SECONDS` | TTL after which a report counts as stale (default 600). |

When the gate blocks a start, the API returns `409` with code `preflight.required` or
`preflight.blocked`. **Admins** can override (the override is written to the audit log);
operators must fix the underlying problem first.

## Step by step

1. Click **Preflight** on a job.
2. Fix red/blocking items first (source, output, stream key, disk space).
3. **Start** when green/yellow. If the start gate blocks you, re-run preflight (or, as an
   admin, override).

## Dry-run / test stream

Besides preflight there is the **dry-run**: a short test encode (~5 seconds) using the
job's profile – **without** a live output and **without** contacting the real destination.

- Invoke: **Stream jobs → Dry-run**.
- Result: 🟢 ok / 🔴 failed, measured **encoding speed** and **FPS**, a plain-language
  message and the last log lines.
- Purpose: checks that the source decodes and the profile encodes, and estimates load.

> ⚠️ **Speed < 1.0×** in the dry-run means the machine can't keep real time →
> [Performance](/docs/en/troubleshooting/performance.md).

## Notes

> 💡 Preflight uses **ffprobe** on the first source – network/mount sources must be
> reachable for this.

## Related pages

- [Stream jobs](/docs/en/user-guide/streams.md)
- [Stream not starting](/docs/en/troubleshooting/stream-not-starting.md)

---
_Last reviewed: 2026-06-29 · Status: stable_
