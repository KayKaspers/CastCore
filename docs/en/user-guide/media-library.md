---
title: "Media library"
description: "Scan sources, index media via ffprobe and pick them as inputs."
lang: en
audience: "Users / Operators"
status: stable
lastReviewed: 2026-06-24
---

# Media library

> The media library scans your sources, analyses each file with **ffprobe** and makes
> them searchable and available as stream inputs.

**Audience:** users / operators. UI area: **Media library** (`/media`).

## Step by step

1. Pick a **source** at the top (from [Sources/storage](/docs/en/user-guide/sources-storage.md)).
2. Click **Scan**. CastCore walks the files, indexes them and reads codec, resolution,
   framerate, duration and bitrate via ffprobe.
3. Narrow the list with **search** and the **"streamable only"** filter.
4. Click **"copy path"** on a file and use the path in the
   [stream editor](/docs/en/user-guide/stream-editor.md) or in a
   [playlist](/docs/en/user-guide/playlists.md).

## Columns

| Column | Meaning |
| --- | --- |
| **File** | File name + relative path; **stream** badge = streamable. |
| **Codec** | Video/audio codec from ffprobe. |
| **Resolution** | Width × height (+ FPS). |
| **Duration / size** | Length and file size. |

## Notes

> 💡 The scan is **incremental** – unchanged files are skipped.

> ⚠️ Files marked not streamable usually lack video/audio or are unreadable → see
> [FFmpeg errors](/docs/en/troubleshooting/ffmpeg-errors.md).

## Related pages

- [Sources / storage](/docs/en/user-guide/sources-storage.md)
- [Playlists](/docs/en/user-guide/playlists.md)
- [Stream editor](/docs/en/user-guide/stream-editor.md)

---
_Last reviewed: 2026-06-24 · Status: stable_
