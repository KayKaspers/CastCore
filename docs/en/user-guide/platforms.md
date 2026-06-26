---
title: "Platforms"
description: "Manage output destinations and platforms (Twitch, YouTube, RTMP)."
lang: en
audience: "Users / Operators"
status: stable
lastReviewed: 2026-06-24
---

# Platforms

> A **destination** describes **where** a stream is sent – a platform (Twitch/YouTube/
> Kick/…), your own RTMP server, an HLS/preview output or a local recording.

**Audience:** users / operators. UI area: **Resources** and inside the stream job.

## Destination fields

| Field | Meaning |
| --- | --- |
| **Name** | Display name. |
| **Kind** | `platform`, `rtmp`, `hls`, `recording`, `preview`. |
| **URL** | Ingest/output URL (e.g. `rtmp://…/app`). |
| **Stream key** | Secret key – stored encrypted, **write-only**. |

For `platform`/`rtmp`, the stream key is securely appended to the URL on start.

## Separating transport and metadata

CastCore deliberately separates:

- **FFmpeg / destination** = transport (URL + stream key).
- **[Platform metadata](/docs/en/user-guide/metadata-thumbnails.md)** = title,
  description, category, tags, thumbnail.

## Step by step

1. Under **Resources** create a destination (name, kind, URL, optional stream key).
2. Assign the destination to an output in the
   [stream editor](/docs/en/user-guide/stream-editor.md).
3. Optionally maintain per-platform
   [metadata](/docs/en/user-guide/metadata-thumbnails.md).

## Notes

> 🔐 Stream keys are stored encrypted and **masked** in previews/logs. Externally only
> *whether* a key is set is visible.

## If something fails

- [Platform errors](/docs/en/troubleshooting/platform-errors.md) (RTMP rejected, wrong key)

## Related pages

- [Metadata & thumbnails](/docs/en/user-guide/metadata-thumbnails.md)
- [Stream editor](/docs/en/user-guide/stream-editor.md)
- [Platform OAuth (YouTube/Twitch)](/docs/en/admin-guide/platform-oauth.md)

---
_Last reviewed: 2026-06-24 · Status: stable_
