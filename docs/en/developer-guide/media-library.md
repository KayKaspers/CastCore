---
title: "Media library (developer)"
description: "Scan/ffprobe pipeline of the media library."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# Media library (developer)

> Structure of the scan/index pipeline. Usage: [Media library](/docs/en/user-guide/media-library.md).

**Audience:** developers.

## Pipeline

`media_service.scan_source(db, source)`:

1. Walks the source's effective path (`os.walk`).
2. Classifies by extension (`video`/`audio`/`image`/`other`), records size/mtime.
3. **Incremental:** unchanged files (size + mtime) are skipped.
4. For media: **ffprobe** (JSON) → container/codecs/resolution/fps/bitrate into
   `media_probe_data`; sets `streamable` + `problem_flags`.

## Models

`media_library_items` (1:1) `media_probe_data`. Unique per `(storage_source_id, rel_path)`.

## Reuse

The function is transport-agnostic and can later be called by the **worker** (arq) for
large libraries in the background.

## ffprobe

Invoked as an argument list (`-v error -print_format json -show_streams -show_format`),
with a per-file timeout.

## Related pages

- [Media library (UI)](/docs/en/user-guide/media-library.md) · [API: media library](/docs/en/api/media-library.md)

---
_Last reviewed: 2026-06-24 · Status: stable_
