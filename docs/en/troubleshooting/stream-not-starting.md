---
title: "Stream not starting"
description: "Diagnose when a stream won't start."
lang: en
audience: "Operators / Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Stream not starting

> When a stream job doesn't move to `running` after you click "Start".

**Audience:** operators / administrators.

## Diagnose in 4 steps

1. **Run preflight.** Red items point to the blocking cause (source unreadable, no video,
   missing output URL/stream key, no disk space).
2. **Open live logs.** The first red line + hint banner usually names the cause.
3. **Check the command preview** (`⌘`): is the input URI correct? Is an output missing?
4. **Check the process-manager log:**
   ```bash
   docker compose logs -f process-manager
   ```

## Common causes

| Cause | Fix |
| --- | --- |
| No active output | Enable at least one output in the stream editor |
| Destination without URL/stream key | Complete the [destination](/docs/en/user-guide/platforms.md) |
| Source unreachable | [Test/mount the source](/docs/en/user-guide/sources-storage.md) |
| FFmpeg parameter error | [FFmpeg errors](/docs/en/troubleshooting/ffmpeg-errors.md) |
| Redis unreachable (control channel) | [Docker problems](/docs/en/troubleshooting/docker.md) |

## Background

The start flow is: **backend → Redis (`castcore:control`) → process manager → FFmpeg**.
If the status stays `starting`, check that `process-manager` and `redis` are running
(`docker compose ps`).

## Related pages

- [Preflight checks](/docs/en/user-guide/preflight-checks.md)
- [Process manager](/docs/en/developer-guide/process-manager.md)

---
_Last reviewed: 2026-06-24 · Status: stable_
