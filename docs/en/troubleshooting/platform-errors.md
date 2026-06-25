---
title: "Platform errors"
description: "RTMP rejected, wrong stream key, API errors."
lang: en
audience: "Operators / Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Platform errors

> When the stream transport to a platform (Twitch/YouTube/…) fails.

**Audience:** operators / administrators.

## Symptom: "RTMP rejected" / connection refused

**Possible causes:** wrong **stream key**, wrong ingest **URL**, account not ready to
stream, stream already live.
**Diagnosis:** check the live logs (RTMP error line); verify the target URL and key in the
[destination](/docs/en/user-guide/platforms.md).
**Fix:** re-copy the stream key from the platform dashboard; set the URL correctly
(e.g. `rtmp://…/app`). The key is stored encrypted – just re-enter it.

## Symptom: no video / no audio on the platform

**Causes:** input has no video/audio stream; codec not platform-compatible.
**Fix:** run [preflight](/docs/en/user-guide/preflight-checks.md); use a re-encode profile
(`libx264`/`aac`) instead of `copy`
([FFmpeg profiles](/docs/en/reference/ffmpeg-profiles.md)).

## Symptom: wrong stream key

The live-log hint points to it. Replace the key in the destination.

## Symptom: metadata/thumbnail not set

Transport (FFmpeg) and metadata are separate. Maintain title/description/thumbnail under
**Meta** per platform ([Metadata & thumbnails](/docs/en/user-guide/metadata-thumbnails.md)).

## Relevant logs

```bash
docker compose logs -f process-manager
```
In the UI: **Stream jobs → Live logs**.

## Related pages

- [Platforms](/docs/en/user-guide/platforms.md)
- [Metadata & thumbnails](/docs/en/user-guide/metadata-thumbnails.md)

---
_Last reviewed: 2026-06-24 · Status: stable_
