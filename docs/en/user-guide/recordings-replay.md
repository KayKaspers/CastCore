---
title: "Recordings & replay"
description: "Record streams, manage and download recordings."
lang: en
audience: "Users / Operators"
status: stable
lastReviewed: 2026-06-24
---

# Recordings & replay

> CastCore can record any stream to MP4 in parallel. Recordings appear with duration,
> size and status in the replay area.

**Audience:** users / operators. UI area: **Recordings / replay** (`/recordings`).

## Enable recording

1. In the [stream editor](/docs/en/user-guide/stream-editor.md) enable the **recording**
   option (or toggle it on an existing job).
2. **Start** the job – alongside the live outputs a recording is created with a
   timestamped filename in the recordings directory.
3. On **stop** the recording is finalized (size, duration, status `completed`).

## Replay list

| Column | Meaning |
| --- | --- |
| **File** | Timestamped filename + start time. |
| **Status** | `recording` (in progress), `completed`, `failed`. |
| **Duration / size** | Length and file size. |
| **↓** | Download (only after completion). |

## Retention

A **retention period (days)** can be set per job. The `retention_until` field is stored;
automatic cleanup is handled by the [scheduler](/docs/en/user-guide/settings.md).

## Notes

> 💡 Recordings live in `RECORDINGS_DIR` (see
> [Environment variables](/docs/en/reference/environment-variables.md)).

## Related pages

- [Stream editor](/docs/en/user-guide/stream-editor.md)
- [Backup & restore](/docs/en/user-guide/backup-restore.md)

---
_Last reviewed: 2026-06-24 · Status: stable_
