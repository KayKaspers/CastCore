---
title: "Process manager"
description: "Supervision of long-running FFmpeg processes."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# Process manager

> A dedicated service (`process_manager/`) that starts, supervises and stops the
> long-running FFmpeg stream processes.

**Audience:** developers.

## How it works

1. Subscribes to the Redis channel **`castcore:control`** and receives
   `{action: start|stop|restart, output_id, job_id, argv}`.
2. Spawns FFmpeg via `asyncio.create_subprocess_exec(*argv)` (**shell-free**) – one
   process per active output.
3. Pumps stderr/stdout **line by line** to **`castcore:logs:<job_id>`**, parses progress
   (fps/bitrate/speed) and samples CPU/RSS via psutil → **`castcore:status`**.
4. Recognises failure patterns and attaches a translatable **hint** code (health assistant).

## Interplay with the backend

The backend **status consumer** reads `castcore:status`, writes `process_status`,
reconciles job/channel status, fires notifications and drives
[self-healing](/docs/en/user-guide/streams.md).

## Channels & recordings

Channels use the FFmpeg concat demuxer (loop → HLS); recordings are synthetic mp4 outputs.
Both are supervised through the same control channel.

## Related pages

- [FFmpeg command builder](/docs/en/developer-guide/ffmpeg-command-builder.md)
- [WebSockets / SSE](/docs/en/developer-guide/websocket-sse.md)
- [Architecture](/docs/en/developer-guide/architecture.md)

---
_Last reviewed: 2026-06-24 · Status: stable_
